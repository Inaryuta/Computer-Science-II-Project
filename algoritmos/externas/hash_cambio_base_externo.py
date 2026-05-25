"""Hash Cambio de Base Externo: interpreta la clave en base diferente"""
from algoritmos.externas._hash_externo_base import HashExternoBase


class HashCambioBaseExternoWindow(HashExternoBase):
    TITULO = "HASH EXTERNO - CAMBIO DE BASE"
    DESCRIPCION = (
        "Funcion hash por cambio de base: la clave decimal se interpreta digito a digito "
        "como si estuviera en base 11, el resultado se convierte a base 10 y se aplica mod M. "
        "Esto distribuye mejor las claves con patrones regulares."
    )

    def calcular_hash(self, clave_int, capacidad):
        # Interpretar los digitos de la clave en base 11
        s = str(clave_int)
        resultado = 0
        for digito in s:
            resultado = resultado * 11 + int(digito)
        return resultado % capacidad
