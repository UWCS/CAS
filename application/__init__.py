from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

APP_NAME = 'UWCS_CoreAuth'

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

engine = create_engine(app.config.get('DATABASE_URI'), convert_unicode=True)

db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def init_db():
    """Create all the models in the database."""
    import application.models
    Base.metadata.create_all(bind=engine)

from core_auth import login

from application.auth_service import service as auth
app.register_blueprint(auth)

from application.u2f_service import service as u2f
app.register_blueprint(u2f, url_prefix='/u2f')

from application.dashboard_service import service as dashboard
app.register_blueprint(dashboard, url_prefix='/dashboard')
