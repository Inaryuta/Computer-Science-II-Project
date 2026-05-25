"""
Índices Externos
----------------
Búsqueda mediante estructura de índices externos.
Soporta índice Primario y Secundario, en Un Nivel o Multinivel.

Estructura:
  - Archivo principal: bloques de registros de datos
  - Estructura de índice: bloques de entradas (puntero + clave)
  - Multinivel: se apilan estructuras de índice hasta llegar a 1 bloque raíz

Cálculos:
  regXBloque  = tamaBloque // tamaRegistro
  cantBloques = ceil(cantRegistros / regXBloque)

  Primario  → cantIndices = cantBloques   (un índice por bloque de datos)
  Secundario→ cantIndices = cantRegistros (un índice por registro)

  indXBloque      = tamaBloque // tamaRegistroIndice
  cantBloquesInd  = ceil(cantIndices / indXBloque)

  Multinivel: se repite sobre cantBloquesInd hasta llegar a 1.
"""
import math
import json
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QScrollArea,
    QMessageBox, QFileDialog, QDialog, QLineEdit, QDialogButtonBox,
    QFrame, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QPaintEvent, QIntValidator

# ─────────────────────────────────────────────────────────────────────────────
ESTILO_GLOBAL = """
    QMainWindow { background-color: #f0f8ff; }
    QWidget     { background-color: #f0f8ff; }
    QLabel      { color: #003366; }
    QPushButton {
        background-color: #e6f2ff; color: #003366; font-weight: bold;
        border: 2px solid #99ccff; border-radius: 6px; padding: 8px;
    }
    QPushButton:hover   { background-color: #cce6ff; }
    QPushButton:pressed { background-color: #b3d9ff; }
    QPushButton:disabled { background-color: #d0e8f8; color: #7aa0c0; }
    QComboBox, QSpinBox {
        background-color: white; border: 2px solid #99ccff;
        border-radius: 4px; padding: 5px; color: #003366;
    }
    QScrollArea { background-color: transparent; border: none; }
    QLineEdit {
        background-color: white; border: 2px solid #99ccff;
        border-radius: 4px; padding: 5px; color: #003366;
    }
    QLineEdit:focus { border: 2px solid #4d94ff; }
"""

ESTILO_HEADER = "QFrame { background-color: #cce6ff; border-radius: 10px; padding: 5px; }"
ESTILO_PANEL  = "QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }"
ESTILO_CANVAS = "background-color: #f0f8ff; border: 2px solid #99ccff; border-radius: 6px;"

COLOR_LINEA_PPAL  = QColor(0, 51, 102)       # azul oscuro — estructura principal
COLOR_LINEA_IDX   = QColor(0, 100, 180)      # azul medio — estructura índice
COLOR_LINEA_MULTI = QColor(50, 130, 200)     # azul claro  — niveles multinivel
COLOR_NEGRITA     = QColor(0, 51, 102)
COLOR_TEXTO       = QColor(0, 51, 102)
COLOR_FONDO_RECT  = QColor(230, 242, 255)    # azul muy claro para relleno


# ─────────────────────────────────────────────────────────────────────────────
class IndiceCanvas(QWidget):
    """Canvas que dibuja la representación visual de los bloques e índices."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(720, 500)
        self.setStyleSheet(ESTILO_CANVAS)

        # Estado del dibujo
        self.activo        = False
        self.resTabla      = []
        self.tipo          = ""
        self.cant_nivel    = ""
        self.tama_bloque   = 0
        self.cant_registro = 0
        self.tama_registro = 0
        self.tama_reg_idx  = 0
        self.cant_indices       = 0
        self.cant_estructuras   = 0
        self.reg_x_bloq         = 0
        self.cant_bloq_regis    = 0
        self.indic_x_bloq       = 0
        self.cant_bloq_indic    = 0

    # ------------------------------------------------------------------ #
    def calcular(self, tipo: str, cant_nivel: str,
                 tama_bloque: int, cant_registro: int,
                 tama_registro: int, tama_reg_idx: int):
        """
        Realiza todos los cálculos y devuelve la tabla de resultados.
        También dispara el repintado.
        """
        self.activo        = True
        self.resTabla      = []
        self.tipo          = tipo
        self.cant_nivel    = cant_nivel
        self.tama_bloque   = tama_bloque
        self.cant_registro = cant_registro
        self.tama_registro = tama_registro
        self.tama_reg_idx  = tama_reg_idx

        # ── Nivel 1: archivo principal ──────────────────────────────────
        self.reg_x_bloq      = tama_bloque // tama_registro
        self.cant_bloq_regis = math.ceil(cant_registro / self.reg_x_bloq)
        self.resTabla.append(["1", "Cant. registros",   str(cant_registro)])
        self.resTabla.append(["1", "Reg. x Bloque",     str(self.reg_x_bloq)])
        self.resTabla.append(["1", "Bloques",            str(self.cant_bloq_regis)])

        # ── Nivel 2: primer índice ──────────────────────────────────────
        self.indic_x_bloq = tama_bloque // tama_reg_idx
        if tipo == "Primario":
            self.cant_indices    = self.cant_bloq_regis
            self.cant_bloq_indic = math.ceil(self.cant_bloq_regis / self.indic_x_bloq)
        else:  # Secundario
            self.cant_indices    = cant_registro
            self.cant_bloq_indic = math.ceil(cant_registro / self.indic_x_bloq)

        self.resTabla.append(["2", "Cant. registros Índice", str(self.cant_indices)])
        self.resTabla.append(["2", "Ind x Bloque",           str(self.indic_x_bloq)])
        self.resTabla.append(["2", "Cant. Bloques Índice",   str(self.cant_bloq_indic)])

        # ── Niveles adicionales (multinivel) ───────────────────────────
        row = 2
        if cant_nivel == "Multinivel":
            cant_bloq_prev = self.cant_bloq_indic
            while cant_bloq_prev != 1:
                row += 1
                self.resTabla.append([str(row), "Cant. registros Índice", str(cant_bloq_prev)])
                self.resTabla.append([str(row), "Ind x Bloque",           str(self.indic_x_bloq)])
                cant_bloq_nuevo = math.ceil(cant_bloq_prev / self.indic_x_bloq)
                self.resTabla.append([str(row), "Cant. Bloques Índice",   str(cant_bloq_nuevo)])
                cant_bloq_prev = cant_bloq_nuevo

        self.cant_estructuras = row

        # Ajustar tamaño del canvas si hay muchos niveles
        if self.cant_estructuras > 3:
            sep       = 100
            borde     = 50
            ancho_est = 140
            nuevo_w   = borde * 2 + self.cant_estructuras * ancho_est + (self.cant_estructuras - 1) * sep
            self.setMinimumWidth(nuevo_w)
        else:
            self.setMinimumWidth(720)

        self.update()
        return self.resTabla

    # ------------------------------------------------------------------ #
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(240, 248, 255))   # fondo azul muy claro

        if not self.activo:
            p.end()
            return

        sep        = 100
        diff       = 30
        borde      = 50
        W          = self.rect().width()
        H          = self.rect().height()

        if self.cant_estructuras <= 3:
            ancho_est = (W - sep * (self.cant_estructuras - 1) - 2 * borde) // self.cant_estructuras
        else:
            ancho_est = 140

        # ── Estructura principal (datos) ────────────────────────────────
        self._dibujar_bloque_principal(p, W, H, borde, sep, ancho_est, diff)

        # ── Primer índice ───────────────────────────────────────────────
        self._dibujar_primer_indice(p, W, H, borde, sep, ancho_est, diff)

        # ── Niveles multinivel ──────────────────────────────────────────
        if self.cant_nivel == "Multinivel":
            self._dibujar_multinivel(p, W, H, borde, sep, ancho_est, diff)

        p.end()

    # ── helpers de dibujo ───────────────────────────────────────────── #
    def _pen(self, p, color, grosor=2):
        p.setPen(QPen(color, grosor))

    def _dibujar_bloque_principal(self, p, W, H, borde, sep, ae, diff):
        x = W - borde - ae
        y = borde
        h = H - 2 * borde

        self._pen(p, COLOR_LINEA_PPAL, 2)
        p.setFont(QFont("Arial", 9, QFont.Bold))
        p.drawText(x + ae // 2 - 30, y - 8, "Principal")
        p.setBrush(COLOR_FONDO_RECT)
        p.drawRect(x, y, ae, h)
        p.setBrush(Qt.NoBrush)

        # línea superior
        self._pen(p, COLOR_LINEA_PPAL, 2)
        p.drawLine(x, y + 10, x + ae, y + 10)
        p.drawText(x - 14, y + 7,  "1")
        p.drawText(x + ae // 2 - 8, y + 33, "B1")

        # línea separadora arriba (negrita = reg_x_bloq)
        self._pen(p, COLOR_NEGRITA, 4)
        p.drawLine(x, y + 58, x + ae, y + 58)
        txt_top = str(self.resTabla[1][2])
        p.drawText(x - len(txt_top) * 6 - 12, y + 58, txt_top)
        self._pen(p, COLOR_LINEA_PPAL, 2)
        p.drawLine(x, y + 48, x + ae, y + 48)

        # línea separadora abajo (negrita = último reg del último bloque)
        self._pen(p, COLOR_NEGRITA, 4)
        p.drawLine(x, y + h - 58, x + ae, y + h - 58)
        txt_bot = str(int(self.resTabla[0][2]) - int(self.resTabla[1][2]))
        p.drawText(x - len(txt_bot) * 6 - 12, y + h - 58, txt_bot)
        self._pen(p, COLOR_LINEA_PPAL, 2)
        p.drawText(x + ae // 2 - 8, y + h - 28, "B" + self.resTabla[2][2])
        p.drawLine(x, y + h - 10, x + ae, y + h - 10)
        p.drawText(x - len(self.resTabla[0][2]) * 6 - 12, y + h - 10, self.resTabla[0][2])

    def _dibujar_primer_indice(self, p, W, H, borde, sep, ae, diff):
        if self.tipo == "Primario":
            x = W - borde - 2 * ae - sep
            y = borde + diff // 2
            h = H - 2 * borde - diff
        else:  # Secundario
            x = W - borde - 2 * ae - sep
            y = borde
            h = H - 2 * borde

        self._pen(p, COLOR_LINEA_IDX, 2)
        p.setFont(QFont("Arial", 9, QFont.Bold))
        p.drawText(x + ae // 2 - 35, y - 8, "Est. Índice")
        p.setBrush(QColor(220, 235, 255))
        p.drawRect(x, y, ae, h)
        p.setBrush(Qt.NoBrush)

        self._pen(p, COLOR_LINEA_IDX, 2)
        p.drawLine(x, y + 10, x + ae, y + 10)
        p.drawText(x - 12, y + 7, "1")
        p.drawText(x + ae // 2 - 8, y + 33, "B1")

        mostrar_interior = (self.cant_bloq_indic != 1 or self.cant_estructuras != 2)
        if mostrar_interior:
            # línea separadora arriba
            self._pen(p, COLOR_NEGRITA, 4)
            p.drawLine(x, y + 58, x + ae, y + 58)
            txt = str(self.resTabla[4][2])
            p.drawText(x - len(txt) * 6 - 12, y + 58, txt)
            self._pen(p, COLOR_LINEA_IDX, 2)
            p.drawLine(x, y + 48, x + ae, y + 48)

            # línea separadora abajo
            self._pen(p, COLOR_NEGRITA, 4)
            p.drawLine(x, y + h - 58, x + ae, y + h - 58)
            txt2 = str(int(self.resTabla[3][2]) - int(self.resTabla[4][2]))
            p.drawText(x - len(txt2) * 6 - 12, y + h - 58, txt2)
            self._pen(p, COLOR_LINEA_IDX, 2)
            p.drawText(x + ae // 2 - 8, y + h - 28, "B" + self.resTabla[5][2])

        self._pen(p, COLOR_LINEA_IDX, 2)
        p.drawLine(x, y + h - 10, x + ae, y + h - 10)
        p.drawText(x - len(self.resTabla[3][2]) * 6 - 12, y + h - 3, self.resTabla[3][2])

        # flechas de conexión → estructura principal
        self._pen(p, COLOR_LINEA_PPAL, 2)
        y_ppal_top = borde + 5
        y_ppal_bot = borde + (H - 2 * borde) - 5
        p.drawLine(x + ae, y + 5,     x + ae + sep, y_ppal_top)
        p.drawLine(x + ae, y + h - 5, x + ae + sep, y_ppal_bot)

    def _dibujar_multinivel(self, p, W, H, borde, sep, ae, diff):
        for nivel in range(2, self.cant_estructuras):
            col   = nivel + 1          # columna desde la derecha (1=principal,2=idx1...)
            x     = W - borde - col * ae - (col - 1) * sep
            despl = (col - 1) * diff // 2
            y_raw = borde + despl
            h_raw = H - 2 * borde - (col - 1) * diff
            y     = y_raw  if h_raw > 160 else 170
            h     = h_raw  if h_raw > 160 else 160
            incl  = 15     if h_raw > 160 else 25

            fila_base = 3 * (nivel)    # índice en resTabla para este nivel
            # resTabla para nivel n (n>=3) ocupa posiciones 3*(n-1), 3*(n-1)+1, 3*(n-1)+2

            self._pen(p, COLOR_LINEA_MULTI, 2)
            p.setFont(QFont("Arial", 8, QFont.Bold))
            etiq = f"Est. Índice {nivel}"
            p.drawText(x + ae // 2 - 40, y - 8, etiq)
            p.setBrush(QColor(210, 228, 255))
            p.drawRect(x, y, ae, h)
            p.setBrush(Qt.NoBrush)

            p.drawLine(x, y + 10, x + ae, y + 10)
            p.drawText(x - 14, y + 7, "1")
            p.drawText(x + ae // 2 - 8, y + 33, "B1")

            es_ultimo = (nivel == self.cant_estructuras - 1)
            if not es_ultimo:
                i_cant = fila_base + 1     # "Cant. registros Índice" de este nivel
                i_ind  = fila_base + 2     # "Ind x Bloque"
                i_bloq = fila_base         # "Cant. Bloques Índice" del nivel anterior
                # Cálculo correcto desde resTabla:
                # fila_base-1 = Cant. Bloques Índice del nivel anterior
                # fila_base   = Cant. registros Índice de este nivel (= cant bloques anterior)
                # fila_base+1 = Ind x Bloque
                # fila_base+2 = Cant. Bloques Índice de este nivel
                idx_cant_reg  = fila_base       # cant_registros_indice de ESTE nivel
                idx_ind_bloq  = fila_base + 1   # ind_x_bloque
                idx_cant_bloq = fila_base + 2   # cant_bloques_indice de ESTE nivel

                self._pen(p, COLOR_NEGRITA, 4)
                p.drawLine(x, y + 58, x + ae, y + 58)
                txt = self.resTabla[idx_ind_bloq][2]
                p.drawText(x - len(txt) * 6 - 12, y + 58, txt)
                self._pen(p, COLOR_LINEA_MULTI, 2)
                p.drawLine(x, y + 48, x + ae, y + 48)

                self._pen(p, COLOR_NEGRITA, 4)
                p.drawLine(x, y + h - 58, x + ae, y + h - 58)
                cant_r = int(self.resTabla[idx_cant_reg][2])
                ind_b  = int(self.resTabla[idx_ind_bloq][2])
                diff_v = cant_r - ind_b
                diff_v = diff_v if diff_v >= ind_b else ind_b + 1
                p.drawText(x - len(str(diff_v)) * 6 - 12, y + h - 58, str(diff_v))
                self._pen(p, COLOR_LINEA_MULTI, 2)
                p.drawText(x + ae // 2 - 8, y + h - 28, "B" + self.resTabla[idx_cant_bloq][2])

            self._pen(p, COLOR_LINEA_MULTI, 2)
            p.drawLine(x, y + h - 10, x + ae, y + h - 10)

            # flechas hacia el nivel anterior (a la derecha)
            x_der    = x + ae + sep
            y_ant    = borde + (nivel - 1) * diff // 2
            h_ant    = H - 2 * borde - (nivel - 1) * diff
            y_ant    = y_ant  if h_ant > 160 else 170
            h_ant    = h_ant  if h_ant > 160 else 160
            incl_ant = 15     if (H - 2 * borde - (nivel - 1) * diff) > 160 else 25

            self._pen(p, COLOR_LINEA_PPAL, 2)
            p.drawLine(x + ae, y + 5,     x_der, y_ant + incl_ant)
            p.drawLine(x + ae, y + h - 5, x_der, y_ant + h_ant - incl_ant)

            # etiqueta cant_registros en borde inferior
            if fila_base - 1 >= 0 and fila_base - 1 < len(self.resTabla):
                txt_r = self.resTabla[fila_base - 1][2]
                p.drawText(x - len(txt_r) * 6 - 12, y + h - 3, txt_r)


# ─────────────────────────────────────────────────────────────────────────────
class IndicesExternosWindow(QMainWindow):
    """
    Ventana de Índices Externos.
    Patrón idéntico a HashExternoBase / EstructuraDinamicaBase.
    Recibe los mismos callbacks: volver_a_busquedas_externas, volver_a_principal.
    """

    TITULO      = "BÚSQUEDA EXTERNA - ÍNDICES"
    DESCRIPCION = (
        "Los índices externos permiten localizar registros en archivos de disco sin recorrer "
        "todos los bloques. El índice Primario crea una entrada por bloque de datos; el Secundario "
        "crea una entrada por registro. Con Multinivel se apilan índices hasta reducir la búsqueda "
        "a un único bloque raíz."
    )

    def __init__(self, volver_a_busquedas_externas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas_externas = volver_a_busquedas_externas
        self.volver_a_principal          = volver_a_principal
        self._ultimo_resultado           = []
        self.initUI()

    # ------------------------------------------------------------------ #
    def initUI(self):
        self.setWindowTitle(self.TITULO)
        self.setGeometry(100, 50, 1250, 740)
        self.setStyleSheet(ESTILO_GLOBAL)

        central = QWidget()
        self.setCentralWidget(central)
        lp = QVBoxLayout(central)
        lp.setSpacing(12)
        lp.setContentsMargins(20, 20, 20, 20)

        # ── Header ──────────────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(ESTILO_HEADER)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 5, 10, 5)

        btn_inicio = QPushButton("🏠  Inicio")
        btn_inicio.setCursor(Qt.PointingHandCursor)
        btn_inicio.clicked.connect(self._ir_a_principal)
        hl.addWidget(btn_inicio)

        btn_menu = QPushButton("🌐  Menú Búsquedas Externas")
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.clicked.connect(self._ir_a_busquedas)
        hl.addWidget(btn_menu)

        hl.addStretch()
        titulo_lbl = QLabel(self.TITULO)
        titulo_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        titulo_lbl.setStyleSheet("color: #003366;")
        hl.addWidget(titulo_lbl)
        hl.addStretch()
        lp.addWidget(header)

        # ── Descripción ─────────────────────────────────────────────────
        desc = QLabel(self.DESCRIPCION)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #336699; font-size: 12px;")
        lp.addWidget(desc)

        # ── Panel de parámetros ─────────────────────────────────────────
        param_frame = QFrame()
        param_frame.setStyleSheet(ESTILO_PANEL)
        param_layout = QVBoxLayout(param_frame)
        param_layout.setSpacing(10)

        # fila 1: tipo + niveles + tamaño bloque
        fila1 = QHBoxLayout()
        fila1.setSpacing(25)

        self.combo_tipo   = self._combo(["Primario", "Secundario"])
        self.combo_nivel  = self._combo(["Un Nivel", "Multinivel"])
        self.spin_tam_blq = self._spinbox(64, 65536, 1024, 100)

        fila1.addLayout(self._campo("Tipo de índice:",         self.combo_tipo))
        fila1.addLayout(self._campo("Niveles:",                self.combo_nivel))
        fila1.addLayout(self._campo("Tamaño bloque (B):",      self.spin_tam_blq))
        fila1.addStretch()
        param_layout.addLayout(fila1)

        # fila 2: cant registros + tam registro + tam reg índice
        fila2 = QHBoxLayout()
        fila2.setSpacing(25)

        self.spin_cant_reg    = self._spinbox(1, 10_000_000, 700_000, 100_000)
        self.spin_tam_reg     = self._spinbox(1, 4096, 20, 1)
        self.spin_tam_reg_idx = self._spinbox(1, 4096, 12, 1)

        fila2.addLayout(self._campo("Cant. registros:",          self.spin_cant_reg))
        fila2.addLayout(self._campo("Tamaño registro (B):",      self.spin_tam_reg))
        fila2.addLayout(self._campo("Tamaño reg. índice (B):",   self.spin_tam_reg_idx))
        fila2.addStretch()
        param_layout.addLayout(fila2)

        # botón calcular
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_calcular = QPushButton("▶  Calcular Índices")
        self.btn_calcular.setMinimumSize(170, 40)
        self.btn_calcular.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #4d94ff; color: white;
                border: 2px solid #1a66ff; border-radius: 6px; padding: 8px;
            }
            QPushButton:hover   { background-color: #3380ff; }
            QPushButton:pressed { background-color: #1a66ff; }
        """)
        self.btn_calcular.clicked.connect(self._calcular)
        btn_row.addWidget(self.btn_calcular)

        self.btn_limpiar = QPushButton("🗑  Limpiar")
        self.btn_limpiar.setMinimumSize(110, 40)
        self.btn_limpiar.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_limpiar.clicked.connect(self._limpiar)
        btn_row.addWidget(self.btn_limpiar)

        self.btn_guardar = QPushButton("💾  Guardar resultado")
        self.btn_guardar.setMinimumSize(160, 40)
        self.btn_guardar.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self._guardar)
        btn_row.addWidget(self.btn_guardar)

        btn_row.addStretch()
        param_layout.addLayout(btn_row)
        lp.addWidget(param_frame)

        # ── Área principal: canvas + tabla ──────────────────────────────
        area = QHBoxLayout()
        area.setSpacing(12)

        # canvas con scroll horizontal
        self.canvas = IndiceCanvas()
        self.scroll_canvas = QScrollArea()
        self.scroll_canvas.setWidget(self.canvas)
        self.scroll_canvas.setWidgetResizable(False)
        self.scroll_canvas.setMinimumSize(722, 400)
        self.scroll_canvas.setStyleSheet(
            "QScrollArea { border: 2px solid #99ccff; border-radius: 6px; "
            "background-color: #f0f8ff; }")
        area.addWidget(self.scroll_canvas, stretch=3)

        # tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setHorizontalHeaderLabels(["Nivel", "Variable", "Valor"])
        self.tabla.setMinimumWidth(300)
        self.tabla.setMaximumWidth(320)
        self.tabla.setFont(QFont("Arial", 9))
        self.tabla.horizontalScrollBar().setVisible(False)
        self.tabla.setColumnWidth(0, 40)
        self.tabla.setColumnWidth(1, 160)
        self.tabla.setColumnWidth(2, 90)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 2px solid #99ccff;
                background-color: #f8fbff;
                color: #003366;
                gridline-color: #b3d4ff;
            }
            QHeaderView::section {
                background-color: #cce6ff;
                color: #003366;
                font-weight: bold;
                border: 1px solid #99ccff;
                padding: 4px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #ddeeff;
                padding: 3px;
            }
            QTableWidget::item:selected {
                background-color: #b3d4ff;
                color: #003366;
            }
        """)
        area.addWidget(self.tabla, stretch=1)
        lp.addLayout(area)

        # ── Barra de info ───────────────────────────────────────────────
        self.lbl_info = QLabel("Configure los parámetros y pulse «Calcular Índices».")
        self.lbl_info.setStyleSheet("color: #003366; font-size: 12px; font-style: italic;")
        lp.addWidget(self.lbl_info)

    # ── Helpers de construcción de UI ───────────────────────────────── #
    def _combo(self, items):
        cb = QComboBox()
        cb.addItems(items)
        return cb

    def _spinbox(self, minv, maxv, val, step):
        sb = QSpinBox()
        sb.setRange(minv, maxv)
        sb.setValue(val)
        sb.setSingleStep(step)
        sb.setFixedWidth(110)
        return sb

    def _campo(self, etiqueta, widget):
        lay = QHBoxLayout()
        lbl = QLabel(etiqueta)
        lbl.setFont(QFont("Arial", 10, QFont.Bold))
        lbl.setStyleSheet("color: #003366;")
        lay.addWidget(lbl)
        lay.addWidget(widget)
        return lay

    # ── Lógica principal ─────────────────────────────────────────────── #
    def _calcular(self):
        try:
            tipo      = self.combo_tipo.currentText()
            nivel     = self.combo_nivel.currentText()
            tam_blq   = self.spin_tam_blq.value()
            cant_reg  = self.spin_cant_reg.value()
            tam_reg   = self.spin_tam_reg.value()
            tam_ridx  = self.spin_tam_reg_idx.value()

            if tam_reg <= 0 or tam_ridx <= 0 or tam_blq <= 0:
                raise ValueError("Los tamaños deben ser mayores a cero.")
            if tam_reg > tam_blq:
                raise ValueError("El tamaño de registro no puede ser mayor al tamaño de bloque.")
            if tam_ridx > tam_blq:
                raise ValueError("El tamaño del registro índice no puede ser mayor al tamaño de bloque.")

            tabla = self.canvas.calcular(tipo, nivel, tam_blq, cant_reg, tam_reg, tam_ridx)

            # Poblar tabla de resultados
            self.tabla.setRowCount(0)
            for fila in tabla:
                r = self.tabla.rowCount()
                self.tabla.insertRow(r)
                for col, val in enumerate(fila):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla.setItem(r, col, item)

            self._ultimo_resultado = tabla
            self.btn_guardar.setEnabled(True)

            # Resumen en barra de info
            reg_x_b = tam_blq // tam_reg
            bloques = math.ceil(cant_reg / reg_x_b)
            ind_x_b = tam_blq // tam_ridx
            if tipo == "Primario":
                cant_idx = bloques
            else:
                cant_idx = cant_reg
            bloq_idx = math.ceil(cant_idx / ind_x_b)
            self.lbl_info.setText(
                f"✔  {tipo} · {nivel}  |  "
                f"Archivo principal: {bloques} bloques  |  "
                f"Índice nivel 1: {bloq_idx} bloque(s)"
            )

        except Exception as e:
            QMessageBox.warning(self, "Error en los parámetros", str(e))

    def _limpiar(self):
        self.canvas.activo = False
        self.canvas.update()
        self.tabla.setRowCount(0)
        self._ultimo_resultado = []
        self.btn_guardar.setEnabled(False)
        self.lbl_info.setText("Configure los parámetros y pulse «Calcular Índices».")

    def _guardar(self):
        if not self._ultimo_resultado:
            QMessageBox.information(self, "Sin datos", "Primero calcule una estructura.")
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar resultado", "", "JSON (*.json)")
        if not ruta:
            return
        datos = {
            "algoritmo":           self.TITULO,
            "fecha":               datetime.now().isoformat(),
            "tipo":                self.combo_tipo.currentText(),
            "niveles":             self.combo_nivel.currentText(),
            "tama_bloque":         self.spin_tam_blq.value(),
            "cant_registros":      self.spin_cant_reg.value(),
            "tama_registro":       self.spin_tam_reg.value(),
            "tama_registro_indice":self.spin_tam_reg_idx.value(),
            "tabla_resultados":    self._ultimo_resultado,
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        QMessageBox.information(self, "Guardado", f"Resultado guardado en:\n{ruta}")

    # ── Navegación ───────────────────────────────────────────────────── #
    def _ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas_externas()

    def _ir_a_principal(self):
        self.close()
        self.volver_a_principal()
