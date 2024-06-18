from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import config as C

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = C.DATA_BASE_URI
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = C.SECRET_KEY
app.config['EXECUTOR_TYPE'] = 'process'
app.config['EXECUTOR_MAX_WORKERS'] = C.WORKERS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from routes import *

with app.app_context():
    from models import Dataset, User
    if not os.path.exists('database.db'):
        db.create_all()

    datasets = Dataset.query.all()
    for dataset in datasets:
        if not User.query.get(dataset.user_id) or not os.path.exists(dataset.path):
            db.session.delete(dataset)
    db.session.commit()

