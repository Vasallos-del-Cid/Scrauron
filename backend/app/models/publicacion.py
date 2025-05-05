from datetime import datetime
from typing import List, Optional
from app.models.concepto_interes import ConceptoInteres

class Publicacion:
    def __init__(
        self,
        titulo: str,
        url: str,
        fecha: Optional[datetime],
        contenido: str,
        fuente: str,
        tono: Optional[int] = None,
        conceptos_relacionados: Optional[List[ConceptoInteres]] = None
    ):
        self.titulo = titulo
        self.url = url
        self.fecha = fecha or datetime.now()
        self.contenido = contenido
        self.fuente = fuente
        self.tono = tono  # positivo, negativo, neutro (opcional al inicio)
        self.conceptos_relacionados = conceptos_relacionados or []

    def agregar_concepto(self, concepto: ConceptoInteres):
        self.conceptos_relacionados.append(concepto)

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "url": self.url,
            "fecha": self.fecha,  # datetime, Mongo lo guarda correctamente
            "contenido": self.contenido,
            "fuente": self.fuente,
            "tono": self.tono,
            "conceptos_relacionados": [c.to_dict() for c in self.conceptos_relacionados]
        }
    @classmethod
    def from_dict(cls, data):
        conceptos = [ConceptoInteres.from_dict(c) for c in data.get("conceptos_relacionados", [])]
        return cls(
            titulo=data["titulo"],
            url=data["url"],
            fecha=data.get("fecha", datetime.utcnow()),
            contenido=data["contenido"],
            fuente=data["fuente"],
            tono=data.get("tono"),
            conceptos_relacionados=conceptos,
        )