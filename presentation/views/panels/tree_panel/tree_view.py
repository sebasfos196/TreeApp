# presentation/views/panels/tree_panel/tree_view.py
"""
Vista mejorada del explorador de árbol con iconos flat y integración drag & drop.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List
from domain.node.node_entity import Node, NodeType, NodeStatus
from application.commands.node.create_node_command import CreateNodeCommand
from application.commands.command_bus import get_command_bus
from .drag_drop import TreeDragDrop


class FlatIcons:
    """Iconos flat modernos para el explorador."""
    
    # Iconos principales
    FOLDER_CLOSED = "📁"
    FOLDER_OPEN = "📂" 
    FILE = "📄"
    
    # Iconos por tipo de archivo
    FILE_TYPES = {
        '.py': '🐍',
        '.js': '📜',
        '.html': '🌐',
        '.css': '🎨',
        '.md': '📝',
        '.json': '⚙️',
        '.txt': '📄',
        '.pdf': '📑',
        '.png': '🖼️',
        '.jpg': '🖼️',
        '.gif': '🖼️',
        '.zip': '📦',
        '.exe': '⚡',
        '.bat': '⚡',
        '.sh': '⚡'
    }
    
    @classmethod
    def get_file_icon(cls, filename: str) -> str:
        """Obtener icono específico según extensión del archivo."""
        if not filename:
            return cls.FILE
        
        # Obtener extensión
        parts = filename.split('.')
        if len(parts) > 1:
            ext = '.' + parts[-1].lower()
            return cls.FILE_TYPES.get(ext, cls.FILE)
        
        return cls.FILE


class TreeView:
    """Vista del explorador de árbol con iconos flat y drag & drop."""
    
    def __init__(self, parent_frame, node_repository):
        self.parent_frame = parent_frame
        self.node_repository = node_repository
        self.command_bus = get_command_bus()
        self._selected_node_id: Optional[str] = None
        self._selection_callback = None
        self._setup_ui()
        self._setup_drag_drop()
        self._load_nodes()
    
    def _setup_ui(self):
        """Configurar interfaz del TreeView."""
        # Frame contenedor
        self.container = tk.Frame(self.parent_frame)
        self.container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título con estilo moderno
        self._setup_header()
        
        # Botones de acción con iconos flat
        self._setup_buttons()
        
        # TreeView con scrollbar
        self._setup_treeview()
        
        # Eventos
        self._setup_events()
    
    def _setup_header(self):
        """Configurar encabezado moderno."""
        header_frame = tk.Frame(self.container, bg='#2c3e50', height=35)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        header_frame.pack_propagate(False)
        
        # Título con icono
        title_label = tk.Label(
            header_frame,
            text="🌳 TreeCreator",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(expand=True)
    
    def _setup_buttons(self):
        """Configurar botones de acción con solo iconos."""
        button_frame = tk.Frame(self.container, bg='#f8f9fa', height=35)
        button_frame.pack(fill=tk.X, pady=(0, 8))
        button_frame.pack_propagate(False)
        
        # Estilo de botones minimalista - solo iconos
        button_style = {
            'font': ('Arial', 16),
            'relief': tk.FLAT,
            'bd': 0,
            'width': 2,
            'height': 1,
            'cursor': 'hand2',
            'bg': '#f8f9fa',
            'activebackground': '#e9ecef'
        }
        
        # Botón crear carpeta
        self.btn_new_folder = tk.Button(
            button_frame,
            text="📁",
            command=self._create_folder,
            fg='#3498db',
            activeforeground='#2980b9',
            **button_style
        )
        self.btn_new_folder.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Botón crear archivo
        self.btn_new_file = tk.Button(
            button_frame,
            text="📄",
            command=self._create_file,
            fg='#27ae60',
            activeforeground='#229954',
            **button_style
        )
        self.btn_new_file.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Botón eliminar
        self.btn_delete = tk.Button(
            button_frame,
            text="🗑️",
            command=self._delete_node,
            fg='#e74c3c',
            activeforeground='#c0392b',
            **button_style
        )
        self.btn_delete.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Botón refrescar
        self.btn_refresh = tk.Button(
            button_frame,
            text="🔄",
            command=self._load_nodes,
            fg='#f39c12',
            activeforeground='#e67e22',
            **button_style
        )
        self.btn_refresh.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Tooltips para los botones
        self._create_tooltip(self.btn_new_folder, "Nueva Carpeta (Ctrl+Shift+N)")
        self._create_tooltip(self.btn_new_file, "Nuevo Archivo (Ctrl+N)")
        self._create_tooltip(self.btn_delete, "Eliminar (Del)")
        self._create_tooltip(self.btn_refresh, "Refrescar (F5)")
    
    def _create_tooltip(self, widget, text):
        """Crear tooltip para un widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#333333", 
                           foreground="white", font=('Arial', 9), relief=tk.SOLID, borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _setup_treeview(self):
        """Configurar TreeView principal con estilo moderno."""
        # Frame para TreeView y scrollbar
        tree_frame = tk.Frame(self.container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView con estilo
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('status',),
            show='tree headings',
            height=15
        )
        
        # Configurar columnas
        self.tree.heading('#0', text='📁 Nombre', anchor='w')
        self.tree.heading('status', text='📊 Estado', anchor='center')
        self.tree.column('#0', width=220, minwidth=150, anchor='w')
        self.tree.column('status', width=80, minwidth=60, anchor='center')
        
        # Configurar estilos de filas
        self.tree.tag_configure('folder', foreground='#2c3e50', font=('Arial', 10, 'bold'))
        self.tree.tag_configure('file', foreground='#34495e', font=('Arial', 10))
        self.tree.tag_configure('completed', background='#d5f4e6')
        self.tree.tag_configure('pending', background='#fadbd8')
        self.tree.tag_configure('in_progress', background='#fdeaa7')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_drag_drop(self):
        """Configurar sistema de drag & drop."""
        self.drag_drop = TreeDragDrop(
            self.tree, 
            self.node_repository,
            on_move_callback=self._on_node_moved
        )
    
    def _setup_events(self):
        """Configurar eventos del TreeView."""
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Configurar menú contextual
        from .context_menu import TreeContextMenu
        self.context_menu = TreeContextMenu(
            self.tree, 
            self.node_repository,
            tree_view_instance=self,  # Pasar referencia a sí mismo
            refresh_callback=self._load_nodes
        )
        self.context_menu.bind_to_tree()
        
        # Hover effects para botones
        self._setup_button_hover_effects()
    
    def _setup_button_hover_effects(self):
        """Configurar efectos hover para botones."""
        buttons = [
            (self.btn_new_folder, '#3498db', '#2980b9'),
            (self.btn_new_file, '#27ae60', '#229954'),
            (self.btn_delete, '#e74c3c', '#c0392b'),
            (self.btn_refresh, '#f39c12', '#e67e22')
        ]
        
        for btn, normal_color, hover_color in buttons:
            btn.bind('<Enter>', lambda e, btn=btn, color=hover_color: btn.config(bg=color))
            btn.bind('<Leave>', lambda e, btn=btn, color=normal_color: btn.config(bg=color))
    
    def _load_nodes(self):
        """Cargar nodos en el TreeView con iconos flat."""
        # Limpiar TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener nodos raíz
        root_nodes = self.node_repository.find_roots()
        
        # Si no hay nodos, crear uno por defecto
        if not root_nodes:
            self._create_default_root()
            root_nodes = self.node_repository.find_roots()
        
        # Cargar nodos raíz
        for node in root_nodes:
            self._insert_node_recursive(node, '')
    
    def _create_default_root(self):
        """Crear nodo raíz por defecto."""
        command = CreateNodeCommand(
            name="Mi Proyecto",
            node_type=NodeType.FOLDER,
            markdown_short="# Mi Proyecto",
            explanation="Carpeta raíz del proyecto",
            status=NodeStatus.IN_PROGRESS
        )
        self.command_bus.execute(command)
    
    def _insert_node_recursive(self, node: Node, parent_id: str):
        """Insertar nodo y sus hijos recursivamente con iconos flat."""
        # Determinar icono según tipo y estado
        if node.is_folder():
            icon = FlatIcons.FOLDER_OPEN
        else:
            icon = FlatIcons.get_file_icon(node.name)
        
        display_name = f"{icon} {node.name}"
        
        # Determinar tags para estilo
        tags = []
        if node.is_folder():
            tags.append('folder')
        else:
            tags.append('file')
        
        # Agregar tag de estado
        if node.status == NodeStatus.COMPLETED:
            tags.append('completed')
        elif node.status == NodeStatus.PENDING:
            tags.append('pending')
        elif node.status == NodeStatus.IN_PROGRESS:
            tags.append('in_progress')
        
        # Insertar nodo
        item_id = self.tree.insert(
            parent_id,
            'end',
            iid=node.node_id,
            text=display_name,
            values=(node.status.value,),
            open=node.is_folder(),  # Abrir carpetas por defecto
            tags=tags
        )
        
        # Insertar hijos
        if node.is_folder():
            children = self.node_repository.find_children(node.node_id)
            # Ordenar: carpetas primero, luego archivos
            children.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for child in children:
                self._insert_node_recursive(child, node.node_id)
    
    def _on_select(self, event):
        """Manejar selección de nodo."""
        selection = self.tree.selection()
        if selection:
            self._selected_node_id = selection[0]
            print(f"🔍 Nodo seleccionado: {self._selected_node_id}")
            
            # Notificar callback externo si existe
            if self._selection_callback:
                self._selection_callback(self._selected_node_id)
        else:
            self._selected_node_id = None
            if self._selection_callback:
                self._selection_callback(None)
    
    def set_selection_callback(self, callback):
        """Establecer callback para cuando se selecciona un nodo."""
        self._selection_callback = callback
    
    def _on_double_click(self, event):
        """Manejar doble click - edición inline o expandir/contraer."""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        node = self.node_repository.find_by_id(item)
        if not node:
            return
        
        # Para carpetas: expandir/contraer + edición inline opcional
        if node.is_folder():
            # Verificar si el click fue en el texto (no en el icono de expansión)
            region = self.tree.identify_region(event.x, event.y)
            if region == "cell":
                # Edición inline
                self._start_inline_edit(item, node)
            else:
                # Alternar estado de apertura
                current_state = self.tree.item(item, 'open')
                self.tree.item(item, open=not current_state)
                
                # Actualizar icono
                new_icon = FlatIcons.FOLDER_OPEN if not current_state else FlatIcons.FOLDER_CLOSED
                current_text = self.tree.item(item, 'text')
                new_text = f"{new_icon}{current_text[1:]}"
                self.tree.item(item, text=new_text)
        else:
            # Para archivos: solo edición inline
            self._start_inline_edit(item, node)
    
    def _start_inline_edit(self, item, node):
        """Iniciar edición inline del nombre del nodo."""
        # Obtener posición del item
        bbox = self.tree.bbox(item, '#0')
        if not bbox:
            return
        
        # Crear Entry temporal para edición
        x, y, width, height = bbox
        
        # Ajustar para que no cubra el icono
        icon_width = 25  # Ancho aproximado del icono
        x += icon_width
        width -= icon_width
        
        self.edit_entry = tk.Entry(
            self.tree,
            font=('Arial', 10),
            bg='#ffffff',
            fg='#2c3e50',
            relief=tk.SOLID,
            bd=1
        )
        
        # Posicionar Entry sobre el item
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        
        # Configurar contenido inicial
        self.edit_entry.insert(0, node.name)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # Guardar referencia al item y nodo
        self.editing_item = item
        self.editing_node = node
        
        # Eventos para finalizar edición
        self.edit_entry.bind('<Return>', self._finish_inline_edit)
        self.edit_entry.bind('<Escape>', self._cancel_inline_edit)
        self.edit_entry.bind('<FocusOut>', self._finish_inline_edit)
    
    def _finish_inline_edit(self, event=None):
        """Finalizar edición inline y actualizar nodo."""
        if not hasattr(self, 'edit_entry') or not self.edit_entry:
            return
        
        new_name = self.edit_entry.get().strip()
        
        # Validar nombre
        if new_name and new_name != self.editing_node.name:
            if self._validate_inline_name(new_name):
                # Actualizar nodo
                old_name = self.editing_node.name
                self.editing_node.name = new_name
                self.editing_node.update_modified()
                
                # Guardar en repositorio
                self.node_repository.save(self.editing_node)
                
                # Actualizar display en TreeView
                self.update_node_display(self.editing_item, new_name)
                
                # Notificar cambio al editor si hay callback
                if self._selection_callback and self.editing_item == self._selected_node_id:
                    # Recargar en el editor
                    self._selection_callback(self.editing_item)
                
                print(f"✏️ Renombrado inline: {old_name} → {new_name}")
        
        # Limpiar edición
        self._cleanup_inline_edit()
    
    def _cancel_inline_edit(self, event=None):
        """Cancelar edición inline."""
        self._cleanup_inline_edit()
    
    def _cleanup_inline_edit(self):
        """Limpiar componentes de edición inline."""
        if hasattr(self, 'edit_entry') and self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        
        if hasattr(self, 'editing_item'):
            del self.editing_item
        
        if hasattr(self, 'editing_node'):
            del self.editing_node
    
    def _validate_inline_name(self, name: str) -> bool:
        """Validar nombre para edición inline."""
        if not name:
            return False
        
        # Caracteres prohibidos
        import re
        forbidden_chars = r'[<>:"/\\|?*]'
        if re.search(forbidden_chars, name):
            tk.messagebox.showerror("Error", "El nombre contiene caracteres prohibidos")
            return False
        
        # Verificar duplicados en el mismo nivel
        if hasattr(self, 'editing_node') and self.editing_node.parent_id:
            siblings = self.node_repository.find_children(self.editing_node.parent_id)
            for sibling in siblings:
                if (sibling.node_id != self.editing_node.node_id and 
                    sibling.name.lower() == name.lower()):
                    tk.messagebox.showerror("Error", f"Ya existe un elemento con el nombre '{name}'")
                    return False
        
        return True
    
    def _on_right_click(self, event):
        """Manejar click derecho - delegado al menú contextual."""
        # Este método ahora es manejado por TreeContextMenu
        pass
    
    def _on_node_moved(self):
        """Callback cuando se mueve un nodo via drag & drop."""
        print("📦 Nodo movido - recargando árbol")
        self._load_nodes()
        
        # Notificar a callback externo si existe
        if hasattr(self, '_move_callback') and self._move_callback:
            self._move_callback()
    
    def _create_folder(self):
        """Crear nueva carpeta."""
        parent_id = self._selected_node_id
        
        command = CreateNodeCommand(
            name="Nueva Carpeta",
            node_type=NodeType.FOLDER,
            parent_id=parent_id,
            markdown_short="# Nueva Carpeta",
            explanation="Carpeta creada desde el explorador"
        )
        
        result = self.command_bus.execute(command)
        if result.success:
            self._load_nodes()  # Recargar árbol
            print(f"✅ Carpeta creada: {result.data.name}")
        else:
            print(f"❌ Error creando carpeta: {result.error}")
    
    def _create_file(self):
        """Crear nuevo archivo con reconocimiento automático de extensión."""
        parent_id = self._selected_node_id
        
        # Solicitar nombre del archivo
        name = tk.simpledialog.askstring(
            "Nuevo Archivo",
            "Nombre del archivo (con extensión):",
            initialvalue="nuevo_archivo.txt"
        )
        
        if not name or not name.strip():
            return
        
        name = name.strip()
        
        # Detectar extensión y generar código apropiado
        code_content = self._generate_code_by_extension(name)
        
        command = CreateNodeCommand(
            name=name,
            node_type=NodeType.FILE,
            parent_id=parent_id,
            markdown_short=f"# {name}",
            explanation=f"Archivo {self._get_language_name(name)} creado desde el explorador",
            code=code_content
        )
        
        result = self.command_bus.execute(command)
        if result.success:
            self._load_nodes()  # Recargar árbol
            print(f"✅ Archivo creado: {result.data.name}")
        else:
            print(f"❌ Error creando archivo: {result.error}")
    
    def _generate_code_by_extension(self, filename: str) -> str:
        """Generar código plantilla según la extensión del archivo."""
        # Obtener extensión
        parts = filename.split('.')
        if len(parts) < 2:
            return f"# Contenido de {filename}\n"
        
        ext = parts[-1].lower()
        
        # Plantillas por extensión
        templates = {
            'py': f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{filename} - Archivo Python generado automáticamente
"""

def main():
    print("Hola desde {filename}")


if __name__ == "__main__":
    main()
''',
            'js': f'''/**
 * {filename} - Archivo JavaScript generado automáticamente
 */

console.log("Hola desde {filename}");

// Tu código aquí
function main() {{
    // Implementar funcionalidad
}}

main();
''',
            'ts': f'''/**
 * {filename} - Archivo TypeScript generado automáticamente
 */

console.log("Hola desde {filename}");

// Tu código aquí
function main(): void {{
    // Implementar funcionalidad
}}

main();
''',
            'html': f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
</head>
<body>
    <h1>Hola desde {filename}</h1>
    
    <!-- Tu contenido aquí -->
    
</body>
</html>
''',
            'css': f'''/**
 * {filename} - Archivo CSS generado automáticamente
 */

/* Reset básico */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

/* Tu estilo aquí */
body {{
    font-family: Arial, sans-serif;
    line-height: 1.6;
}}
''',
            'md': f'''# {filename.replace('.md', '').replace('_', ' ').title()}

## Descripción

Este documento fue generado automáticamente.

## Contenido

- Punto 1
- Punto 2
- Punto 3

## Notas

Agregar contenido aquí...
''',
            'json': f'''{{
  "name": "{filename.replace('.json', '')}",
  "version": "1.0.0",
  "description": "Archivo JSON generado automáticamente",
  "created": "{self._get_current_timestamp()}",
  "data": {{
    "example": "valor"
  }}
}}
''',
            'rs': f'''// {filename} - Archivo Rust generado automáticamente

fn main() {{
    println!("Hola desde {filename}");
    
    // Tu código aquí
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_example() {{
        // Implementar test
        assert_eq!(2 + 2, 4);
    }}
}}
''',
            'go': f'''// {filename} - Archivo Go generado automáticamente
package main

import "fmt"

func main() {{
    fmt.Println("Hola desde {filename}")
    
    // Tu código aquí
}}
''',
            'java': f'''/**
 * {filename} - Archivo Java generado automáticamente
 */

public class {filename.replace('.java', '').capitalize()} {{
    
    public static void main(String[] args) {{
        System.out.println("Hola desde {filename}");
        
        // Tu código aquí
    }}
}}
''',
            'cpp': f'''/**
 * {filename} - Archivo C++ generado automáticamente
 */

#include <iostream>
#include <string>

int main() {{
    std::cout << "Hola desde {filename}" << std::endl;
    
    // Tu código aquí
    
    return 0;
}}
''',
            'c': f'''/**
 * {filename} - Archivo C generado automáticamente
 */

#include <stdio.h>
#include <stdlib.h>

int main() {{
    printf("Hola desde {filename}\\n");
    
    // Tu código aquí
    
    return 0;
}}
''',
            'sh': f'''#!/bin/bash
# {filename} - Script Bash generado automáticamente

echo "Hola desde {filename}"

# Tu código aquí
''',
            'bat': f'''@echo off
REM {filename} - Script Batch generado automáticamente

echo Hola desde {filename}

REM Tu código aquí
pause
''',
            'txt': f'''Archivo de texto: {filename}
Creado automáticamente por TreeCreator

Contenido:
----------

Tu texto aquí...
''',
            'xml': f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- {filename} - Archivo XML generado automáticamente -->
<root>
    <metadata>
        <name>{filename}</name>
        <created>{self._get_current_timestamp()}</created>
    </metadata>
    
    <data>
        <!-- Tu contenido XML aquí -->
    </data>
</root>
''',
            'yml': f'''# {filename} - Archivo YAML generado automáticamente
name: {filename.replace('.yml', '').replace('.yaml', '')}
version: 1.0.0
description: "Archivo YAML generado automáticamente"

# Tu configuración aquí
config:
  example: valor
  enabled: true
''',
            'yaml': f'''# {filename} - Archivo YAML generado automáticamente
name: {filename.replace('.yml', '').replace('.yaml', '')}
version: 1.0.0
description: "Archivo YAML generado automáticamente"

# Tu configuración aquí
config:
  example: valor
  enabled: true
'''
        }
        
        return templates.get(ext, f"# Contenido de {filename}\n# Archivo {ext.upper()} generado automáticamente\n\n")
    
    def _get_language_name(self, filename: str) -> str:
        """Obtener nombre del lenguaje por extensión."""
        parts = filename.split('.')
        if len(parts) < 2:
            return "genérico"
        
        ext = parts[-1].lower()
        
        language_names = {
            'py': 'Python',
            'js': 'JavaScript', 
            'ts': 'TypeScript',
            'html': 'HTML',
            'css': 'CSS',
            'md': 'Markdown',
            'json': 'JSON',
            'rs': 'Rust',
            'go': 'Go',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'sh': 'Bash',
            'bat': 'Batch',
            'txt': 'Texto',
            'xml': 'XML',
            'yml': 'YAML',
            'yaml': 'YAML'
        }
        
        return language_names.get(ext, ext.upper())
    
    def _get_current_timestamp(self) -> str:
        """Obtener timestamp actual."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _delete_node(self):
        """Eliminar nodo seleccionado."""
        if self._selected_node_id:
            # Confirmar eliminación
            node = self.node_repository.find_by_id(self._selected_node_id)
            if node:
                confirm = messagebox.askyesno(
                    "Confirmar eliminación",
                    f"¿Eliminar '{node.name}'?\n\n"
                    f"{'⚠️ Esta carpeta contiene archivos' if node.is_folder() else '📄 Este archivo se eliminará permanentemente'}",
                    icon='warning'
                )
                if confirm:
                    success = self.node_repository.delete(self._selected_node_id)
                    if success:
                        self._load_nodes()  # Recargar árbol
                        print(f"✅ Eliminado: {node.name}")
                    else:
                        print(f"❌ Error eliminando: {node.name}")
        else:
            messagebox.showwarning(
                "Sin selección",
                "Selecciona un archivo o carpeta para eliminar"
            )
    
    def update_node_display(self, node_id: str, new_name: str):
        """Actualizar el nombre del nodo en el TreeView sin recargar todo."""
        try:
            # Verificar que el nodo existe en el TreeView
            if self.tree.exists(node_id):
                # Obtener el nodo del repositorio para obtener su tipo
                node = self.node_repository.find_by_id(node_id)
                if node:
                    # Determinar icono según el tipo
                    if node.is_folder():
                        # Verificar si está abierto o cerrado
                        is_open = self.tree.item(node_id, 'open')
                        icon = FlatIcons.FOLDER_OPEN if is_open else FlatIcons.FOLDER_CLOSED
                    else:
                        icon = FlatIcons.get_file_icon(new_name)
                    
                    display_name = f"{icon} {new_name}"
                    
                    # Actualizar el texto en el TreeView
                    self.tree.item(node_id, text=display_name)
                    
                    print(f"🔄 TreeView actualizado: {node.name} → {new_name}")
                else:
                    print(f"❌ Nodo {node_id} no encontrado en repositorio")
            else:
                print(f"❌ Nodo {node_id} no existe en TreeView")
        except Exception as e:
            print(f"❌ Error actualizando TreeView: {e}")
    
    def get_selected_node_id(self) -> Optional[str]:
        """Obtener ID del nodo seleccionado."""
        return self._selected_node_id
    
    def refresh(self):
        """Refrescar el árbol."""
        self._load_nodes()
    
    def enable_drag_drop(self):
        """Habilitar drag & drop."""
        if hasattr(self, 'drag_drop'):
            self.drag_drop.enable()
    
    def disable_drag_drop(self):
        """Deshabilitar drag & drop."""
        if hasattr(self, 'drag_drop'):
            self.drag_drop.disable()
    
    def set_move_callback(self, callback):
        """Establecer callback para cuando se mueven nodos."""
        self._move_callback = callback
    
    def expand_all(self):
        """Expandir todos los nodos."""
        def expand_recursive(item):
            self.tree.item(item, open=True)
            # Actualizar icono a carpeta abierta
            if self._is_folder_item(item):
                current_text = self.tree.item(item, 'text')
                new_text = f"{FlatIcons.FOLDER_OPEN}{current_text[1:]}"
                self.tree.item(item, text=new_text)
            
            for child in self.tree.get_children(item):
                expand_recursive(child)
        
        for root_item in self.tree.get_children():
            expand_recursive(root_item)
        
        print("📂 Todos los nodos expandidos")
    
    def collapse_all(self):
        """Colapsar todos los nodos."""
        def collapse_recursive(item):
            self.tree.item(item, open=False)
            # Actualizar icono a carpeta cerrada
            if self._is_folder_item(item):
                current_text = self.tree.item(item, 'text')
                new_text = f"{FlatIcons.FOLDER_CLOSED}{current_text[1:]}"
                self.tree.item(item, text=new_text)
            
            for child in self.tree.get_children(item):
                collapse_recursive(child)
        
        for root_item in self.tree.get_children():
            collapse_recursive(root_item)
        
        print("📁 Todos los nodos colapsados")
    
    def _is_folder_item(self, item) -> bool:
        """Verificar si un item del tree es una carpeta."""
        try:
            node = self.node_repository.find_by_id(item)
            return node and node.is_folder()
        except:
            return False
    
    def search_nodes(self, query: str):
        """Buscar nodos por nombre (funcionalidad futura)."""
        # TODO: Implementar búsqueda y filtrado
        pass
    
    def get_tree_statistics(self) -> Dict[str, int]:
        """Obtener estadísticas del árbol."""
        stats = {
            'total_folders': 0,
            'total_files': 0,
            'completed': 0,
            'in_progress': 0,
            'pending': 0
        }
        
        all_nodes = self.node_repository.find_all()
        for node in all_nodes:
            if node.is_folder():
                stats['total_folders'] += 1
            else:
                stats['total_files'] += 1
            
            if node.status == NodeStatus.COMPLETED:
                stats['completed'] += 1
            elif node.status == NodeStatus.IN_PROGRESS:
                stats['in_progress'] += 1
            elif node.status == NodeStatus.PENDING:
                stats['pending'] += 1
        
        return stats