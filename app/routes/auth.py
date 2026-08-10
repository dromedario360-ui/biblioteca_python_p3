from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario, Prestamo
from app.utils import guardar_imagen

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not nombre or not email or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("auth.registro"))

        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo.", "danger")
            return redirect(url_for("auth.registro"))

        usuario = Usuario(nombre=nombre, email=email)
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()

        flash("Cuenta creada exitosamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            return redirect(url_for("main.index"))

        flash("Correo o contraseña incorrectos.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if nombre:
            current_user.nombre = nombre

        nueva_foto = guardar_imagen(request.files.get("foto"), "perfiles")
        if nueva_foto:
            current_user.foto = nueva_foto

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("auth.perfil"))

    historial = (
        Prestamo.query.filter_by(usuario_id=current_user.id)
        .order_by(Prestamo.fecha_prestamo.desc())
        .all()
    )
    return render_template("auth/perfil.html", historial=historial)
