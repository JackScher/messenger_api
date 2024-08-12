import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .logger import log
from .database import db
from .routes import post_blueprint, auth_blueprint, comment_blueprint


def create_app(**kwargs) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    log(log.INFO, "App initialized: [%s]", app.__class__.__name__)

    # Database.
    if kwargs:
        database_config = kwargs["SQLALCHEMY_DATABASE_URI"]
    else:
        database_config = os.environ.get("SQLALCHEMY_DATABASE_URI")
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Migrations.
    migrate = Migrate(app, db)

    # JWT.
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    # Register blueprints.
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(post_blueprint, url_prefix='/api/post')
    app.register_blueprint(comment_blueprint, url_prefix='/api/comment')

    return app
