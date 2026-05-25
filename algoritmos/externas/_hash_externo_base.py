"""
Base compartida para las ventanas de Hash Externas.
Cada funcion hash concreta hereda de HashExternoBase
y sobreescribe solo: TITULO, DESCRIPCION y calcular_hash(clave, capacidad).
"""
import json
import math
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
                border-radius: 4px; padding: 5px; color: #003366; font-size: 14px;
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


ESTILO_GLOBAL = """
    QMainWindow { background-color: #f0f8ff; }
    QLabel      { color: #003366; }
    QPushButton {
        background-color: #e6f2ff; color: #003366; font-weight: bold;
        border: 2px solid #99ccff; border-radius: 6px; padding: 8px;
    }
    QPushButton:hover   { background-color: #cce6ff; }
    QPushButton:pressed { background-color: #b3d9ff; }
    QComboBox, QSpinBox {
        background-color: white; border: 2px solid #99ccff;
        border-radius: 4px; padding: 5px; color: #003366;
    }
    QScrollArea { background-color: transparent; border: none; }
"""


# ------------------------------------------------------------------ #
class HashExternoBase(QMainWindow):
    """
    Clase base.  Subclases deben definir:
        TITULO      = "..."
        DESCRIPCION = "..."
    y el metodo:
        calcular_hash(self, clave_int, capacidad) -> int
    """
    TITULO = "Hash Externo"
    DESCRIPCION = ""

    def __init__(self, volver_a_busquedas_externas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas_externas = volver_a_busquedas_externas
        self.volver_a_principal = volver_a_principal

        # Estado
        self.estructura = []    # lista de listas (cubetas/bloques)
        self.capacidad = 0      # numero de cubetas
        self.tam_cubeta = 3     # registros por cubeta
        self.digitos = 4
        self.historial = []

        self.initUI()

    # ---------------------------------------------------------------- #
    def calcular_hash(self, clave_int, capacidad):
        raise NotImplementedError

    # ---------------------------------------------------------------- #
    def initUI(self):
        self.setWindowTitle(self.TITULO)
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet(ESTILO_GLOBAL)

        central = QWidget()
        self.setCentralWidget(central)
        lp = QVBoxLayout(central)
        lp.setSpacing(15)
        lp.setContentsMargins(20, 20, 20, 20)

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
        titulo_lbl = QLabel(self.TITULO)
        titulo_lbl.setFont(QFont("Arial", 18, QFont.Bold))
        titulo_lbl.setStyleSheet("color: #003366;")
        hl.addWidget(titulo_lbl)
        hl.addStretch()
        lp.addWidget(header)

        if self.DESCRIPCION:
            desc = QLabel(self.DESCRIPCION)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #336699; font-size: 13px;")
            lp.addWidget(desc)

        # Config
        cf = QFrame()
        cf.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        cl = QHBoxLayout(cf)
        cl.addWidget(QLabel("Numero de cubetas:"))
        self.spin_cap = QSpinBox()
        self.spin_cap.setRange(1, 50)
        self.spin_cap.setValue(7)
        self.spin_cap.setFixedWidth(80)
        cl.addWidget(self.spin_cap)
        cl.addSpacing(20)
        cl.addWidget(QLabel("Registros por cubeta:"))
        self.spin_tam = QSpinBox()
        self.spin_tam.setRange(1, 10)
        self.spin_tam.setValue(self.tam_cubeta)
        self.spin_tam.setFixedWidth(80)
        cl.addWidget(self.spin_tam)
        cl.addSpacing(20)
        cl.addWidget(QLabel("Digitos de clave:"))
        self.spin_digitos = QSpinBox()
        self.spin_digitos.setRange(1, 10)
        self.spin_digitos.setValue(self.digitos)
        self.spin_digitos.setFixedWidth(80)
        cl.addWidget(self.spin_digitos)
        cl.addStretch()
        lp.addWidget(cf)

        # Acciones
        af = QFrame()
        af.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        al = QGridLayout(af)
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
        lp.addWidget(af)

        # Scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.contenedor = QWidget()
        self.contenedor_layout = QVBoxLayout(self.contenedor)
        self.contenedor_layout.setSpacing(10)
        self.contenedor_layout.setContentsMargins(20, 20, 20, 20)
        self.contenedor_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.scroll.setWidget(self.contenedor)
        lp.addWidget(self.scroll)

        self.habilitar_botones(False)

    # ---------------------------------------------------------------- #
    def habilitar_botones(self, h):
        for n in ["Insertar clave", "Buscar clave", "Eliminar clave",
                  "Guardar estructura", "Eliminar estructura", "Deshacer"]:
            self.btns[n].setEnabled(h)
        self.btns["Cargar estructura"].setEnabled(True)

    def limpiar_vista(self):
        while self.contenedor_layout.count():
            item = self.contenedor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def actualizar_vista(self, resaltar_cubeta=-1, resaltar_pos=-1, color="#ffff99"):
        self.limpiar_vista()
        for c_idx, cubeta in enumerate(self.estructura):
            lbl_t = QLabel(f"Cubeta {c_idx}")
            lbl_t.setFont(QFont("Arial", 11, QFont.Bold))
            lbl_t.setStyleSheet("color: #003366;")
            self.contenedor_layout.addWidget(lbl_t)

            fila = QWidget()
            fl = QHBoxLayout(fila)
            fl.setSpacing(4)
            fl.setContentsMargins(0, 0, 0, 0)
            fl.setAlignment(Qt.AlignLeft)
            for r_idx, reg in enumerate(cubeta):
                lbl = QLabel(str(reg) if reg is not None else "---")
                lbl.setFixedSize(80, 50)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Arial", 12, QFont.Bold))
                if c_idx == resaltar_cubeta and r_idx == resaltar_pos:
                    lbl.setStyleSheet(f"background-color: {color}; border: 2px solid #003366; border-radius: 6px;")
                elif reg is None:
                    lbl.setStyleSheet("background-color: #f8f8f8; border: 1px dashed #aaccff; border-radius: 6px; color: #aaaaaa;")
                else:
                    lbl.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 6px;")
                fl.addWidget(lbl)
            self.contenedor_layout.addWidget(fila)

    # ---------------------------------------------------------------- #
    def crear_estructura(self):
        self.capacidad = self.spin_cap.value()
        self.tam_cubeta = self.spin_tam.value()
        self.digitos = self.spin_digitos.value()
        self.estructura = [[None] * self.tam_cubeta for _ in range(self.capacidad)]
        self.historial.clear()
        self.actualizar_vista()
        self.habilitar_botones(True)
        QMessageBox.information(self, "Listo",
                                f"Estructura creada: {self.capacidad} cubetas x {self.tam_cubeta} registros.")

    def insertar_clave(self):
        if not self.estructura:
            QMessageBox.warning(self, "Sin estructura", "Primero cree la estructura.")
            return
        dlg = DialogoClave(self.digitos, "Insertar clave", "insertar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())
        idx = self.calcular_hash(clave, self.capacidad)
        cubeta = self.estructura[idx]
        for r_idx, reg in enumerate(cubeta):
            if reg is None:
                snap = [list(c) for c in self.estructura]
                self.historial.append(snap)
                self.estructura[idx][r_idx] = clave
                self.actualizar_vista(idx, r_idx, "#aaffaa")
                QMessageBox.information(self, "Insertado",
                                        f"Clave {clave}  →  hash={idx}  →  Cubeta {idx}, pos {r_idx}.")
                return
        QMessageBox.warning(self, "Cubeta llena",
                            f"La cubeta {idx} esta llena (desbordamiento no implementado en modo externo basico).")

    def buscar_clave(self):
        if not self.estructura:
            QMessageBox.warning(self, "Sin estructura", "Primero cree la estructura.")
            return
        dlg = DialogoClave(self.digitos, "Buscar clave", "buscar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())
        idx = self.calcular_hash(clave, self.capacidad)
        cubeta = self.estructura[idx]
        for r_idx, reg in enumerate(cubeta):
            if reg == clave:
                self.actualizar_vista(idx, r_idx, "#aaffaa")
                QMessageBox.information(self, "Encontrada",
                                        f"Clave {clave} en Cubeta {idx}, posicion {r_idx}.")
                return
        self.actualizar_vista(idx, -1)
        QMessageBox.warning(self, "No encontrada",
                            f"Clave {clave} no encontrada (hash={idx}, cubeta revisada).")

    def eliminar_clave(self):
        if not self.estructura:
            QMessageBox.warning(self, "Sin estructura", "Primero cree la estructura.")
            return
        dlg = DialogoClave(self.digitos, "Eliminar clave", "eliminar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())
        idx = self.calcular_hash(clave, self.capacidad)
        cubeta = self.estructura[idx]
        for r_idx, reg in enumerate(cubeta):
            if reg == clave:
                snap = [list(c) for c in self.estructura]
                self.historial.append(snap)
                self.estructura[idx][r_idx] = None
                self.actualizar_vista(idx, r_idx, "#ffaaaa")
                QMessageBox.information(self, "Eliminada",
                                        f"Clave {clave} eliminada de Cubeta {idx}, pos {r_idx}.")
                return
        QMessageBox.warning(self, "No encontrada", f"Clave {clave} no encontrada.")

    def guardar_estructura(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if not ruta:
            return
        datos = {
            "algoritmo": self.TITULO,
            "fecha": datetime.now().isoformat(),
            "capacidad": self.capacidad,
            "tam_cubeta": self.tam_cubeta,
            "digitos": self.digitos,
            "estructura": self.estructura,
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        QMessageBox.information(self, "Guardado", f"Guardado en:\n{ruta}")

    def cargar_estructura(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Cargar", "", "JSON (*.json)")
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.capacidad = datos["capacidad"]
            self.tam_cubeta = datos["tam_cubeta"]
            self.digitos = datos["digitos"]
            self.estructura = datos["estructura"]
            self.historial.clear()
            self.actualizar_vista()
            self.habilitar_botones(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {e}")

    def eliminar_estructura(self):
        dlg = DialogoClave(0, "Confirmar", "confirmar", self, "¿Eliminar toda la estructura?")
        if dlg.exec() != QDialog.Accepted:
            return
        self.estructura.clear()
        self.historial.clear()
        self.limpiar_vista()
        self.habilitar_botones(False)

    def deshacer(self):
        if not self.historial:
            QMessageBox.information(self, "Deshacer", "No hay acciones para deshacer.")
            return
        self.estructura = self.historial.pop()
        self.actualizar_vista()

    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas_externas()

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()
