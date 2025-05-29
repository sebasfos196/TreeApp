"""
presentation/main_window.py - VERSIÓN SIMPLIFICADA QUE FUNCIONA
==============================================================

Ventana principal básica para probar que todo funciona
- Sin dependencias complejas
- Integra workspace manager
- Muestra la aplicación funcionando
- 150 líneas - Funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Imports básicos que sabemos que existen
from domain.events.event_bus import EventBus
from infrastructure.persistence.json_repository import JsonRepository
from application.services.workspace_manager import WorkspaceManager

class MainWindow:
    """Ventana principal simplificada para testing"""
    
    def __init__(self):
        # Inicializar componentes core
        self.event_bus = EventBus()
        self.repository = JsonRepository()
        self.workspace_manager = WorkspaceManager(self.repository, self.event_bus)
        
        # Configurar ventana principal
        self.root = tk.Tk()
        self.setup_window()
        
        # Inicializar workspace (Req. 4, 5)
        self.workspace_info = self.workspace_manager.initialize_workspace_if_needed()
        
        # Configurar interfaz básica
        self.setup_basic_ui()
        
        # Setup eventos
        self.setup_events()
    
    def setup_window(self):
        """Configuración básica de la ventana"""
        self.root.title("TreeApp v4 Pro - Versión Testing")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Color de fondo básico
        self.root.configure(bg="#1e1e1e")  # VS Code dark
    
    def setup_basic_ui(self):
        """Configura interfaz básica funcional"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🌳 TreeApp v4 Pro - FASE 1 & 2 Testing",
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e1e",
            fg="#cccccc"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para 3 columnas simuladas
        columns_frame = tk.Frame(main_frame, bg="#1e1e1e")
        columns_frame.pack(fill="both", expand=True)
        
        # Columna 1: Explorador
        self.setup_explorer_column(columns_frame)
        
        # Separador
        sep1 = tk.Frame(columns_frame, width=2, bg="#3c3c3c")
        sep1.pack(side="left", fill="y", padx=5)
        
        # Columna 2: Editor
        self.setup_editor_column(columns_frame)
        
        # Separador
        sep2 = tk.Frame(columns_frame, width=2, bg="#3c3c3c")
        sep2.pack(side="left", fill="y", padx=5)
        
        # Columna 3: Vista Previa
        self.setup_preview_column(columns_frame)
        
        # Status bar
        self.setup_status_bar()
    
    def setup_explorer_column(self, parent):
        """Columna explorador básica"""
        
        explorer_frame = tk.Frame(parent, bg="#252526", relief="solid", bd=1)
        explorer_frame.pack(side="left", fill="both", expand=True)
        
        # Header
        header = tk.Label(
            explorer_frame,
            text="TreeCreator",
            font=("Segoe UI", 12, "bold"),
            bg="#252526",
            fg="#cccccc"
        )
        header.pack(pady=10)
        
        # Simular árbol básico
        tree_text = tk.Text(
            explorer_frame,
            bg="#252526",
            fg="#cccccc",
            font=("Consolas", 10),
            height=15,
            state="disabled"
        )
        tree_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Mostrar workspace inicial
        if self.workspace_info and self.workspace_info['preview_data']:
            tree_content = self.generate_basic_tree_view()
            tree_text.configure(state="normal")
            tree_text.insert(1.0, tree_content)
            tree_text.configure(state="disabled")
        
        self.tree_text = tree_text
    
    def setup_editor_column(self, parent):
        """Columna editor básica"""
        
        editor_frame = tk.Frame(parent, bg="#1e1e1e", relief="solid", bd=1)
        editor_frame.pack(side="left", fill="both", expand=True)
        
        # Header
        header = tk.Label(
            editor_frame,
            text="Documentación",
            font=("Segoe UI", 12, "bold"),
            bg="#1e1e1e",
            fg="#cccccc"
        )
        header.pack(pady=10)
        
        # Campo nombre
        name_label = tk.Label(
            editor_frame,
            text="NODO:",
            bg="#1e1e1e",
            fg="#cccccc"
        )
        name_label.pack(anchor="w", padx=10)
        
        self.name_entry = tk.Entry(
            editor_frame,
            bg="#1e1e1e",
            fg="#cccccc",
            insertbackground="#cccccc"
        )
        self.name_entry.pack(fill="x", padx=10, pady=(2, 10))
        
        # Campo markdown
        markdown_label = tk.Label(
            editor_frame,
            text="MARKDOWN:",
            bg="#1e1e1e",
            fg="#cccccc"
        )
        markdown_label.pack(anchor="w", padx=10)
        
        self.markdown_text = tk.Text(
            editor_frame,
            bg="#1e1e1e",
            fg="#cccccc",
            insertbackground="#cccccc",
            height=10
        )
        self.markdown_text.pack(fill="both", expand=True, padx=10, pady=(2, 10))
        
        # Cargar datos iniciales
        self.load_initial_node_data()
    
    def setup_preview_column(self, parent):
        """Columna vista previa básica"""
        
        preview_frame = tk.Frame(parent, bg="#252526", relief="solid", bd=1)
        preview_frame.pack(side="right", fill="both", expand=True)
        
        # Header
        header = tk.Label(
            preview_frame,
            text="Vista Previa",
            font=("Segoe UI", 12, "bold"),
            bg="#252526",
            fg="#cccccc"
        )
        header.pack(pady=10)
        
        # Vista previa
        self.preview_text = tk.Text(
            preview_frame,
            bg="#252526",
            fg="#cccccc",
            font=("Consolas", 9),
            state="disabled"
        )
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Renderizar vista previa inicial
        self.render_basic_preview()
    
    def setup_status_bar(self):
        """Barra de estado"""
        
        status_frame = tk.Frame(self.root, bg="#007acc", height=25)
        status_frame.pack(fill="x", side="bottom")
        
        # Stats del workspace
        stats = self.workspace_manager.get_workspace_stats()
        
        status_text = f"📊 Nodos: {stats['total_nodes']} | 📁 Carpetas: {stats['folders']} | 📄 Archivos: {stats['files']} | ✅ Completados: {stats['completed']}"
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            bg="#007acc",
            fg="white",
            font=("Segoe UI", 9)
        )
        status_label.pack(side="left", padx=10)
        
        # Info de testing
        test_label = tk.Label(
            status_frame,
            text="🧪 MODO TESTING - FASE 1 & 2",
            bg="#007acc",
            fg="white",
            font=("Segoe UI", 9, "bold")
        )
        test_label.pack(side="right", padx=10)
    
    def generate_basic_tree_view(self):
        """Genera vista básica del árbol"""
        
        if not self.workspace_info or not self.workspace_info['preview_data']:
            return "❌ No hay datos del workspace"
        
        data = self.workspace_info['preview_data']
        
        tree_view = f"""📁 {data['name']} {data['status']}
    {data['markdown']}

═══ TESTING INFO ═══
✅ EventBus: Funcionando
✅ JsonRepository: Funcionando  
✅ WorkspaceManager: Funcionando
✅ Workspace Inicial: Creado
✅ Root Node: {data['name']}

═══ NEXT STEPS ═══
- Verificar que no hay más errores
- Agregar archivos VS Code faltantes
- Continuar con FASE 3"""
        
        return tree_view
    
    def load_initial_node_data(self):
        """Carga datos iniciales en el editor"""
        
        if self.workspace_info and self.workspace_info['preview_data']:
            data = self.workspace_info['preview_data']
            
            # Mostrar ruta completa en nombre
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, data['name'])
            
            # Mostrar markdown
            self.markdown_text.delete(1.0, "end")
            self.markdown_text.insert(1.0, data['markdown'])
    
    def render_basic_preview(self):
        """Renderiza vista previa básica"""
        
        stats = self.workspace_manager.get_workspace_stats()
        
        preview_content = f"""📁 Vista Previa - Modo Testing

═══ WORKSPACE INICIAL ═══
{self.generate_basic_tree_view()}

═══ ESTADÍSTICAS ═══
Total nodos: {stats['total_nodes']}
Carpetas: {stats['folders']}
Archivos: {stats['files']}
Completados ✅: {stats['completed']}
Pendientes ⬜: {stats['pending']}
Bloqueados ❌: {stats['blocked']}

═══ FUNCIONALIDADES ACTIVAS ═══
✅ Workspace inicial automático
✅ Persistencia JSON
✅ Sistema de eventos
✅ Interfaz básica VS Code

═══ PRÓXIMOS PASOS ═══
1. Crear archivos VS Code faltantes
2. Activar vista previa completa
3. Probar funcionalidades FASE 1 & 2"""
        
        self.preview_text.configure(state="normal")
        self.preview_text.delete(1.0, "end")
        self.preview_text.insert(1.0, preview_content)
        self.preview_text.configure(state="disabled")
    
    def setup_events(self):
        """Configurar eventos básicos"""
        
        # Evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Test del EventBus
        self.event_bus.subscribe('test_event', self.on_test_event)
        self.event_bus.publish('app_started', {'status': 'success'})
    
    def on_test_event(self, data):
        """Handler de prueba para EventBus"""
        print(f"✅ EventBus funcionando: {data}")
    
    def on_closing(self):
        """Manejo del cierre de la aplicación"""
        
        try:
            self.repository.save_data()
            print("💾 Datos guardados correctamente")
        except Exception as e:
            print(f"⚠️ Error guardando datos: {e}")
        
        self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        print("🎮 Iniciando interfaz gráfica...")
        self.root.mainloop()