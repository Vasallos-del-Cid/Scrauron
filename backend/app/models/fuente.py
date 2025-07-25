import logging
from datetime import time, datetime
from typing import Optional


class Fuente:
    _id = None
    fecha_alta = None
    activa = None
    tipo = None
    url = None
    nombre = None
    etiqueta_titulo = None
    etiqueta_contenido = None
    url_imagen = None  # Nuevo campo

    def __init__(self,
                 nombre: str,
                 url: str,
                 tipo: str,
                 fecha_alta: time,
                 activa: bool = True,
                 _id: Optional[str] = None,
                 etiqueta_titulo: str = "",
                 etiqueta_contenido: str = "",
                 url_imagen: Optional[str] = None  
                 ):
        self._id = _id
        self.nombre = nombre
        self.url = url
        self.tipo = tipo
        self.activa = activa
        self.fecha_alta = fecha_alta
        self.etiqueta_titulo = etiqueta_titulo
        self.etiqueta_contenido = etiqueta_contenido
        self.url_imagen = url_imagen

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "url": self.url,
            "tipo": self.tipo,
            "activa": self.activa,
            "fecha_alta": self.fecha_alta,
            "etiqueta_titulo": self.etiqueta_titulo,
            "etiqueta_contenido": self.etiqueta_contenido,
            "url_imagen": self.url_imagen  
        }
        if self._id:
            data["_id"] = str(self._id)
        return data

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                nombre=data["nombre"],
                url=data["url"],
                tipo=data.get("tipo", "rss"),
                activa=data.get("activa", True),
                fecha_alta=data.get("fecha_alta", datetime.now().isoformat()),
                etiqueta_titulo=data.get("etiqueta_titulo", ""),
                etiqueta_contenido=data.get("etiqueta_contenido", ""),
                url_imagen=data.get("url_imagen"),  # Nuevo campo
                _id=str(data.get("_id")) if data.get("_id") else None
            )
        except Exception as e:
            logging.error("❌ Error al crear la fuente desde el diccionario", e)
            raise e

    def __repr__(self):
        return f"Fuente(nombre='{self.nombre}', url='{self.url}', tipo={self.tipo}, activa={self.activa}, fecha_alta={self.fecha_alta}, etiqueta_titulo={self.etiqueta_titulo}, url_imagen={self.url_imagen})"
