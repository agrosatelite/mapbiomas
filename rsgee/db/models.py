import enum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Enum

from rsgee.db.factory import Base

class TaskTypes(enum.Enum):
    GENERATION = 1
    CLASSIFICATION = 2
    POSTPROCESSING = 3


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    model = Column(String)
    type = Column(Enum(TaskTypes))
    specifications = Column(String)
    state = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)


class TaskLog(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    task = Column(Integer, ForeignKey('tasks.id'))
    state = Column(String)
    date = Column(DateTime)
    info = Column(String)
