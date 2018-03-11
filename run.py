from model.user import Base, engine
from app import app

@app.before_first_request
def setup_database():
    if not engine.dialect.has_table(engine, 'users'):
        Base.metadata.create_all(engine)
