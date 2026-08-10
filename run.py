from app import create_app, db
from app.models import Usuario, Categoria, Libro

app = create_app()


@app.cli.command("seed")
def seed():
    """Carga datos de ejemplo: admin, categorías y libros."""
    with app.app_context():
        if not Usuario.query.filter_by(email="admin@biblioteca.com").first():
            admin = Usuario(nombre="Administrador", email="admin@biblioteca.com", es_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)

        categorias = ["Ficción", "Tecnología", "Historia", "Ciencia"]
        for nombre in categorias:
            if not Categoria.query.filter_by(nombre=nombre).first():
                db.session.add(Categoria(nombre=nombre))
        db.session.commit()

        tech = Categoria.query.filter_by(nombre="Tecnología").first()
        ficcion = Categoria.query.filter_by(nombre="Ficción").first()

        libros_demo = [
            ("Clean Code", "Robert C. Martin", tech.id, 3,
             "Una guía práctica sobre cómo escribir código legible y mantenible."),
            ("Cien años de soledad", "Gabriel García Márquez", ficcion.id, 2,
             "La historia de la familia Buendía en el pueblo de Macondo."),
            ("Introduction to Algorithms", "Thomas Cormen", tech.id, 2,
             "Referencia clásica sobre algoritmos y estructuras de datos."),
        ]
        for titulo, autor, cat_id, copias, descripcion in libros_demo:
            if not Libro.query.filter_by(titulo=titulo).first():
                db.session.add(
                    Libro(
                        titulo=titulo,
                        autor=autor,
                        categoria_id=cat_id,
                        copias_totales=copias,
                        copias_disponibles=copias,
                        descripcion=descripcion,
                    )
                )
        db.session.commit()
        print("Datos de ejemplo cargados. Usuario admin: admin@biblioteca.com / admin123")


if __name__ == "__main__":
    app.run(debug=True)
