from datetime import datetime
from typing import List, Optional

class Publicacion:
    def __init__(
        self,
        titulo: str,
        url: str,
        fecha: Optional[datetime],
        contenido: str,
        fuente: str,
        tono: Optional[int] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.titulo = titulo
        self.url = url
        self.fecha = fecha or datetime.now()
        self.contenido = contenido
        self.fuente = fuente
        self.tono = tono

    def to_dict(self):
        data = {
            "titulo": self.titulo,
            "url": self.url,
            "fecha": self.fecha,
            "contenido": self.contenido,
            "fuente": self.fuente,
            "tono": self.tono
        }
        if self._id:
            data["_id"] = str(self._id)
        return data



    @classmethod
    def from_dict(cls, data):
        fecha_raw = data.get("fecha", datetime.utcnow())
        fecha_obj = (
            fecha_raw if isinstance(fecha_raw, datetime)
            else datetime.fromisoformat(fecha_raw)
        )

        return cls(
            titulo=data["titulo"],
            url=data["url"],
            fecha=fecha_obj,
            contenido=data["contenido"],
            fuente=data["fuente"],
            tono=data.get("tono"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )
    
    def __repr__(self):
        return (
            f"Publicacion(_id='{self._id}', titulo='{self.titulo[:30]}', "
            f"url='{self.url}', fuente='{self.fuente}')"
        )

