"""Hash Mod Externo: h(k) = k mod M"""
from algoritmos.externas._hash_externo_base import HashExternoBase


class HashModExternoWindow(HashExternoBase):
    TITULO = "HASH EXTERNO - MODULO (MOD)"
    DESCRIPCION = (
        "Funcion hash: h(k) = k mod M   donde M = numero de cubetas. "
        "Cada clave se almacena en la cubeta que indica su resto al dividir entre M."
    )

    def calcular_hash(self, clave_int, capacidad):
        return clave_int % capacidad
