"""
Reduccion Parcial
-----------------
Cuando una cubeta queda vacía o con muy pocos elementos,
SOLO ESA CUBETA se fusiona con la cubeta adyacente.
El resto de la estructura NO cambia.
"""
from algoritmos.externas._estructura_dinamica_base import EstructuraDinamicaBase
from PySide6.QtWidgets import QMessageBox


class ReduccionParcialWindow(EstructuraDinamicaBase):
    TITULO = "ESTRUCTURA DINAMICA - REDUCCION PARCIAL"
    DESCRIPCION = (
        "Cuando una cubeta queda completamente vacia, se fusiona con su cubeta vecina "
        "y los registros se combinan. Solo afecta a las dos cubetas involucradas. "
        "El resto de la estructura permanece intacto."
    )
    COLOR_ACCION = "#ffaaaa"

    def _expandir(self, clave_nueva):
        # En reduccion parcial, si se llena agregamos una cubeta al final
        nueva_cubeta = [None] * self.tam_cubeta
        nueva_cubeta[0] = clave_nueva
        self.estructura.append(nueva_cubeta)
        return f"Cubeta llena. Nueva cubeta agregada al final (total: {len(self.estructura)})."

    def _post_eliminar(self, idx_cubeta):
        """Si la cubeta queda vacia, fusionarla con la vecina."""
        cubeta = self.estructura[idx_cubeta]
        ocupados = sum(1 for r in cubeta if r is not None)
        if ocupados == 0 and len(self.estructura) > 1:
            msg = self._reducir_cubeta(idx_cubeta)
            self.actualizar_vista()
            QMessageBox.information(None, "Reduccion parcial activada", msg)

    def _reducir_cubeta(self, idx_vacia):
        # Elegir vecino: siguiente si existe, anterior si no
        if idx_vacia + 1 < len(self.estructura):
            idx_vecino = idx_vacia + 1
        else:
            idx_vecino = idx_vacia - 1

        # Fusionar registros del vecino en una sola cubeta
        registros_vecino = [r for r in self.estructura[idx_vecino] if r is not None]
        cubeta_fusion = [None] * self.tam_cubeta
        for i, r in enumerate(registros_vecino[:self.tam_cubeta]):
            cubeta_fusion[i] = r

        # Reemplazar: eliminar la cubeta vacia y colocar fusion en el vecino
        if idx_vacia < idx_vecino:
            self.estructura[idx_vacia] = cubeta_fusion
            self.estructura.pop(idx_vecino)
        else:
            self.estructura[idx_vecino] = cubeta_fusion
            self.estructura.pop(idx_vacia)

        return (
            f"REDUCCION PARCIAL: Cubeta {idx_vacia} vacia fusionada con Cubeta {idx_vecino}.\n"
            f"Total de cubetas: {len(self.estructura) + 1} → {len(self.estructura)}."
        )

    def _reducir(self):
        pass
