from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mysqlpool import MySQLPool

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///database.db')
session = Session(engine)


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = '#r5zfpmleLLM043l$'

db = SQLAlchemy(app)
#db = MySQLPool(app)
migrate = Migrate(app, db)
migrate.init_app(app, db, render_as_batch=True)
bcrypt = Bcrypt(app)
