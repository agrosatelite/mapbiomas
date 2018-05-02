from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from rsgee.conf import settings

Base = declarative_base()

class DatabaseManager():
    def __init__(self):
        self.__engine = create_engine('{0}://{1}:{2}@{3}:{4}/{5}'.format(settings.DATABASE['ENGINE'], settings.DATABASE['USER'], settings.DATABASE['PASSWORD'], settings.DATABASE['HOST'], settings.DATABASE['PORT'], settings.DATABASE['NAME']), convert_unicode=True)
    def get_session(self):
        session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=self.__engine))
        return session

    def migrate(self):
        session = self.get_session()
        from rsgee.db.models import Task, TaskLog
        Base.metadata.drop_all(bind=self.__engine)
        Base.metadata.create_all(bind=self.__engine)
        session.commit()
