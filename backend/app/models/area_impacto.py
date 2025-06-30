from typing import Optional

class AreaImpacto:
    def __init__(
        self,
        nombre: str,
        descripcion: Optional[str] = "",
        area_id: Optional[str] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.descripcion = descripcion
        self.area_id = area_id

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "area_id": self.area_id
        }
        if self._id:
            data["_id"] = str(self._id)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            area_id=data.get("area_id"),  # No convertir a str
            _id=str(data.get("_id")) if data.get("_id") else None
        )


    def __repr__(self):
        return f"AreaImpacto(nombre='{self.nombre}', descripcion='{self.descripcion}', area_id='{self.area_id}')"
