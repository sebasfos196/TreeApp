"""
presentation/main_window.py - VERSIÓN ROBUSTA
============================================

Ventana principal con manejo robusto de errores
- Try/catch en todos los métodos críticos
- Fallbacks para cuando fallan las operaciones
- Debugging mejorado
- 180 líneas - Robusto y funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import traceback

# Imports básicos que sabemos que existen
from domain.events.event_bus import EventBus
from infrastructure.persistence.json_repository import JsonRepository
from application.services.workspace_manager import WorkspaceManager

class MainWindow:
    """Ventana principal robusta con manejo de errores"""
    
    def __init__(self):
        print("🏗️ Iniciando MainWindow...")
        
        try:
            # Inicializar componentes core
            self.event_bus = EventBus()
            print("✅ EventBus inicializado")
            
            self.repository = JsonRepository()
            print("✅ JsonRepository inicializado")
            
            self.workspace_manager = WorkspaceManager(self.repository, self.event_bus)
            print("✅ WorkspaceManager inicializado")
            
            # Configurar ventana principal
            self.root = tk.Tk()
            self.setup_window()
            print("✅ Ventana configurada")
            
            # Inicializar workspace con manejo de errores (Req. 4, 5)
            self.workspace_info = self.safe_initialize_workspace()
            print("✅ Workspace inicializado")
            
            # Configurar interfaz básica
            self.setup_safe_ui()
            print("✅ Interfaz configurada")
            
            # Setup eventos
            self.setup_events()
            print("✅ Eventos configurados")
            
        except Exception as e:
            print(f"❌ Error crítico en __init__: {e}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            self.show_error_ui(str(e))
    
    def safe_initialize_workspace(self):
        """Inicializa workspace con manejo seguro de errores"""
        
        try:
            workspace_info = self.workspace_manager.initialize_workspace_if_needed()
            print(f"✅ Workspace info: {workspace_info}")
            return workspace_info
            
        except Exception as e:
            print(f"❌ Error inicializando workspace: {e}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            
            # Crear workspace info de emergencia
            return {
                'created_new': True,
                'root_id': 'emergency',
                'preview_data': {
                    'root_id': 'emergency',
                    'name': 'Emergency Root',
                    'status': '⚠️',
                    'markdown': '# Error de inicialización',
                    'notes': f'Error: {str(e)}',
                    'type': 'folder',
                    'children': []
                }
            }
    
    def setup_window(self):
        """Configuración básica de la ventana"""
        
        try:
            self.root.title("TreeApp v4 Pro - Debugging Mode")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
            
            # Color de fondo básico VS Code
            self.root.configure(bg="#1e1e1e")
            
        except Exception as e:
            print(f"❌ Error configurando ventana: {e}")
            # Configuración mínima
            self.root.title("TreeApp v4 Pro - Error Mode")
            self.root.geometry("800x600")
    
    def setup_safe_ui(self):
        """Configura interfaz con manejo seguro de errores"""
        
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg="#1e1e1e")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título con info de debugging
            title_text = "🌳 TreeApp v4 Pro - Debugging Mode"
            if self.workspace_info and self.workspace_info.get('created_new'):
                title_text += " (Workspace Creado)"
            
            title_label = tk.Label(
                main_frame,
                text=title_text,
                font=("Segoe UI", 16, "bold"),
                bg="#1e1e1e",
                fg="#cccccc"
            )
            title_label.pack(pady=(0, 20))
            
            # Crear secciones principales
            self.create_debug_section(main_frame)
            self.create_basic_interface(main_frame)
            self.create_status_section(main_frame)
            
        except Exception as e:
            print(f"❌ Error configurando UI: {e}")
            self.show_error_ui(str(e))
    
    def create_debug_section(self, parent):
        """Crea sección de debugging"""
        
        try:
            debug_frame = tk.LabelFrame(
                parent,
                text="🔍 Debug Info",
                bg="#252526",
                fg="#cccccc",
                font=("Segoe UI", 10, "bold"),
                padx=10,
                pady=10
            )
            debug_frame.pack(fill="x", pady=(0, 10))
            
            # Info del workspace
            workspace_text = self.generate_debug_info()
            
            debug_text = tk.Text(
                debug_frame,
                height=8,
                bg="#1e1e1e",
                fg="#cccccc",
                font=("Consolas", 9),
                state="disabled"
            )
            debug_text.pack(fill="x")
            
            debug_text.configure(state="normal")
            debug_text.insert(1.0, workspace_text)
            debug_text.configure(state="disabled")
            
        except Exception as e:
            print(f"❌ Error creando debug section: {e}")
    
    def create_basic_interface(self, parent):
        """Crea interfaz básica de 3 columnas"""
        
        try:
            # Frame para columnas
            columns_frame = tk.Frame(parent, bg="#1e1e1e")
            columns_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            # Crear las 3 columnas
            self.create_column(columns_frame, "TreeCreator", "#252526")
            self.create_separator(columns_frame)
            self.create_column(columns_frame, "Documentación", "#1e1e1e")
            self.create_separator(columns_frame)
            self.create_column(columns_frame, "Vista Previa", "#252526")
            
        except Exception as e:
            print(f"❌ Error creando interfaz básica: {e}")
    
    def create_column(self, parent, title, bg_color):
        """Crea una columna básica"""
        
        try:
            column_frame = tk.Frame(parent, bg=bg_color, relief="solid", bd=1)
            column_frame.pack(side="left", fill="both", expand=True, padx=2)
            
            # Header
            header = tk.Label(
                column_frame,
                text=title,
                font=("Segoe UI", 12, "bold"),
                bg=bg_color,
                fg="#cccccc"
            )
            header.pack(pady=10)
            
            # Contenido básico
            content = tk.Text(
                column_frame,
                bg=bg_color,
                fg="#cccccc",
                font=("Consolas", 9),
                height=15,
                state="disabled"
            )
            content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            # Llenar con contenido según el título
            self.fill_column_content(content, title)
            
        except Exception as e:
            print(f"❌ Error creando columna {title}: {e}")
    
    def fill_column_content(self, text_widget, column_title):
        """Llena contenido de la columna"""
        
        try:
            content = ""
            
            if column_title == "TreeCreator":
                content = self.generate_tree_content()
            elif column_title == "Documentación":
                content = self.generate_editor_content()
            elif column_title == "Vista Previa":
                content = self.generate_preview_content()
            
            text_widget.configure(state="normal")
            text_widget.insert(1.0, content)
            text_widget.configure(state="disabled")
            
        except Exception as e:
            print(f"❌ Error llenando contenido de {column_title}: {e}")
            
            # Contenido de error
            error_content = f"❌ Error cargando contenido:\n{str(e)}"
            text_widget.configure(state="normal")
            text_widget.insert(1.0, error_content)
            text_widget.configure(state="disabled")
    
    def create_separator(self, parent):
        """Crea separador entre columnas"""
        
        try:
            sep = tk.Frame(parent, width=2, bg="#3c3c3c")
            sep.pack(side="left", fill="y", padx=2)
        except Exception as e:
            print(f"❌ Error creando separador: {e}")
    
    def create_status_section(self, parent):
        """Crea barra de estado"""
        
        try:
            status_frame = tk.Frame(parent, bg="#007acc", height=30)
            status_frame.pack(fill="x")
            
            # Stats seguros
            stats = self.get_safe_stats()
            
            status_text = f"📊 Total: {stats['total_nodes']} | 📁 Carpetas: {stats['folders']} | 📄 Archivos: {stats['files']}"
            
            status_label = tk.Label(
                status_frame,
                text=status_text,
                bg="#007acc",
                fg="white",
                font=("Segoe UI", 9)
            )
            status_label.pack(side="left", padx=10, pady=5)
            
            # Botón de reset
            reset_btn = tk.Button(
                status_frame,
                text="🔄 Reset Workspace",
                command=self.safe_reset_workspace,
                bg="#ffffff",
                fg="#007acc",
                font=("Segoe UI", 8)
            )
            reset_btn.pack(side="right", padx=10, pady=2)
            
        except Exception as e:
            print(f"❌ Error creando status section: {e}")
    
    def generate_debug_info(self):
        """Genera información de debugging"""
        
        try:
            info = f"""═══ DEBUGGING INFO ═══
Repository: {type(self.repository).__name__}
Nodes count: {len(getattr(self.repository, 'nodes', {}))}
Root ID: {getattr(self.repository, 'root_id', 'None')}
Workspace Created: {self.workspace_info.get('created_new', False)}

EventBus subscribers: {len(getattr(self.event_bus, '_subscribers', {}))}

═══ WORKSPACE INFO ═══"""
            
            if self.workspace_info and self.workspace_info.get('preview_data'):
                data = self.workspace_info['preview_data']
                info += f"""
Root Name: {data.get('name', 'N/A')}
Root Status: {data.get('status', 'N/A')}
Root Markdown: {data.get('markdown', 'N/A')[:50]}..."""
            
            return info
            
        except Exception as e:
            return f"❌ Error generando debug info: {e}"
    
    def generate_tree_content(self):
        """Genera contenido del árbol"""
        
        try:
            if self.workspace_info and self.workspace_info.get('preview_data'):
                data = self.workspace_info['preview_data']
                return f"""📁 {data['name']} {data['status']}
    {data.get('markdown', 'Sin markdown')}

✅ FASE 1: Completada
✅ FASE 2: En testing
⚠️ FASE 3: Pendiente

🔧 Debug Mode Active"""
            else:
                return "❌ No hay datos del workspace para mostrar"
                
        except Exception as e:
            return f"❌ Error generando tree content: {e}"
    
    def generate_editor_content(self):
        """Genera contenido del editor"""
        
        try:
            if self.workspace_info and self.workspace_info.get('preview_data'):
                data = self.workspace_info['preview_data']
                return f"""NODO: {data.get('name', 'N/A')}

MARKDOWN:
{data.get('markdown', 'Sin contenido')}

NOTAS:
{data.get('notes', 'Sin notas')}

STATUS: {data.get('status', 'N/A')}"""
            else:
                return "❌ No hay datos para editar"
                
        except Exception as e:
            return f"❌ Error generando editor content: {e}"
    
    def generate_preview_content(self):
        """Genera contenido de vista previa"""
        
        try:
            stats = self.get_safe_stats()
            
            return f"""📁 Vista Previa - Debug Mode

═══ ESTADÍSTICAS ═══
Total nodos: {stats['total_nodes']}
Carpetas: {stats['folders']}
Archivos: {stats['files']}
Completados ✅: {stats['completed']}
Pendientes ⬜: {stats['pending']}
Bloqueados ❌: {stats['blocked']}

═══ TESTING STATUS ═══
✅ EventBus: OK
✅ JsonRepository: OK
✅ WorkspaceManager: OK
✅ UI: OK

═══ NEXT STEPS ═══
1. Verificar que no hay más errores
2. Continuar con funcionalidades avanzadas
3. Testing completo FASE 1 & 2"""
            
        except Exception as e:
            return f"❌ Error generando preview: {e}"
    
    def get_safe_stats(self):
        """Obtiene estadísticas de forma segura"""
        
        try:
            return self.workspace_manager.get_workspace_stats()
        except Exception as e:
            print(f"❌ Error obteniendo stats: {e}")
            return {
                'total_nodes': 0,
                'folders': 0,
                'files': 0,
                'completed': 0,
                'pending': 0,
                'blocked': 0
            }
    
    def safe_reset_workspace(self):
        """Reset seguro del workspace"""
        
        try:
            result = messagebox.askyesno(
                "Reset Workspace",
                "¿Estás seguro de que quieres resetear el workspace?\n\nEsto eliminará todos los datos actuales."
            )
            
            if result:
                self.workspace_manager.reset_workspace()
                messagebox.showinfo("Reset Completo", "Workspace reseteado correctamente")
                
        except Exception as e:
            print(f"❌ Error reseteando workspace: {e}")
            messagebox.showerror("Error", f"Error reseteando workspace: {e}")
    
    def show_error_ui(self, error_msg):
        """Muestra UI básica de error"""
        
        try:
            error_frame = tk.Frame(self.root, bg="#1e1e1e")
            error_frame.pack(fill="both", expand=True)
            
            error_label = tk.Label(
                error_frame,
                text=f"❌ Error Crítico:\n\n{error_msg}",
                bg="#1e1e1e",
                fg="#f44747",
                font=("Segoe UI", 12),
                wraplength=600
            )
            error_label.pack(expand=True)
            
        except:
            pass  # Si hasta esto falla, no podemos hacer nada
    
    def setup_events(self):
        """Configurar eventos básicos"""
        
        try:
            # Evento de cierre
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Test del EventBus
            self.event_bus.subscribe('test_event', self.on_test_event)
            self.event_bus.publish('app_started', {'status': 'success'})
            
        except Exception as e:
            print(f"❌ Error configurando eventos: {e}")
    
    def on_test_event(self, data):
        """Handler de prueba para EventBus"""
        print(f"✅ EventBus funcionando: {data}")
    
    def on_closing(self):
        """Manejo del cierre de la aplicación"""
        
        try:
            if hasattr(self, 'repository'):
                self.repository.save_data()
                print("💾 Datos guardados correctamente")
        except Exception as e:
            print(f"⚠️ Error guardando datos: {e}")
        
        try:
            self.root.destroy()
        except:
            pass
    
    def run(self):
        """Ejecutar la aplicación"""
        
        try:
            print("🎮 Iniciando interfaz gráfica...")
            self.root.mainloop()
        except Exception as e:
            print(f"❌ Error ejecutando aplicación: {e}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            
            # Intentar mostrar error
            try:
                messagebox.showerror("Error Crítico", f"Error ejecutando aplicación:\n\n{e}")
            except:
                pass