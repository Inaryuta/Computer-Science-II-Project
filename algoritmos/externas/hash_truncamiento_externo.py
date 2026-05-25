"""Hash Truncamiento Externo: se toman los primeros digitos de la clave"""
from algoritmos.externas._hash_externo_base import HashExternoBase


class HashTruncamientoExternoWindow(HashExternoBase):
    TITULO = "HASH EXTERNO - TRUNCAMIENTO"
    DESCRIPCION = (
        "Funcion hash por truncamiento: se toman los primeros digitos de la clave "
        "para formar el indice, luego se aplica mod M para ajustar al rango de cubetas."
    )

    def calcular_hash(self, clave_int, capacidad):
        # Tomamos los 2 primeros digitos del numero como indice base
        s = str(clave_int)
        parte = s[:2] if len(s) >= 2 else s
        return int(parte) % capacidad
