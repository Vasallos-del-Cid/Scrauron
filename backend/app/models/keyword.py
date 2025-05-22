import logging
from typing import Optional


class Keyword:
    _id = None
    nombre = None

    def __init__(self,
                 nombre: str,
                 _id: Optional[str] = None,
                 ):
        self._id = _id
        self.nombre = nombre

    def to_dict(self):
        data = {
            "nombre": self.nombre,
        }
        if self._id:
            data["_id"] = str(self._id)

        return data

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                nombre=data["nombre"],
                _id=str(data.get("_id")) if data.get("_id") else None
            )
        except Exception as e:
            logging.error("❌ Error al crear la keyword")
            raise e

    def __repr__(self):
        return f"Fuente(nombre='{self.nombre}'"
