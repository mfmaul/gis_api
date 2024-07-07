# application/__init__.py
import config
import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    environment_configuration = os.environ['CONFIGURATION_SETUP']
    app.config.from_object(environment_configuration)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['RESTX_MASK_SWAGGER'] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Register blueprints
        from .apis.user_apis import user_apis_blueprint
        app.register_blueprint(user_apis_blueprint, url_prefix='/users')
        # app.register_blueprint(user_apis_blueprint, url_prefix='/' if os.environ.get('DEPLOY_PLATFORM') != 'DEV' else '/users')

        from .apis.gis_apis import gis_apis_blueprint
        app.register_blueprint(gis_apis_blueprint, url_prefix='/giss')

        return app
