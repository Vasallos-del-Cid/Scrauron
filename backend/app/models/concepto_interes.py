from typing import List, Optional
from app.models.publicacion import Publicacion

class ConceptoInteres:
    def __init__(
        self,
        nombre: str,
        descripcion: str,
        keywords: List[str],
        publicaciones_relacionadas: Optional[List[Publicacion]] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.descripcion = descripcion
        self.keywords = keywords
        self.publicaciones_relacionadas = publicaciones_relacionadas or []

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "keywords": self.keywords,
            "publicaciones_relacionadas": [
                p.to_dict() for p in self.publicaciones_relacionadas if p._id
            ]
        }
        if self._id:
            data["_id"] = str(self._id)

        return data


    @classmethod
    def from_dict(cls, data):
        publicaciones = [
            Publicacion.from_dict(p) for p in data.get("publicaciones_relacionadas", [])
        ]
        return cls(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            keywords=data.get("keywords", []),
            publicaciones_relacionadas=publicaciones,
            _id=str(data.get("_id")) if data.get("_id") else None

        )
