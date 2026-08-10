from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Libro, Categoria
from app.utils import guardar_imagen

libros_bp = Blueprint("libros", __name__)


def _solo_admin():
    return current_user.is_authenticated and current_user.es_admin


@libros_bp.route("/")
def listar():
    q = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", "").strip()

    query = Libro.query
    if q:
        query = query.filter(
            (Libro.titulo.ilike(f"%{q}%")) | (Libro.autor.ilike(f"%{q}%"))
        )
    if categoria_id:
        query = query.filter(Libro.categoria_id == categoria_id)

    libros = query.order_by(Libro.titulo).all()
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template(
        "libros/list.html",
        libros=libros,
        categorias=categorias,
        q=q,
        categoria_id=categoria_id,
    )


@libros_bp.route("/<int:libro_id>")
def detalle(libro_id):
    libro = Libro.query.get_or_404(libro_id)
    return render_template("libros/detalle.html", libro=libro)


@libros_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if not _solo_admin():
        flash("No tienes permiso para agregar libros.", "danger")
        return redirect(url_for("libros.listar"))

    categorias = Categoria.query.order_by(Categoria.nombre).all()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        isbn = request.form.get("isbn", "").strip() or None
        descripcion = request.form.get("descripcion", "").strip() or None
        copias = int(request.form.get("copias", 1))
        categoria_id = request.form.get("categoria_id") or None
        imagen = guardar_imagen(request.files.get("imagen"), "libros")

        if not titulo or not autor:
            flash("Título y autor son obligatorios.", "danger")
            return redirect(url_for("libros.nuevo"))

        libro = Libro(
            titulo=titulo,
            autor=autor,
            isbn=isbn,
            descripcion=descripcion,
            imagen=imagen,
            copias_totales=copias,
            copias_disponibles=copias,
            categoria_id=categoria_id,
        )
        db.session.add(libro)
        db.session.commit()
        flash("Libro agregado correctamente.", "success")
        return redirect(url_for("libros.listar"))

    return render_template("libros/form.html", categorias=categorias, libro=None)


@libros_bp.route("/<int:libro_id>/editar", methods=["GET", "POST"])
@login_required
def editar(libro_id):
    if not _solo_admin():
        flash("No tienes permiso para editar libros.", "danger")
        return redirect(url_for("libros.listar"))

    libro = Libro.query.get_or_404(libro_id)
    categorias = Categoria.query.order_by(Categoria.nombre).all()

    if request.method == "POST":
        libro.titulo = request.form.get("titulo", "").strip()
        libro.autor = request.form.get("autor", "").strip()
        libro.isbn = request.form.get("isbn", "").strip() or None
        libro.descripcion = request.form.get("descripcion", "").strip() or None
        libro.categoria_id = request.form.get("categoria_id") or None

        nuevas_totales = int(request.form.get("copias", libro.copias_totales))
        diferencia = nuevas_totales - libro.copias_totales
        libro.copias_totales = nuevas_totales
        libro.copias_disponibles = max(0, libro.copias_disponibles + diferencia)

        nueva_imagen = guardar_imagen(request.files.get("imagen"), "libros")
        if nueva_imagen:
            libro.imagen = nueva_imagen

        db.session.commit()
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("libros.listar"))

    return render_template("libros/form.html", categorias=categorias, libro=libro)


@libros_bp.route("/<int:libro_id>/eliminar", methods=["POST"])
@login_required
def eliminar(libro_id):
    if not _solo_admin():
        flash("No tienes permiso para eliminar libros.", "danger")
        return redirect(url_for("libros.listar"))

    libro = Libro.query.get_or_404(libro_id)
    db.session.delete(libro)
    db.session.commit()
    flash("Libro eliminado.", "info")
    return redirect(url_for("libros.listar"))
