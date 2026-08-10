from tests.conftest import login


def test_registro_usuario_exitoso(client):
    resp = client.post(
        "/auth/registro",
        data={"nombre": "Maria Lopez", "email": "maria@test.com", "password": "1234"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Cuenta creada exitosamente".encode("utf-8") in resp.data


def test_registro_email_duplicado(client, usuario_normal):
    resp = client.post(
        "/auth/registro",
        data={"nombre": "Otro", "email": "juan@test.com", "password": "1234"},
        follow_redirects=True,
    )
    assert "Ya existe una cuenta".encode("utf-8") in resp.data


def test_login_exitoso(client, usuario_normal):
    resp = login(client, "juan@test.com", "clave123")
    assert "Bienvenido".encode("utf-8") in resp.data


def test_login_credenciales_invalidas(client, usuario_normal):
    resp = login(client, "juan@test.com", "clave-incorrecta")
    assert "incorrectos".encode("utf-8") in resp.data


def test_logout(client, usuario_normal):
    login(client, "juan@test.com", "clave123")
    resp = client.get("/auth/logout", follow_redirects=True)
    assert "Sesión cerrada".encode("utf-8") in resp.data
