from app import db
from app.models import Libro, Prestamo
from tests.conftest import login


def test_solicitar_prestamo_exitoso(client, usuario_normal, libro_demo, app):
    login(client, "juan@test.com", "clave123")
    resp = client.post(f"/prestamos/{libro_demo}/pedir", follow_redirects=True)
    assert "registrado correctamente".encode("utf-8") in resp.data

    with app.app_context():
        libro = db.session.get(Libro, libro_demo)
        assert libro.copias_disponibles == 1
        assert Prestamo.query.count() == 1


def test_no_se_puede_prestar_mismo_libro_dos_veces(client, usuario_normal, libro_demo, app):
    login(client, "juan@test.com", "clave123")
    client.post(f"/prestamos/{libro_demo}/pedir", follow_redirects=True)
    resp = client.post(f"/prestamos/{libro_demo}/pedir", follow_redirects=True)
    assert "ya tienes un préstamo activo".encode("utf-8") in resp.data.lower()


def test_no_hay_copias_disponibles(client, usuario_normal, app):
    with app.app_context():
        libro = Libro(titulo="Libro Agotado", autor="X", copias_totales=1, copias_disponibles=0)
        db.session.add(libro)
        db.session.commit()
        libro_id = libro.id

    login(client, "juan@test.com", "clave123")
    resp = client.post(f"/prestamos/{libro_id}/pedir", follow_redirects=True)
    assert "No hay copias disponibles".encode("utf-8") in resp.data


def test_devolver_prestamo(client, usuario_normal, libro_demo, app):
    login(client, "juan@test.com", "clave123")
    client.post(f"/prestamos/{libro_demo}/pedir", follow_redirects=True)

    with app.app_context():
        prestamo = Prestamo.query.first()
        prestamo_id = prestamo.id

    resp = client.post(f"/prestamos/{prestamo_id}/devolver", follow_redirects=True)
    assert "devuelto correctamente".encode("utf-8") in resp.data

    with app.app_context():
        libro = db.session.get(Libro, libro_demo)
        assert libro.copias_disponibles == 2
        prestamo = db.session.get(Prestamo, prestamo_id)
        assert prestamo.devuelto is True


def test_mis_prestamos_requiere_login(client):
    resp = client.get("/prestamos/mis-prestamos", follow_redirects=True)
    assert "Debes iniciar sesión".encode("utf-8") in resp.data
