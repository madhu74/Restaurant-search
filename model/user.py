from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# engine = create_engine('mysql+cymysql://user:test@localhost')
# CREATE DATABASE testbed; run teh db schema creation command
engine = create_engine('mysql+mysqldb://user:test@localhost')

Session = sessionmaker(bind=engine)
Base = declarative_base()
db_session = Session()
class User(Base):
    """The table structure that store the user information"""
    __tablename__ = 'users'
    __table_args__ = (UniqueConstraint('email_address'), UniqueConstraint('user_name'), {'schema' : 'testbed'})
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    last_name =  Column(String(150), nullable=False)
    first_name =  Column(String(150), nullable=False)
    email_address = Column(String(250), nullable=False)
    user_name = Column(String(250), nullable=False)
    password = Column(String(500), nullable=False)
    created_date = Column(DateTime, nullable=False, default=func.now())

if __name__='main':
    Base.metadata.create_all(engine)
