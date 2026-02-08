# main.py
import sys
import os

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Iniciando aplicación...")

try:
    from PySide6.QtWidgets import QApplication
    from ventanas_principales.ventana_principal import VentanaPrincipal
    
    app = QApplication(sys.argv)
    app.setApplicationName("Algoritmos y Grafos")
    
    ventana = VentanaPrincipal()
    ventana.show()
    
    print("✅ Aplicación iniciada correctamente")
    sys.exit(app.exec())
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("\n💡 Ejecuta: pip install PySide6")
    input("Presiona Enter para salir...")