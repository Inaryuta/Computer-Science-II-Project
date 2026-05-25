"""
Busqueda Lineal Externa
-----------------------
Simula busqueda lineal sobre un archivo externo (lista de bloques).
Cada bloque contiene un numero fijo de registros.
El algoritmo recorre bloque a bloque hasta encontrar la clave.
"""
import json
import os
import random
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QScrollArea,
    QMessageBox, QFileDialog, QDialog, QLineEdit, QDialogButtonBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator


# ------------------------------------------------------------------ #
#  Dialogo reutilizable para ingresar clave                           #
# ------------------------------------------------------------------ #
class DialogoClave(QDialog):
    def __init__(self, longitud, titulo="Ingresar clave", modo="insertar",
                 parent=None, mensaje=None):
        super().__init__(parent)
        self.longitud = longitud
        self.modo = modo
        self.clave_ingresada = ""
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog { background-color: #f0f8ff; }
            QLabel  { color: #003366; font-size: 14px; }
            QLineEdit {
                background-color: white; border: 2px solid #99ccff;
                border-radius: 4px; padding: 5px;
                color: #003366; font-size: 14px;
            }
            QPushButton {
                background-color: #e6f2ff; color: #003366;
                border: 2px solid #99ccff; border-radius: 5px;
                padding: 8px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #cce6ff; }
        """)
        layout = QVBoxLayout(self)
        if modo in ("mensaje", "confirmar"):
            lbl = QLabel(mensaje or "")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)
            if modo == "confirmar":
                bb = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
                bb.accepted.connect(self.accept)
                bb.rejected.connect(self.reject)
            else:
                bb = QPushButton("Aceptar")
                bb.clicked.connect(self.accept)
            layout.addWidget(bb)
        else:
            layout.addWidget(QLabel(f"Ingrese una clave de {longitud} digitos:"))
            self.edit_clave = QLineEdit()
            self.edit_clave.setMaxLength(longitud)
            self.edit_clave.setValidator(QIntValidator(0, 10 ** longitud - 1))
            self.edit_clave.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.edit_clave)
            bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            bb.accepted.connect(self.validar_y_aceptar)
            bb.rejected.connect(self.reject)
            layout.addWidget(bb)

    def validar_y_aceptar(self):
        clave = self.edit_clave.text()
        if len(clave) != self.longitud:
            QMessageBox.warning(self, "Error",
                                f"La clave debe tener exactamente {self.longitud} digitos.")
            return
        self.clave_ingresada = clave
        self.accept()

    def get_clave(self):
        return self.clave_ingresada


# ------------------------------------------------------------------ #
#  Ventana principal                                                  #
# ------------------------------------------------------------------ #
ESTILO_GLOBAL = """
    QMainWindow { background-color: #f0f8ff; }
    QLabel      { color: #003366; }
    QPushButton {
        background-color: #e6f2ff; color: #003366;
        font-weight: bold; border: 2px solid #99ccff;
        border-radius: 6px; padding: 8px;
    }
    QPushButton:hover   { background-color: #cce6ff; }
    QPushButton:pressed { background-color: #b3d9ff; }
    QComboBox, QSpinBox {
        background-color: white; border: 2px solid #99ccff;
        border-radius: 4px; padding: 5px; color: #003366;
    }
    QScrollArea { background-color: transparent; border: none; }
"""


class BusquedaLinealExternaWindow(QMainWindow):
    def __init__(self, volver_a_busquedas_externas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas_externas = volver_a_busquedas_externas
        self.volver_a_principal = volver_a_principal

        # Estado
        self.bloques = []          # lista de listas; cada sublista = bloque
        self.capacidad_bloque = 3  # registros por bloque
        self.digitos = 4
        self.historial = []

        self.labels_bloques = []   # lista de listas de QLabel
        self.initUI()

    # ---------------------------------------------------------------- #
    def initUI(self):
        self.setWindowTitle("Busqueda Lineal Externa")
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet(ESTILO_GLOBAL)

        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QFrame()
        header.setStyleSheet("QFrame { background-color: #cce6ff; border-radius: 10px; padding: 5px; }")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 5, 10, 5)

        btn_inicio = QPushButton("  Inicio")
        btn_inicio.setCursor(Qt.PointingHandCursor)
        btn_inicio.clicked.connect(self.ir_a_principal)
        hl.addWidget(btn_inicio)

        btn_menu = QPushButton("  Menu Busquedas Externas")
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.clicked.connect(self.ir_a_busquedas)
        hl.addWidget(btn_menu)

        hl.addStretch()
        titulo = QLabel("BUSQUEDA LINEAL EXTERNA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        hl.addWidget(titulo)
        hl.addStretch()
        layout_principal.addWidget(header)

        # Descripcion
        desc = QLabel(
            "Simula busqueda en archivo externo organizado en bloques. "
            "El algoritmo lee bloque a bloque hasta encontrar la clave."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #336699; font-size: 13px;")
        layout_principal.addWidget(desc)

        # Config
        config_frame = QFrame()
        config_frame.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        cl = QHBoxLayout(config_frame)

        cl.addWidget(QLabel("Registros por bloque:"))
        self.spin_cap = QSpinBox()
        self.spin_cap.setRange(1, 10)
        self.spin_cap.setValue(self.capacidad_bloque)
        self.spin_cap.setFixedWidth(80)
        cl.addWidget(self.spin_cap)

        cl.addSpacing(20)
        cl.addWidget(QLabel("Digitos de clave:"))
        self.spin_digitos = QSpinBox()
        self.spin_digitos.setRange(1, 10)
        self.spin_digitos.setValue(self.digitos)
        self.spin_digitos.setFixedWidth(80)
        cl.addWidget(self.spin_digitos)
        cl.addStretch()
        layout_principal.addWidget(config_frame)

        # Acciones
        acciones_frame = QFrame()
        acciones_frame.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        al = QGridLayout(acciones_frame)

        botones = [
            ("Crear estructura",    self.crear_estructura),
            ("Insertar clave",      self.insertar_clave),
            ("Buscar clave",        self.buscar_clave),
            ("Eliminar clave",      self.eliminar_clave),
            ("Guardar estructura",  self.guardar_estructura),
            ("Cargar estructura",   self.cargar_estructura),
            ("Eliminar estructura", self.eliminar_estructura),
            ("Deshacer",            self.deshacer),
        ]
        self.btns = {}
        for i, (texto, slot) in enumerate(botones):
            btn = QPushButton(texto)
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            al.addWidget(btn, i // 4, i % 4)
            self.btns[texto] = btn

        layout_principal.addWidget(acciones_frame)

        # Area de visualizacion
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.contenedor = QWidget()
        self.contenedor_layout = QVBoxLayout(self.contenedor)
        self.contenedor_layout.setSpacing(10)
        self.contenedor_layout.setContentsMargins(20, 20, 20, 20)
        self.contenedor_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.scroll.setWidget(self.contenedor)
        layout_principal.addWidget(self.scroll)

        self.habilitar_botones(False)

    # ---------------------------------------------------------------- #
    #  Helpers                                                          #
    # ---------------------------------------------------------------- #
    def habilitar_botones(self, habilitar):
        for nombre in ["Insertar clave", "Buscar clave", "Eliminar clave",
                       "Guardar estructura", "Eliminar estructura", "Deshacer"]:
            self.btns[nombre].setEnabled(habilitar)
        self.btns["Cargar estructura"].setEnabled(True)

    def limpiar_vista(self):
        while self.contenedor_layout.count():
            item = self.contenedor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.labels_bloques.clear()

    def actualizar_vista(self, resaltar_bloque=-1, resaltar_pos=-1, color_res="#ffff99"):
        self.limpiar_vista()
        for b_idx, bloque in enumerate(self.bloques):
            # Titulo del bloque
            lbl_titulo = QLabel(f"Bloque {b_idx}")
            lbl_titulo.setFont(QFont("Arial", 11, QFont.Bold))
            lbl_titulo.setStyleSheet("color: #003366;")
            self.contenedor_layout.addWidget(lbl_titulo)

            fila_widget = QWidget()
            fila_layout = QHBoxLayout(fila_widget)
            fila_layout.setSpacing(4)
            fila_layout.setContentsMargins(0, 0, 0, 0)
            fila_layout.setAlignment(Qt.AlignLeft)

            fila_labels = []
            for r_idx, registro in enumerate(bloque):
                lbl = QLabel(str(registro) if registro is not None else "---")
                lbl.setFixedSize(80, 50)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Arial", 12, QFont.Bold))

                if b_idx == resaltar_bloque and r_idx == resaltar_pos:
                    lbl.setStyleSheet(
                        f"background-color: {color_res}; border: 2px solid #003366; border-radius: 6px;")
                elif registro is None:
                    lbl.setStyleSheet(
                        "background-color: #f8f8f8; border: 1px dashed #aaccff; border-radius: 6px; color: #aaaaaa;")
                else:
                    lbl.setStyleSheet(
                        "background-color: white; border: 2px solid #99ccff; border-radius: 6px;")
                fila_layout.addWidget(lbl)
                fila_labels.append(lbl)

            self.contenedor_layout.addWidget(fila_widget)
            self.labels_bloques.append(fila_labels)

    # ---------------------------------------------------------------- #
    #  Acciones                                                         #
    # ---------------------------------------------------------------- #
    def crear_estructura(self):
        self.capacidad_bloque = self.spin_cap.value()
        self.digitos = self.spin_digitos.value()
        # Empezamos con 3 bloques vacios
        self.bloques = [[None] * self.capacidad_bloque for _ in range(3)]
        self.historial.clear()
        self.actualizar_vista()
        self.habilitar_botones(True)
        QMessageBox.information(self, "Listo",
                                f"Estructura creada con 3 bloques de {self.capacidad_bloque} registros cada uno.")

    def insertar_clave(self):
        dlg = DialogoClave(self.digitos, "Insertar clave", "insertar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())

        # Buscar espacio libre
        for b_idx, bloque in enumerate(self.bloques):
            for r_idx, reg in enumerate(bloque):
                if reg is None:
                    snapshot = [list(b) for b in self.bloques]
                    self.historial.append(snapshot)
                    self.bloques[b_idx][r_idx] = clave
                    self.actualizar_vista(b_idx, r_idx, "#aaffaa")
                    QMessageBox.information(self, "Insertado",
                                            f"Clave {clave} insertada en Bloque {b_idx}, posicion {r_idx}.")
                    return

        # No hay espacio: agregar bloque nuevo
        snapshot = [list(b) for b in self.bloques]
        self.historial.append(snapshot)
        nuevo = [None] * self.capacidad_bloque
        nuevo[0] = clave
        self.bloques.append(nuevo)
        self.actualizar_vista(len(self.bloques) - 1, 0, "#aaffaa")
        QMessageBox.information(self, "Nuevo bloque",
                                f"No habia espacio. Se agrego un nuevo bloque y se inserto la clave {clave}.")

    def buscar_clave(self):
        dlg = DialogoClave(self.digitos, "Buscar clave", "buscar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())

        for b_idx, bloque in enumerate(self.bloques):
            for r_idx, reg in enumerate(bloque):
                if reg == clave:
                    self.actualizar_vista(b_idx, r_idx, "#aaffaa")
                    QMessageBox.information(self, "Encontrada",
                                            f"Clave {clave} encontrada en Bloque {b_idx}, posicion {r_idx}.\n"
                                            f"Se revisaron {b_idx * self.capacidad_bloque + r_idx + 1} registros.")
                    return
        self.actualizar_vista()
        QMessageBox.warning(self, "No encontrada", f"La clave {clave} no esta en la estructura.")

    def eliminar_clave(self):
        dlg = DialogoClave(self.digitos, "Eliminar clave", "eliminar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())

        for b_idx, bloque in enumerate(self.bloques):
            for r_idx, reg in enumerate(bloque):
                if reg == clave:
                    snapshot = [list(b) for b in self.bloques]
                    self.historial.append(snapshot)
                    self.bloques[b_idx][r_idx] = None
                    self.actualizar_vista(b_idx, r_idx, "#ffaaaa")
                    QMessageBox.information(self, "Eliminada",
                                            f"Clave {clave} eliminada del Bloque {b_idx}, posicion {r_idx}.")
                    return
        QMessageBox.warning(self, "No encontrada", f"La clave {clave} no esta en la estructura.")

    def guardar_estructura(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if not ruta:
            return
        datos = {
            "algoritmo": "Busqueda Lineal Externa",
            "fecha": datetime.now().isoformat(),
            "capacidad_bloque": self.capacidad_bloque,
            "digitos": self.digitos,
            "bloques": self.bloques,
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        QMessageBox.information(self, "Guardado", f"Estructura guardada en:\n{ruta}")

    def cargar_estructura(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.capacidad_bloque = datos["capacidad_bloque"]
            self.digitos = datos["digitos"]
            self.bloques = datos["bloques"]
            self.historial.clear()
            self.actualizar_vista()
            self.habilitar_botones(True)
            QMessageBox.information(self, "Cargado", "Estructura cargada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {e}")

    def eliminar_estructura(self):
        dlg = DialogoClave(0, "Confirmar", "confirmar", self,
                           "¿Desea eliminar toda la estructura?")
        if dlg.exec() != QDialog.Accepted:
            return
        self.bloques.clear()
        self.historial.clear()
        self.limpiar_vista()
        self.habilitar_botones(False)
        QMessageBox.information(self, "Eliminada", "Estructura eliminada.")

    def deshacer(self):
        if not self.historial:
            QMessageBox.information(self, "Deshacer", "No hay acciones para deshacer.")
            return
        self.bloques = self.historial.pop()
        self.actualizar_vista()
        QMessageBox.information(self, "Deshacer", "Ultima accion deshecha.")

    # ---------------------------------------------------------------- #
    #  Navegacion                                                       #
    # ---------------------------------------------------------------- #
    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas_externas()

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()
