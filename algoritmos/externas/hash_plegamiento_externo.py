"""Hash Plegamiento Externo: se suman partes de la clave"""
from algoritmos.externas._hash_externo_base import HashExternoBase


class HashPlegamientoExternoWindow(HashExternoBase):
    TITULO = "HASH EXTERNO - PLEGAMIENTO"
    DESCRIPCION = (
        "Funcion hash por plegamiento: la clave se divide en partes de 2 digitos, "
        "se suman todas las partes y el resultado se aplica mod M."
    )

    def calcular_hash(self, clave_int, capacidad):
        s = str(clave_int).zfill(self.digitos)
        # Partir en grupos de 2 digitos y sumar
        total = 0
        for i in range(0, len(s), 2):
            parte = s[i:i + 2]
            total += int(parte)
        return total % capacidad
