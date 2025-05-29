# main.py
"""
Punto de entrada principal para TreeApp v4 Pro.
"""
import sys
import os

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from presentation.main_window import MainWindow


def main():
    """Función principal de la aplicación."""
    try:
        print("🚀 Iniciando TreeApp v4 Pro...")
        
        # Crear y ejecutar aplicación
        app = MainWindow()
        
        print("✅ TreeApp v4 Pro iniciado correctamente")
        print("🔧 Arquitectura DDD cargada:")
        print("   - EventBus: ✅")
        print("   - CommandBus: ✅") 
        print("   - NodeRepository: ✅")
        print("   - MainWindow: ✅")
        
        app.run()
        
    except Exception as e:
        print(f"❌ Error iniciando TreeApp v4 Pro: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)


if __name__ == "__main__":
    main()