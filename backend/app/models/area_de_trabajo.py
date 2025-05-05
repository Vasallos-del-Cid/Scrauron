from typing import List, Optional
from .concepto_interes import ConceptoInteres
from .fuente import Fuente
from .publicacion import Publicacion

class AreaDeTrabajo:
    def __init__(
        self,
        nombre: str,
        conceptos_interes: List[ConceptoInteres] = None,
        fuentes: List[Fuente] = None,
        publicacionesRelacionadas: List[Publicacion] = None,
        periodicidadScraping: Optional[int] = 24,  # Por ejemplo: cada 24 horas
        _id: Optional[str] = None
    ):
        self._id = _id
        self.nombre = nombre
        self.conceptos_interes = conceptos_interes or []
        self.fuentes = fuentes or []
        self.publicacionesRelacionadas = publicacionesRelacionadas or []
        self.periodicidadScraping = periodicidadScraping

    def agregar_concepto(self, concepto: ConceptoInteres):
        if concepto and concepto not in self.conceptos_interes:
            self.conceptos_interes.append(concepto)

    def agregar_fuente(self, fuente: Fuente):
        if fuente and fuente not in self.fuentes:
            self.fuentes.append(fuente)

    def agregar_publicacion(self, publicacion: Publicacion):
        if publicacion and publicacion not in self.publicacionesRelacionadas:
            self.publicacionesRelacionadas.append(publicacion)

    def to_dict(self):
        return {
            "_id": self._id,
            "nombre": self.nombre,
            "conceptos_interes": [c.to_dict() for c in self.conceptos_interes],
            "fuentes": [f.to_dict() for f in self.fuentes],
            "publicacionesRelacionadas": [p.to_dict() for p in self.publicacionesRelacionadas],
            "periodicidadScraping": self.periodicidadScraping
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            conceptos_interes=[ConceptoInteres.from_dict(c) for c in data.get("conceptos_interes", [])],
            fuentes=[Fuente.from_dict(f) for f in data.get("fuentes", [])],
            publicacionesRelacionadas=[Publicacion.from_dict(p) for p in data.get("publicacionesRelacionadas", [])],
            periodicidadScraping=data.get("periodicidadScraping", 24),
            _id=data.get("_id")
        )

    def __repr__(self):
        return (
            f"AreaDeTrabajo(nombre='{self.nombre}', conceptos_interes={self.conceptos_interes}, "
            f"fuentes={self.fuentes}, publicacionesRelacionadas={self.publicacionesRelacionadas}, "
            f"periodicidadScraping={self.periodicidadScraping})"
        )
