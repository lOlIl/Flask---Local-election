from app import app

from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
