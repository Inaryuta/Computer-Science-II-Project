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


# ---------- Diálogo para ingresar una clave ----------
class DialogoClave(QDialog):
    def __init__(self, longitud, titulo="Ingresar clave", modo="insertar", parent=None, mensaje=None):
        """
        longitud: número de dígitos requerido.
        modo: "insertar", "buscar", "eliminar", "mensaje", "confirmar"
        """
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
            # Mostrar solo un mensaje
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
            # Modo ingreso de clave
            lbl_info = QLabel(f"Ingrese una clave de {longitud} dígitos:")
            layout.addWidget(lbl_info)

            self.edit_clave = QLineEdit()
            self.edit_clave.setMaxLength(longitud)
            self.edit_clave.setValidator(QIntValidator(0, 10**longitud - 1))
            self.edit_clave.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.edit_clave)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect (self.validar_y_aceptar)
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


# ---------- Ventana principal de Búsqueda Lineal ----------
class BusquedaLinealWindow(QMainWindow):
    def __init__(self, volver_a_busquedas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.volver_a_principal = volver_a_principal

        # Atributos de la estructura
        self.capacidad = 0
        self.digitos = 4          # valor por defecto
        self.estructura = {}       # diccionario {indice: clave}
        self.historial = []        # lista de acciones para deshacer

        # Referencias a widgets de visualización
        self.labels = []           # lista de QLabel que muestran las claves
        self.indices_labels = []   # lista de QLabel que muestran los índices
        self.indices_reales = []   # lista de índices reales (posición en el arreglo)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Búsqueda Lineal - Estructura")
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

        titulo = QLabel("BÚSQUEDA LINEAL")
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
        self.rango_combo.addItems([str(i) for i in range(1, 7)])  # 10^1 a 10^6
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

        # Estilo adicional para estos botones
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

        # ----- Conexiones de señales -----
        self.btn_crear.clicked.connect(self.crear_estructura)
        self.btn_insertar.clicked.connect(self.insertar_clave)
        self.btn_buscar.clicked.connect(self.buscar_clave)
        self.btn_eliminar_clave.clicked.connect(self.eliminar_clave)
        self.btn_guardar.clicked.connect(self.guardar_estructura)
        self.btn_cargar.clicked.connect(self.cargar_estructura)
        self.btn_eliminar_estructura.clicked.connect(self.eliminar_estructura)
        self.btn_deshacer.clicked.connect(self.deshacer)

        # Inicialmente deshabilitamos los botones que requieren estructura creada
        self.habilitar_botones_estructura(False)

    # ---------- Métodos auxiliares ----------
    def habilitar_botones_estructura(self, habilitar):
        """Habilita/deshabilita botones que dependen de una estructura existente."""
        self.btn_insertar.setEnabled(habilitar)
        self.btn_buscar.setEnabled(habilitar)
        self.btn_eliminar_clave.setEnabled(habilitar)
        self.btn_guardar.setEnabled(habilitar)
        self.btn_eliminar_estructura.setEnabled(habilitar)
        self.btn_deshacer.setEnabled(habilitar)
        # El botón cargar siempre está habilitado
        self.btn_cargar.setEnabled(True)

    def limpiar_vista(self):
        while self.contenedor_layout.count():
            item = self.contenedor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Si hay un layout, eliminamos sus widgets también
                self._eliminar_layout(item.layout())
        self.labels.clear()
        self.indices_labels.clear()
        self.indices_reales.clear()

    def _eliminar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._eliminar_layout(item.layout())

    # Constante para el número de columnas
    COLUMNAS = 10
    MAX_CELDAS_VISIBLES = 200  # Mostrar hasta 200 celdas (20 filas)

    def reconstruir_vista(self):
        """Reconstruye la visualización usando un grid layout."""
        self.limpiar_vista()
        if self.capacidad <= 0:
            return

        # Crear un QGridLayout para colocar las celdas en filas y columnas
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.contenedor_layout.addLayout(self.grid_layout)

        # Determinar cuántas celdas mostrar (limitado por rendimiento)
        mostrar = min(self.capacidad, self.MAX_CELDAS_VISIBLES)

        for idx in range(mostrar):
            fila = idx // self.COLUMNAS
            columna = idx % self.COLUMNAS
            celda = self._crear_celda(idx)
            self.grid_layout.addWidget(celda, fila, columna)

        # Si la capacidad es mayor que el límite, mostrar un mensaje
        if self.capacidad > self.MAX_CELDAS_VISIBLES:
            lbl_aviso = QLabel(f"(Mostrando las primeras {self.MAX_CELDAS_VISIBLES} de {self.capacidad} celdas)")
            lbl_aviso.setAlignment(Qt.AlignCenter)
            lbl_aviso.setStyleSheet("color: #336699; font-style: italic; margin-top: 10px;")
            self.contenedor_layout.addWidget(lbl_aviso)

    def _crear_celda(self, idx_real):
        """Crea y retorna un widget contenedor para la celda en el índice real dado."""
        contenedor = QWidget()
        contenedor.setFixedSize(80, 100)  # Ancho y alto fijo
        vbox = QVBoxLayout(contenedor)
        vbox.setSpacing(2)
        vbox.setContentsMargins(0, 0, 0, 0)

        # Cuadro que muestra el valor
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

        # Etiqueta con el número de índice (1-based)
        numero = QLabel(str(idx_real + 1))
        numero.setAlignment(Qt.AlignCenter)
        numero.setFixedHeight(20)
        numero.setStyleSheet("font-size: 12px; color: #336699; background: transparent;")

        vbox.addWidget(cuadro)
        vbox.addWidget(numero)

        # Guardar referencias para actualizaciones posteriores
        self.labels.append(cuadro)
        self.indices_labels.append(numero)
        self.indices_reales.append(idx_real)

        return contenedor

    def actualizar_vista(self):
        """Actualiza los valores mostrados según self.estructura."""
        for i, idx_real in enumerate(self.indices_reales):
            lbl = self.labels[i]
            valor = self.estructura.get(idx_real, "")
            if valor:
                lbl.setText(str(valor))
                lbl.setStyleSheet("""
                    QLabel {
                        background-color: #4d9de0;
                        border: 2px solid #1e6bb8;
                        border-radius: 8px;
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
                        border-radius: 8px;
                        font-size: 16px;
                        color: #003366;
                    }
                """)

    def reset_estilos(self):
        """Restaura los estilos normales de todas las celdas."""
        for i, lbl in enumerate(self.labels):
            if self.estructura.get(self.indices_reales[i], ""):
                lbl.setStyleSheet("""
                    QLabel {
                        background-color: #4d9de0;
                        border: 2px solid #1e6bb8;
                        border-radius: 8px;
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
                        border-radius: 8px;
                        font-size: 16px;
                        color: #003366;
                    }
                """)

    # ---------- Funcionalidades ----------
    def crear_estructura(self):
        """Crea una nueva estructura vacía con la capacidad y dígitos seleccionados."""
        n = int(self.rango_combo.currentText())
        capacidad = 10 ** n
        digitos = self.digitos_spin.value()

        self.capacidad = capacidad
        self.digitos = digitos
        self.estructura = {}  # vacía
        self.historial = []

        self.reconstruir_vista()
        self.actualizar_vista()

        # Deshabilitar controles de creación
        self.rango_combo.setEnabled(False)
        self.digitos_spin.setEnabled(False)
        self.btn_crear.setEnabled(False)

        # Habilitar botones de manipulación
        self.habilitar_botones_estructura(True)

        QMessageBox.information(self, "Éxito", f"Estructura creada con capacidad {capacidad}.")

    def insertar_clave(self):
        """Inserta una clave en la primera posición libre."""
        if not self.capacidad:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        # Verificar si hay espacio
        if len(self.estructura) >= self.capacidad:
            QMessageBox.warning(self, "Error", "La estructura está llena.")
            return

        dlg = DialogoClave(self.digitos, titulo="Insertar clave", modo="insertar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()

        # Validar que no esté repetida
        if clave in self.estructura.values():
            QMessageBox.warning(self, "Clave duplicada", "Esa clave ya existe en la estructura.")
            return

        # Buscar primera posición libre (menor índice no ocupado)
        for i in range(self.capacidad):
            if i not in self.estructura:
                self.estructura[i] = clave
                self.historial.append(("insertar", i, clave))
                break

        self.actualizar_vista()
        QMessageBox.information(self, "Éxito", f"Clave {clave} insertada.")

    def buscar_clave(self):
        """Busca una clave y resalta la celda donde se encuentra."""
        if not self.capacidad:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        dlg = DialogoClave(self.digitos, titulo="Buscar clave", modo="buscar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()

        # Búsqueda lineal
        encontrado = None
        for idx, val in self.estructura.items():
            if val == clave:
                encontrado = idx
                break

        if encontrado is None:
            QMessageBox.information(self, "Resultado", f"La clave {clave} no se encuentra en la estructura.")
            return

        # Resaltar la celda encontrada
        self.reset_estilos()
        # Buscar la posición en la lista visual
        try:
            pos_visual = self.indices_reales.index(encontrado)
            self.labels[pos_visual].setStyleSheet("""
                QLabel {
                    background-color: #2ecc71;
                    border: 3px solid #27ae60;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }
            """)
            QMessageBox.information(self, "Resultado", f"Clave {clave} encontrada en la posición {encontrado + 1}.")
        except ValueError:
            # El índice no está visible (por límite de visualización)
            QMessageBox.information(self, "Resultado",
                                    f"Clave {clave} encontrada en la posición {encontrado + 1}, pero no está visible actualmente.")

    def eliminar_clave(self):
        """Elimina una clave de la estructura."""
        if not self.capacidad:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        dlg = DialogoClave(self.digitos, titulo="Eliminar clave", modo="eliminar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()

        # Buscar la clave
        idx_eliminar = None
        for idx, val in self.estructura.items():
            if val == clave:
                idx_eliminar = idx
                break

        if idx_eliminar is None:
            QMessageBox.information(self, "Resultado", f"La clave {clave} no existe.")
            return

        # Eliminar
        del self.estructura[idx_eliminar]
        self.historial.append(("eliminar", idx_eliminar, clave))
        self.actualizar_vista()
        QMessageBox.information(self, "Éxito", f"Clave {clave} eliminada.")

    def guardar_estructura(self):
        """Guarda la estructura actual en un archivo JSON."""
        if not self.capacidad:
            QMessageBox.warning(self, "Error", "No hay estructura para guardar.")
            return

        datos = {
            "rango": self.rango_combo.currentText(),
            "digitos": self.digitos,
            "capacidad": self.capacidad,
            "claves": {str(k): v for k, v in self.estructura.items()}
        }

        nombre_defecto = f"busqueda_lineal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar estructura", nombre_defecto, "JSON (*.json)"
        )
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
        """Carga una estructura desde un archivo JSON."""
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo JSON", "", "JSON (*.json)")
        if not ruta:
            return

        try:
            datos = ManejadorArchivos.leer_json(ruta)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{str(e)}")
            return

        # Validar estructura del JSON
        if not all(k in datos for k in ("rango", "digitos", "capacidad", "claves")):
            QMessageBox.critical(self, "Error", "El archivo no tiene el formato esperado.")
            return

        # Preguntar si ya hay una estructura actual
        if self.capacidad > 0:
            resp = QMessageBox.question(
                self, "Confirmar",
                "Ya hay una estructura cargada. ¿Desea sobrescribirla?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                return

        # Restaurar datos
        self.rango_combo.setCurrentText(datos["rango"])
        self.digitos_spin.setValue(datos["digitos"])
        self.capacidad = datos["capacidad"]
        self.digitos = datos["digitos"]
        # Convertir claves a enteros
        self.estructura = {int(k): v for k, v in datos["claves"].items()}
        self.historial = []

        # Reconstruir vista
        self.reconstruir_vista()
        self.actualizar_vista()

        # Bloquear controles de creación
        self.rango_combo.setEnabled(False)
        self.digitos_spin.setEnabled(False)
        self.btn_crear.setEnabled(False)

        self.habilitar_botones_estructura(True)

        QMessageBox.information(self, "Éxito", "Estructura cargada correctamente.")

    def eliminar_estructura(self):
        """Elimina la estructura actual (vacía todo)."""
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "No hay estructura para eliminar.")
            return

        resp = QMessageBox.question(
            self, "Confirmar",
            "¿Está seguro de eliminar la estructura actual?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.No:
            return

        self.capacidad = 0
        self.estructura = {}
        self.historial = []
        self.limpiar_vista()

        # Habilitar controles de creación
        self.rango_combo.setEnabled(True)
        self.digitos_spin.setEnabled(True)
        self.btn_crear.setEnabled(True)

        self.habilitar_botones_estructura(False)

        QMessageBox.information(self, "Éxito", "Estructura eliminada.")

    def deshacer(self):
        """Deshace la última operación (insertar o eliminar)."""
        if not self.historial:
            QMessageBox.information(self, "Deshacer", "No hay acciones para deshacer.")
            return

        ultimo = self.historial.pop()
        tipo, idx, clave = ultimo

        if tipo == "insertar":
            # Se insertó clave en idx; deshacer es eliminar
            if idx in self.estructura and self.estructura[idx] == clave:
                del self.estructura[idx]
        elif tipo == "eliminar":
            # Se eliminó clave de idx; deshacer es volver a insertar
            self.estructura[idx] = clave

        self.actualizar_vista()
        QMessageBox.information(self, "Deshacer", "Última acción deshecha.")

    def ir_a_principal(self):
        """Cierra y vuelve a la ventana principal."""
        self.close()
        self.volver_a_principal()

    def ir_a_busquedas(self):
        """Cierra y vuelve al menú de búsquedas."""
        self.close()
        self.volver_a_busquedas()