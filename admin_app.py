"""
Panel de administración de la Biblioteca Online, construido con Flet.

Se conecta directamente a la misma base de datos que usa la app web (Flask),
reutilizando los mismos modelos (app.models). Permite al administrador:
  - Gestionar categorías (crear, editar, eliminar)
  - Gestionar libros: título, autor, ISBN, descripción, imagen de portada,
    categoría y cantidad de copias (crear, editar, eliminar)

Ejecutar con:  python admin_app.py
"""
import os
import shutil
import uuid

import flet as ft

from app import create_app, db
from app.models import Libro, Categoria

flask_app = create_app()


# ---------- Helpers de datos (usan el contexto de la app Flask) ----------

def obtener_libros():
    with flask_app.app_context():
        return Libro.query.order_by(Libro.titulo).all()


def obtener_categorias():
    with flask_app.app_context():
        return Categoria.query.order_by(Categoria.nombre).all()


def guardar_libro(datos, libro_id=None):
    with flask_app.app_context():
        if libro_id:
            libro = Libro.query.get(libro_id)
        else:
            libro = Libro()
            db.session.add(libro)

        libro.titulo = datos["titulo"]
        libro.autor = datos["autor"]
        libro.isbn = datos["isbn"] or None
        libro.descripcion = datos["descripcion"] or None
        libro.categoria_id = int(datos["categoria_id"]) if datos["categoria_id"] else None

        nuevas_totales = int(datos["copias"])
        if libro_id:
            diferencia = nuevas_totales - libro.copias_totales
            libro.copias_disponibles = max(0, libro.copias_disponibles + diferencia)
        else:
            libro.copias_disponibles = nuevas_totales
        libro.copias_totales = nuevas_totales

        if datos.get("imagen_path"):
            libro.imagen = _copiar_imagen(datos["imagen_path"])

        db.session.commit()


def eliminar_libro(libro_id):
    with flask_app.app_context():
        libro = Libro.query.get(libro_id)
        if libro:
            db.session.delete(libro)
            db.session.commit()


def guardar_categoria(nombre, categoria_id=None):
    with flask_app.app_context():
        if categoria_id:
            categoria = Categoria.query.get(categoria_id)
            categoria.nombre = nombre
        else:
            db.session.add(Categoria(nombre=nombre))
        db.session.commit()


def eliminar_categoria(categoria_id):
    with flask_app.app_context():
        categoria = Categoria.query.get(categoria_id)
        if categoria:
            for libro in categoria.libros:
                libro.categoria_id = None
            db.session.delete(categoria)
            db.session.commit()


def _copiar_imagen(origen):
    """Copia la imagen elegida a app/static/uploads/libros con un nombre único."""
    ext = origen.rsplit(".", 1)[-1].lower()
    nombre_unico = f"{uuid.uuid4().hex}.{ext}"
    destino_dir = os.path.join(flask_app.config["UPLOAD_FOLDER"], "libros")
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, nombre_unico)
    shutil.copy(origen, destino)
    return f"uploads/libros/{nombre_unico}"


def _ruta_imagen_absoluta(libro):
    if not libro.imagen:
        return None
    return os.path.join(flask_app.config["UPLOAD_FOLDER"], "..", *libro.imagen.split("/")[1:])


# ---------- Interfaz Flet ----------

def main(page: ft.Page):
    page.title = "Biblioteca Online — Panel de Administración"
    page.window.width = 1100
    page.window.height = 750
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    estado = {"imagen_seleccionada": None, "editando_libro_id": None, "editando_categoria_id": None}

    # ---- Widgets del formulario de libros ----
    campo_titulo = ft.TextField(label="Título", width=350)
    campo_autor = ft.TextField(label="Autor", width=350)
    campo_isbn = ft.TextField(label="ISBN (opcional)", width=350)
    campo_descripcion = ft.TextField(label="Descripción", width=350, multiline=True, min_lines=3, max_lines=5)
    campo_copias = ft.TextField(label="Cantidad de copias", width=350, value="1")
    dropdown_categoria = ft.Dropdown(label="Categoría", width=350, options=[])
    texto_imagen = ft.Text("Ninguna imagen seleccionada", italic=True, size=12)
    tabla_libros = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Título")),
        ft.DataColumn(ft.Text("Autor")),
        ft.DataColumn(ft.Text("Categoría")),
        ft.DataColumn(ft.Text("Copias")),
        ft.DataColumn(ft.Text("Acciones")),
    ], rows=[])

    # ---- Widgets de categorías ----
    campo_nombre_categoria = ft.TextField(label="Nombre de la categoría", width=300)
    tabla_categorias = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Nombre")),
        ft.DataColumn(ft.Text("Libros")),
        ft.DataColumn(ft.Text("Acciones")),
    ], rows=[])

    snack = ft.SnackBar(content=ft.Text(""))
    page.overlay.append(snack)

    def notificar(mensaje):
        snack.content = ft.Text(mensaje)
        snack.open = True
        page.update()

    # ---- Selector de imagen ----
    def on_imagen_elegida(e: ft.FilePickerResultEvent):
        if e.files:
            estado["imagen_seleccionada"] = e.files[0].path
            texto_imagen.value = f"Imagen: {e.files[0].name}"
            page.update()

    selector_imagen = ft.FilePicker(on_result=on_imagen_elegida)
    page.overlay.append(selector_imagen)

    # ---- Refrescar tablas ----
    def refrescar_categorias():
        categorias = obtener_categorias()
        dropdown_categoria.options = [ft.dropdown.Option(key=str(c.id), text=c.nombre) for c in categorias]

        tabla_categorias.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(c.nombre)),
                ft.DataCell(ft.Text(str(len(c.libros)))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, tooltip="Editar", on_click=lambda e, c=c: cargar_categoria(c)),
                    ft.IconButton(ft.Icons.DELETE, tooltip="Eliminar", icon_color=ft.Colors.RED,
                                  on_click=lambda e, c=c: confirmar_eliminar_categoria(c)),
                ])),
            ]) for c in categorias
        ]
        page.update()

    def refrescar_libros():
        libros = obtener_libros()
        tabla_libros.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(l.titulo)),
                ft.DataCell(ft.Text(l.autor)),
                ft.DataCell(ft.Text(l.categoria.nombre if l.categoria else "—")),
                ft.DataCell(ft.Text(f"{l.copias_disponibles}/{l.copias_totales}")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, tooltip="Editar", on_click=lambda e, l=l: cargar_libro(l)),
                    ft.IconButton(ft.Icons.DELETE, tooltip="Eliminar", icon_color=ft.Colors.RED,
                                  on_click=lambda e, l=l: confirmar_eliminar_libro(l)),
                ])),
            ]) for l in libros
        ]
        page.update()

    # ---- Formulario de libro: cargar / limpiar ----
    def cargar_libro(libro):
        estado["editando_libro_id"] = libro.id
        campo_titulo.value = libro.titulo
        campo_autor.value = libro.autor
        campo_isbn.value = libro.isbn or ""
        campo_descripcion.value = libro.descripcion or ""
        campo_copias.value = str(libro.copias_totales)
        dropdown_categoria.value = str(libro.categoria_id) if libro.categoria_id else None
        texto_imagen.value = "Imagen actual conservada (elige una nueva para reemplazarla)" if libro.imagen else "Sin imagen"
        estado["imagen_seleccionada"] = None
        boton_guardar_libro.text = "Guardar cambios"
        page.update()

    def limpiar_form_libro():
        estado["editando_libro_id"] = None
        estado["imagen_seleccionada"] = None
        campo_titulo.value = ""
        campo_autor.value = ""
        campo_isbn.value = ""
        campo_descripcion.value = ""
        campo_copias.value = "1"
        dropdown_categoria.value = None
        texto_imagen.value = "Ninguna imagen seleccionada"
        boton_guardar_libro.text = "Agregar libro"
        page.update()

    def guardar_libro_click(e):
        if not campo_titulo.value or not campo_autor.value:
            notificar("Título y autor son obligatorios.")
            return
        try:
            copias = int(campo_copias.value)
        except ValueError:
            notificar("La cantidad de copias debe ser un número.")
            return

        guardar_libro({
            "titulo": campo_titulo.value.strip(),
            "autor": campo_autor.value.strip(),
            "isbn": campo_isbn.value.strip(),
            "descripcion": campo_descripcion.value.strip(),
            "categoria_id": dropdown_categoria.value,
            "copias": copias,
            "imagen_path": estado["imagen_seleccionada"],
        }, libro_id=estado["editando_libro_id"])

        notificar("Libro guardado correctamente.")
        limpiar_form_libro()
        refrescar_libros()
        refrescar_categorias()

    def confirmar_eliminar_libro(libro):
        def si(e):
            eliminar_libro(libro.id)
            page.close(dialogo)
            notificar("Libro eliminado.")
            refrescar_libros()

        def no(e):
            page.close(dialogo)

        dialogo = ft.AlertDialog(
            title=ft.Text("Eliminar libro"),
            content=ft.Text(f'¿Seguro que deseas eliminar "{libro.titulo}"?'),
            actions=[ft.TextButton("Cancelar", on_click=no), ft.TextButton("Eliminar", on_click=si)],
        )
        page.open(dialogo)

    boton_guardar_libro = ft.ElevatedButton("Agregar libro", icon=ft.Icons.SAVE, on_click=guardar_libro_click)

    # ---- Formulario de categoría ----
    def cargar_categoria(categoria):
        estado["editando_categoria_id"] = categoria.id
        campo_nombre_categoria.value = categoria.nombre
        boton_guardar_categoria.text = "Guardar cambios"
        page.update()

    def limpiar_form_categoria():
        estado["editando_categoria_id"] = None
        campo_nombre_categoria.value = ""
        boton_guardar_categoria.text = "Agregar categoría"
        page.update()

    def guardar_categoria_click(e):
        if not campo_nombre_categoria.value.strip():
            notificar("El nombre de la categoría es obligatorio.")
            return
        guardar_categoria(campo_nombre_categoria.value.strip(), categoria_id=estado["editando_categoria_id"])
        notificar("Categoría guardada.")
        limpiar_form_categoria()
        refrescar_categorias()
        refrescar_libros()

    def confirmar_eliminar_categoria(categoria):
        def si(e):
            eliminar_categoria(categoria.id)
            page.close(dialogo)
            notificar("Categoría eliminada.")
            refrescar_categorias()
            refrescar_libros()

        def no(e):
            page.close(dialogo)

        dialogo = ft.AlertDialog(
            title=ft.Text("Eliminar categoría"),
            content=ft.Text(f'¿Seguro que deseas eliminar "{categoria.nombre}"? Los libros quedarán sin categoría.'),
            actions=[ft.TextButton("Cancelar", on_click=no), ft.TextButton("Eliminar", on_click=si)],
        )
        page.open(dialogo)

    boton_guardar_categoria = ft.ElevatedButton("Agregar categoría", icon=ft.Icons.SAVE, on_click=guardar_categoria_click)

    # ---- Layout: pestañas ----
    tab_libros = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text("Formulario de libro", size=18, weight=ft.FontWeight.BOLD),
                campo_titulo, campo_autor, campo_isbn, campo_descripcion,
                dropdown_categoria, campo_copias,
                ft.Row([
                    ft.ElevatedButton("Elegir imagen", icon=ft.Icons.IMAGE,
                                      on_click=lambda e: selector_imagen.pick_files(
                                          allow_multiple=False,
                                          file_type=ft.FilePickerFileType.IMAGE)),
                    texto_imagen,
                ]),
                ft.Row([boton_guardar_libro, ft.TextButton("Cancelar / Limpiar", on_click=lambda e: limpiar_form_libro())]),
            ], width=380),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("Libros registrados", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([tabla_libros], scroll=ft.ScrollMode.AUTO),
            ], expand=True, scroll=ft.ScrollMode.AUTO),
        ], vertical_alignment=ft.CrossAxisAlignment.START),
        padding=10,
    )

    tab_categorias = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text("Formulario de categoría", size=18, weight=ft.FontWeight.BOLD),
                campo_nombre_categoria,
                ft.Row([boton_guardar_categoria, ft.TextButton("Cancelar / Limpiar", on_click=lambda e: limpiar_form_categoria())]),
            ], width=380),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("Categorías registradas", size=18, weight=ft.FontWeight.BOLD),
                tabla_categorias,
            ], expand=True),
        ], vertical_alignment=ft.CrossAxisAlignment.START),
        padding=10,
    )

    page.add(
        ft.Text("📚 Biblioteca Online — Panel de Administración", size=24, weight=ft.FontWeight.BOLD),
        ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Libros", icon=ft.Icons.MENU_BOOK, content=tab_libros),
            ft.Tab(text="Categorías", icon=ft.Icons.CATEGORY, content=tab_categorias),
        ], expand=True),
    )

    refrescar_categorias()
    refrescar_libros()


if __name__ == "__main__":
    ft.app(target=main)
