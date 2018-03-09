from model.user import Base, engine
from app import app

Base.metadata.create_all(engine)
