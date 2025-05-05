from typing import List

class ConceptoInteres:
    def __init__(self, nombre: str, descripcion: str, keywords: List[str]):
        self.nombre = nombre
        self.descripcion = descripcion
        self.keywords = keywords

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "keywords": self.keywords
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            keywords=data.get("keywords", [])
        )
