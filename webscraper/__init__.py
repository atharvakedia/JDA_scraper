from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///JDA_schemes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Lightning-Mcqueen-Kha-Chow'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from webscraper import routes, models