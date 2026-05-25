"""
Busqueda Binaria Externa
------------------------
Simula busqueda binaria sobre un archivo externo ordenado en bloques.
Se compara la clave buscada contra la clave mayor de cada bloque
para determinar en cual bloque leer (division binaria de bloques).
"""
import json
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSpinBox, QScrollArea,
    QMessageBox, QFileDialog, QDialog, QLineEdit, QDialogButtonBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator


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


class BusquedaBinariaExternaWindow(QMainWindow):
    def __init__(self, volver_a_busquedas_externas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas_externas = volver_a_busquedas_externas
        self.volver_a_principal = volver_a_principal

        self.bloques = []          # lista de listas ordenadas
        self.capacidad_bloque = 4
        self.digitos = 4
        self.historial = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Busqueda Binaria Externa")
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
        titulo = QLabel("BUSQUEDA BINARIA EXTERNA")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        hl.addWidget(titulo)
        hl.addStretch()
        lp.addWidget(header)

        desc = QLabel(
            "Archivo externo ordenado dividido en bloques. "
            "La busqueda compara contra el mayor de cada bloque y divide el espacio a la mitad."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #336699; font-size: 13px;")
        lp.addWidget(desc)

        # Config
        cf = QFrame()
        cf.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        cl = QHBoxLayout(cf)
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
        self.cl = QVBoxLayout(self.contenedor)
        self.cl.setSpacing(10)
        self.cl.setContentsMargins(20, 20, 20, 20)
        self.cl.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.scroll.setWidget(self.contenedor)
        lp.addWidget(self.scroll)

        self.habilitar_botones(False)

    def habilitar_botones(self, h):
        for n in ["Insertar clave", "Buscar clave", "Eliminar clave",
                  "Guardar estructura", "Eliminar estructura", "Deshacer"]:
            self.btns[n].setEnabled(h)
        self.btns["Cargar estructura"].setEnabled(True)

    def limpiar_vista(self):
        while self.cl.count():
            item = self.cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def actualizar_vista(self, resaltar_bloque=-1, resaltar_pos=-1, color="#ffff99"):
        self.limpiar_vista()
        for b_idx, bloque in enumerate(self.bloques):
            lbl_t = QLabel(f"Bloque {b_idx}  |  mayor: {max((x for x in bloque if x is not None), default='—')}")
            lbl_t.setFont(QFont("Arial", 11, QFont.Bold))
            lbl_t.setStyleSheet("color: #003366;")
            self.cl.addWidget(lbl_t)

            fila = QWidget()
            fl = QHBoxLayout(fila)
            fl.setSpacing(4)
            fl.setContentsMargins(0, 0, 0, 0)
            fl.setAlignment(Qt.AlignLeft)
            for r_idx, reg in enumerate(bloque):
                lbl = QLabel(str(reg) if reg is not None else "---")
                lbl.setFixedSize(80, 50)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Arial", 12, QFont.Bold))
                if b_idx == resaltar_bloque and r_idx == resaltar_pos:
                    lbl.setStyleSheet(f"background-color: {color}; border: 2px solid #003366; border-radius: 6px;")
                elif reg is None:
                    lbl.setStyleSheet("background-color: #f8f8f8; border: 1px dashed #aaccff; border-radius: 6px; color: #aaaaaa;")
                else:
                    lbl.setStyleSheet("background-color: white; border: 2px solid #99ccff; border-radius: 6px;")
                fl.addWidget(lbl)
            self.cl.addWidget(fila)

    def _insertar_ordenado(self, clave):
        """Inserta manteniendo orden dentro de cada bloque y entre bloques."""
        todos = sorted([r for b in self.bloques for r in b if r is not None] + [clave])
        # Redistribuir en bloques
        nuevo_bloques = []
        for i in range(0, len(todos), self.capacidad_bloque):
            chunk = todos[i:i + self.capacidad_bloque]
            while len(chunk) < self.capacidad_bloque:
                chunk.append(None)
            nuevo_bloques.append(chunk)
        if not nuevo_bloques:
            nuevo_bloques = [[None] * self.capacidad_bloque]
        self.bloques = nuevo_bloques

    def crear_estructura(self):
        self.capacidad_bloque = self.spin_cap.value()
        self.digitos = self.spin_digitos.value()
        self.bloques = [[None] * self.capacidad_bloque for _ in range(3)]
        self.historial.clear()
        self.actualizar_vista()
        self.habilitar_botones(True)
        QMessageBox.information(self, "Listo",
                                f"Estructura creada: 3 bloques de {self.capacidad_bloque} registros (ordenada).")

    def insertar_clave(self):
        dlg = DialogoClave(self.digitos, "Insertar clave", "insertar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())
        snap = [list(b) for b in self.bloques]
        self.historial.append(snap)
        self._insertar_ordenado(clave)
        self.actualizar_vista()
        QMessageBox.information(self, "Insertado", f"Clave {clave} insertada y bloques reordenados.")

    def buscar_clave(self):
        dlg = DialogoClave(self.digitos, "Buscar clave", "buscar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())

        izq, der = 0, len(self.bloques) - 1
        pasos = 0
        while izq <= der:
            mid = (izq + der) // 2
            bloque = self.bloques[mid]
            validos = [r for r in bloque if r is not None]
            pasos += 1
            if not validos:
                der = mid - 1
                continue
            mayor = max(validos)
            menor = min(validos)
            if clave in validos:
                pos = bloque.index(clave)
                self.actualizar_vista(mid, pos, "#aaffaa")
                QMessageBox.information(self, "Encontrada",
                                        f"Clave {clave} en Bloque {mid}, posicion {pos}.\n"
                                        f"Bloques revisados: {pasos}.")
                return
            elif clave > mayor:
                izq = mid + 1
            else:
                der = mid - 1

        self.actualizar_vista()
        QMessageBox.warning(self, "No encontrada", f"La clave {clave} no esta en la estructura.")

    def eliminar_clave(self):
        dlg = DialogoClave(self.digitos, "Eliminar clave", "eliminar", self)
        if dlg.exec() != QDialog.Accepted:
            return
        clave = int(dlg.get_clave())
        for b_idx, bloque in enumerate(self.bloques):
            if clave in bloque:
                snap = [list(b) for b in self.bloques]
                self.historial.append(snap)
                pos = bloque.index(clave)
                self.bloques[b_idx][pos] = None
                # Recompactar
                todos = sorted([r for b in self.bloques for r in b if r is not None])
                nuevo = []
                for i in range(0, len(todos), self.capacidad_bloque):
                    chunk = todos[i:i + self.capacidad_bloque]
                    while len(chunk) < self.capacidad_bloque:
                        chunk.append(None)
                    nuevo.append(chunk)
                if not nuevo:
                    nuevo = [[None] * self.capacidad_bloque for _ in range(3)]
                self.bloques = nuevo
                self.actualizar_vista()
                QMessageBox.information(self, "Eliminada", f"Clave {clave} eliminada.")
                return
        QMessageBox.warning(self, "No encontrada", f"La clave {clave} no esta en la estructura.")

    def guardar_estructura(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if not ruta:
            return
        datos = {
            "algoritmo": "Busqueda Binaria Externa",
            "fecha": datetime.now().isoformat(),
            "capacidad_bloque": self.capacidad_bloque,
            "digitos": self.digitos,
            "bloques": self.bloques,
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
            self.capacidad_bloque = datos["capacidad_bloque"]
            self.digitos = datos["digitos"]
            self.bloques = datos["bloques"]
            self.historial.clear()
            self.actualizar_vista()
            self.habilitar_botones(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {e}")

    def eliminar_estructura(self):
        dlg = DialogoClave(0, "Confirmar", "confirmar", self, "¿Eliminar toda la estructura?")
        if dlg.exec() != QDialog.Accepted:
            return
        self.bloques.clear()
        self.historial.clear()
        self.limpiar_vista()
        self.habilitar_botones(False)

    def deshacer(self):
        if not self.historial:
            QMessageBox.information(self, "Deshacer", "No hay acciones para deshacer.")
            return
        self.bloques = self.historial.pop()
        self.actualizar_vista()

    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas_externas()

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()
