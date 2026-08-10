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
- Catálogo de libros con búsqueda por título/autor y filtro por categoría
- Gestión de libros (agregar/editar/eliminar) con imagen y descripción — solo administradores
- Gestión de categorías (CRUD) — solo administradores
- Solicitud y devolución de préstamos, incluyendo varias copias de un mismo libro
- Perfil de usuario con foto editable e historial de préstamos
- Control de copias disponibles y préstamos atrasados
- Panel con estadísticas básicas
- Panel de administración de escritorio (Flet) para gestionar libros y categorías fuera del navegador

## Instalación local

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m flask --app run seed      # carga datos de ejemplo (usuario admin incluido)
python run.py
```

Usuario administrador de prueba: `admin@biblioteca.com` / `admin123`

### Panel de administración (Flet)

Con el entorno virtual activado y la base de datos ya creada (haber corrido `run.py` al menos una vez):

```powershell
python admin_app.py
```

Se abre una ventana de escritorio con pestañas **Libros** y **Categorías**, donde puedes
crear, editar y eliminar registros, incluyendo la imagen de portada de cada libro.
Usa la misma base de datos SQLite que la app web, así que los cambios se reflejan
de inmediato al recargar el catálogo en el navegador.

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
