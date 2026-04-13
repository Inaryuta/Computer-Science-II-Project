from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QSpinBox, QDialogButtonBox

class DialogoArista(QDialog):
    def __init__(self, num_vertices, parent=None, etiquetas=None):
        super().__init__(parent)
        self.num_vertices = num_vertices
        self.etiquetas = etiquetas if etiquetas else {i: str(i+1) for i in range(num_vertices)}
        self.setWindowTitle("Arista")
        layout = QVBoxLayout(self)

        # Origen
        layout.addWidget(QLabel("Vértice origen:"))
        self.combo_origen = QComboBox()
        for i in range(num_vertices):
            etiqueta = self.etiquetas.get(i, str(i+1))
            self.combo_origen.addItem(etiqueta, i)  # guardar índice como userData
        layout.addWidget(self.combo_origen)

        # Destino
        layout.addWidget(QLabel("Vértice destino:"))
        self.combo_destino = QComboBox()
        for i in range(num_vertices):
            etiqueta = self.etiquetas.get(i, str(i+1))
            self.combo_destino.addItem(etiqueta, i)
        layout.addWidget(self.combo_destino)

        # Peso (opcional)
        layout.addWidget(QLabel("Peso:"))
        self.spin_peso = QSpinBox()
        self.spin_peso.setRange(1, 100)
        self.spin_peso.setValue(1)
        layout.addWidget(self.spin_peso)

        # Botones
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_arista(self):
        origen = self.combo_origen.currentData()
        destino = self.combo_destino.currentData()
        peso = self.spin_peso.value()
        return origen, destino, peso
    