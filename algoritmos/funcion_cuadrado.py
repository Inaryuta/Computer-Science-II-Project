import json
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QScrollArea,
    QMessageBox, QFileDialog, QDialog, QLineEdit, QDialogButtonBox,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator


# ---------- Diálogo para ingresar una clave ----------
class DialogoClave(QDialog):
    def __init__(self, longitud, titulo="Ingresar clave", modo="insertar", parent=None, mensaje=None):
        super().__init__(parent)
        self.longitud = longitud
        self.modo = modo
        self.clave_ingresada = ""

        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #003366;
                font-size: 14px;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #99ccff;
                border-radius: 4px;
                padding: 5px;
                color: #003366;
                font-size: 14px;
            }
            QPushButton {
                background-color: #e6f2ff;
                color: #003366;
                border: 2px solid #99ccff;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cce6ff;
            }
        """)

        layout = QVBoxLayout(self)

        if modo in ("mensaje", "confirmar"):
            lbl_mensaje = QLabel(mensaje if mensaje else "")
            lbl_mensaje.setWordWrap(True)
            layout.addWidget(lbl_mensaje)

            if modo == "confirmar":
                button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
                button_box.accepted.connect(self.accept)
                button_box.rejected.connect(self.reject)
                layout.addWidget(button_box)
            else:
                btn_ok = QPushButton("Aceptar")
                btn_ok.clicked.connect(self.accept)
                layout.addWidget(btn_ok)
        else:
            lbl_info = QLabel(f"Ingrese una clave de {longitud} dígitos:")
            layout.addWidget(lbl_info)

            self.edit_clave = QLineEdit()
            self.edit_clave.setMaxLength(longitud)
            self.edit_clave.setValidator(QIntValidator(0, 10**longitud - 1))
            self.edit_clave.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.edit_clave)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(self.validar_y_aceptar)
            button_box.rejected.connect(self.reject)
            layout.addWidget(button_box)

    def validar_y_aceptar(self):
        clave = self.edit_clave.text()
        if len(clave) != self.longitud:
            QMessageBox.warning(self, "Error", f"La clave debe tener exactamente {self.longitud} dígitos.")
            return
        self.clave_ingresada = clave
        self.accept()

    def get_clave(self):
        return self.clave_ingresada


# ---------- Diálogo para elegir estrategia de colisión ----------
class DialogoEstrategia(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar estrategia de colisión")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #003366;
                font-size: 14px;
            }
            QPushButton {
                background-color: #e6f2ff;
                color: #003366;
                border: 2px solid #99ccff;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #cce6ff;
            }
        """)
        self.estrategia = None

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        lbl = QLabel("Se ha producido una colisión.\nElija una estrategia de manejo:")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        btn_lineal = QPushButton("Lineal")
        btn_lineal.clicked.connect(lambda: self.seleccionar("Lineal"))
        layout.addWidget(btn_lineal)

        btn_cuadratica = QPushButton("Cuadrática")
        btn_cuadratica.clicked.connect(lambda: self.seleccionar("Cuadrática"))
        layout.addWidget(btn_cuadratica)

        btn_doble_hash = QPushButton("Doble función hash")
        btn_doble_hash.clicked.connect(lambda: self.seleccionar("Doble Hash"))
        layout.addWidget(btn_doble_hash)

        btn_anidado = QPushButton("Arreglo anidado")
        btn_anidado.clicked.connect(lambda: self.seleccionar("Arreglo anidado"))
        layout.addWidget(btn_anidado)

        btn_encadenada = QPushButton("Lista encadenada")
        btn_encadenada.clicked.connect(lambda: self.seleccionar("Lista encadenada"))
        layout.addWidget(btn_encadenada)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar)

    def seleccionar(self, estrategia):
        self.estrategia = estrategia
        self.accept()

    def get_estrategia(self):
        return self.estrategia


# ---------- Manejador de archivos JSON ----------
class ManejadorArchivos:
    @staticmethod
    def guardar_json(ruta, datos):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    @staticmethod
    def leer_json(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)


# ---------- Ventana principal de Función Cuadrado ----------
class FuncionCuadradoWindow(QMainWindow):
    # Objeto especial para marcar posiciones borradas en direccionamiento abierto
    class DELETED:
        pass

    def __init__(self, volver_a_busquedas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.volver_a_principal = volver_a_principal

        # Atributos de la estructura
        self.capacidad = 0
        self.digitos = 4
        self.estructura = []          # Lista de tamaño capacidad, con valores, None o DELETED
        self.estructura_anidada = []   # Solo para estrategias cerradas
        self.historial = []            # Lista de acciones para deshacer
        self.estrategia_actual = None  # "Lineal", "Cuadrática", "Doble Hash", "Arreglo anidado", "Lista encadenada"

        # Referencias a widgets de visualización
        self.labels = []                # QLabel para valores
        self.indices_labels = []        # QLabel para índices
        self.indices_reales = []        # índices reales

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Función Hash - Cuadrado")
        self.setGeometry(100, 50, 1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #003366;
            }
            QPushButton {
                background-color: #e6f2ff;
                color: #003366;
                font-weight: bold;
                border: 2px solid #99ccff;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #cce6ff;
            }
            QPushButton:pressed {
                background-color: #b3d9ff;
            }
            QComboBox, QSpinBox {
                background-color: white;
                border: 2px solid #99ccff;
                border-radius: 4px;
                padding: 5px;
                color: #003366;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # ----- HEADER con botones Inicio y Menú Búsqueda -----
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #cce6ff;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        btn_inicio = QPushButton("🏠 Inicio")
        btn_inicio.setCursor(Qt.PointingHandCursor)
        btn_inicio.clicked.connect(self.ir_a_principal)
        header_layout.addWidget(btn_inicio)

        btn_menu_busqueda = QPushButton("🔍 Menú Búsqueda")
        btn_menu_busqueda.setCursor(Qt.PointingHandCursor)
        btn_menu_busqueda.clicked.connect(self.ir_a_busquedas)
        header_layout.addWidget(btn_menu_busqueda)

        header_layout.addStretch()

        titulo = QLabel("FUNCIÓN HASH - CUADRADO")
        titulo.setFont(QFont("Arial", 20, QFont.Bold))
        titulo.setStyleSheet("color: #003366;")
        header_layout.addWidget(titulo)

        header_layout.addStretch()
        layout_principal.addWidget(header)

        # ----- Panel de configuración (rango y dígitos) -----
        config_frame = QFrame()
        config_frame.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        config_layout = QHBoxLayout(config_frame)

        lbl_rango = QLabel("Rango (10^n):")
        self.rango_combo = QComboBox()
        self.rango_combo.addItems([str(i) for i in range(1, 7)])
        self.rango_combo.setFixedWidth(80)

        lbl_digitos = QLabel("Dígitos de clave:")
        self.digitos_spin = QSpinBox()
        self.digitos_spin.setRange(1, 10)
        self.digitos_spin.setValue(self.digitos)
        self.digitos_spin.setFixedWidth(80)

        config_layout.addWidget(lbl_rango)
        config_layout.addWidget(self.rango_combo)
        config_layout.addSpacing(20)
        config_layout.addWidget(lbl_digitos)
        config_layout.addWidget(self.digitos_spin)
        config_layout.addStretch()

        layout_principal.addWidget(config_frame)

        # ----- Botones de acciones principales (grid) -----
        acciones_frame = QFrame()
        acciones_frame.setStyleSheet("QFrame { background-color: #e6f2ff; border-radius: 8px; padding: 10px; }")
        acciones_layout = QGridLayout(acciones_frame)

        self.btn_crear = QPushButton("Crear estructura")
        self.btn_insertar = QPushButton("Insertar claves")
        self.btn_buscar = QPushButton("Buscar clave")
        self.btn_eliminar_clave = QPushButton("Eliminar clave")
        self.btn_guardar = QPushButton("Guardar estructura")
        self.btn_cargar = QPushButton("Cargar estructura")
        self.btn_eliminar_estructura = QPushButton("Eliminar estructura")
        self.btn_deshacer = QPushButton("Deshacer")

        for btn in [self.btn_crear, self.btn_insertar, self.btn_buscar,
                    self.btn_eliminar_clave, self.btn_guardar, self.btn_cargar,
                    self.btn_eliminar_estructura, self.btn_deshacer]:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)

        acciones_layout.addWidget(self.btn_crear, 0, 0)
        acciones_layout.addWidget(self.btn_insertar, 0, 1)
        acciones_layout.addWidget(self.btn_buscar, 0, 2)
        acciones_layout.addWidget(self.btn_eliminar_clave, 0, 3)
        acciones_layout.addWidget(self.btn_guardar, 1, 0)
        acciones_layout.addWidget(self.btn_cargar, 1, 1)
        acciones_layout.addWidget(self.btn_eliminar_estructura, 1, 2)
        acciones_layout.addWidget(self.btn_deshacer, 1, 3)

        layout_principal.addWidget(acciones_frame)

        # ----- Área de visualización con scroll -----
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self.contenedor = QWidget()
        self.contenedor_layout = QVBoxLayout(self.contenedor)
        self.contenedor_layout.setSpacing(10)
        self.contenedor_layout.setContentsMargins(20, 20, 20, 20)
        self.contenedor_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.scroll.setWidget(self.contenedor)
        layout_principal.addWidget(self.scroll)

        # ----- Conexiones -----
        self.btn_crear.clicked.connect(self.crear_estructura)
        self.btn_insertar.clicked.connect(self.insertar_clave)
        self.btn_buscar.clicked.connect(self.buscar_clave)
        self.btn_eliminar_clave.clicked.connect(self.eliminar_clave)
        self.btn_guardar.clicked.connect(self.guardar_estructura)
        self.btn_cargar.clicked.connect(self.cargar_estructura)
        self.btn_eliminar_estructura.clicked.connect(self.eliminar_estructura)
        self.btn_deshacer.clicked.connect(self.deshacer)

        self.habilitar_botones_estructura(False)

    # ---------- Métodos auxiliares ----------
    def habilitar_botones_estructura(self, habilitar):
        self.btn_insertar.setEnabled(habilitar)
        self.btn_buscar.setEnabled(habilitar)
        self.btn_eliminar_clave.setEnabled(habilitar)
        self.btn_guardar.setEnabled(habilitar)
        self.btn_eliminar_estructura.setEnabled(habilitar)
        self.btn_deshacer.setEnabled(habilitar)
        self.btn_cargar.setEnabled(True)

    def limpiar_vista(self):
        while self.contenedor_layout.count():
            item = self.contenedor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._eliminar_layout(item.layout())
        self.labels.clear()
        self.indices_labels.clear()
        self.indices_reales.clear()
        if hasattr(self, 'grid_layout'):
            del self.grid_layout

    def _eliminar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._eliminar_layout(item.layout())

    # Constantes para vista normal (grid)
    COLUMNAS = 10
    MAX_CELDAS_VISIBLES = 200

    def reconstruir_vista_normal(self):
        """Vista en grid sin colisiones (solo estructura principal)."""
        self.limpiar_vista()
        if self.capacidad <= 0:
            return

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.contenedor_layout.addLayout(self.grid_layout)

        mostrar = min(self.capacidad, self.MAX_CELDAS_VISIBLES)
        for idx in range(mostrar):
            fila = idx // self.COLUMNAS
            col = idx % self.COLUMNAS
            celda = self._crear_celda(idx)
            self.grid_layout.addWidget(celda, fila, col)

        if self.capacidad > self.MAX_CELDAS_VISIBLES:
            lbl_aviso = QLabel(f"(Mostrando primeras {self.MAX_CELDAS_VISIBLES} de {self.capacidad} celdas)")
            lbl_aviso.setAlignment(Qt.AlignCenter)
            lbl_aviso.setStyleSheet("color: #336699; font-style: italic; margin-top: 10px;")
            self.contenedor_layout.addWidget(lbl_aviso)

    def _crear_celda(self, idx_real):
        contenedor = QWidget()
        contenedor.setFixedSize(80, 100)
        vbox = QVBoxLayout(contenedor)
        vbox.setSpacing(2)
        vbox.setContentsMargins(0, 0, 0, 0)

        cuadro = QLabel("")
        cuadro.setAlignment(Qt.AlignCenter)
        cuadro.setFixedSize(80, 80)
        cuadro.setStyleSheet("""
            QLabel {
                background-color: #99ccff;
                border: 1px solid #4d9de0;
                font-size: 16px;
                font-weight: bold;
                color: #003366;
            }
        """)

        numero = QLabel(str(idx_real + 1))
        numero.setAlignment(Qt.AlignCenter)
        numero.setFixedHeight(20)
        numero.setStyleSheet("font-size: 12px; color: #336699; background: transparent;")

        vbox.addWidget(cuadro)
        vbox.addWidget(numero)

        self.labels.append(cuadro)
        self.indices_labels.append(numero)
        self.indices_reales.append(idx_real)

        return contenedor

    def actualizar_vista_normal(self):
        """Actualiza los valores de la vista normal (estructura principal)."""
        for i, idx in enumerate(self.indices_reales):
            lbl = self.labels[i]
            valor = self.estructura[idx] if idx < len(self.estructura) else None
            if valor is not None and valor is not self.DELETED:
                lbl.setText(str(valor))
                lbl.setStyleSheet("""
                    QLabel {
                        background-color: #4d9de0;
                        border: 2px solid #1e6bb8;
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                    }
                """)
            else:
                lbl.setText("")
                lbl.setStyleSheet("""
                    QLabel {
                        background-color: #99ccff;
                        border: 2px solid #4d9de0;
                        font-size: 16px;
                        color: #003366;
                    }
                """)

    # ---------- Función hash de cuadrado (dígitos centrales) ----------
    def hash_cuadrado(self, clave):
        """
        Calcula la posición usando el método de los dígitos centrales del cuadrado.
        clave: string de dígitos.
        Retorna: índice entre 0 y capacidad-1.
        """
        clave_int = int(clave)
        cuadrado = clave_int * clave_int
        # Convertir a string y rellenar con ceros a la izquierda para tener al menos 2*digitos caracteres
        cuadrado_str = str(cuadrado).zfill(2 * self.digitos)
        # Tomar los dígitos centrales (la misma cantidad que self.digitos)
        inicio = (len(cuadrado_str) - self.digitos) // 2
        digitos_centrales = cuadrado_str[inicio:inicio + self.digitos]
        hash_int = int(digitos_centrales)
        return hash_int % self.capacidad

    # ---------- Métodos de probing para estrategias abiertas ----------
    def probar_lineal(self, clave, intento):
        """Probing lineal: pos = (h(clave) + intento) % capacidad"""
        h = self.hash_cuadrado(clave)
        return (h + intento) % self.capacidad

    def probar_cuadratica(self, clave, intento):
        """Probing cuadrática: pos = (h(clave) + c1*intento + c2*intento^2) % capacidad
        Usamos c1=1, c2=1 para simplificar."""
        h = self.hash_cuadrado(clave)
        return (h + intento + intento * intento) % self.capacidad

    def probar_doble_hash(self, clave, intento):
        """Doble hash: pos = (h1(clave) + intento * h2(clave)) % capacidad
        h1 = hash_cuadrado, h2 = 1 + (clave % (capacidad-2)) para asegurar que sea coprimo con capacidad."""
        h1 = self.hash_cuadrado(clave)
        # Segunda función hash: un número primo menor que capacidad
        h2 = 1 + (int(clave) % (self.capacidad - 1)) if self.capacidad > 1 else 1
        return (h1 + intento * h2) % self.capacidad

    # ---------- Funcionalidades ----------
    def crear_estructura(self):
        n = int(self.rango_combo.currentText())
        capacidad = 10 ** n
        digitos = self.digitos_spin.value()

        self.capacidad = capacidad
        self.digitos = digitos
        self.estructura = [None] * capacidad
        self.estructura_anidada = [[] for _ in range(capacidad)]
        self.historial = []
        self.estrategia_actual = None

        self.reconstruir_vista_normal()
        self.actualizar_vista_normal()

        self.rango_combo.setEnabled(False)
        self.digitos_spin.setEnabled(False)
        self.btn_crear.setEnabled(False)

        self.habilitar_botones_estructura(True)

        QMessageBox.information(self, "Éxito", f"Estructura creada con capacidad {capacidad}.")

    def insertar_clave(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        # Verificar si hay espacio (considerando que en abierto puede haber borrados)
        ocupadas = sum(1 for x in self.estructura if x is not None and x is not self.DELETED)
        if self.estrategia_actual in ("Arreglo anidado", "Lista encadenada"):
            ocupadas += sum(len(lst) for lst in self.estructura_anidada)

        if ocupadas >= self.capacidad:
            QMessageBox.warning(self, "Error", "La estructura está llena.")
            return

        dlg = DialogoClave(self.digitos, titulo="Insertar clave", modo="insertar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()
        clave_int = int(clave)

        # Verificar duplicado (depende de la estrategia)
        if self.estrategia_actual in ("Arreglo anidado", "Lista encadenada"):
            if clave_int in [x for x in self.estructura if x is not None and x is not self.DELETED]:
                QMessageBox.warning(self, "Clave duplicada", "Esa clave ya existe en la estructura principal.")
                return
            for lista in self.estructura_anidada:
                if clave_int in lista:
                    QMessageBox.warning(self, "Clave duplicada", "Esa clave ya existe en una colisión.")
                    return
        else:
            # En abierto, buscar en toda la tabla
            if self.buscar_posicion_por_clave(clave_int) is not None:
                QMessageBox.warning(self, "Clave duplicada", "Esa clave ya existe en la estructura.")
                return

        pos = self.hash_cuadrado(clave)

        # Si la posición está libre (None o DELETED) y es estrategia cerrada, insertar sin colisión
        if self.estructura[pos] is None or self.estructura[pos] is self.DELETED:
            # Sin colisión
            self.estructura[pos] = clave_int
            self.historial.append(("insertar", pos, clave_int, self.estrategia_actual))
            self._actualizar_segun_estrategia()
            QMessageBox.information(self, "Éxito", f"Clave {clave} insertada en posición {pos+1}.")
            return

        # Hay colisión
        if self.estrategia_actual is None:
            # Primera colisión, preguntar estrategia
            dlg_est = DialogoEstrategia(self)
            if dlg_est.exec() != QDialog.Accepted:
                return
            self.estrategia_actual = dlg_est.get_estrategia()

        # Ahora manejamos según la estrategia
        if self.estrategia_actual in ("Arreglo anidado", "Lista encadenada"):
            # Estrategias cerradas: usar estructura_anidada
            self.estructura_anidada[pos].append(clave_int)
            self.historial.append(("insertar", pos, clave_int, self.estrategia_actual))
            self._actualizar_segun_estrategia()
            QMessageBox.information(self, "Éxito", f"Clave {clave} insertada con estrategia {self.estrategia_actual}.")

        else:
            # Estrategias abiertas: buscar la siguiente posición libre mediante probing
            intento = 1
            max_intentos = self.capacidad
            while intento <= max_intentos:
                if self.estrategia_actual == "Lineal":
                    nueva_pos = self.probar_lineal(clave, intento)
                elif self.estrategia_actual == "Cuadrática":
                    nueva_pos = self.probar_cuadratica(clave, intento)
                elif self.estrategia_actual == "Doble Hash":
                    nueva_pos = self.probar_doble_hash(clave, intento)
                else:
                    break

                if self.estructura[nueva_pos] is None or self.estructura[nueva_pos] is self.DELETED:
                    self.estructura[nueva_pos] = clave_int
                    self.historial.append(("insertar", nueva_pos, clave_int, self.estrategia_actual))
                    self._actualizar_segun_estrategia()
                    QMessageBox.information(self, "Éxito", f"Clave {clave} insertada en posición {nueva_pos+1} (probing).")
                    return
                intento += 1

            QMessageBox.critical(self, "Error", "No se pudo insertar la clave (tabla llena o sin espacio libre).")

    def buscar_posicion_por_clave(self, clave_int):
        """Devuelve la posición donde se encuentra la clave, o None si no existe."""
        if self.estrategia_actual in ("Lineal", "Cuadrática", "Doble Hash"):
            h = self.hash_cuadrado(str(clave_int))
            intento = 0
            max_intentos = self.capacidad
            while intento <= max_intentos:
                if self.estrategia_actual == "Lineal":
                    pos = self.probar_lineal(str(clave_int), intento)
                elif self.estrategia_actual == "Cuadrática":
                    pos = self.probar_cuadratica(str(clave_int), intento)
                else:
                    pos = self.probar_doble_hash(str(clave_int), intento)

                if self.estructura[pos] == clave_int:
                    return pos
                if self.estructura[pos] is None:
                    return None
                intento += 1
            return None
        else:
            for i, val in enumerate(self.estructura):
                if val == clave_int:
                    return i
            for i, lista in enumerate(self.estructura_anidada):
                if clave_int in lista:
                    return i
            return None

    def buscar_clave(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        dlg = DialogoClave(self.digitos, titulo="Buscar clave", modo="buscar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()
        clave_int = int(clave)

        if self.estrategia_actual in ("Lineal", "Cuadrática", "Doble Hash"):
            h = self.hash_cuadrado(clave)
            intento = 0
            max_intentos = self.capacidad
            while intento <= max_intentos:
                if self.estrategia_actual == "Lineal":
                    pos = self.probar_lineal(clave, intento)
                elif self.estrategia_actual == "Cuadrática":
                    pos = self.probar_cuadratica(clave, intento)
                else:
                    pos = self.probar_doble_hash(clave, intento)

                if self.estructura[pos] == clave_int:
                    self._resaltar_posicion(pos)
                    QMessageBox.information(
                        self,
                        "Resultado",
                        f"✅ Clave {clave} encontrada en posición {pos+1} (probing)."
                    )
                    return
                if self.estructura[pos] is None:
                    break
                intento += 1
            QMessageBox.information(self, "Resultado", f"❌ Clave {clave} no encontrada.")

        elif self.estrategia_actual in ("Arreglo anidado", "Lista encadenada"):
            for i, val in enumerate(self.estructura):
                if val == clave_int:
                    self._resaltar_posicion(i)
                    QMessageBox.information(
                        self,
                        "Resultado",
                        f"✅ Clave {clave} encontrada en posición {i+1} (principal)."
                    )
                    return
            for i, lista in enumerate(self.estructura_anidada):
                if clave_int in lista:
                    idx_col = lista.index(clave_int) + 1
                    tipo = "arreglo anidado" if self.estrategia_actual == "Arreglo anidado" else "lista encadenada"
                    self._resaltar_posicion(i)
                    QMessageBox.information(
                        self,
                        "Resultado",
                        f"✅ Clave {clave} encontrada en posición {i+1}, {tipo} #{idx_col}."
                    )
                    return
            QMessageBox.information(self, "Resultado", f"❌ Clave {clave} no encontrada.")
        else:
            for i, val in enumerate(self.estructura):
                if val == clave_int:
                    self._resaltar_posicion(i)
                    QMessageBox.information(
                        self,
                        "Resultado",
                        f"✅ Clave {clave} encontrada en posición {i+1}."
                    )
                    return
            QMessageBox.information(self, "Resultado", f"❌ Clave {clave} no encontrada.")

    def _resaltar_posicion(self, idx):
        try:
            pos_label = self.indices_reales.index(idx)
            self._reset_label_styles()
            self.labels[pos_label].setStyleSheet("""
                QLabel {
                    background-color: #2ecc71;
                    border: 3px solid #27ae60;
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                }
            """)
        except ValueError:
            pass

    def _reset_label_styles(self):
        for i, idx in enumerate(self.indices_reales):
            lbl = self.labels[i]
            valor = self.estructura[idx] if idx < len(self.estructura) else None
            if valor is not None and valor is not self.DELETED:
                lbl.setStyleSheet("""
                    QLabel {
                        background-color: #4d9de0;
                        border: 2px solid #1e6bb8;
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                    }
                """)
            else:
                lbl.setStyleSheet("""
                    QLabel {
                        background-color: #99ccff;
                        border: 2px solid #4d9de0;
                        font-size: 16px;
                        color: #003366;
                    }
                """)

    def eliminar_clave(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        dlg = DialogoClave(self.digitos, titulo="Eliminar clave", modo="eliminar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()
        clave_int = int(clave)

        if self.estrategia_actual in ("Lineal", "Cuadrática", "Doble Hash"):
            h = self.hash_cuadrado(clave)
            intento = 0
            max_intentos = self.capacidad
            while intento <= max_intentos:
                if self.estrategia_actual == "Lineal":
                    pos = self.probar_lineal(clave, intento)
                elif self.estrategia_actual == "Cuadrática":
                    pos = self.probar_cuadratica(clave, intento)
                else:
                    pos = self.probar_doble_hash(clave, intento)

                if self.estructura[pos] == clave_int:
                    self.estructura[pos] = self.DELETED
                    self.historial.append(("eliminar", pos, clave_int, self.estrategia_actual))
                    self._actualizar_segun_estrategia()
                    QMessageBox.information(self, "Éxito", f"Clave {clave} eliminada de la posición {pos+1}.")
                    return
                if self.estructura[pos] is None:
                    break
                intento += 1
            QMessageBox.information(self, "Resultado", f"Clave {clave} no encontrada.")

        elif self.estrategia_actual in ("Arreglo anidado", "Lista encadenada"):
            for i, val in enumerate(self.estructura):
                if val == clave_int:
                    self.estructura[i] = None
                    self.historial.append(("eliminar", i, clave_int, self.estrategia_actual))
                    self._actualizar_segun_estrategia()
                    QMessageBox.information(self, "Éxito", f"Clave {clave} eliminada de la posición {i+1}.")
                    return
            for i, lista in enumerate(self.estructura_anidada):
                if clave_int in lista:
                    lista.remove(clave_int)
                    self.historial.append(("eliminar", i, clave_int, self.estrategia_actual))
                    self._actualizar_segun_estrategia()
                    QMessageBox.information(self, "Éxito", f"Clave {clave} eliminada de colisión en posición {i+1}.")
                    return
            QMessageBox.information(self, "Resultado", f"Clave {clave} no encontrada.")
        else:
            for i, val in enumerate(self.estructura):
                if val == clave_int:
                    self.estructura[i] = None
                    self.historial.append(("eliminar", i, clave_int, None))
                    self._actualizar_segun_estrategia()
                    QMessageBox.information(self, "Éxito", f"Clave {clave} eliminada de la posición {i+1}.")
                    return
            QMessageBox.information(self, "Resultado", f"Clave {clave} no encontrada.")

    def _actualizar_segun_estrategia(self):
        if self.estrategia_actual == "Arreglo anidado":
            self.actualizar_vista_anidada()
        elif self.estrategia_actual == "Lista encadenada":
            self.actualizar_vista_encadenada()
        else:
            self.reconstruir_vista_normal()
            self.actualizar_vista_normal()

    def actualizar_vista_anidada(self):
        self.limpiar_vista()
        max_colisiones = max((len(lst) for lst in self.estructura_anidada), default=0)
        layout_vertical = QVBoxLayout()
        layout_vertical.setSpacing(5)
        titulo = QLabel("Arreglo principal con arreglos anidados (colisiones)")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #003366; margin-bottom: 10px;")
        layout_vertical.addWidget(titulo)

        for i in range(self.capacidad):
            fila_layout = QHBoxLayout()
            fila_layout.setSpacing(0)

            val = self.estructura[i]
            lbl_principal = QLabel(str(val) if val is not None and val is not self.DELETED else "")
            lbl_principal.setFixedSize(80, 80)
            lbl_principal.setAlignment(Qt.AlignCenter)
            if val is not None and val is not self.DELETED:
                lbl_principal.setStyleSheet("""
                    QLabel {
                        background-color: #4d9de0;
                        border: 2px solid #1e6bb8;
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                    }
                """)
            else:
                lbl_principal.setStyleSheet("""
                    QLabel {
                        background-color: #99ccff;
                        border: 2px solid #4d9de0;
                        font-size: 16px;
                        color: #003366;
                    }
                """)
            fila_layout.addWidget(lbl_principal)

            for j, clave in enumerate(self.estructura_anidada[i]):
                lbl_anidado = QLabel(str(clave))
                lbl_anidado.setFixedSize(80, 80)
                lbl_anidado.setAlignment(Qt.AlignCenter)
                lbl_anidado.setStyleSheet("""
                    QLabel {
                        background-color: #b3d9ff;
                        border: 2px solid #4d9de0;
                        border-left: none;
                        font-size: 16px;
                        color: #003366;
                    }
                """)
                fila_layout.addWidget(lbl_anidado)

            for _ in range(len(self.estructura_anidada[i]), max_colisiones):
                vacio = QLabel("")
                vacio.setFixedSize(80, 80)
                vacio.setStyleSheet("border: 1px dashed #99ccff; background-color: #f0f8ff;")
                fila_layout.addWidget(vacio)

            idx_label = QLabel(str(i+1))
            idx_label.setFixedWidth(30)
            idx_label.setAlignment(Qt.AlignCenter)
            idx_label.setStyleSheet("color: #336699; font-weight: bold;")

            fila_contenedor = QWidget()
            fila_contenedor_layout = QHBoxLayout(fila_contenedor)
            fila_contenedor_layout.setContentsMargins(0, 0, 0, 0)
            fila_contenedor_layout.addWidget(idx_label)
            fila_contenedor_layout.addLayout(fila_layout)
            fila_contenedor_layout.addStretch()

            layout_vertical.addWidget(fila_contenedor)

        contenedor_final = QWidget()
        contenedor_final.setLayout(layout_vertical)
        self.contenedor_layout.addWidget(contenedor_final)

    def actualizar_vista_encadenada(self):
        self.limpiar_vista()
        layout_vertical = QVBoxLayout()
        layout_vertical.setSpacing(5)
        titulo = QLabel("Lista encadenada (colisiones con punteros)")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #003366; margin-bottom: 10px;")
        layout_vertical.addWidget(titulo)

        for i in range(self.capacidad):
            fila_layout = QHBoxLayout()
            fila_layout.setSpacing(5)

            val = self.estructura[i]
            lbl_principal = QLabel(str(val) if val is not None and val is not self.DELETED else "")
            lbl_principal.setFixedSize(80, 80)
            lbl_principal.setAlignment(Qt.AlignCenter)
            if val is not None and val is not self.DELETED:
                lbl_principal.setStyleSheet("""
                    QLabel {
                        background-color: #4d9de0;
                        border: 2px solid #1e6bb8;
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                    }
                """)
            else:
                lbl_principal.setStyleSheet("""
                    QLabel {
                        background-color: #99ccff;
                        border: 2px solid #4d9de0;
                        font-size: 16px;
                        color: #003366;
                    }
                """)
            fila_layout.addWidget(lbl_principal)

            for j, clave in enumerate(self.estructura_anidada[i]):
                flecha = QLabel("→")
                flecha.setAlignment(Qt.AlignCenter)
                flecha.setStyleSheet("font-size: 20px; color: #336699;")
                fila_layout.addWidget(flecha)

                lbl_nodo = QLabel(str(clave))
                lbl_nodo.setFixedSize(80, 80)
                lbl_nodo.setAlignment(Qt.AlignCenter)
                lbl_nodo.setStyleSheet("""
                    QLabel {
                        background-color: #b3d9ff;
                        border: 2px solid #4d9de0;
                        font-size: 16px;
                        color: #003366;
                    }
                """)
                fila_layout.addWidget(lbl_nodo)

            idx_label = QLabel(str(i+1))
            idx_label.setFixedWidth(30)
            idx_label.setAlignment(Qt.AlignCenter)
            idx_label.setStyleSheet("color: #336699; font-weight: bold;")

            fila_contenedor = QWidget()
            fila_contenedor_layout = QHBoxLayout(fila_contenedor)
            fila_contenedor_layout.setContentsMargins(0, 0, 0, 0)
            fila_contenedor_layout.addWidget(idx_label)
            fila_contenedor_layout.addLayout(fila_layout)
            fila_contenedor_layout.addStretch()

            layout_vertical.addWidget(fila_contenedor)

        contenedor_final = QWidget()
        contenedor_final.setLayout(layout_vertical)
        self.contenedor_layout.addWidget(contenedor_final)

    def guardar_estructura(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "No hay estructura para guardar.")
            return

        estructura_serializable = []
        for val in self.estructura:
            if val is self.DELETED:
                estructura_serializable.append("__DELETED__")
            else:
                estructura_serializable.append(val)

        datos = {
            "rango": self.rango_combo.currentText(),
            "digitos": self.digitos,
            "capacidad": self.capacidad,
            "estructura": estructura_serializable,
            "estructura_anidada": self.estructura_anidada,
            "estrategia_actual": self.estrategia_actual
        }

        nombre_defecto = f"hash_cuadrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar estructura", nombre_defecto, "JSON (*.json)")
        if not ruta:
            return
        if not ruta.lower().endswith(".json"):
            ruta += ".json"

        try:
            ManejadorArchivos.guardar_json(ruta, datos)
            QMessageBox.information(self, "Éxito", f"Estructura guardada en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{str(e)}")

    def cargar_estructura(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo JSON", "", "JSON (*.json)")
        if not ruta:
            return

        try:
            datos = ManejadorArchivos.leer_json(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{str(e)}")
            return

        if not all(k in datos for k in ("rango", "digitos", "capacidad", "estructura", "estructura_anidada")):
            QMessageBox.critical(self, "Error", "El archivo no tiene el formato esperado.")
            return

        if self.capacidad > 0:
            resp = QMessageBox.question(self, "Confirmar", "¿Sobrescribir estructura actual?", QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.No:
                return

        self.rango_combo.setCurrentText(datos["rango"])
        self.digitos_spin.setValue(datos["digitos"])
        self.capacidad = datos["capacidad"]
        self.digitos = datos["digitos"]
        estructura_raw = datos["estructura"]
        self.estructura = []
        for val in estructura_raw:
            if val == "__DELETED__":
                self.estructura.append(self.DELETED)
            else:
                self.estructura.append(val)
        self.estructura_anidada = datos["estructura_anidada"]
        self.estrategia_actual = datos.get("estrategia_actual")
        self.historial = []

        self._actualizar_segun_estrategia()

        self.rango_combo.setEnabled(False)
        self.digitos_spin.setEnabled(False)
        self.btn_crear.setEnabled(False)
        self.habilitar_botones_estructura(True)

        QMessageBox.information(self, "Éxito", "Estructura cargada correctamente.")

    def eliminar_estructura(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "No hay estructura para eliminar.")
            return

        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar estructura actual?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.No:
            return

        self.capacidad = 0
        self.estructura = []
        self.estructura_anidada = []
        self.historial = []
        self.estrategia_actual = None
        self.limpiar_vista()

        self.rango_combo.setEnabled(True)
        self.digitos_spin.setEnabled(True)
        self.btn_crear.setEnabled(True)
        self.habilitar_botones_estructura(False)

        QMessageBox.information(self, "Éxito", "Estructura eliminada.")

    def deshacer(self):
        if not self.historial:
            QMessageBox.information(self, "Deshacer", "No hay acciones para deshacer.")
            return

        ultimo = self.historial.pop()
        tipo, pos, valor, estrategia = ultimo

        if tipo == "insertar":
            if estrategia in ("Arreglo anidado", "Lista encadenada"):
                if pos < len(self.estructura_anidada) and valor in self.estructura_anidada[pos]:
                    self.estructura_anidada[pos].remove(valor)
                else:
                    self.estructura[pos] = None
            else:
                self.estructura[pos] = self.DELETED
        elif tipo == "eliminar":
            if estrategia in ("Arreglo anidado", "Lista encadenada"):
                if self.estructura[pos] is None:
                    self.estructura[pos] = valor
                else:
                    self.estructura_anidada[pos].append(valor)
            else:
                self.estructura[pos] = valor

        self._actualizar_segun_estrategia()
        QMessageBox.information(self, "Deshacer", "Última acción deshecha.")

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()

    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas()