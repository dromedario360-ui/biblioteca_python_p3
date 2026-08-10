from app import db
from app.models import Libro
from tests.conftest import login


def test_listar_libros_vacio(client):
    resp = client.get("/libros/")
    assert resp.status_code == 200
    assert "No hay libros registrados".encode("utf-8") in resp.data


def test_admin_puede_agregar_libro(client, usuario_admin, app):
    login(client, "admin@test.com", "admin123")
    resp = client.post(
        "/libros/nuevo",
        data={"titulo": "1984", "autor": "George Orwell", "isbn": "", "copias": "3"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        libro = Libro.query.filter_by(titulo="1984").first()
        assert libro is not None
        assert libro.copias_disponibles == 3


def test_usuario_normal_no_puede_agregar_libro(client, usuario_normal, app):
    login(client, "juan@test.com", "clave123")
    resp = client.post(
        "/libros/nuevo",
        data={"titulo": "1984", "autor": "George Orwell", "copias": "3"},
        follow_redirects=True,
    )
    assert "No tienes permiso".encode("utf-8") in resp.data
    with app.app_context():
        assert Libro.query.filter_by(titulo="1984").first() is None


def test_busqueda_de_libros(client, libro_demo, app):
    resp = client.get("/libros/?q=Clean")
    assert b"Clean Code" in resp.data
    resp2 = client.get("/libros/?q=NoExiste")
    assert "No hay libros registrados".encode("utf-8") in resp2.data


def test_admin_puede_eliminar_libro(client, usuario_admin, libro_demo, app):
    login(client, "admin@test.com", "admin123")
    resp = client.post(f"/libros/{libro_demo}/eliminar", follow_redirects=True)
    assert "Libro eliminado".encode("utf-8") in resp.data
    with app.app_context():
        assert db.session.get(Libro, libro_demo) is None
