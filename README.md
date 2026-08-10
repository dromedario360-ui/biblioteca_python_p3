# 📚 Biblioteca Online

Sistema de gestión de préstamos de libros — **Proyecto Final de Programación III**.
Desarrollado con metodología **Agile-Scrum** y flujo de ramas **Git Flow**.

## Tecnologías

- Python 3.12
- Flask 3 (Flask-SQLAlchemy, Flask-Login)
- SQLite
- Bootstrap 5
- Pytest (pruebas automatizadas) + GitHub Actions (CI)

## Funcionalidades (Release 1)

- Registro e inicio de sesión de usuarios
- Catálogo de libros con búsqueda por título/autor
- Gestión de libros (agregar/eliminar) — solo administradores
- Solicitud y devolución de préstamos
- Control de copias disponibles y préstamos atrasados
- Panel con estadísticas básicas

## Instalación local

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask --app run seed      # carga datos de ejemplo (usuario admin incluido)
python run.py
```

Usuario administrador de prueba: `admin@biblioteca.com` / `admin123`

## Ejecutar las pruebas automatizadas

```powershell
python -m pytest tests/ -v --cov=app
```

Las pruebas también se ejecutan automáticamente en cada `push` y `pull request`
mediante GitHub Actions (ver pestaña **Actions** del repositorio).

## Flujo de trabajo (Git Flow)

- `main` → versión estable / producción
- `qa` → rama de control de calidad, previo a producción
- `dev` → integración de features en desarrollo
- `feature/*` → una rama por funcionalidad, integrada a `dev` vía Pull Request
- `hotfix/*` → corrección urgente, integrada directo a `main` (y luego sincronizada a `dev`/`qa`) vía Pull Request

Cada rama `feature/` y `hotfix/` se integra mediante **Pull Requests** revisados
y cerrados hacia `dev`, `qa` y `main`, según corresponda.

## Documentación del proyecto

La planificación completa (Scrum, historias de usuario, plan de pruebas) se
encuentra en el documento entregado junto a este repositorio.
