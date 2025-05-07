from typing import List, Optional
from bson import ObjectId

class ConceptoInteres:
    def __init__(
        self,
        nombre: str,
        descripcion: str,
        keywords: List[str],
        publicaciones_relacionadas_ids: Optional[List[ObjectId]] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.descripcion = descripcion
        self.keywords = keywords
        self.publicaciones_relacionadas_ids = publicaciones_relacionadas_ids or []

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "keywords": self.keywords,
            "publicaciones_relacionadas_ids": [
                str(pid) for pid in self.publicaciones_relacionadas_ids
            ]
        }
        if self._id:
            data["_id"] = ObjectId(self._id) if ObjectId.is_valid(self._id) else self._id

        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            keywords=data.get("keywords", []),
            publicaciones_relacionadas_ids=[
                ObjectId(pid) if ObjectId.is_valid(str(pid)) else pid
                for pid in data.get("publicaciones_relacionadas_ids", [])
            ],
            _id=str(data.get("_id")) if data.get("_id") else None
        )