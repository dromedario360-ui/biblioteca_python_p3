from flask import Blueprint, render_template
from app.models import Libro, Prestamo

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    total_libros = Libro.query.count()
    total_disponibles = sum(l.copias_disponibles for l in Libro.query.all())
    prestamos_activos = Prestamo.query.filter_by(devuelto=False).count()
    return render_template(
        "index.html",
        total_libros=total_libros,
        total_disponibles=total_disponibles,
        prestamos_activos=prestamos_activos,
    )
