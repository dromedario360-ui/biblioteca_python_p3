from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    foto = db.Column(db.String(300), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    prestamos = db.relationship("Prestamo", backref="usuario", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.email}>"


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)

    libros = db.relationship("Libro", backref="categoria", lazy=True)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Libro(db.Model):
    __tablename__ = "libros"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    imagen = db.Column(db.String(300), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    copias_totales = db.Column(db.Integer, default=1, nullable=False)
    copias_disponibles = db.Column(db.Integer, default=1, nullable=False)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)

    prestamos = db.relationship("Prestamo", backref="libro", lazy=True)

    @property
    def disponible(self):
        return self.copias_disponibles > 0

    def __repr__(self):
        return f"<Libro {self.titulo}>"


class Prestamo(db.Model):
    __tablename__ = "prestamos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    libro_id = db.Column(db.Integer, db.ForeignKey("libros.id"), nullable=False)
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    fecha_prestamo = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_limite = db.Column(
        db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14)
    )
    fecha_devolucion = db.Column(db.DateTime, nullable=True)
    devuelto = db.Column(db.Boolean, default=False)

    @property
    def esta_atrasado(self):
        if self.devuelto:
            return False
        return datetime.utcnow() > self.fecha_limite

    def __repr__(self):
        return f"<Prestamo libro={self.libro_id} usuario={self.usuario_id}>"
