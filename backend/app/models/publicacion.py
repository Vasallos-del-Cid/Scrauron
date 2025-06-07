from datetime import datetime
from typing import Optional, List
from bson import ObjectId

class Publicacion:
    def __init__(
        self,
        titulo: str,
        url: str,
        fecha: Optional[datetime],
        contenido: str,
        fuente_id: ObjectId,
        tono: Optional[int] = None,
        keywords_relacionadas_ids: Optional[List[ObjectId]] = None,
        ciudad_region: Optional[str] = None,
        pais: Optional[str] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.titulo = titulo
        self.url = url
        self.fecha = fecha or datetime.now()
        self.contenido = contenido
        self.fuente_id = fuente_id
        self.tono = tono
        self.keywords_relacionadas_ids = keywords_relacionadas_ids or []
        self.ciudad_region = ciudad_region
        self.pais = pais

    def to_dict(self):
        data = {
            "titulo": self.titulo,
            "url": self.url,
            "fecha": self.fecha,
            "contenido": self.contenido,
            "fuente_id": str(self.fuente_id) if self.fuente_id else None,
            "tono": self.tono,
            "keywords_relacionadas_ids": [str(kid) for kid in self.keywords_relacionadas_ids],
            "ciudad_region": self.ciudad_region,
            "pais": self.pais
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

        fuente_id_raw = data.get("fuente_id")
        if not fuente_id_raw:
            raise ValueError("El campo 'fuente_id' es obligatorio.")
        fuente_oid = ObjectId(str(fuente_id_raw))

        keywords_ids_raw = data.get("keywords_relacionadas_ids", [])
        keywords_ids = [ObjectId(k) for k in keywords_ids_raw]

        return cls(
            titulo=data.get("titulo"),
            url=data.get("url"),
            fecha=fecha_obj,
            contenido=data.get("contenido"),
            fuente_id=fuente_oid,
            tono=data.get("tono"),
            keywords_relacionadas_ids=keywords_ids,
            ciudad_region=data.get("ciudad_region"),
            pais=data.get("pais"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )

    def __repr__(self):
        return (
            f"Publicacion(_id='{self._id}', titulo='{self.titulo[:30]}', "
            f"url='{self.url}', fuente_id='{self.fuente_id}', ciudad_region='{self.ciudad_region}', pais='{self.pais}')"
        )
