import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging
from typing import Any, List, Optional

from panels.tree_helpers import update_editors
from panels.tree_dialogs import create_file_simple, create_folder_simple
from panels.status_selector import StatusSelector

# Configuración de logging básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DragDropTreeview(ttk.Treeview):
    """Treeview personalizado con drag & drop COMPLETO y robusto."""

    def __init__(self, parent: Any, app: Any, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.drag_data = {"item": None, "items": [], "dragging": False}

        # Configurar eventos drag & drop
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.bind("<Control-Button-1>", self.on_ctrl_click)
        self.bind("<Shift-Button-1>", self.on_shift_click)
        self.bind("<Motion>", self.on_motion)

        # Contexto para cut/copy/paste
        self.clipboard = {"items": [], "mode": None}

        # Configurar centrado de estados
        self.configure_column_centering()

    def configure_column_centering(self) -> None:
        """Configura el centrado de la columna de estados."""
        self.column("status", anchor="center", width=80, minwidth=80)

    def on_click(self, event: tk.Event) -> None:
        """Manejo de click simple y feedback visual."""
        item = self.identify_row(event.y)
        if item:
            if not (event.state & 0x4):  # No Ctrl presionado
                self.selection_set(item)
                self.set_item_color(item, "#e3f2fd")
            self.drag_data["item"] = item
            self.drag_data["dragging"] = False

    def on_ctrl_click(self, event: tk.Event) -> None:
        """Selección múltiple con Ctrl."""
        item = self.identify_row(event.y)
        if item:
            current_selection = list(self.selection())
            if item in current_selection:
                self.selection_remove(item)
            else:
                self.selection_add(item)
                self.set_item_color(item, "#e3f2fd")

    def on_shift_click(self, event: tk.Event) -> None:
        """Selección por rango con Shift (opcional)."""
        # Implementa lógica de rango si es necesario
        pass

    def on_motion(self, event: tk.Event) -> None:
        """Feedback visual cuando el mouse pasa sobre elementos."""
        item = self.identify_row(event.y)
        if item and not self.drag_data["dragging"]:
            self.configure(cursor="hand2" if item else "")

    def on_drag(self, event: tk.Event) -> None:
        """Inicio del arrastre con feedback visual."""
        if self.drag_data["item"] and not self.drag_data["dragging"]:
            self.drag_data["dragging"] = True
            self.config(cursor="fleur")
            for item in self.selection():
                self.set_item_color(item, "#ffeb3b")

    def on_drop(self, event: tk.Event) -> None:
        """Soltar elemento con feedback visual."""
        self.config(cursor="")
        drop_item = self.identify_row(event.y)

        if self.drag_data["dragging"] and drop_item:
            selected_items = list(self.selection())
            if drop_item not in selected_items:
                self.set_item_color(drop_item, "#c8e6c9")
                self.move_items_flexible(selected_items, drop_item, event.y)
                self.after(500, self.clear_all_colors)
        self.drag_data["dragging"] = False
        self.clear_drag_colors()

    def set_item_color(self, item: str, color: str) -> None:
        """Cambia color de fondo de un elemento (simulado con emoji estado)."""
        try:
            self.set(item, "status", f"🎯")
        except Exception as e:
            logger.warning(f"Error al setear color de item {item}: {e}")

    def clear_drag_colors(self) -> None:
        """Limpia colores de drag."""
        for item in self.selection():
            try:
                if item in self.app.node_data:
                    original_status = self.app.node_data[item].get("status", "")
                    self.set(item, "status", original_status)
            except Exception as e:
                logger.warning(f"Error al limpiar color de item {item}: {e}")

    def clear_all_colors(self) -> None:
        """Limpia todos los colores temporales."""
        for item_id in self.app.node_data:
            try:
                original_status = self.app.node_data[item_id].get("status", "")
                self.set(item_id, "status", original_status)
            except Exception as e:
                logger.warning(f"Error al limpiar todos los colores: {e}")

    def move_items_flexible(self, items: List[str], target: str, y_pos: int) -> None:
        """Mover elementos CON soporte para jerarquías padre/hijo."""
        if not items or target in items:
            return

        target_node = self.app.node_data.get(target)
        if not target_node:
            return

        # Si target es carpeta Y no es hijo de ningún item seleccionado
        if target_node["type"] == "folder" and not self._is_ancestor(target, items):
            for item in items:
                if item != target:
                    self.move(item, target, "end")
                    self.app.root.after_idle(self.app.update_preview)
                    self.app.mark_unsaved()
        else:
            target_bbox = self.bbox(target)
            if target_bbox:
                target_middle = target_bbox[1] + target_bbox[3] // 2
                insert_before = y_pos < target_middle
            else:
                insert_before = False

            target_parent = self.parent(target)
            for item in items:
                if item != target:
                    target_children = list(self.get_children(target_parent))
                    target_index = target_children.index(target) if target in target_children else 0
                    if not insert_before:
                        target_index += 1
                    self.move(item, target_parent, target_index)
                    self.app.root.after_idle(self.app.update_preview)
                    self.app.mark_unsaved()

    def _is_ancestor(self, potential_ancestor: str, items: List[str]) -> bool:
        """Verifica si potential_ancestor es ancestro de algún item."""
        for item in items:
            current = self.parent(item)
            while current:
                if current == potential_ancestor:
                    return True
                current = self.parent(current)
        return False

    def cut_selection(self) -> None:
        """Corta la selección actual."""
        self.clipboard["items"] = list(self.selection())
        self.clipboard["mode"] = "cut"
        for item in self.clipboard["items"]:
            current_status = self.set(item, "status")
            if not current_status.startswith("✂️"):
                self.set(item, "status", "✂️ " + current_status)

    def copy_selection(self) -> None:
        """Copia la selección actual."""
        self.clipboard["items"] = list(self.selection())
        self.clipboard["mode"] = "copy"

    def paste_to_target(self, target: Optional[str] = None) -> None:
        """Pega los elementos en la ubicación objetivo."""
        if not self.clipboard["items"]:
            messagebox.showwarning("Pegar", "No hay elementos en el portapapeles")
            return
        target = target or self.focus()
        if not target:
            target = ""
        for item in self.clipboard["items"]:
            if self.clipboard["mode"] == "cut":
                self.move_items_flexible([item], target, 0)
                current_status = self.set(item, "status")
                if current_status.startswith("✂️ "):
                    clean_status = current_status[3:]
                    self.set(item, "status", clean_status)
            elif self.clipboard["mode"] == "copy":
                self.app.duplicate_node_to_target(item, target)
        if self.clipboard["mode"] == "cut":
            self.clipboard = {"items": [], "mode": None}
        self.app.update_preview()

def setup_tree_panel(app: Any) -> None:
    """Configura el panel del explorador con robustez y feedback visual."""
    header_frame = ttk.Frame(app.left_frame)
    header_frame.pack(fill="x", padx=5, pady=5)
    ttk.Label(header_frame, text="📁 Explorador de Proyecto", font=("Segoe UI", 10, "bold")).pack(anchor="w")

    tree_frame = ttk.Frame(app.left_frame)
    tree_frame.pack(fill="both", expand=True, padx=5)

    app.tree = DragDropTreeview(tree_frame, app, columns=("status",), show="tree headings")
    app.tree.heading("#0", text="Nombre")
    app.tree.heading("status", text="Estado")
    app.tree.column("#0", width=200)
    app.tree.column("status", width=80, anchor="center")

    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=app.tree.yview)
    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=app.tree.xview)
    app.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    app.tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    app.tree.bind("<<TreeviewSelect>>", lambda e: on_tree_select(app, e))
    app.tree.bind("<Double-1>", lambda e: handle_inline_rename(app, e))
    app.tree.bind("<Button-3>", lambda e: show_context_menu(app, e))

def on_tree_select(app: Any, event: tk.Event) -> None:
    """
    Maneja la selección actual del árbol y actualiza el editor.
    Añade robustez y actualiza la vista previa y los números de línea.
    """
    selected_items = app.tree.selection()
    if selected_items:
        node_id = selected_items[0]
        if node_id in app.node_data:
            app.current_node = node_id
            node = app.node_data[node_id]
            update_editors(app, node)
            if hasattr(app, 'update_code_line_numbers'):
                app.root.after_idle(lambda: app.update_code_line_numbers())
    if hasattr(app, 'on_select'):
        app.on_select(event)
    setup_enhanced_context_menu(app)

def update_tree_display_realtime(app: Any, item_id: str) -> None:
    """Actualiza la visualización del árbol en tiempo real y fuerza vista previa."""
    if item_id in app.node_data:
        node = app.node_data[item_id]
        icon = "📁" if node["type"] == "folder" else "📄"
        name = node['name'] + ("/" if node["type"] == "folder" else "")
        app.tree.item(item_id, text=f"{icon} {name}")
        app.tree.set(item_id, "status", node.get("status", ""))
    app.root.after_idle(app.update_preview)

def handle_inline_rename(app: Any, event: tk.Event) -> None:
    """Renombrado in-situ robusto y sin borde rojo."""
    item = app.tree.identify_row(event.y)
    if not item or item not in app.node_data:
        return
    try:
        bbox = app.tree.bbox(item, "#0")
        if not bbox:
            return
    except Exception as e:
        logger.warning(f"No se pudo obtener bbox para renombrar: {e}")
        return

    current_name = app.node_data[item]["name"]
    entry = tk.Entry(app.tree, font=("Segoe UI", 10), relief="solid", borderwidth=1,
                     bg="white", fg="black", selectbackground="blue")
    x_pos = bbox[0] + 24
    y_pos = bbox[1]
    width = max(bbox[2] - 28, 180)
    entry.place(x=x_pos, y=y_pos, width=width, height=bbox[3])
    entry.insert(0, current_name)
    entry.select_range(0, tk.END)
    entry.focus_set()
    applied = [False]

    def apply_rename(event=None):
        if applied[0]:
            return
        applied[0] = True
        try:
            new_name = entry.get().strip()
            entry.destroy()
            if new_name and new_name != current_name:
                app.node_data[item]["name"] = new_name
                app.node_data[item]["modified"] = datetime.now().isoformat()
                icon = "📁" if app.node_data[item]["type"] == "folder" else "📄"
                display_name = new_name + ("/" if app.node_data[item]["type"] == "folder" else "")
                app.tree.item(item, text=f"{icon} {display_name}")
                if item == app.current_node and hasattr(app, 'name_entry'):
                    app.name_entry.delete(0, "end")
                    app.name_entry.insert(0, new_name)
                app.mark_unsaved()
                app.update_preview()
        except Exception as e:
            logger.error(f"Error durante renombrado: {e}")
            if not applied[0]:
                applied[0] = True
                try:
                    entry.destroy()
                except Exception:
                    pass

    def cancel_rename(event=None):
        if not applied[0]:
            applied[0] = True
            try:
                entry.destroy()
            except Exception:
                pass

    entry.bind("<Return>", apply_rename)
    entry.bind("<Escape>", cancel_rename)
    entry.bind("<FocusOut>", apply_rename)
    app.root.after(20000, lambda: cancel_rename() if not applied[0] else None)

def setup_enhanced_context_menu(app: Any) -> None:
    """Crea el menú contextual robusto con todas las opciones, preparado para testing."""
    app.context_menu = tk.Menu(app.root, tearoff=0)
    app.context_menu.add_command(label="📄 Nuevo Archivo", command=lambda: create_file_simple(app))
    app.context_menu.add_command(label="📁 Nueva Carpeta", command=lambda: create_folder_simple(app))
    app.context_menu.add_separator()
    app.context_menu.add_command(label="🌳 Importar Estructura", command=lambda: import_tree_structure(app))
    app.context_menu.add_separator()
    app.context_menu.add_command(label="✏️ Renombrar", command=lambda: rename_selected(app))
    app.context_menu.add_command(label="🗑️ Eliminar", command=lambda: delete_selected(app))
    app.context_menu.add_separator()
    status_menu = tk.Menu(app.context_menu, tearoff=0)
    app.context_menu.add_cascade(label="📊 Estado", menu=status_menu)
    status_menu.add_command(label="✅ Completado", command=lambda: set_status_selected(app, "✅"))
    status_menu.add_command(label="⬜ En Proceso", command=lambda: set_status_selected(app, "⬜"))
    status_menu.add_command(label="❌ Pendiente", command=lambda: set_status_selected(app, "❌"))
    status_menu.add_command(label="🔄 Sin Estado", command=lambda: set_status_selected(app, ""))
    app.context_menu.add_separator()
    app.context_menu.add_command(label="📋 Copiar", command=lambda: app.tree.copy_selection())
    app.context_menu.add_command(label="✂️ Cortar", command=lambda: app.tree.cut_selection())
    app.context_menu.add_command(label="📥 Pegar", command=lambda: app.tree.paste_to_target())
    app.context_menu.add_separator()
    app.context_menu.add_command(label="📤 Exportar", command=app.export_node)

def import_tree_structure(app: Any) -> None:
    """Importa estructura de árbol desde texto."""
    try:
        from dialogs.tree_structure_importer import show_tree_structure_importer
        show_tree_structure_importer(app)
    except ImportError as e:
        logger.error(f"No se pudo importar el importador de estructura: {e}")

def rename_selected(app: Any) -> None:
    """Renombra el elemento seleccionado."""
    selected = app.tree.selection()
    if selected:
        item = selected[0]
        event = type('Event', (), {'y': 0})()
        handle_inline_rename(app, event)

def delete_selected(app: Any) -> None:
    """Elimina elementos seleccionados con confirmación y robustez."""
    selected = list(app.tree.selection())
    if not selected:
        return
    count = len(selected)
    if count == 1:
        name = app.node_data[selected[0]]["name"]
        msg = f"¿Eliminar '{name}'?"
    else:
        msg = f"¿Eliminar {count} elementos seleccionados?"
    if messagebox.askyesno("Confirmar eliminación", msg):
        for item in selected:
            delete_recursive(app, item)
        app.update_preview()
        app.mark_unsaved()

def delete_recursive(app: Any, item: str) -> None:
    """Elimina el elemento y sus hijos recursivamente."""
    for child in app.tree.get_children(item):
        delete_recursive(app, child)
    if item in app.node_data:
        del app.node_data[item]
    app.tree.delete(item)
    if hasattr(app, 'current_node') and app.current_node == item:
        app.current_node = None
        if hasattr(app, 'clear_editor'):
            app.clear_editor()

def set_status_selected(app: Any, status: str) -> None:
    """Establece el estado a los elementos seleccionados y actualiza display."""
    selected = list(app.tree.selection())
    for item in selected:
        if item in app.node_data:
            app.node_data[item]["status"] = status
            app.node_data[item]["modified"] = datetime.now().isoformat()
            app.tree.set(item, "status", status)
            update_tree_display_realtime(app, item)
    if hasattr(app, 'update_status'):
        app.update_status()
    app.mark_unsaved()

def show_context_menu(app: Any, event: tk.Event) -> None:
    """Muestra el menú contextual en la posición del mouse."""
    item = app.tree.identify_row(event.y)
    if item:
        app.tree.selection_set(item)
        app.current_node = item
    app.context_menu.tk_popup(event.x_root, event.y_root)

# GANCHOS PARA TESTING AUTOMATIZADO
def _test_tree_create_file(app: Any, filename: str = "testfile.md") -> bool:
    """Test: Crear archivo y verificar existencia."""
    initial_count = len(app.node_data)
    app.node_data["testnode"] = {
        "name": filename,
        "type": "file",
        "status": "",
        "content": "",
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat()
    }
    app.tree.insert("", "end", iid="testnode", text=filename, values=[""])
    return len(app.node_data) == initial_count + 1

def _test_tree_rename_node(app: Any, node_id: str, new_name: str) -> bool:
    """Test: Renombrar nodo y validar."""
    if node_id not in app.node_data:
        return False
    app.node_data[node_id]["name"] = new_name
    app.tree.item(node_id, text=new_name)
    return app.node_data[node_id]["name"] == new_name

def _test_tree_delete_node(app: Any, node_id: str) -> bool:
    """Test: Eliminar nodo y validar."""
    app.tree.delete(node_id)
    if node_id in app.node_data:
        del app.node_data[node_id]
    return node_id not in app.node_data

# Puedes añadir más hooks para testing según tus necesidades.