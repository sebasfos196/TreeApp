# presentation/views/panels/editor_panel/editor_container.py
"""
Panel de Documentación con 4 campos editables, guardado automático y campos flexibles.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from domain.node.node_entity import Node


class EditorContainer:
    """Contenedor principal del panel de documentación con 4 campos."""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.current_node: Optional[Node] = None
        self.auto_save_delay = 500  # ms después del último cambio
        self.auto_save_timer = None
        self.tree_update_callback = None  # Callback para actualizar TreeView
        self._loading = False  # Flag para evitar callbacks durante carga
        self._setup_ui()
    
    def set_tree_update_callback(self, callback):
        """Establecer callback para actualizar el TreeView cuando cambie el nombre."""
        self.tree_update_callback = callback
    
    def _setup_ui(self):
        """Configurar interfaz del panel de documentación."""
        # Frame principal que ocupa todo el espacio con separación pequeña
        self.main_frame = tk.Frame(self.parent_frame, bg='#ecf0f1')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Título principal
        self._setup_header()
        
        # PanedWindow principal para campos redimensionables
        self.main_paned = tk.PanedWindow(
            self.main_frame, 
            orient=tk.VERTICAL,
            sashwidth=3,
            relief=tk.FLAT,
            bg='#bdc3c7',
            sashrelief=tk.RAISED
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, pady=(0, 2))
        
        # Los 4 campos de documentación en PanedWindows
        self._setup_name_field()
        self._setup_markdown_field()
        self._setup_notes_field()
        self._setup_code_field()
    
    def _setup_header(self):
        """Configurar encabezado del panel."""
        header_frame = tk.Frame(self.main_frame, bg='#ecf0f1')
        header_frame.pack(fill=tk.X, padx=2, pady=(2, 5))
        
        # Título principal
        title_label = tk.Label(
            header_frame,
            text="📝 Documentación",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(anchor="w", padx=8)
    
    def _setup_name_field(self):
        """Campo 1: Nodo."""
        frame = self._create_field_frame("NODO", minsize=60)
        
        # Entry para el nombre
        self.name_entry = tk.Entry(
            frame,
            font=('Arial', 11),
            relief=tk.FLAT,
            bg='#ffffff',
            fg='#2c3e50',
            insertbackground='#3498db',
            bd=0
        )
        self.name_entry.pack(fill=tk.X, padx=0, pady=0, ipady=8)
        
        # EVENTOS MÚLTIPLES PARA CAPTURAR CAMBIOS EN TIEMPO REAL
        self.name_entry.bind('<KeyRelease>', self._on_name_change)      # Cada tecla
        self.name_entry.bind('<KeyPress>', self._on_name_change_delayed) # Antes de escribir
        self.name_entry.bind('<FocusOut>', self._on_name_change)        # Al perder foco
        self.name_entry.bind('<Return>', self._on_name_change)          # Enter
        self.name_entry.bind('<Tab>', self._on_name_change)             # Tab
        
        # Trace para capturar TODOS los cambios (incluso pegado)
        self.name_var = tk.StringVar()
        self.name_entry.config(textvariable=self.name_var)
        self.name_var.trace('w', self._on_name_trace)  # Trace en la variable
    
    def _setup_markdown_field(self):
        """Campo 2: Markdown (2 líneas)."""
        frame = self._create_field_frame("MARKDOWN", minsize=70)
        
        # Text widget pequeño para markdown
        self.markdown_text = tk.Text(
            frame,
            height=2,
            font=('Consolas', 10),
            relief=tk.FLAT,
            bg='#ffffff',
            fg='#2c3e50',
            insertbackground='#3498db',
            wrap=tk.WORD,
            bd=0
        )
        self.markdown_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.markdown_text.bind('<KeyRelease>', self._on_markdown_change)
    
    def _setup_notes_field(self):
        """Campo 3: Notas Técnicas."""
        frame = self._create_field_frame("NOTAS TECNICAS", minsize=120)
        
        # Frame interno para texto y scrollbar
        text_container = tk.Frame(frame, bg='#ffffff')
        text_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.notes_text = tk.Text(
            text_container,
            font=('Arial', 10),
            relief=tk.FLAT,
            bg='#ffffff',
            fg='#2c3e50',
            insertbackground='#3498db',
            wrap=tk.WORD,
            bd=0
        )
        
        # Scrollbar para notas
        notes_scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notes_text.bind('<KeyRelease>', self._on_notes_change)
    
    def _setup_code_field(self):
        """Campo 4: Código con numeración de líneas."""
        frame = self._create_field_frame("CODIGO", minsize=180)
        
        # Frame interno para código
        code_container = tk.Frame(frame, bg='#ffffff')
        code_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Frame para numeración + código
        code_frame = tk.Frame(code_container, bg='#ffffff')
        code_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget para numeración de líneas
        self.line_numbers = tk.Text(
            code_frame,
            width=4,
            font=('Consolas', 9),
            relief=tk.FLAT,
            bg='#f8f9fa',
            fg='#7f8c8d',
            bd=0,
            state=tk.DISABLED,
            wrap=tk.NONE
        )
        
        # Text widget para código
        self.code_text = tk.Text(
            code_frame,
            font=('Consolas', 9),
            relief=tk.FLAT,
            bg='#ffffff',
            fg='#2c3e50',
            insertbackground='#3498db',
            wrap=tk.NONE,
            bd=0
        )
        
        # Scrollbars
        code_scroll_v = ttk.Scrollbar(code_frame, orient="vertical")
        code_scroll_h = ttk.Scrollbar(code_container, orient="horizontal")
        
        # Configurar scrolling sincronizado
        def scroll_both(*args):
            self.line_numbers.yview(*args)
            self.code_text.yview(*args)
        
        code_scroll_v.config(command=scroll_both)
        code_scroll_h.config(command=self.code_text.xview)
        
        self.code_text.config(yscrollcommand=code_scroll_v.set, xscrollcommand=code_scroll_h.set)
        self.line_numbers.config(yscrollcommand=code_scroll_v.set)
        
        # Layout del código
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        code_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Eventos
        self.code_text.bind('<KeyRelease>', self._on_code_change)
        self.code_text.bind('<Button-1>', self._update_line_numbers)
        self.code_text.bind('<MouseWheel>', self._on_code_scroll)
        
        # Botón especial para agregar estructura
        btn_frame = tk.Frame(frame, bg='#ecf0f1')
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(
            btn_frame, 
            text="➕ Agregar al Proyecto", 
            command=self._add_to_project,
            bg='#f39c12', 
            fg='white', 
            font=('Arial', 9, 'bold'), 
            relief=tk.FLAT,
            pady=5
        ).pack(side=tk.RIGHT)
    
    def _create_field_frame(self, title: str, minsize: int) -> tk.Frame:
        """Crear frame flexible para un campo dentro del PanedWindow."""
        # Frame principal del campo
        field_frame = tk.Frame(self.main_frame, bg='#ecf0f1')
        
        # Header compacto
        header_frame = tk.Frame(field_frame, bg='#bdc3c7', height=25)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Título compacto
        title_label = tk.Label(
            header_frame,
            text=title,
            font=('Arial', 9, 'bold'),
            bg='#bdc3c7',
            fg='#2c3e50'
        )
        title_label.pack(anchor="w", padx=8, pady=4)
        
        # Frame de contenido
        content_frame = tk.Frame(field_frame, bg='#ffffff')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Agregar al PanedWindow con tamaño mínimo
        self.main_paned.add(field_frame, minsize=minsize)
        
        return content_frame
    
    def _on_code_scroll(self, event):
        """Manejar scroll en el código."""
        self._update_line_numbers()
    
    def _update_line_numbers(self, event=None):
        """Actualizar numeración de líneas."""
        # Obtener contenido del código
        content = self.code_text.get('1.0', tk.END)
        lines = content.split('\n')
        
        # Generar números de línea
        line_numbers_content = '\n'.join(str(i) for i in range(1, len(lines)))
        
        # Actualizar widget de numeración
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_content)
        self.line_numbers.config(state=tk.DISABLED)
    
    # ==================== CARGA Y LIMPIEZA ====================
    
    def load_node(self, node: Node):
        """Cargar un nodo en el editor."""
        self.current_node = node
        
        # Cargar datos en los campos SIN activar callbacks
        self._loading = True
        
        # Cargar nombre usando StringVar para evitar eventos
        self.name_var.set(node.name)
        
        self.markdown_text.delete('1.0', tk.END)
        self.markdown_text.insert('1.0', node.markdown_short)
        
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert('1.0', node.explanation)
        
        self.code_text.delete('1.0', tk.END)
        self.code_text.insert('1.0', node.code)
        
        self._update_line_numbers()
        
        # Activar callbacks después de cargar
        self._loading = False
        
        print(f"📝 Nodo cargado en editor: {node.name}")
    
    def clear_editor(self):
        """Limpiar el editor."""
        self.current_node = None
        self._loading = True
        
        self.name_var.set("")
        self.markdown_text.delete('1.0', tk.END)
        self.notes_text.delete('1.0', tk.END)
        self.code_text.delete('1.0', tk.END)
        
        self._update_line_numbers()
        self._loading = False
    
    # ==================== AUTO-SAVE EN TIEMPO REAL ====================
    
    def _schedule_auto_save(self):
        """Programar guardado automático."""
        if self._loading:
            return
            
        if self.auto_save_timer:
            self.parent_frame.after_cancel(self.auto_save_timer)
        
        self.auto_save_timer = self.parent_frame.after(self.auto_save_delay, self._auto_save)
    
    def _auto_save(self):
        """Guardar automáticamente."""
        if not self.current_node or self._loading:
            return
        
        try:
            # Actualizar nodo con los cambios
            self.current_node.name = self.name_var.get()
            self.current_node.markdown_short = self.markdown_text.get('1.0', tk.END).strip()
            self.current_node.explanation = self.notes_text.get('1.0', tk.END).strip()
            self.current_node.code = self.code_text.get('1.0', tk.END).strip()
            self.current_node.update_modified()
            
            # Guardar en repositorio
            self.node_repository.save(self.current_node)
            print(f"💾 Auto-guardado: {self.current_node.name}")
            
        except Exception as e:
            print(f"❌ Error en auto-guardado: {e}")
    
    # ==================== CALLBACKS DE CAMBIOS MEJORADOS ====================
    
    def _on_name_trace(self, *args):
        """Callback principal para trace de StringVar - TIEMPO REAL."""
        if self._loading or not self.current_node:
            return
        
        new_name = self.name_var.get()
        old_name = self.current_node.name
        
        # Solo procesar si realmente cambió
        if new_name != old_name:
            print(f"🔄 Cambio en tiempo real: '{old_name}' → '{new_name}'")
            
            # ACTUALIZAR TREEVIEW INMEDIATAMENTE
            if self.tree_update_callback:
                self.tree_update_callback(self.current_node.node_id, new_name)
            
            # Programar auto-save
            self._schedule_auto_save()
    
    def _on_name_change(self, event=None):
        """Callback adicional para eventos del Entry."""
        # El trace ya maneja todo, pero mantenemos por si acaso
        pass
    
    def _on_name_change_delayed(self, event=None):
        """Callback para capturar cambios antes de escribir."""
        # Programar actualización para después del evento de escritura
        if not self._loading and self.current_node:
            self.parent_frame.after(10, self._on_name_trace)
    
    def _on_markdown_change(self, event=None):
        """Callback cuando cambia el markdown."""
        if self.current_node and not self._loading:
            self._schedule_auto_save()
    
    def _on_notes_change(self, event=None):
        """Callback cuando cambian las notas."""
        if self.current_node and not self._loading:
            self._schedule_auto_save()
    
    def _on_code_change(self, event=None):
        """Callback cuando cambia el código."""
        self._update_line_numbers()
        if self.current_node and not self._loading:
            self._schedule_auto_save()
    
    # ==================== AGREGAR AL PROYECTO ====================
    
    def _add_to_project(self):
        """Agregar estructura desde código al proyecto."""
        code_content = self.code_text.get('1.0', tk.END).strip()
        
        if not code_content:
            messagebox.showwarning("Sin contenido", "No hay código para agregar al proyecto")
            return
        
        print("➕ Procesando código para agregar al proyecto...")
        print(f"Código a procesar:\n{code_content}")
        
        # TODO: Implementar parser y creación de estructura
        messagebox.showinfo("Próximamente", 
                          f"Funcionalidad para agregar estructura al proyecto:\n\n"
                          f"Líneas de código: {len(code_content.splitlines())}\n"
                          f"Caracteres: {len(code_content)}")
        
        # Aquí se implementará el parser de estructura y creación de nodos