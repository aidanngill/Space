import os
from marshmallow import ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix

from flask import Flask
from flask_cors import CORS

from . import config
from .extensions import db, limiter, migrate

from .resources.auth import auth
from .resources.base import base
from .resources.tool import tool
from .resources.user import user

def create_app(_config=config.Production):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    app.config.from_object(_config)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    file_dir = app.config.get("UPLOAD_FOLDER", "./files/")

    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    app.register_blueprint(auth)
    app.register_blueprint(base)
    app.register_blueprint(tool)
    app.register_blueprint(user)

    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={"*": {"origins": "*"}})

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return {
            "success": False,
            "message": error.messages
        }, 400

    return app
