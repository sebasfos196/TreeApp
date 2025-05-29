# presentation/views/panels/tree_panel/context_menu.py
"""
Menú contextual avanzado para TreeView con acciones específicas por tipo de nodo.
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional, Callable
from domain.node.node_entity import Node, NodeType, NodeStatus
from application.commands.node.create_node_command import CreateNodeCommand
from application.commands.command_bus import get_command_bus


class TreeContextMenu:
    """Menú contextual para TreeView con acciones avanzadas."""
    
    def __init__(self, tree_widget, node_repository, tree_view_instance=None, refresh_callback: Optional[Callable] = None):
        self.tree = tree_widget
        self.node_repository = node_repository
        self.tree_view = tree_view_instance  # Referencia al objeto TreeView
        self.refresh_callback = refresh_callback
        self.command_bus = get_command_bus()
        self.current_item = None
        self.current_node = None
        
        # Crear menú contextual
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Crear menú contextual con todas las opciones."""
        self.context_menu = tk.Menu(self.tree, tearoff=0, font=('Arial', 10))
        
        # Separar menús por tipo de nodo
        self._create_folder_menu()
        self._create_file_menu()
        self._create_common_menu()
    
    def _create_folder_menu(self):
        """Crear opciones específicas para carpetas."""
        # Opciones de creación
        create_menu = tk.Menu(self.context_menu, tearoff=0)
        create_menu.add_command(
            label="📁 Nueva Carpeta",
            command=self._create_new_folder,
            accelerator="Ctrl+Shift+N"
        )
        create_menu.add_command(
            label="📄 Nuevo Archivo",
            command=self._create_new_file,
            accelerator="Ctrl+N"
        )
        create_menu.add_separator()
        create_menu.add_command(
            label="🐍 Archivo Python",
            command=lambda: self._create_file_with_extension('.py')
        )
        create_menu.add_command(
            label="📝 Archivo Markdown",
            command=lambda: self._create_file_with_extension('.md')
        )
        create_menu.add_command(
            label="⚙️ Archivo JSON",
            command=lambda: self._create_file_with_extension('.json')
        )
        
        self.folder_menu_items = [
            ("➕ Nuevo", create_menu),
            None,  # Separador
        ]
    
    def _create_file_menu(self):
        """Crear opciones específicas para archivos."""
        self.file_menu_items = [
            ("📋 Copiar nombre", self._copy_name),
            ("📋 Copiar ruta", self._copy_path),
            None,  # Separador
        ]
    
    def _create_common_menu(self):
        """Crear opciones comunes para todos los nodos."""
        # Menú de estados
        status_menu = tk.Menu(self.context_menu, tearoff=0)
        status_menu.add_command(
            label="✅ Completado",
            command=lambda: self._change_status(NodeStatus.COMPLETED)
        )
        status_menu.add_command(
            label="⬜ En Progreso",
            command=lambda: self._change_status(NodeStatus.IN_PROGRESS)
        )
        status_menu.add_command(
            label="❌ Pendiente",
            command=lambda: self._change_status(NodeStatus.PENDING)
        )
        status_menu.add_command(
            label="🔘 Sin Estado",
            command=lambda: self._change_status(NodeStatus.NONE)
        )
        
        self.common_menu_items = [
            ("✏️ Renombrar", self._rename_node),
            ("📊 Cambiar Estado", status_menu),
            None,  # Separador
            ("📂 Expandir Todo", self._expand_all),
            ("📁 Colapsar Todo", self._collapse_all),
            None,  # Separador
            ("📄 Propiedades", self._show_properties),
            None,  # Separador
            ("🗑️ Eliminar", self._delete_node),
        ]
    
    def show_menu(self, event, item_id: str):
        """Mostrar menú contextual para un item específico."""
        if not item_id:
            return
        
        self.current_item = item_id
        self.current_node = self.node_repository.find_by_id(item_id)
        
        if not self.current_node:
            return
        
        # Limpiar menú anterior
        self.context_menu.delete(0, tk.END)
        
        # Agregar opciones según el tipo de nodo
        if self.current_node.is_folder():
            self._add_menu_items(self.folder_menu_items)
        else:
            self._add_menu_items(self.file_menu_items)
        
        # Agregar opciones comunes
        self._add_menu_items(self.common_menu_items)
        
        # Mostrar menú en la posición del cursor
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _add_menu_items(self, items):
        """Agregar items al menú contextual."""
        for item in items:
            if item is None:
                # Separador
                self.context_menu.add_separator()
            elif isinstance(item[1], tk.Menu):
                # Submenú
                self.context_menu.add_cascade(label=item[0], menu=item[1])
            else:
                # Comando normal
                self.context_menu.add_command(label=item[0], command=item[1])
    
    def _create_new_folder(self):
        """Crear nueva carpeta en el nodo actual."""
        if not self.current_node or not self.current_node.is_folder():
            return
        
        name = simpledialog.askstring(
            "Nueva Carpeta",
            "Nombre de la nueva carpeta:",
            initialvalue="Nueva Carpeta"
        )
        
        if name and name.strip():
            command = CreateNodeCommand(
                name=name.strip(),
                node_type=NodeType.FOLDER,
                parent_id=self.current_item,
                markdown_short=f"# {name.strip()}",
                explanation="Carpeta creada desde menú contextual"
            )
            
            result = self.command_bus.execute(command)
            if result.success:
                self._refresh_view()
                print(f"✅ Carpeta creada: {result.data.name}")
            else:
                messagebox.showerror("Error", f"Error creando carpeta:\n{result.error}")
    
    def _create_new_file(self):
        """Crear nuevo archivo en el nodo actual."""
        if not self.current_node or not self.current_node.is_folder():
            return
        
        name = simpledialog.askstring(
            "Nuevo Archivo",
            "Nombre del nuevo archivo:",
            initialvalue="nuevo_archivo.txt"
        )
        
        if name and name.strip():
            command = CreateNodeCommand(
                name=name.strip(),
                node_type=NodeType.FILE,
                parent_id=self.current_item,
                markdown_short=f"# {name.strip()}",
                explanation="Archivo creado desde menú contextual",
                code=f"# Contenido de {name.strip()}\n"
            )
            
            result = self.command_bus.execute(command)
            if result.success:
                self._refresh_view()
                print(f"✅ Archivo creado: {result.data.name}")
            else:
                messagebox.showerror("Error", f"Error creando archivo:\n{result.error}")
    
    def _create_file_with_extension(self, extension: str):
        """Crear archivo con extensión específica."""
        if not self.current_node or not self.current_node.is_folder():
            return
        
        # Plantillas por extensión
        templates = {
            '.py': {
                'name': f'nuevo_archivo{extension}',
                'code': '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n"""\nNuevo archivo Python\n"""\n\nif __name__ == "__main__":\n    print("Hola, TreeApp!")\n'
            },
            '.md': {
                'name': f'nuevo_documento{extension}',
                'code': '# Nuevo Documento\n\n## Descripción\n\nEste es un nuevo documento markdown.\n\n## Contenido\n\n- Punto 1\n- Punto 2\n- Punto 3\n'
            },
            '.json': {
                'name': f'nuevo_config{extension}',
                'code': '{\n  "name": "nuevo_config",\n  "version": "1.0.0",\n  "description": "Archivo de configuración",\n  "settings": {\n    "enabled": true,\n    "debug": false\n  }\n}\n'
            }
        }
        
        template = templates.get(extension, {'name': f'nuevo_archivo{extension}', 'code': ''})
        
        name = simpledialog.askstring(
            f"Nuevo Archivo {extension.upper()}",
            f"Nombre del archivo {extension}:",
            initialvalue=template['name']
        )
        
        if name and name.strip():
            if not name.endswith(extension):
                name += extension
            
            command = CreateNodeCommand(
                name=name,
                node_type=NodeType.FILE,
                parent_id=self.current_item,
                markdown_short=f"# {name}",
                explanation=f"Archivo {extension} creado desde menú contextual",
                code=template['code']
            )
            
            result = self.command_bus.execute(command)
            if result.success:
                self._refresh_view()
                print(f"✅ Archivo {extension} creado: {result.data.name}")
            else:
                messagebox.showerror("Error", f"Error creando archivo:\n{result.error}")
    
    def _rename_node(self):
        """Renombrar nodo actual."""
        if not self.current_node:
            return
        
        new_name = simpledialog.askstring(
            "Renombrar",
            f"Nuevo nombre para '{self.current_node.name}':",
            initialvalue=self.current_node.name
        )
        
        if new_name and new_name.strip() and new_name.strip() != self.current_node.name:
            self.current_node.name = new_name.strip()
            self.current_node.update_modified()
            
            self.node_repository.save(self.current_node)
            self._refresh_view()
            print(f"✅ Renombrado a: {new_name}")
    
    def _change_status(self, new_status: NodeStatus):
        """Cambiar estado del nodo."""
        if not self.current_node:
            return
        
        self.current_node.status = new_status
        self.current_node.update_modified()
        
        self.node_repository.save(self.current_node)
        self._refresh_view()
        print(f"✅ Estado cambiado a: {new_status.value}")
    
    def _copy_name(self):
        """Copiar nombre del nodo al portapapeles."""
        if not self.current_node:
            return
        
        self.tree.clipboard_clear()
        self.tree.clipboard_append(self.current_node.name)
        print(f"📋 Nombre copiado: {self.current_node.name}")
    
    def _copy_path(self):
        """Copiar ruta completa del nodo al portapapeles."""
        if not self.current_node:
            return
        
        path = self._get_node_path(self.current_node)
        self.tree.clipboard_clear()
        self.tree.clipboard_append(path)
        print(f"📋 Ruta copiada: {path}")
    
    def _get_node_path(self, node: Node) -> str:
        """Obtener ruta completa de un nodo."""
        path_parts = [node.name]
        current = node
        
        while current.parent_id:
            parent = self.node_repository.find_by_id(current.parent_id)
            if parent:
                path_parts.insert(0, parent.name)
                current = parent
            else:
                break
        
        return "/" + "/".join(path_parts)
    
    def _expand_all(self):
        """Expandir todos los nodos."""
        if self.tree_view:
            self.tree_view.expand_all()
        else:
            print("📂 Expandir todo - TreeView no disponible")
    
    def _collapse_all(self):
        """Colapsar todos los nodos."""
        if self.tree_view:
            self.tree_view.collapse_all()
        else:
            print("📁 Colapsar todo - TreeView no disponible")
    
    def _show_properties(self):
        """Mostrar propiedades del nodo."""
        if not self.current_node:
            return
        
        # Crear ventana de propiedades
        props_window = tk.Toplevel(self.tree)
        props_window.title(f"Propiedades - {self.current_node.name}")
        props_window.geometry("400x300")
        props_window.resizable(False, False)
        
        # Información del nodo
        info_frame = tk.Frame(props_window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        props = [
            ("Nombre:", self.current_node.name),
            ("Tipo:", "📁 Carpeta" if self.current_node.is_folder() else "📄 Archivo"),
            ("Estado:", self.current_node.status.value or "Sin estado"),
            ("ID:", self.current_node.node_id),
            ("Ruta:", self._get_node_path(self.current_node)),
            ("Creado:", self.current_node.created),
            ("Modificado:", self.current_node.modified),
        ]
        
        for i, (label, value) in enumerate(props):
            tk.Label(info_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', pady=2
            )
            tk.Label(info_frame, text=str(value), font=('Arial', 10)).grid(
                row=i, column=1, sticky='w', padx=(10, 0), pady=2
            )
        
        # Botón cerrar
        tk.Button(
            props_window,
            text="Cerrar",
            command=props_window.destroy,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def _delete_node(self):
        """Eliminar nodo actual."""
        if not self.current_node:
            return
        
        # Confirmar eliminación
        node_type = "carpeta" if self.current_node.is_folder() else "archivo"
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar {node_type} '{self.current_node.name}'?\n\n"
            f"{'⚠️ Esta acción eliminará todo el contenido' if self.current_node.is_folder() else '📄 Esta acción es permanente'}",
            icon='warning'
        )
        
        if confirm:
            success = self.node_repository.delete(self.current_item)
            if success:
                self._refresh_view()
                print(f"✅ Eliminado: {self.current_node.name}")
            else:
                messagebox.showerror("Error", f"Error eliminando {node_type}")
    
    def _refresh_view(self):
        """Refrescar la vista del árbol."""
        if self.refresh_callback:
            self.refresh_callback()
    
    def bind_to_tree(self):
        """Vincular menú contextual al TreeView."""
        def show_context_menu(event):
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self.show_menu(event, item)
        
        self.tree.bind('<Button-3>', show_context_menu)  # Click derecho
        
        # Atajos de teclado opcionales
        self.tree.bind('<Delete>', lambda e: self._delete_node())  # Tecla Delete
        self.tree.bind('<F2>', lambda e: self._rename_node())      # F2 para renombrar