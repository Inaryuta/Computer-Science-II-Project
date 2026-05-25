"""
Expansion Parcial
-----------------
Cuando una cubeta se llena, solo ESA cubeta se divide en dos.
Los registros de la cubeta llena se redistribuyen entre las dos nuevas cubetas.
El resto de la estructura NO cambia.
"""
from algoritmos.externas._estructura_dinamica_base import EstructuraDinamicaBase


class ExpansionParcialWindow(EstructuraDinamicaBase):
    TITULO = "ESTRUCTURA DINAMICA - EXPANSION PARCIAL"
    DESCRIPCION = (
        "Al llenarse una cubeta, SOLO ESA cubeta se divide en dos nuevas cubetas. "
        "Los registros de la cubeta llena se redistribuyen entre ellas. "
        "El resto de la estructura permanece intacto. Menos costosa que la expansion total."
    )
    COLOR_ACCION = "#aaffaa"

    def _expandir(self, clave_nueva):
        # Encontrar la cubeta llena (la del hash de clave_nueva)
        idx_llena = clave_nueva % len(self.estructura)
        cubeta_llena = self.estructura[idx_llena]

        # Los registros de esa cubeta + la nueva clave
        registros = [r for r in cubeta_llena if r is not None] + [clave_nueva]

        # Crear dos nuevas cubetas en lugar de la cubeta llena
        cubeta_a = [None] * self.tam_cubeta
        cubeta_b = [None] * self.tam_cubeta
        idx_a, idx_b = 0, 0

        nueva_m = len(self.estructura) + 1  # M temporal para redistribuir dentro de las 2
        for reg in registros:
            if reg % 2 == clave_nueva % 2:
                if idx_a < self.tam_cubeta:
                    cubeta_a[idx_a] = reg
                    idx_a += 1
            else:
                if idx_b < self.tam_cubeta:
                    cubeta_b[idx_b] = reg
                    idx_b += 1

        # Reemplazar la cubeta llena con las dos nuevas
        self.estructura[idx_llena] = cubeta_a
        self.estructura.insert(idx_llena + 1, cubeta_b)

        return (
            f"EXPANSION PARCIAL: Cubeta {idx_llena} dividida en dos.\n"
            f"Total de cubetas: {len(self.estructura) - 1} → {len(self.estructura)}.\n"
            f"Solo los {len(registros)} registros de esa cubeta fueron redistribuidos."
        )

    def _reducir(self):
        pass
