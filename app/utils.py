import os
import uuid
from flask import current_app


def guardar_imagen(file_storage, subcarpeta):
    """Guarda una imagen subida y devuelve la ruta relativa (o None si no hay archivo)."""
    if not file_storage or file_storage.filename == "":
        return None

    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in current_app.config["EXTENSIONES_PERMITIDAS"]:
        return None

    nombre_unico = f"{uuid.uuid4().hex}.{ext}"
    ruta_absoluta = os.path.join(
        current_app.config["UPLOAD_FOLDER"], subcarpeta, nombre_unico
    )
    file_storage.save(ruta_absoluta)
    return f"uploads/{subcarpeta}/{nombre_unico}"
