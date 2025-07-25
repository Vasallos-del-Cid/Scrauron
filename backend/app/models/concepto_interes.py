from typing import List, Optional
from bson import ObjectId

class ConceptoInteres:
    def __init__(
        self,
        nombre: str,
        descripcion: str,
        keywords_ids: Optional[List[ObjectId]] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.descripcion = descripcion
        self.keywords_ids = keywords_ids or []

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "keywords_ids": [str(kid) for kid in self.keywords_ids]
        }
        if self._id:
            data["_id"] = str(self._id)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            keywords_ids=[
                ObjectId(kid) if ObjectId.is_valid(str(kid)) else kid
                for kid in data.get("keywords_ids", [])
            ],
            _id=str(data.get("_id")) if data.get("_id") else None
        )
