import datetime
from enum import Enum
from typing import (
    List,
    Optional
)

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    TIMESTAMP,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from psr.execqueue.config import *

class CloudStatus(Enum):
    RUNNING = 1
    FINISHED = 3
    ERROR = 4
    RESULTS_AVAILABLE = 5
    LOGS_AVAILABLE_ERROR = 6


DB_NAME = "app.db"


LOCAL_EXECUTION_RUNNING = 0
LOCAL_EXECUTION_FINISHED = 1
LOCAL_EXECUTION_ERROR = 2


def get_db_path():
    return os.path.join(STORAGE_PATH, DB_NAME)


Base = declarative_base()


class Case(Base):
    __tablename__ = 'cases'

    case_id = Column(String(26), primary_key=True)
    upload_time = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    checksum = Column(Text)
    removed = Column(Integer, default=0)

    local_executions = relationship("LocalExecution", back_populates="case")
    cloud_uploads = relationship("CloudUpload", back_populates="case")
    cloud_executions = relationship("CloudExecution", back_populates="case")


class LocalExecution(Base):
    __tablename__ = 'local_executions'

    execution_id = Column(String(26), primary_key=True)
    case_id = Column(String(26), ForeignKey('cases.case_id'))
    start_time = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    finish_time = Column(TIMESTAMP)
    status = Column(Integer, default=LOCAL_EXECUTION_RUNNING)
    # Module-related fields
    is_module = Column(Integer, default=0)  # 0 = no, 1 = yes
    module = Column(String(128))  # optional module name

    case = relationship("Case", back_populates="local_executions")


class CloudUpload(Base):
    __tablename__ = 'cloud_uploads'

    cloud_upload_id = Column(String(26), primary_key=True)
    case_id = Column(String(26), ForeignKey('cases.case_id'))
    start_time = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="cloud_uploads")
    cloud_executions = relationship("CloudExecution", back_populates="cloud_upload")


class CloudExecution(Base):
    __tablename__ = 'cloud_executions'

    repository_id = Column(Integer, primary_key=True)
    cloud_upload_id = Column(String(26), ForeignKey('cloud_uploads.cloud_upload_id'))
    case_id = Column(String(26), ForeignKey('cases.case_id'))
    start_time = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    archived = Column(Integer, default=0)
    status = Column(Integer, default=0)

    case = relationship("Case", back_populates="cloud_executions")
    cloud_upload = relationship("CloudUpload", back_populates="cloud_executions")


def initialize():
    # Create the SQLite database and create the tables
    _db_path = get_db_path()
    _create_db = not os.path.exists(_db_path)
    engine = create_engine(f'sqlite:///{_db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    if _create_db:
        Base.metadata.create_all(engine)
        _first_time_setup(session)
    else:
        # Basic migration: add columns if missing
        # Note: SQLite supports limited ALTERs; use simple try/except for idempotency
        from sqlalchemy import inspect
        inspector = inspect(engine)
        cols = {c['name'] for c in inspector.get_columns('local_executions')}
        with engine.connect() as conn:
            if 'is_module' not in cols:
                try:
                    conn.execute("ALTER TABLE local_executions ADD COLUMN is_module INTEGER DEFAULT 0")
                except Exception:
                    pass
            if 'module' not in cols:
                try:
                    conn.execute("ALTER TABLE local_executions ADD COLUMN module VARCHAR(128)")
                except Exception:
                    pass

    return session, engine


def close(session):
    session.close()


def _first_time_setup(session):
    pass


def register_case(session, case_id, checksum):
    case = Case(case_id=case_id,
                checksum=checksum,
                upload_time=datetime.datetime.utcnow()
                )
    session.add(case)
    session.commit()
    # registry.configure()

    return case


def register_local_execution(session, case_id: str, execution_id: str, *, is_module: int = 0, module: Optional[str] = None):
    case = session.query(Case).filter(Case.case_id == case_id).first()
    local_execution = LocalExecution(
        execution_id=execution_id,
        case_id=case_id,
        start_time=datetime.datetime.utcnow(),
        is_module=is_module,
        module=module,
    )
    case.local_executions.append(local_execution)
    session.commit()
    return local_execution


def get_case_id_from_execution_id(session, execution_id: str) -> Optional[str]:
    local_execution = session.query(LocalExecution).filter(LocalExecution.execution_id == execution_id).first()
    return local_execution.case_id if local_execution else None


def update_local_execution_status(session, execution_id: str, status: int):
    local_execution = session.query(LocalExecution).filter(LocalExecution.execution_id == execution_id).first()
    if local_execution:
        if status not in [LOCAL_EXECUTION_FINISHED, LOCAL_EXECUTION_ERROR,
                      LOCAL_EXECUTION_RUNNING]:
            raise ValueError("Wrong status for update.")
        local_execution.status = status
        if status in [LOCAL_EXECUTION_FINISHED, LOCAL_EXECUTION_ERROR]:
            local_execution.finish_time = datetime.datetime.utcnow()
        session.commit()
        return True

def update_cloud_execution_status(session, repository_id: int, status: int):
    cloud_execution = session.query(CloudExecution).filter(CloudExecution.repository_id == repository_id).first()
    if cloud_execution:
        if CloudStatus(status) not in CloudStatus:
            raise ValueError("Wrong status for update.")
        cloud_execution.status = status
        session.commit()
        return True
    
def get_local_execution_status(session, execution_id: str) -> Optional[int]:
    local_execution = session.query(LocalExecution).filter(LocalExecution.execution_id == execution_id).first()
    return local_execution.status if local_execution else None

def any_running_modules_for_case(session, case_id: str) -> bool:
    return session.query(LocalExecution).filter(
        LocalExecution.case_id == case_id,
        LocalExecution.is_module == 1,
        LocalExecution.status == LOCAL_EXECUTION_RUNNING
    ).count() > 0

def any_failed_modules_for_case(session, case_id: str) -> bool:
    return session.query(LocalExecution).filter(
        LocalExecution.case_id == case_id,
        LocalExecution.is_module == 1,
        LocalExecution.status == LOCAL_EXECUTION_ERROR
    ).count() > 0

def last_module_execution_for_case(session, case_id: str, module: Optional[str] = None) -> Optional[LocalExecution]:
    q = session.query(LocalExecution).filter(
        LocalExecution.case_id == case_id,
        LocalExecution.is_module == 1
    )
    if module:
        q = q.filter(LocalExecution.module == module)
    return q.order_by(LocalExecution.start_time.desc()).first()

def get_distinct_module_names_for_case(session, case_id: str) -> List[str]:
    rows = session.query(LocalExecution.module).filter(
        LocalExecution.case_id == case_id,
        LocalExecution.is_module == 1,
        LocalExecution.module.isnot(None)
    ).distinct().all()
    # rows is a list of tuples [(module,), ...]
    return [r[0] for r in rows if r and r[0]]


def register_cloud_upload(session, case_id: str, cloud_upload_id: str):
    case = session.query(Case).filter(Case.case_id == case_id).first()
    cloud_upload = CloudUpload(cloud_upload_id=cloud_upload_id,
                               case_id=case_id,
                               start_time=datetime.datetime.utcnow()
                               )
    case.cloud_uploads.append(cloud_upload)
    session.commit()
    return cloud_upload


def register_cloud_execution(session, repository_id: int, cloud_upload_id: str, case_id: str):
    cloud_upload = session.query(CloudUpload).filter(CloudUpload.cloud_upload_id == cloud_upload_id).first()
    cloud_execution = CloudExecution(repository_id=repository_id,
                                     cloud_upload_id=cloud_upload_id,
                                     case_id=case_id,
                                     start_time=datetime.datetime.utcnow(),
                                     status=CloudStatus.RUNNING.value
                                     )
    cloud_upload.cloud_executions.append(cloud_execution)
    session.commit()
    return cloud_execution


def get_case_id_from_cloud_execution_id(session, repository_id: int) -> Optional[str]:
    cloud_execution = session.query(CloudExecution).filter(CloudExecution.repository_id == repository_id).first()
    return cloud_execution.case_id if cloud_execution else None


def get_case_id_from_repository_id(session, repository_id: int) -> Optional[str]:
    cloud_execution = session.query(CloudExecution).filter(CloudExecution.repository_id == repository_id).first()
    return cloud_execution.case_id if cloud_execution else None

def get_repository_id_from_cloud_upload_id(session, cloud_upload_id: str) -> Optional[int]:
    cloud_execution = session.query(CloudExecution).filter(CloudExecution.cloud_upload_id == cloud_upload_id).first()
    return cloud_execution.repository_id if cloud_execution else None

def get_repository_ids_from_case_id(session, case_id: str) -> List[int]:
    cloud_executions = session.query(CloudExecution).filter(CloudExecution.case_id == case_id).all()
    return [ce.repository_id for ce in cloud_executions]

def get_runing_cloud_executions(session) -> List[CloudExecution]:
    return session.query(CloudExecution).filter(CloudExecution.status == CloudStatus.RUNNING.value).all()

def get_cloud_execution_status(session, repository_id: int) -> Optional[int]:
    cloud_execution = session.query(CloudExecution).filter(CloudExecution.repository_id == repository_id).first()
    return cloud_execution.status if cloud_execution else None

def get_cloud_finished_executions(session) -> List[CloudExecution]:
    return session.query(CloudExecution).filter(CloudExecution.status == CloudStatus.FINISHED.value).all()

def get_cloud_failed_executions(session) -> List[CloudExecution]:
    return session.query(CloudExecution).filter(CloudExecution.status == CloudStatus.ERROR.value).all()