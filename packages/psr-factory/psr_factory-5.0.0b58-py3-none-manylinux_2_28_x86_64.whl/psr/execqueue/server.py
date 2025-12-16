import hashlib
import os
import queue
import shutil
import sys
import threading
import time
import zipfile
import subprocess
import shlex
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    jsonify,
    send_file
)
import ulid


import psr.runner
import psr.cloud

from psr.execqueue.config import *
from psr.execqueue import db

_execution_queue = queue.Queue()
_cloud_upload_queue = queue.Queue()


os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(LOCAL_RESULTS_FOLDER, exist_ok=True)
os.makedirs(CLOUD_RESULTS_FOLDER, exist_ok=True)
os.makedirs(TEMPORARY_UPLOAD_FOLDER, exist_ok=True)


load_dotenv()


try:
    client = psr.cloud.Client(cluster=psrcloud_cluster, verbose=True)
except psr.cloud.CloudInputError as e:
    print(f"Error connecting to PSR Cloud. Check user credentials: {e}")
    exit(1)

_cloud_execution_case_map = {}

app = Flask(__name__, root_path=os.getcwd())
session = None


def get_file_checksum(file_path: str) -> str:
    with open(file_path, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()


def run_local_case(execution_id: str, case_path: str):
    global session
    success = False
    try:
        psr.runner.run_sddp(case_path, sddp_path, parallel_run=False)
        success = True
    except RuntimeError as e:
        print(f"Error running {execution_id}: {e}")

    status = db.LOCAL_EXECUTION_FINISHED if success else db.LOCAL_EXECUTION_ERROR
    db.update_local_execution_status(session, execution_id, status)


def _ensure_case_workdir(case_id: str) -> str:
    """Ensure a working directory exists at uploads/<case_id> with extracted contents.
    If it does not exist or is empty, extract the uploaded zip there.
    Returns the absolute path to the working directory.
    """
    workdir = os.path.join(UPLOADS_FOLDER, case_id)
    zip_upload_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    os.makedirs(workdir, exist_ok=True)

    # If directory is empty or looks incomplete, (re)extract
    try:
        if not os.listdir(workdir):
            with zipfile.ZipFile(zip_upload_path, 'r') as zip_ref:
                zip_ref.extractall(workdir)
    except FileNotFoundError:
        # If there's no zip, still return folder (may be pre-populated)
        pass
    return workdir


def run_local_module(execution_id: str, case_id: str, module_name: str) -> int:
    """Run a configured module locally inside the case's upload workdir.
    Returns process return code (0=success, non-zero=failure).
    Updates LocalExecution status accordingly.
    """
    global session
    # Fetch module configuration
    module_cfg = MODULES.get(module_name) if isinstance(MODULES, dict) else None
    if not module_cfg or 'command' not in module_cfg:
        print(f"Module '{module_name}' not configured.")
        db.update_local_execution_status(session, execution_id, db.LOCAL_EXECUTION_ERROR)
        return 1

    workdir = _ensure_case_workdir(case_id)

    # Build command and log file path
    cmd_tmpl = module_cfg.get('command')
    # Allow placeholders
    cmd = cmd_tmpl.format(case_path=workdir, case_id=case_id, module=module_name)
    log_name = module_cfg.get('log_file', f"module_{module_name}.log")
    log_path = os.path.join(workdir, log_name)

    print(f"Running module '{module_name}' for case {case_id} in {workdir}")
    print(f"Command: {cmd}")

    rc = 1
    try:
        # Prefer to run without shell to avoid platform-specific exit code mappings
        # If the command starts with 'python' or references .py, build argv accordingly
        argv = None
        # Heuristic: if command contains .py, run with current Python executable
        if '.py' in cmd:
            parts = shlex.split(cmd)
            # If the command already starts with python, use as-is; else prepend sys.executable
            if parts[0].endswith('python') or parts[0].endswith('python.exe'):
                argv = parts
            else:
                argv = [sys.executable] + parts
        else:
            argv = shlex.split(cmd)

        with open(log_path, 'a', encoding='utf-8', errors='ignore') as logf:
            proc = subprocess.Popen(
                argv,
                cwd=workdir,
                stdout=logf,
                stderr=logf,
            )
            rc = proc.wait()

        # Now rc follows the subprocess return code semantics: 0 success, non-zero failure
        status = db.LOCAL_EXECUTION_FINISHED if rc == 0 else db.LOCAL_EXECUTION_ERROR
        db.update_local_execution_status(session, execution_id, status)
    except Exception as e:
        print(f"Error running module {module_name} for case {case_id}: {e}")
        db.update_local_execution_status(session, execution_id, db.LOCAL_EXECUTION_ERROR)
        rc = 1
    return rc


def _copy_tree(src: str, dst: str):
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target_root = os.path.join(dst, rel) if rel != '.' else dst
        os.makedirs(target_root, exist_ok=True)
        for d in dirs:
            os.makedirs(os.path.join(target_root, d), exist_ok=True)
        for f in files:
            s = os.path.join(root, f)
            t = os.path.join(target_root, f)
            try:
                shutil.copy2(s, t)
            except Exception:
                # Best-effort copy; skip problematic files
                pass


def initialize_db():
    session, engine = db.initialize()
    return session


def run_cloud_case(execution_id: str, case_path: str):
    global client
    # Run the case
    case = psr.cloud.Case(
        name="LSEG Server "+ execution_id,
        data_path=case_path,
        program="SDDP",
        program_version = "17.3.9",
        execution_type="Default",
        memory_per_process_ratio='2:1',
        price_optimized=False,
        number_of_processes=64,
        repository_duration=1,
    )
    case_id = client.run_case(case)

    return str(case_id)


def process_local_execution_queue():
    global session
    while True:
        item = _execution_queue.get()
        try:
            # Detect item type (backward compatibility for tuple)
            if isinstance(item, dict) and item.get('type') == 'module':
                execution_id = item['execution_id']
                case_id = item['case_id']
                module_name = item['module']
                print(f"Processing module {module_name} for case {case_id} (exec {execution_id})...")
                run_local_module(execution_id, case_id, module_name)
            else:
                if isinstance(item, (list, tuple)):
                    execution_id, case_id = item
                else:
                    execution_id = item.get('execution_id')
                    case_id = item.get('case_id')

                print(f"Processing case execution {execution_id} for case {case_id}...")

                # Wait for running modules to finish; abort if any failed
                wait_loops = 0
                while db.any_running_modules_for_case(session, case_id):
                    print(f"Case {case_id} has running modules; waiting...")
                    time.sleep(5)
                    wait_loops += 1
                    # Safety: avoid infinite wait in worker
                    if wait_loops > 240:  # ~20 minutes
                        break

                # Check last execution per distinct module: if any last module execution failed, mark error
                failing_modules = []
                for mname in db.get_distinct_module_names_for_case(session, case_id):
                    last = db.last_module_execution_for_case(session, case_id, mname)
                    if last and last.status == db.LOCAL_EXECUTION_ERROR:
                        failing_modules.append(mname)

                if failing_modules:
                    print(f"Case {case_id} has failed modules {failing_modules}; marking local execution {execution_id} as error and skipping run")
                    db.update_local_execution_status(session, execution_id, db.LOCAL_EXECUTION_ERROR)
                else:
                    # Prepare a dedicated results folder copying the current working directory (with module changes)
                    execution_extraction_path = os.path.join(LOCAL_RESULTS_FOLDER, execution_id)
                    os.makedirs(execution_extraction_path, exist_ok=True)
                    workdir = _ensure_case_workdir(case_id)
                    _copy_tree(workdir, execution_extraction_path)
                    # Run SDDP
                    run_local_case(execution_id, execution_extraction_path)

        except Exception as e:
            # Use safe prints in case execution_id isn't available
            try:
                print(f"Error processing {execution_id}: {e}")
            except Exception:
                print(f"Error processing item: {e}")
        finally:
            _execution_queue.task_done()


threading.Thread(target=process_local_execution_queue, daemon=True).start()


def process_cloud_execution_queue():
    global client
    global session
    while True:
        cloud_upload_id, case_id = _cloud_upload_queue.get()
        try:
            print(f"Processing {cloud_upload_id}...")
            # Wait for running modules to finish; abort if any failed
            wait_loops = 0
            while db.any_running_modules_for_case(session, case_id):
                print(f"Case {case_id} has running modules; waiting before cloud run...")
                time.sleep(5)
                wait_loops += 1
                if wait_loops > 240:  # ~20 minutes
                    break
            # Block if the last execution of any distinct module failed
            failing_modules = []
            for mname in db.get_distinct_module_names_for_case(session, case_id):
                last = db.last_module_execution_for_case(session, case_id, mname)
                if last and last.status == db.LOCAL_EXECUTION_ERROR:
                    failing_modules.append(mname)
            if failing_modules:
                print(f"Case {case_id} has failing modules in last execution {failing_modules}; skipping cloud run for upload {cloud_upload_id}")
                # Nothing else to do; do not run in the cloud
                continue
            # Prepare temp folder by copying current working directory (with module changes)
            tmp_extraction_path = os.path.join(TEMPORARY_UPLOAD_FOLDER, cloud_upload_id)
            workdir = _ensure_case_workdir(case_id)
            if os.path.isdir(tmp_extraction_path):
                shutil.rmtree(tmp_extraction_path, ignore_errors=True)
            os.makedirs(tmp_extraction_path, exist_ok=True)
            _copy_tree(workdir, tmp_extraction_path)

            # Run SDDP
            repository_id = run_cloud_case(cloud_upload_id, tmp_extraction_path)

            #delete the extraction path folder recursively
            shutil.rmtree(tmp_extraction_path)

            execution_extraction_path = os.path.join(CLOUD_RESULTS_FOLDER, repository_id)
            if os.path.isdir(execution_extraction_path):
                shutil.rmtree(execution_extraction_path, ignore_errors=True)
            os.makedirs(execution_extraction_path, exist_ok=True)
            _copy_tree(workdir, execution_extraction_path)

            db.register_cloud_execution(session, repository_id, cloud_upload_id, case_id)

        except Exception as e:
            print(f"Error processing {cloud_upload_id}: {e}")
        finally:
            _cloud_upload_queue.task_done()


threading.Thread(target=process_cloud_execution_queue, daemon=True).start()


def monitor_cloud_runs():
    global client
    global session

    #wait for cloud upload queue to be empty
    while not _cloud_upload_queue.empty():
        time.sleep(10)

    while True:
        if session:
            #check running executions
            for cloud_execution in db.get_runing_cloud_executions(session):
                case_id = cloud_execution.repository_id
                print(f"Checking status of {case_id}...")
                status, status_msg = client.get_status(case_id)
                if status in psr.cloud.FAULTY_TERMINATION_STATUS:
                    print(f"Execution {case_id} finished with errors")
                    db.update_cloud_execution_status(session, case_id, db.CloudStatus.ERROR.value)
                elif status == psr.cloud.ExecutionStatus.SUCCESS:
                    print(f"Execution {case_id} finished successfully")
                    db.update_cloud_execution_status(session, case_id, db.CloudStatus.FINISHED.value)

            #download finished executions
            for cloud_execution in db.get_cloud_finished_executions(session):
                repository_id = cloud_execution.repository_id
                print(f"Downloading results for {repository_id}...")
                result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
                client.download_results(repository_id, result_path)
                db.update_cloud_execution_status(session, repository_id, db.CloudStatus.RESULTS_AVAILABLE.value)
            
            #download failed executions
            for cloud_execution in db.get_cloud_failed_executions(session):
                try:
                    repository_id = cloud_execution.repository_id
                    print(f"Downloading results for {repository_id}...")
                    result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
                    client.download_results(repository_id, result_path, extensions=['log'])
                    db.update_cloud_execution_status(session, repository_id, db.CloudStatus.LOGS_AVAILABLE_ERROR.value)
                except Exception as e:
                    print(f"Error downloading results for {repository_id}: {e}")
                    print("Forcing execution to Failed downloaded execution")
                    db.update_cloud_execution_status(session, repository_id, db.CloudStatus.LOGS_AVAILABLE_ERROR.value)
                    continue
        else:
            print("Database not initialized. Retrying in 30s...")
        time.sleep(30)

threading.Thread(target=monitor_cloud_runs, daemon=True).start()

@app.route('/upload', methods=['POST'])
def upload_file():
    global session
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    case_id = str(ulid.ULID())
    zip_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    file.save(zip_path)

    checksum = get_file_checksum(zip_path)
    db.register_case(session, case_id, checksum)

    return jsonify({'case_id': case_id}), 200


# route to run an uploaded file
@app.route('/run', methods=['POST'])
def run_endpoint():
    global session
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'
    case_id = request.form.get('case_id')

    if not case_id:
        return jsonify({'error': 'Case ID not provided'}), 400

    zip_case_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    if not os.path.exists(zip_case_path):
        return jsonify({'error': 'Upload file for this case ID not found'}), 404

    # Pre-check: for each distinct module, if the last execution failed, block the run
    failing_modules = []
    for mname in db.get_distinct_module_names_for_case(session, case_id):
        last = db.last_module_execution_for_case(session, case_id, mname)
        if last and last.status == db.LOCAL_EXECUTION_ERROR:
            failing_modules.append(mname)
    if failing_modules:
        return jsonify({'error': 'Case has failed modules in last execution', 'modules': failing_modules}), 409

    if cloud_execution:
        cloud_upload_id = str(ulid.ULID())
        _cloud_upload_queue.put((cloud_upload_id, case_id))

        db.register_cloud_upload(session, case_id, cloud_upload_id)

        return jsonify({'case_id': case_id, 'cloud_upload_id': cloud_upload_id}), 200
    else:
        execution_id = str(ulid.ULID())
        _execution_queue.put((execution_id, case_id))

        db.register_local_execution(session, case_id, execution_id)
        # Mark as running explicitly
        db.update_local_execution_status(session, execution_id, db.LOCAL_EXECUTION_RUNNING)

        return jsonify({'case_id': case_id, 'execution_id': execution_id}), 200


@app.route('/run_module', methods=['POST'])
def run_module_endpoint():
    global session
    case_id = request.form.get('case_id')
    module_name = request.form.get('module') or request.form.get('module_name')

    if not case_id or not module_name:
        return jsonify({'error': 'case_id and module are required'}), 400

    # Validate case zip exists
    zip_case_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    workdir = os.path.join(UPLOADS_FOLDER, case_id)
    if not os.path.exists(zip_case_path) and not os.path.isdir(workdir):
        return jsonify({'error': 'Upload file or working directory for this case ID not found'}), 404

    # Validate module exists in config
    module_cfg = MODULES.get(module_name) if isinstance(MODULES, dict) else None
    if not module_cfg or 'command' not in module_cfg:
        return jsonify({'error': f"Module '{module_name}' not configured"}), 400

    execution_id = str(ulid.ULID())
    _execution_queue.put({'type': 'module', 'execution_id': execution_id, 'case_id': case_id, 'module': module_name})
    db.register_local_execution(session, case_id, execution_id, is_module=1, module=module_name)
    db.update_local_execution_status(session, execution_id, db.LOCAL_EXECUTION_RUNNING)

    return jsonify({'case_id': case_id, 'module': module_name, 'execution_id': execution_id}), 200


@app.route('/upload_and_run', methods=['POST'])
def upload_and_run_file():
    global session
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'

    case_id = str(ulid.ULID())
    zip_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    file.save(zip_path)
    db.register_case(session, case_id, get_file_checksum(zip_path))

    if cloud_execution:
        cloud_upload_id = str(ulid.ULID())
        _cloud_upload_queue.put((cloud_upload_id, case_id))
        db.register_cloud_upload(session, case_id, cloud_upload_id)
        return jsonify({'case_id': case_id, 'cloud_upload_id': cloud_upload_id}), 200
    else:
        execution_id = str(ulid.ULID())
        _execution_queue.put((execution_id, case_id))
        db.register_local_execution(session, case_id, execution_id)
        return jsonify({'case_id': case_id, 'execution_id': execution_id}), 200


@app.route('/status/<execution_id>', methods=['GET'])
def get_status(execution_id):
    """
    Get the status of an execution
    ---
    tags:
      - Execution
    parameters:
      - name: execution_id
        in: path
        type: string
        required: true
        description: The ID of the execution
    responses:
      200:
        description: Execution status
        schema:
          type: object
      404:
        description: Execution ID not found
    """
    global client
    global session
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'

    if cloud_execution:
        repository_id = db.get_repository_id_from_cloud_upload_id(session, execution_id)
        if repository_id is None:
            return jsonify({'error': 'Execution ID not found in Cloud'}), 404
        status = db.get_cloud_execution_status(session, repository_id)
        if status == db.CloudStatus.ERROR.value:
            status_msg = 'Execution finished with errors. Only log files will be downloaded'
        elif status == db.CloudStatus.RUNNING.value:
            status_msg = 'Execution not finished yet'
        elif status == db.CloudStatus.FINISHED.value:
            status_msg = 'Execution finished, but download not yet started from Cloud server'
        elif status == db.CloudStatus.RESULTS_AVAILABLE.value:
            status_msg = 'Execution finished and results are available to download'
        elif status == db.CloudStatus.LOGS_AVAILABLE_ERROR.value:
            status_msg = 'Execution finished with errors and log files are avaialble to download'
        else:
            status_msg = 'Unknown status'
        print(f"Cloud execution status for {execution_id} ({repository_id}): {status_msg}")
        return jsonify({'status_id': status, 'status_msg': status_msg}), 200
    else:
        status = db.get_local_execution_status(session, execution_id)
        if status == db.LOCAL_EXECUTION_ERROR:
            status_msg = 'Execution finished with errors'
        elif status != db.LOCAL_EXECUTION_FINISHED:
            status_msg = 'Execution not finished yet'
        else:
            status_msg = 'Execution finished'
        return jsonify({'status_id': status, 'status_msg': status_msg}), 200


@app.route('/results/<execution_id>', methods=['GET'])
def get_results(execution_id: str):
    global session
    global client
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'

    if cloud_execution:
        repository_id = db.get_repository_id_from_cloud_upload_id(session, execution_id)
        if repository_id is None:
            return jsonify({'error': 'Execution ID not found in Cloud'}),
        status = db.get_cloud_execution_status(session, execution_id)

        if status == db.CloudStatus.RUNNING:
            return jsonify({'error': f'{repository_id} execution not finished yet'}), 402
        elif status == db.CloudStatus.FINISHED:
            return jsonify({'error': f'{repository_id} results not available yet'}), 403
        else:
            #fazer download da pasta do resultado
            result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
            if not os.path.exists(result_path):
                return jsonify({'error': f'{repository_id} execution result folder not found'}), 404
            result_files = os.listdir(result_path)
            result_files = [f for f in result_files if os.path.isfile(os.path.join(result_path, f))]
            return jsonify({'execution_id': repository_id, 'files': result_files}), 200
    else:
        status = db.get_local_execution_status(session, execution_id)
        if status == db.LOCAL_EXECUTION_ERROR:
            return jsonify({'error': 'Execution finished with errors'}), 401
        if status != db.LOCAL_EXECUTION_FINISHED:
            return jsonify({'error': 'Execution not finished yet'}), 402
        result_path = os.path.join(LOCAL_RESULTS_FOLDER, execution_id)
        if not os.path.exists(result_path):
            return jsonify({'error': 'Execution result folder not found'}), 404
    result_files = os.listdir(result_path)
    return jsonify({'execution_id': execution_id, 'files': result_files}), 200


@app.route('/module_log/<case_id>', methods=['GET'])
def get_module_log(case_id: str):
    """Return the content of the module's fixed log file for the last module run of the case,
    or for a specific module if provided as query parameter ?module=<name>.
    """
    global session
    module_name = request.args.get('module') or request.args.get('module_name')

    # Determine module and log file name
    if not module_name:
        last = db.last_module_execution_for_case(session, case_id)
        if not last or not last.module:
            return jsonify({'error': 'No module execution found for this case'}), 404
        module_name = last.module
    module_cfg = MODULES.get(module_name) if isinstance(MODULES, dict) else None
    if not module_cfg:
        return jsonify({'error': f"Module '{module_name}' not configured"}), 400
    log_name = module_cfg.get('log_file', f"module_{module_name}.log")

    workdir = os.path.join(UPLOADS_FOLDER, case_id)
    if not os.path.isdir(workdir):
        # Ensure workdir is created (may extract zip if needed)
        workdir = _ensure_case_workdir(case_id)
    log_path = os.path.join(workdir, log_name)
    if not os.path.exists(log_path):
        return jsonify({'error': 'Log file not found', 'module': module_name, 'log': log_name}), 404

    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<execution_id>/<file>', methods=['GET'])
def download_file(execution_id: str, file):
    global session

    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'
    
    if cloud_execution:
        repository_id = db.get_repository_id_from_cloud_upload_id(session, execution_id)
        result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
    else:
        result_path = os.path.join(LOCAL_RESULTS_FOLDER, execution_id)
    if not os.path.exists(result_path):
        if cloud_execution:
            msg = f'{repository_id} execution result folder not found'
        else:
            msg = f'Execution result folder not found'
        return jsonify({'error': msg}), 404

    file_path = os.path.normpath(os.path.join(result_path, file)).replace("\\", "/")
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
       return send_file(file_path, download_name=file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting server...")
    session = initialize_db()
    try:
        app.run(host=settings.get("host", DEFAULT_HOST), debug=FLASK_DEBUG,
                port=settings.get("port", DEFAULT_PORT),
                threaded=True,
                use_reloader=False,)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

