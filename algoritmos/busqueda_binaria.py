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


# ---------- Manejador de archivos JSON (reutilizado) ----------
class ManejadorArchivos:
    @staticmethod
    def guardar_json(ruta, datos):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    @staticmethod
    def leer_json(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)


# ---------- Diálogo para ingresar una clave (reutilizado) ----------
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

# ---------- Ventana principal de Búsqueda Binaria ----------
class BusquedaBinariaWindow(QMainWindow):
    def __init__(self, volver_a_busquedas, volver_a_principal):
        super().__init__()
        self.volver_a_busquedas = volver_a_busquedas
        self.volver_a_principal = volver_a_principal

        # Atributos de la estructura
        self.capacidad = 0
        self.digitos = 4
        self.estructura = []          # Lista de longitud capacidad, con valores o None
        self.historial = []            # Lista de acciones para deshacer (tuplas)

        # Referencias a widgets de visualización
        self.labels = []                # QLabel para valores
        self.indices_labels = []        # QLabel para índices
        self.indices_reales = []        # índices reales (siempre 0..capacidad-1 en vista)

        self.initUI()
        
    COLUMNAS = 10
    MAX_CELDAS_VISIBLES = 200

    def initUI(self):
        self.setWindowTitle("Búsqueda Binaria - Estructura Ordenada")
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

        titulo = QLabel("BÚSQUEDA BINARIA")
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

        # Inicialmente deshabilitamos botones que requieren estructura
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

    def reconstruir_vista(self):
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
            columna = idx % self.COLUMNAS
            celda = self._crear_celda(idx)
            self.grid_layout.addWidget(celda, fila, columna)

        if self.capacidad > self.MAX_CELDAS_VISIBLES:
            lbl_aviso = QLabel(f"(Mostrando las primeras {self.MAX_CELDAS_VISIBLES} de {self.capacidad} celdas)")
            lbl_aviso.setAlignment(Qt.AlignCenter)
            lbl_aviso.setStyleSheet("color: #336699; font-style: italic; margin-top: 10px;")
            self.contenedor_layout.addWidget(lbl_aviso)

    def _crear_fila(self, inicio, fin):
        fila_widget = QWidget()
        fila_widget.setStyleSheet("background: transparent;")
        fila_layout = QHBoxLayout(fila_widget)
        fila_layout.setSpacing(5)
        fila_layout.setContentsMargins(0, 0, 0, 0)
        fila_layout.setAlignment(Qt.AlignCenter)

        for idx in range(inicio, fin):
            self._agregar_celda(fila_layout, idx)

        self.contenedor_layout.addWidget(fila_widget, 0, Qt.AlignCenter)

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

    def actualizar_vista(self):
        """Actualiza los valores mostrados según self.estructura."""
        for i, idx in enumerate(self.indices_reales):
            lbl = self.labels[i]
            valor = self.estructura[idx] if idx < len(self.estructura) else None
            if valor is not None:
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
        for i, idx in enumerate(self.indices_reales):
            if self.estructura[idx] is not None:
                self.labels[i].setStyleSheet("""
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
                self.labels[i].setStyleSheet("""
                    QLabel {
                        background-color: #99ccff;
                        border: 2px solid #4d9de0;
                        border-radius: 8px;
                        font-size: 16px;
                        color: #003366;
                    }
                """)

    # ---------- Lógica de estructura ordenada ----------
    def cantidad_ocupados(self):
        """Retorna cuántos elementos no None hay en la estructura."""
        return sum(1 for x in self.estructura if x is not None)

    def buscar_posicion_insercion(self, clave):
        """Retorna el índice donde debería insertarse la clave para mantener orden."""
        # Convertir clave a entero para comparar
        clave_int = int(clave)
        ocupados = [x for x in self.estructura if x is not None]
        # Búsqueda binaria sobre la lista de ocupados (valores)
        izq, der = 0, len(ocupados) - 1
        while izq <= der:
            mid = (izq + der) // 2
            if ocupados[mid] < clave_int:
                izq = mid + 1
            else:
                der = mid - 1
        # izq es la posición en la lista de ocupados donde debe ir
        # Ahora necesitamos el índice real en self.estructura correspondiente a esa posición
        # Dado que los ocupados están en las primeras posiciones (índices 0..k-1), la posición de inserción es izq
        return izq

    def insertar_en_posicion(self, clave, pos):
        """Inserta la clave en la posición pos, desplazando elementos a la derecha."""
        # Verificar si hay espacio
        if self.cantidad_ocupados() >= self.capacidad:
            return False
        # Desplazar elementos desde el final hasta pos
        for i in range(self.capacidad - 1, pos, -1):
            self.estructura[i] = self.estructura[i-1]
        self.estructura[pos] = int(clave)
        return True

    def eliminar_en_posicion(self, pos):
        """Elimina el elemento en pos y desplaza a la izquierda."""
        if pos < 0 or pos >= self.capacidad or self.estructura[pos] is None:
            return False
        for i in range(pos, self.capacidad - 1):
            self.estructura[i] = self.estructura[i+1]
        self.estructura[self.capacidad - 1] = None
        return True

    # ---------- Acciones de la interfaz ----------
    def crear_estructura(self):
        n = int(self.rango_combo.currentText())
        capacidad = 10 ** n
        digitos = self.digitos_spin.value()

        self.capacidad = capacidad
        self.digitos = digitos
        self.estructura = [None] * capacidad
        self.historial = []

        self.reconstruir_vista()
        self.actualizar_vista()

        self.rango_combo.setEnabled(False)
        self.digitos_spin.setEnabled(False)
        self.btn_crear.setEnabled(False)

        self.habilitar_botones_estructura(True)

        QMessageBox.information(self, "Éxito", f"Estructura creada con capacidad {capacidad}.")

    def insertar_clave(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        if self.cantidad_ocupados() >= self.capacidad:
            QMessageBox.warning(self, "Error", "La estructura está llena.")
            return

        dlg = DialogoClave(self.digitos, titulo="Insertar clave", modo="insertar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()
        clave_int = int(clave)

        # Verificar que no esté repetida (la búsqueda binaria puede fallar si está repetida)
        if clave_int in [x for x in self.estructura if x is not None]:
            QMessageBox.warning(self, "Clave duplicada", "Esa clave ya existe en la estructura.")
            return

        # Determinar posición de inserción
        pos = self.buscar_posicion_insercion(clave)
        # Insertar
        if self.insertar_en_posicion(clave, pos):
            self.historial.append(("insertar", pos, clave_int))
            self.actualizar_vista()
            QMessageBox.information(self, "Éxito", f"Clave {clave} insertada en posición {pos+1}.")
        else:
            QMessageBox.critical(self, "Error", "No se pudo insertar (problema interno).")

    def buscar_clave(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        dlg = DialogoClave(self.digitos, titulo="Buscar clave", modo="buscar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()
        clave_int = int(clave)

        # Búsqueda binaria sobre los valores ocupados (primeros k elementos)
        ocupados = [x for x in self.estructura if x is not None]
        izq, der = 0, len(ocupados) - 1
        encontrado = False
        pos_encontrada = -1
        while izq <= der and not encontrado:
            mid = (izq + der) // 2
            if ocupados[mid] == clave_int:
                encontrado = True
                # Necesitamos el índice real en self.estructura (que es mid, porque los ocupados están en índices 0..k-1)
                pos_encontrada = mid
            elif ocupados[mid] < clave_int:
                izq = mid + 1
            else:
                der = mid - 1

        if encontrado:
            # Resaltar la celda correspondiente
            self.reset_estilos()
            if pos_encontrada < len(self.indices_reales):
                self.labels[pos_encontrada].setStyleSheet("""
                    QLabel {
                        background-color: #2ecc71;
                        border: 3px solid #27ae60;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                        color: white;
                    }
                """)
                QMessageBox.information(self, "Resultado", f"Clave {clave} encontrada en la posición {pos_encontrada+1}.")
            else:
                QMessageBox.information(self, "Resultado", f"Clave {clave} encontrada en la posición {pos_encontrada+1}, pero no está visible.")
        else:
            QMessageBox.information(self, "Resultado", f"La clave {clave} no se encuentra en la estructura.")

    def eliminar_clave(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "Primero debe crear la estructura.")
            return

        dlg = DialogoClave(self.digitos, titulo="Eliminar clave", modo="eliminar", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return

        clave = dlg.get_clave()
        clave_int = int(clave)

        # Buscar la clave (binaria)
        ocupados = [x for x in self.estructura if x is not None]
        izq, der = 0, len(ocupados) - 1
        pos = -1
        while izq <= der:
            mid = (izq + der) // 2
            if ocupados[mid] == clave_int:
                pos = mid
                break
            elif ocupados[mid] < clave_int:
                izq = mid + 1
            else:
                der = mid - 1

        if pos == -1:
            QMessageBox.information(self, "Resultado", f"La clave {clave} no existe.")
            return

        # Eliminar
        if self.eliminar_en_posicion(pos):
            self.historial.append(("eliminar", pos, clave_int))
            self.actualizar_vista()
            QMessageBox.information(self, "Éxito", f"Clave {clave} eliminada.")
        else:
            QMessageBox.critical(self, "Error", "No se pudo eliminar.")

    def guardar_estructura(self):
        if self.capacidad == 0:
            QMessageBox.warning(self, "Error", "No hay estructura para guardar.")
            return

        datos = {
            "rango": self.rango_combo.currentText(),
            "digitos": self.digitos,
            "capacidad": self.capacidad,
            "claves": [v for v in self.estructura if v is not None]  # guardar solo las ocupadas
        }

        nombre_defecto = f"busqueda_binaria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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

        if not all(k in datos for k in ("rango", "digitos", "capacidad", "claves")):
            QMessageBox.critical(self, "Error", "El archivo no tiene el formato esperado.")
            return

        if self.capacidad > 0:
            resp = QMessageBox.question(self, "Confirmar", "¿Sobrescribir estructura actual?", QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.No:
                return

        # Restaurar
        self.rango_combo.setCurrentText(datos["rango"])
        self.digitos_spin.setValue(datos["digitos"])
        self.capacidad = datos["capacidad"]
        self.digitos = datos["digitos"]
        # Reconstruir estructura: colocar las claves en las primeras posiciones
        self.estructura = [None] * self.capacidad
        claves_ordenadas = sorted(datos["claves"])  # por si acaso no vienen ordenadas
        for i, val in enumerate(claves_ordenadas):
            if i < self.capacidad:
                self.estructura[i] = val
        self.historial = []

        self.reconstruir_vista()
        self.actualizar_vista()

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
        self.historial = []
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
        tipo, pos, valor = ultimo

        if tipo == "insertar":
            # Deshacer inserción: eliminar en esa posición
            self.eliminar_en_posicion(pos)
        elif tipo == "eliminar":
            # Deshacer eliminación: insertar en esa posición (desplazando)
            # Para simplificar, usamos el método de inserción pero debemos asegurar que la posición esté libre
            # Como al eliminar se desplazaron, la posición pos ahora está libre y los elementos a la derecha se movieron a la izquierda.
            # Para reinsertar, debemos desplazar a la derecha desde pos.
            if self.cantidad_ocupados() >= self.capacidad:
                QMessageBox.warning(self, "Error", "No se puede deshacer, estructura llena.")
                self.historial.append(ultimo)  # devolver
                return
            for i in range(self.capacidad - 1, pos, -1):
                self.estructura[i] = self.estructura[i-1]
            self.estructura[pos] = valor

        self.actualizar_vista()
        QMessageBox.information(self, "Deshacer", "Última acción deshecha.")

    def ir_a_principal(self):
        self.close()
        self.volver_a_principal()

    def ir_a_busquedas(self):
        self.close()
        self.volver_a_busquedas()