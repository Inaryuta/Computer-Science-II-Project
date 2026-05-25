"""
Expansion Total
---------------
Cuando una cubeta se llena, se DUPLICA el numero total de cubetas
y se redistribuyen TODOS los registros con la nueva funcion hash.
"""
from algoritmos.externas._estructura_dinamica_base import EstructuraDinamicaBase


class ExpansionTotalWindow(EstructuraDinamicaBase):
    TITULO = "ESTRUCTURA DINAMICA - EXPANSION TOTAL"
    DESCRIPCION = (
        "Al llenarse cualquier cubeta, el numero de cubetas se DUPLICA completamente "
        "y TODOS los registros existentes se redistribuyen usando la nueva funcion hash (k mod nuevaM). "
        "Costosa pero garantiza balance total."
    )
    COLOR_ACCION = "#aaffaa"

    def _expandir(self, clave_nueva):
        nueva_m = len(self.estructura) * 2
        nueva_estructura = [[None] * self.tam_cubeta for _ in range(nueva_m)]
        # Redistribuir todos los registros existentes + la nueva clave
        todos = [r for c in self.estructura for r in c if r is not None]
        todos.append(clave_nueva)
        for clave in todos:
            idx = clave % nueva_m
            for r_idx, reg in enumerate(nueva_estructura[idx]):
                if reg is None:
                    nueva_estructura[idx][r_idx] = clave
                    break
        self.estructura = nueva_estructura
        return (
            f"EXPANSION TOTAL: {nueva_m // 2} cubetas → {nueva_m} cubetas.\n"
            f"Todos los {len(todos)} registros fueron redistribuidos."
        )

    def _reducir(self):
        pass  # No aplica en expansion
