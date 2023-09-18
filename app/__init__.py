from flask import Flask
from .site.routes import site
from .authentication.routes import auth
from .api.routes import api
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from models import db as root_db, login_manager, ma
from flask_cors import CORS
from helpers import JSONEncoder

# from jinja2 import FileSystemLoader


app = Flask(__name__)


# loader = FileSystemLoader("static")

app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(api)
app.config.from_object(Config)

root_db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
#                           'signin' 
ma.init_app(app)

migrate = Migrate(app, root_db, compare_type=True)
app.json_encoder = JSONEncoder
CORS(app)