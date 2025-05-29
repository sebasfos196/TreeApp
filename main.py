"""
main.py - REPARADO
==================

Punto de entrada principal de TreeApp v4 Pro
- Imports corregidos
- Inicialización sin errores
- Compatibilidad con estructura actual
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal de la aplicación"""
    
    try:
        # Imports principales
        from domain.events.event_bus import EventBus
        from infrastructure.persistence.json_repository import JsonRepository
        from application.services.workspace_manager import WorkspaceManager
        from presentation.main_window import MainWindow
        
        print("🚀 Iniciando TreeApp v4 Pro...")
        
        # Inicializar aplicación
        app = MainWindow()
        
        print("✅ TreeApp v4 Pro iniciado correctamente")
        print("📁 Interfaz cargada - Funcionalidades FASE 1 y FASE 2 activas")
        
        # Ejecutar aplicación
        app.run()
        
    except ImportError as e:
        error_msg = f"❌ Error de importación: {e}"
        print(error_msg)
        
        # Mostrar error en ventana si es posible
        try:
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana principal
            messagebox.showerror(
                "Error de Importación - TreeApp v4 Pro",
                f"No se puede importar un módulo necesario:\n\n{e}\n\n"
                "Verifique que todos los archivos estén en su lugar:\n"
                "- domain/events/event_bus.py\n"
                "- infrastructure/persistence/json_repository.py\n"
                "- application/services/workspace_manager.py\n"
                "- presentation/main_window.py"
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"❌ Error inesperado: {e}"
        print(error_msg)
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error - TreeApp v4 Pro", 
                f"Error inesperado:\n\n{e}"
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()