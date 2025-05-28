#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TreeApp v4 Pro - Organizador Visual de Proyectos
Aplicación principal que usa los módulos existentes
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Configurar el path del proyecto para imports absolutos
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def check_basic_requirements():
    """Verificar requisitos básicos del sistema"""
    try:
        # Verificar versión de Python
        if sys.version_info < (3, 8):
            tk.messagebox.showerror(
                "Versión de Python",
                f"Se requiere Python 3.8 o superior.\n"
                f"Versión actual: {sys.version_info.major}.{sys.version_info.minor}"
            )
            return False
        
        # Verificar Tkinter
        import tkinter
        
        # Verificar JSON
        import json
        
        return True
    except ImportError as e:
        tk.messagebox.showerror(
            "Dependencias Faltantes",
            f"Error importando dependencias básicas: {e}\n"
            "Asegúrate de tener tkinter instalado."
        )
        return False

def initialize_application():
    """Inicializa la aplicación principal"""
    # Crear ventana principal
    root = tk.Tk()
    root.withdraw()  # Ocultar hasta que esté lista
    
    # Configurar ventana principal
    root.title("TreeApp v4 Pro")
    
    # Centrar ventana en pantalla
    window_width = 1400
    window_height = 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    return root

def handle_exception(exc_type, exc_value, exc_traceback):
    """Manejo global de excepciones"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    import traceback
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    try:
        import tkinter.messagebox as mb
        mb.showerror(
            "Error Crítico",
            f"Ha ocurrido un error inesperado:\n\n{str(exc_value)}\n\n"
            f"Detalles técnicos guardados en error.log"
        )
    except:
        print(f"Error crítico: {error_msg}")
    
    # Guardar error en archivo
    try:
        with open("error.log", "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"\n{'='*50}\n")
            f.write(f"Error en: {datetime.now()}\n")
            f.write(error_msg)
            f.write(f"{'='*50}\n")
    except:
        pass

def main():
    """Función principal de la aplicación"""
    try:
        # Configurar manejo de excepciones
        sys.excepthook = handle_exception
        
        # Verificar requisitos básicos
        if not check_basic_requirements():
            return
        
        # Inicializar aplicación
        root = initialize_application()
        if root is None:
            return
        
        try:
            # Importar la aplicación principal usando tree_app_consolidated.py
            from core.tree_app_consolidated import TreeAppV4Pro
            
            # Crear instancia de la aplicación
            app = TreeAppV4Pro(root)
            
            # Mostrar aplicación
            root.deiconify()
            root.focus_force()
            
            # Configurar cierre limpio
            def on_app_closing():
                try:
                    if hasattr(app, 'on_closing'):
                        app.on_closing()
                    else:
                        root.destroy()
                except Exception as e:
                    print(f"Error al cerrar: {e}")
                    root.destroy()
            
            root.protocol("WM_DELETE_WINDOW", on_app_closing)
            
            # Iniciar bucle principal
            print("🚀 TreeApp v4 Pro iniciado correctamente")
            root.mainloop()
            
        except ImportError as e:
            print(f"Error importando módulos: {e}")
            tk.messagebox.showerror(
                "Error de Importación",
                f"Error importando módulos: {e}\n"
                "Asegúrate de que todos los archivos estén en su lugar correcto.\n\n"
                f"Verifica que exista el archivo: core/tree_app_consolidated.py"
            )
            root.destroy()
            
    except Exception as e:
        print(f"Error crítico en main(): {e}")
        import traceback
        traceback.print_exc()
        
        try:
            tk.messagebox.showerror(
                "Error de Inicio",
                f"No se pudo iniciar TreeApp v4 Pro:\n{str(e)}"
            )
        except:
            pass

if __name__ == "__main__":
    main()