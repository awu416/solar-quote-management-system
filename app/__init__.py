from flask import Flask

from config import Config
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models

    from app.blueprints.main import main_bp
    from app.blueprints.customers import customers_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.products import products_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)

    return app