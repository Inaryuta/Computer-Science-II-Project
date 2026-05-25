"""
Reduccion Total
---------------
Cuando la ocupacion global cae por debajo del 25%, se REDUCE a la mitad
el numero de cubetas y se redistribuyen todos los registros.
"""
from algoritmos.externas._estructura_dinamica_base import EstructuraDinamicaBase
from PySide6.QtWidgets import QMessageBox


class ReduccionTotalWindow(EstructuraDinamicaBase):
    TITULO = "ESTRUCTURA DINAMICA - REDUCCION TOTAL"
    DESCRIPCION = (
        "Cuando la ocupacion global cae por debajo del 25%, el numero de cubetas se REDUCE A LA MITAD "
        "y TODOS los registros se redistribuyen. "
        "Libera memoria cuando los datos disminuyen significativamente."
    )
    COLOR_ACCION = "#ffaaaa"

    def _expandir(self, clave_nueva):
        # En reduccion total, si se llena simplemente agregamos una cubeta
        nueva_cubeta = [None] * self.tam_cubeta
        nueva_cubeta[0] = clave_nueva
        self.estructura.append(nueva_cubeta)
        return f"Cubeta llena. Se agrego una nueva cubeta (total: {len(self.estructura)})."

    def _post_eliminar(self, idx_cubeta):
        """Verifica si debe reducir tras una eliminacion."""
        total_slots = len(self.estructura) * self.tam_cubeta
        ocupados = sum(1 for c in self.estructura for r in c if r is not None)
        if total_slots > 0 and (ocupados / total_slots) < 0.25 and len(self.estructura) > 1:
            msg = self._reducir()
            self.actualizar_vista()
            QMessageBox.information(None, "Reduccion activada", msg)

    def _reducir(self):
        nueva_m = max(1, len(self.estructura) // 2)
        nueva_estructura = [[None] * self.tam_cubeta for _ in range(nueva_m)]
        todos = [r for c in self.estructura for r in c if r is not None]
        for clave in todos:
            idx = clave % nueva_m
            for r_idx, reg in enumerate(nueva_estructura[idx]):
                if reg is None:
                    nueva_estructura[idx][r_idx] = clave
                    break
        old_m = len(self.estructura)
        self.estructura = nueva_estructura
        return (
            f"REDUCCION TOTAL: {old_m} cubetas → {nueva_m} cubetas.\n"
            f"Ocupacion era menor al 25%. Todos los registros redistribuidos."
        )
