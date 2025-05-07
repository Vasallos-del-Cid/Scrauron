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
        fuentes_ids: Optional[List[str]] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.conceptos_interes_ids = conceptos_interes_ids or []
        self.fuentes_ids = fuentes_ids or []

    def agregar_concepto(self, concepto: ConceptoInteres):
        if concepto._id not in self.conceptos_interes_ids:
            self.conceptos_interes_ids.append(concepto._id)

    def agregar_fuente(self, fuente: Fuente):
        if fuente._id not in self.fuentes_ids:
            self.fuentes_ids.append(fuente._id)

    def to_dict(self):
        data = {
            "nombre": self.nombre,
            "conceptos_interes_ids": self.conceptos_interes_ids,
            "fuentes_ids": self.fuentes_ids
        }
        if self._id:
            data["_id"] = str(self._id)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            conceptos_interes_ids = [str(cid) for cid in data.get("conceptos_interes_ids", [])],
            fuentes_ids = [str(fid) for fid in data.get("fuentes_ids", [])],
            _id=str(data.get("_id")) if data.get("_id") else None
        )

    def get_conceptos(self) -> List[ConceptoInteres]:
        return [get_concepto_by_id(cid) for cid in self.conceptos_interes_ids]

    def get_fuentes(self) -> List[Fuente]:
        return [get_fuente_by_id(fid) for fid in self.fuentes_ids]

    def __repr__(self):
        return (
            f"AreaDeTrabajo(nombre='{self.nombre}', conceptos_interes_ids={self.conceptos_interes_ids}, "
            f"fuentes_ids={self.fuentes_ids})"
        )
