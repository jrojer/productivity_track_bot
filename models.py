from sqlalchemy import Column, Integer, String, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                                self.name, self.fullname, self.nickname)


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_name = Column(String(50),nullable=False)
    datetime = Column(DateTime, nullable=False)
    emotions = Column(String(500))
    energy = Column(String(500))
    attention = Column(String(500))
    conscientiousness = Column(String(500))
    procrastination = Column(String(500))
    stress = Column(String(500))
    regime = Column(String(500))
    body = Column(String(500))
    comment = Column(String(500))
    rating = Column(Integer)

    def __repr__(self):
        return "<Record(user_id='%s', user_name='%s', datetime='%s')>" % (                   self.user_id, self.user_name, self.datetime, self.nickname)

