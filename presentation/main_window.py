# presentation/main_window.py
"""
Ventana principal de TreeCreator v4 Pro.
Configura el layout de 3 paneles, coordina la UI y maneja la infraestructura.
Versión refactorizada con componentes especializados.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from typing import Optional

# Agregar paths para imports absolutos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Imports de infraestructura
from application.commands.command_bus import get_command_bus
from infrastructure.persistence.json_repository import NodeRepository
from application.commands.node.create_node_command import CreateNodeCommandHandler, CreateNodeCommand

# Imports de componentes refactorizados
from presentation.views.panels.tree_panel.tree_view import TreeView
from presentation.views.panels.editor_panel.editor_container import EditorContainer
from presentation.views.panels.preview_panel.preview_container import PreviewContainer

# Import del gestor de configuración
try:
    from shared.config.config_manager import get_config_manager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️ ConfigManager no disponible, usando configuración por defecto")


class MainWindow:
    """
    Ventana principal de TreeCreator v4 Pro.
    
    Responsabilidades:
    - Configurar layout de 3 paneles
    - Inicializar infraestructura (repositories, command bus)
    - Coordinar comunicación entre paneles
    - Manejar eventos de ventana y aplicación
    """
    
    def __init__(self):
        self.root = tk.Tk()
        
        # Configuración de ventana
        self._setup_window_config()
        
        # Inicializar componentes
        self._setup_infrastructure()
        self._setup_layout()
        self._setup_panels()
        self._setup_inter_panel_communication()
        self._setup_window_events()
        
        print("✅ TreeCreator v4 Pro inicializado correctamente")
    
    def _setup_window_config(self):
        """Configurar propiedades básicas de la ventana."""
        self.root.title("🌳 TreeCreator v4 Pro - Organizador Visual de Proyectos")
        
        # Configuración desde ConfigManager si está disponible
        if CONFIG_AVAILABLE:
            self.config_manager = get_config_manager()
            window_config = self.config_manager.get_window_config()
            
            width = window_config.get('width', 1400)
            height = window_config.get('height', 800)
            
            # Posición guardada si existe
            x = self.config_manager.get('app.window_x')
            y = self.config_manager.get('app.window_y')
            
            if x is not None and y is not None:
                self.root.geometry(f"{width}x{height}+{x}+{y}")
            else:
                self.root.geometry(f"{width}x{height}")
                # Centrar ventana
                self.root.eval('tk::PlaceWindow . center')
        else:
            self.config_manager = None
            self.root.geometry("1400x800")
            self.root.eval('tk::PlaceWindow . center')
        
        # Configuraciones adicionales
        self.root.minsize(1000, 600)
        self.root.state('zoomed' if os.name == 'nt' else 'normal')  # Maximizar en Windows
        
        # Icono de la aplicación (si existe)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'treeapp.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Ignorar si no hay icono disponible
    
    def _setup_infrastructure(self):
        """Configurar infraestructura de la aplicación."""
        try:
            # Repositorio de nodos
            self.node_repository = NodeRepository()
            
            # Command bus y handlers
            self.command_bus = get_command_bus()
            self.command_bus.register_handler(
                CreateNodeCommand, 
                CreateNodeCommandHandler(self.node_repository)
            )
            
            print("✅ Infraestructura configurada correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando infraestructura: {e}")
            messagebox.showerror(
                "Error de Inicialización",
                f"Error configurando infraestructura:\n{str(e)}\n\nLa aplicación podría no funcionar correctamente."
            )
    
    def _setup_layout(self):
        """Configurar layout principal de 3 paneles."""
        # Frame principal para mejor control
        self.main_container = tk.Frame(self.root, bg='#f0f0f0')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # PanedWindow principal con 3 columnas
        self.main_paned = tk.PanedWindow(
            self.main_container, 
            orient=tk.HORIZONTAL,
            sashwidth=6,
            relief=tk.RAISED,
            bg='#e0e0e0',
            sashrelief=tk.RAISED
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame izquierdo - TreeCreator (Explorador de árbol)
        self.left_frame = tk.Frame(
            self.main_paned, 
            bg='#f0f0f0', 
            relief=tk.SUNKEN, 
            bd=1
        )
        self.main_paned.add(self.left_frame, minsize=280, width=350)
        
        # Frame central - Editor de documentación (4 campos)
        self.center_frame = tk.Frame(
            self.main_paned, 
            bg='#ffffff', 
            relief=tk.SUNKEN, 
            bd=1
        )
        self.main_paned.add(self.center_frame, minsize=400, width=500)
        
        # Frame derecho - Vista previa
        self.right_frame = tk.Frame(
            self.main_paned, 
            bg='#f8f8f8', 
            relief=tk.SUNKEN, 
            bd=1
        )
        self.main_paned.add(self.right_frame, minsize=320, width=400)
        
        print("✅ Layout de 3 paneles configurado")
    
    def _setup_panels(self):
        """Configurar los 3 paneles principales."""
        try:
            # Panel del árbol (izquierda) - TreeCreator
            self._setup_tree_panel()
            
            # Panel del editor (centro) - Documentación
            self._setup_editor_panel()
            
            # Panel de vista previa (derecha)
            self._setup_preview_panel()
            
            print("✅ Todos los paneles configurados correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando paneles: {e}")
            messagebox.showerror(
                "Error de Paneles",
                f"Error configurando paneles:\n{str(e)}"
            )
    
    def _setup_tree_panel(self):
        """Configurar panel del explorador de árbol (TreeCreator)."""
        try:
            # Crear TreeView con la nueva arquitectura refactorizada
            self.tree_view = TreeView(self.left_frame, self.node_repository)
            
            print("✅ TreeCreator configurado")
            
        except Exception as e:
            print(f"❌ Error configurando TreeCreator: {e}")
            
            # Crear un placeholder en caso de error
            error_label = tk.Label(
                self.left_frame,
                text=f"❌ Error cargando TreeCreator:\n{str(e)}",
                bg='#f0f0f0',
                fg='red',
                justify=tk.LEFT,
                wraplength=250
            )
            error_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    def _setup_editor_panel(self):
        """Configurar panel del editor de documentación."""
        try:
            # Crear EditorContainer (ya refactorizado previamente)
            self.editor_container = EditorContainer(self.center_frame, self.node_repository)
            
            print("✅ Editor de documentación configurado")
            
        except Exception as e:
            print(f"❌ Error configurando editor: {e}")
            
            # Crear un placeholder en caso de error
            error_label = tk.Label(
                self.center_frame,
                text=f"❌ Error cargando Editor:\n{str(e)}",
                bg='#ffffff',
                fg='red',
                justify=tk.LEFT,
                wraplength=350
            )
            error_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    def _setup_preview_panel(self):
        """Configurar panel de vista previa."""
        try:
            # Crear PreviewContainer con la nueva arquitectura de renderers
            self.preview_container = PreviewContainer(self.right_frame, self.node_repository)
            
            print("✅ Vista previa configurada")
            
        except Exception as e:
            print(f"❌ Error configurando vista previa: {e}")
            
            # Crear un placeholder en caso de error
            error_label = tk.Label(
                self.right_frame,
                text=f"❌ Error cargando Vista Previa:\n{str(e)}",
                bg='#f8f8f8',
                fg='red',
                justify=tk.LEFT,
                wraplength=300
            )
            error_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    
    def _setup_inter_panel_communication(self):
        """Configurar comunicación entre paneles."""
        try:
            # Verificar que todos los paneles se crearon correctamente
            if not hasattr(self, 'tree_view') or not hasattr(self, 'editor_container'):
                print("⚠️ No se puede configurar comunicación: paneles no disponibles")
                return
            
            # Conectar selección del árbol con el editor
            self._connect_tree_to_editor()
            
            # Conectar cambios para refrescar vista previa
            if hasattr(self, 'preview_container'):
                self._connect_preview_updates()
            
            print("✅ Comunicación entre paneles configurada")
            
        except Exception as e:
            print(f"❌ Error configurando comunicación entre paneles: {e}")
    
    def _connect_tree_to_editor(self):
        """Conectar selección del árbol con el editor."""
        def on_tree_select(selected_id: Optional[str]):
            """Callback cuando se selecciona un nodo en el árbol."""
            try:
                if selected_id:
                    node = self.node_repository.find_by_id(selected_id)
                    if node:
                        self.editor_container.load_node(node)
                        print(f"📝 Nodo cargado en editor: {node.name}")
                    else:
                        self.editor_container.clear_editor()
                        print("⚠️ Nodo no encontrado, editor limpiado")
                else:
                    self.editor_container.clear_editor()
                    print("📝 Editor limpiado por deselección")
                    
            except Exception as e:
                print(f"❌ Error en selección de árbol: {e}")
        
        def on_name_update(node_id: str, new_name: str):
            """Callback cuando se actualiza el nombre de un nodo desde el editor."""
            try:
                # Actualizar TreeView
                if hasattr(self.tree_view, 'update_node_display'):
                    success = self.tree_view.update_node_display(node_id, new_name)
                    if success:
                        print(f"🔄 TreeView actualizado: {new_name}")
                
                # Refrescar vista previa si está disponible
                if hasattr(self, 'preview_container'):
                    self.preview_container.refresh()
                    
            except Exception as e:
                print(f"❌ Error actualizando nombre: {e}")
        
        # Establecer callbacks bidireccionales
        self.tree_view.set_selection_callback(on_tree_select)
        self.editor_container.set_tree_update_callback(on_name_update)
    
    def _connect_preview_updates(self):
        """Conectar eventos que requieren actualizar la vista previa."""
        # Wrapper para operaciones CRUD en el árbol
        self._wrap_tree_operations()
        
        # Wrapper para auto-save del editor
        self._wrap_editor_operations()
    
    def _wrap_tree_operations(self):
        """Envolver operaciones del árbol para refrescar vista previa."""
        if not hasattr(self.tree_view, '_create_folder'):
            return
        
        # Guardar métodos originales
        original_create_folder = self.tree_view._create_folder
        original_create_file = self.tree_view._create_file
        original_delete_node = self.tree_view._delete_node
        
        def refresh_after_create_folder():
            try:
                result = original_create_folder()
                self.preview_container.refresh()
                return result
            except Exception as e:
                print(f"❌ Error en crear carpeta: {e}")
        
        def refresh_after_create_file():
            try:
                result = original_create_file()
                self.preview_container.refresh()
                return result
            except Exception as e:
                print(f"❌ Error en crear archivo: {e}")
        
        def refresh_after_delete():
            try:
                result = original_delete_node()
                self.preview_container.refresh()
                return result
            except Exception as e:
                print(f"❌ Error en eliminar nodo: {e}")
        
        # Reemplazar métodos con wrappers
        self.tree_view._create_folder = refresh_after_create_folder
        self.tree_view._create_file = refresh_after_create_file
        self.tree_view._delete_node = refresh_after_delete
    
    def _wrap_editor_operations(self):
        """Envolver operaciones del editor para refrescar vista previa."""
        if not hasattr(self.editor_container, '_auto_save'):
            return
        
        # Guardar método original
        original_auto_save = self.editor_container._auto_save
        
        def refresh_after_save():
            try:
                result = original_auto_save()
                # Refrescar vista previa después del guardado
                if hasattr(self, 'preview_container'):
                    self.preview_container.refresh()
                return result
            except Exception as e:
                print(f"❌ Error en auto-save: {e}")
        
        # Reemplazar método
        self.editor_container._auto_save = refresh_after_save
    
    def _setup_window_events(self):
        """Configurar eventos de ventana."""
        # Evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Eventos de redimensionado (si ConfigManager está disponible)
        if self.config_manager:
            self.root.bind('<Configure>', self._on_window_configure)
        
        # Atajos de teclado globales
        self._setup_keyboard_shortcuts()
    
    def _setup_keyboard_shortcuts(self):
        """Configurar atajos de teclado globales."""
        # Atajos para el árbol
        self.root.bind('<Control-n>', lambda e: self._safe_call(self.tree_view._create_file))
        self.root.bind('<Control-Shift-N>', lambda e: self._safe_call(self.tree_view._create_folder))
        self.root.bind('<Delete>', lambda e: self._safe_call(self.tree_view._delete_node))
        self.root.bind('<F5>', lambda e: self._safe_call(self.tree_view.refresh))
        
        # Atajos para vista previa
        if hasattr(self, 'preview_container'):
            self.root.bind('<Control-r>', lambda e: self._safe_call(self.preview_container.refresh))
        
        # Atajos generales
        self.root.bind('<Control-q>', lambda e: self._on_closing())
        self.root.bind('<F1>', lambda e: self._show_help())
        
        print("✅ Atajos de teclado configurados")
    
    def _safe_call(self, method):
        """Llamar método de forma segura con manejo de errores."""
        try:
            if callable(method):
                method()
        except Exception as e:
            print(f"❌ Error en atajo de teclado: {e}")
    
    def _on_window_configure(self, event):
        """Manejar redimensionado de ventana."""
        # Solo procesar eventos de la ventana principal
        if event.widget == self.root and self.config_manager:
            # Guardar tamaño y posición con debounce
            if hasattr(self, '_configure_timer'):
                self.root.after_cancel(self._configure_timer)
            
            self._configure_timer = self.root.after(1000, self._save_window_state)
    
    def _save_window_state(self):
        """Guardar estado de ventana."""
        if self.config_manager:
            try:
                geometry = self.root.geometry()
                # Parsear geometry string (ej: "1400x800+100+50")
                size_pos = geometry.split('+')
                size = size_pos[0].split('x')
                
                width = int(size[0])
                height = int(size[1])
                
                x = int(size_pos[1]) if len(size_pos) > 1 else None
                y = int(size_pos[2]) if len(size_pos) > 2 else None
                
                self.config_manager.save_window_state(width, height, x, y)
                
            except Exception as e:
                print(f"❌ Error guardando estado de ventana: {e}")
    
    def _show_help(self):
        """Mostrar ayuda de la aplicación."""
        help_text = """🌳 TreeCreator v4 Pro - Ayuda Rápida

📁 TREECREATOR (Panel Izquierdo):
• Doble clic: Editar nombre inline
• Clic derecho: Menú contextual
• Drag & Drop: Mover elementos
• Ctrl+N: Nuevo archivo
• Ctrl+Shift+N: Nueva carpeta
• Delete: Eliminar seleccionado

📝 EDITOR (Panel Central):
• 4 campos editables con auto-guardado
• Plantillas automáticas por extensión
• Sincronización en tiempo real

🔍 VISTA PREVIA (Panel Derecho):
• 4 modos de visualización
• Configuración personalizable  
• Exportación a TXT
• Selección y copia habilitada

⌨️ ATAJOS GLOBALES:
• F5: Refrescar
• Ctrl+R: Refrescar vista previa
• Ctrl+Q: Salir
• F1: Ayuda
"""
        
        messagebox.showinfo("Ayuda - TreeCreator v4 Pro", help_text)
    
    def _on_closing(self):
        """Manejar cierre de la aplicación."""
        try:
            # Guardar configuración si está disponible
            if self.config_manager:
                self._save_window_state()
                self.config_manager.save_config()
                print("✅ Configuración guardada al cerrar")
            
            # Cancelar edición inline si está activa
            if hasattr(self.tree_view, 'inline_editor') and self.tree_view.inline_editor:
                self.tree_view.inline_editor.cancel_edit()
            
            print("👋 Cerrando TreeCreator v4 Pro")
            self.root.destroy()
            
        except Exception as e:
            print(f"❌ Error al cerrar aplicación: {e}")
            # Forzar cierre aunque haya errores
            self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación."""
        try:
            print("🚀 Iniciando TreeCreator v4 Pro...")
            self.root.mainloop()
        except Exception as e:
            print(f"❌ Error ejecutando aplicación: {e}")
            messagebox.showerror(
                "Error Crítico",
                f"Error ejecutando TreeCreator:\n{str(e)}"
            )
    
    # ==================== MÉTODOS PÚBLICOS ADICIONALES ====================
    
    def get_selected_node_id(self) -> Optional[str]:
        """Obtener ID del nodo seleccionado en el árbol."""
        if hasattr(self.tree_view, 'get_selected_node_id'):
            return self.tree_view.get_selected_node_id()
        return None
    
    def refresh_all_panels(self):
        """Refrescar todos los paneles."""
        try:
            if hasattr(self.tree_view, 'refresh'):
                self.tree_view.refresh()
            
            if hasattr(self, 'preview_container'):
                self.preview_container.refresh()
                
            print("✅ Todos los paneles refrescados")
            
        except Exception as e:
            print(f"❌ Error refrescando paneles: {e}")
    
    def show_statistics(self):
        """Mostrar estadísticas del proyecto."""
        try:
            if hasattr(self.tree_view, 'get_tree_statistics'):
                stats = self.tree_view.get_tree_statistics()
                
                stats_text = f"""📊 Estadísticas del Proyecto

📁 Total carpetas: {stats.get('total_folders', 0)}
📄 Total archivos: {stats.get('total_files', 0)}

Estados:
✅ Completados: {stats.get('completed', 0)}
⬜ En progreso: {stats.get('in_progress', 0)}
❌ Pendientes: {stats.get('pending', 0)}

🔢 Total elementos: {stats.get('total_folders', 0) + stats.get('total_files', 0)}
"""
                
                messagebox.showinfo("Estadísticas del Proyecto", stats_text)
            
        except Exception as e:
            print(f"❌ Error mostrando estadísticas: {e}")
            messagebox.showerror("Error", f"Error obteniendo estadísticas:\n{str(e)}")


# ==================== PUNTO DE ENTRADA ====================

def main():
    """Función principal de la aplicación."""
    try:
        # Crear y ejecutar aplicación
        app = MainWindow()
        app.run()
        
    except Exception as e:
        print(f"❌ Error crítico en main: {e}")
        
        # Mostrar error en interfaz si es posible
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana vacía
        
        messagebox.showerror(
            "Error Crítico - TreeCreator",
            f"Error crítico al inicializar TreeCreator:\n\n{str(e)}\n\n"
            f"Por favor, verifica que todos los módulos estén correctamente instalados."
        )
        
        root.destroy()


if __name__ == "__main__":
    main()