from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Categoria

categorias_bp = Blueprint("categorias", __name__)


def _solo_admin():
    return current_user.is_authenticated and current_user.es_admin


@categorias_bp.route("/")
@login_required
def listar():
    if not _solo_admin():
        flash("No tienes permiso para gestionar categorías.", "danger")
        return redirect(url_for("libros.listar"))
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template("categorias/list.html", categorias=categorias)


@categorias_bp.route("/nueva", methods=["POST"])
@login_required
def nueva():
    if not _solo_admin():
        flash("No tienes permiso para gestionar categorías.", "danger")
        return redirect(url_for("libros.listar"))

    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("El nombre de la categoría es obligatorio.", "danger")
    elif Categoria.query.filter_by(nombre=nombre).first():
        flash("Ya existe una categoría con ese nombre.", "danger")
    else:
        db.session.add(Categoria(nombre=nombre))
        db.session.commit()
        flash("Categoría creada.", "success")

    return redirect(url_for("categorias.listar"))


@categorias_bp.route("/<int:categoria_id>/editar", methods=["POST"])
@login_required
def editar(categoria_id):
    if not _solo_admin():
        flash("No tienes permiso para gestionar categorías.", "danger")
        return redirect(url_for("libros.listar"))

    categoria = Categoria.query.get_or_404(categoria_id)
    nombre = request.form.get("nombre", "").strip()
    if nombre:
        categoria.nombre = nombre
        db.session.commit()
        flash("Categoría actualizada.", "success")
    return redirect(url_for("categorias.listar"))


@categorias_bp.route("/<int:categoria_id>/eliminar", methods=["POST"])
@login_required
def eliminar(categoria_id):
    if not _solo_admin():
        flash("No tienes permiso para gestionar categorías.", "danger")
        return redirect(url_for("libros.listar"))

    categoria = Categoria.query.get_or_404(categoria_id)
    for libro in categoria.libros:
        libro.categoria_id = None
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoría eliminada. Los libros asociados quedan sin categoría.", "info")
    return redirect(url_for("categorias.listar"))
