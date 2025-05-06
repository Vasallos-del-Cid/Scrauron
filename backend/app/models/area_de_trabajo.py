from typing import List, Optional
from .concepto_interes import ConceptoInteres
from .fuente import Fuente
from .publicacion import Publicacion  # Si alguna vez necesitas publicaciones sueltas
from ..mongo.mongo_conceptos import get_concepto_by_id
from ..mongo.mongo_fuentes import get_fuente_by_id


class AreaDeTrabajo:
    def __init__(
        self,
        nombre: str,
        conceptos_interes: List[ConceptoInteres] = None,
        fuentes: List[Fuente] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.conceptos_interes = conceptos_interes or []
        self.fuentes = fuentes or []

    def agregar_concepto(self, concepto: ConceptoInteres):
        if concepto and all(c._id != concepto._id for c in self.conceptos_interes):
            self.conceptos_interes.append(concepto)

    def agregar_fuente(self, fuente: Fuente):
        if fuente and all(f._id != fuente._id for f in self.fuentes):
            self.fuentes.append(fuente)

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "conceptos_interes": [c.to_dict() for c in self.conceptos_interes],
            "fuentes": [f.to_dict() for f in self.fuentes]
        }
        if self._id:
            data["_id"] = str(self._id)
        return data

    @classmethod
    def from_dict(cls, data):
        conceptos_raw = data.get("conceptos_interes", [])
        fuentes_raw = data.get("fuentes", [])

        conceptos = []
        for c in conceptos_raw:
            if isinstance(c, dict) and "_id" in c:
                concepto = get_concepto_by_id(str(c["_id"]))
                if concepto:
                    conceptos.append(concepto)

        fuentes = []
        for f in fuentes_raw:
            if isinstance(f, dict) and "_id" in f:
                fuente = get_fuente_by_id(str(f["_id"]))
                if fuente:
                    fuentes.append(fuente)

        return cls(
            nombre=data["nombre"],
            conceptos_interes=conceptos,
            fuentes=fuentes,
            _id=str(data.get("_id")) if data.get("_id") else None
        )

    def __repr__(self):
        return (
            f"AreaDeTrabajo(nombre='{self.nombre}', conceptos_interes={self.conceptos_interes}, "
            f"fuentes={self.fuentes})"
        )
