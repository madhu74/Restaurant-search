from model.user import Base, engine
from app import app

@app.before_first_request
def db_tablessetup():
    Base.metadata.create_all(engine)
