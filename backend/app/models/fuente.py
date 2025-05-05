from typing import Optional

class Fuente:
    def __init__(self, nombre: str, url: str, _id: Optional[str] = None):
        self._id = _id
        self.nombre = nombre
        self.url = url

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "url": self.url
        }
        if self._id is not None:
            data["_id"] = self._id
        return data


    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            url=data["url"],
            _id=str(data.get("_id")) if data.get("_id") else None
        )

    def __repr__(self):
        return f"Fuente(nombre='{self.nombre}', url='{self.url}')"
