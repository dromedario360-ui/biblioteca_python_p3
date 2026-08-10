import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    os.makedirs(
        os.path.join(app.config["UPLOAD_FOLDER"], "libros"), exist_ok=True
    )
    os.makedirs(
        os.path.join(app.config["UPLOAD_FOLDER"], "perfiles"), exist_ok=True
    )

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.libros import libros_bp
    from app.routes.prestamos import prestamos_bp
    from app.routes.categorias import categorias_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(libros_bp, url_prefix="/libros")
    app.register_blueprint(prestamos_bp, url_prefix="/prestamos")
    app.register_blueprint(categorias_bp, url_prefix="/categorias")

    with app.app_context():
        db.create_all()

    return app
