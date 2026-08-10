from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Libro, Prestamo

prestamos_bp = Blueprint("prestamos", __name__)


@prestamos_bp.route("/mis-prestamos")
@login_required
def mis_prestamos():
    prestamos = (
        Prestamo.query.filter_by(usuario_id=current_user.id)
        .order_by(Prestamo.fecha_prestamo.desc())
        .all()
    )
    return render_template("prestamos/lista.html", prestamos=prestamos)


@prestamos_bp.route("/<int:libro_id>/pedir", methods=["POST"])
@login_required
def pedir(libro_id):
    libro = Libro.query.get_or_404(libro_id)

    if libro.copias_disponibles <= 0:
        flash("No hay copias disponibles de este libro.", "danger")
        return redirect(url_for("libros.listar"))

    ya_prestado = Prestamo.query.filter_by(
        usuario_id=current_user.id, libro_id=libro.id, devuelto=False
    ).first()
    if ya_prestado:
        flash("Ya tienes un préstamo activo de este libro.", "warning")
        return redirect(url_for("libros.listar"))

    prestamo = Prestamo(usuario_id=current_user.id, libro_id=libro.id)
    libro.copias_disponibles -= 1
    db.session.add(prestamo)
    db.session.commit()

    flash(f'Préstamo de "{libro.titulo}" registrado correctamente.', "success")
    return redirect(url_for("prestamos.mis_prestamos"))


@prestamos_bp.route("/<int:prestamo_id>/devolver", methods=["POST"])
@login_required
def devolver(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)

    if prestamo.usuario_id != current_user.id and not current_user.es_admin:
        flash("No puedes devolver un préstamo que no es tuyo.", "danger")
        return redirect(url_for("prestamos.mis_prestamos"))

    if prestamo.devuelto:
        flash("Este préstamo ya fue devuelto.", "info")
        return redirect(url_for("prestamos.mis_prestamos"))

    prestamo.devuelto = True
    prestamo.fecha_devolucion = datetime.utcnow()
    prestamo.libro.copias_disponibles += 1
    db.session.commit()

    flash("Libro devuelto correctamente.", "success")
    return redirect(url_for("prestamos.mis_prestamos"))
