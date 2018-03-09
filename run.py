from model.user import Base, engine
from app import app

@app.before_first_request
def setup_database():
    Base.metadata.create_all(engine)
