from flask import Flask

app = Flask(__name__)
app.config.from_object('settings.LocalConfig')

from flaskext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
