import pytest
from app import create_app, db
from app.models import Usuario, Libro, Categoria


@pytest.fixture
def app():
    app = create_app("config.TestConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario_normal(app):
    with app.app_context():
        u = Usuario(nombre="Juan Pérez", email="juan@test.com")
        u.set_password("clave123")
        db.session.add(u)
        db.session.commit()
        return u.id


@pytest.fixture
def usuario_admin(app):
    with app.app_context():
        u = Usuario(nombre="Admin", email="admin@test.com", es_admin=True)
        u.set_password("admin123")
        db.session.add(u)
        db.session.commit()
        return u.id


@pytest.fixture
def libro_demo(app):
    with app.app_context():
        libro = Libro(titulo="Clean Code", autor="Robert C. Martin",
                       copias_totales=2, copias_disponibles=2)
        db.session.add(libro)
        db.session.commit()
        return libro.id


def login(client, email, password):
    return client.post(
        "/auth/login", data={"email": email, "password": password}, follow_redirects=True
    )
