class ConceptoInteres:
    def __init__(self, nombre: str, descripcion: str):
        self.nombre = nombre
        self.descripcion = descripcion

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

    @classmethod
    def from_dict(cls, data):
        return cls(nombre=data["nombre"], 
                   descripcion=data.get("descripcion")
                   )