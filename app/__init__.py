from flask import Flask

from config import Config

from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from app import models
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    return app