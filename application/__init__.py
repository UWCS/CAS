from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

engine = create_engine(app.config.get('DATABASE_URI'), convert_unicode=True)

db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def init_db():
    """Create all the models in the database."""
    from models import *
    Base.metadata.create_all(bind=engine)

from application.auth_service import service
from core_auth import login
app.register_blueprint(service)
