from models import db

def init_db():
    db.bind(provider='sqlite', filename='data/db.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)
