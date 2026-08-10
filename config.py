import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-biblioteca-itla-p3")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'biblioteca.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Carpeta donde se guardan las imágenes subidas (libros y fotos de perfil)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB por archivo
    EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
