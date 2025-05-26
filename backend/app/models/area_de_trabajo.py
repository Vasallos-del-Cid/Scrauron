from typing import List, Optional
from .concepto_interes import ConceptoInteres
from .fuente import Fuente
from ..mongo.mongo_conceptos import get_concepto_by_id
from ..mongo.mongo_fuentes import get_fuente_by_id


class AreaDeTrabajo:
    def __init__(
        self,
        nombre: str,
        conceptos_interes_ids: Optional[List[str]] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.conceptos_interes_ids = conceptos_interes_ids or []

    def agregar_concepto(self, concepto: ConceptoInteres):
        if concepto._id not in self.conceptos_interes_ids:
            self.conceptos_interes_ids.append(concepto._id)


    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "conceptos_interes_ids": self.conceptos_interes_ids
        }
        if self._id:
            data["_id"] = str(self._id)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            conceptos_interes_ids = [str(cid) for cid in data.get("conceptos_interes_ids", [])],
            _id=str(data.get("_id")) if data.get("_id") else None
        )

    def get_conceptos(self) -> List[ConceptoInteres]:
        return [get_concepto_by_id(cid) for cid in self.conceptos_interes_ids]

    def __repr__(self):
        return (
            f"AreaDeTrabajo(nombre='{self.nombre}', conceptos_interes_ids={self.conceptos_interes_ids})"
        )
