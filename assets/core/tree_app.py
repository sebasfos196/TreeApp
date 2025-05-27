# carpetatree/core/tree_app.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import logging
from typing import Any, Optional

from config.config_manager import ConfigManager
from core.theme import ThemedStyle
from core.autosave import setup_autosave
from core.clock import update_clock

from components.menu_bar import setup_menu_bar
from components.toolbar import setup_toolbar
from components.status_bar import setup_status_bar
from components.layout import setup_main_layout

from panels.tree_panel import setup_tree_panel
from panels.editor_panel import setup_editor_panel
from panels.preview_panel import setup_preview_panel, update_preview_improved
from panels.import_panel import setup_import_panel

from export.html_exporter import generate_html_export
from export.text_exporter import generate_text_export
from export.node_exporter import export_node as export_selected_node

from logic.stats_generator import generate_project_stats
from logic.filters import filter_tree
from logic.content_manager import load_node_content, save_current_content

from dialogs.search import SearchDialog
from dialogs.insert_link import show_insert_link
from dialogs.insert_table import show_insert_table
from dialogs.insert_image import show_insert_image
from dialogs.tree_structure_importer import show_tree_structure_importer
from dialogs.help_about import (
    show_about_dialog,
    show_shortcuts_dialog,
    show_markdown_guide
)
from logic.node_manager import (
    rename_node as rename_node_func,
    set_node_status as set_node_status_func,
    add_file,
    add_folder
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TreeAppV4")

class TreeAppV4:
    """
    Aplicación principal TreeAppV4, gestionando el ciclo de vida del proyecto,
    la interfaz gráfica y la lógica de negocio.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Workspace Interactivo Jumper v4 Pro")
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config

        self.node_data: dict = {}
        self.current_node: Optional[str] = None
        self.project_file: Optional[str] = None
        self.unsaved_changes: bool = False
        self.history = []
        self.history_index = -1

        self.style = ThemedStyle(self.config["theme"], self.config["font_size"])
        self.root.configure(bg=self.style.themes[self.config["theme"]]["bg"])

        self.root.geometry(self.config["window_geometry"])
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 🔥 CONFIGURACIÓN CORREGIDA DE PANELES
        setup_menu_bar(self)
        setup_toolbar(self)
        setup_main_layout(self)
        setup_tree_panel(self)
        setup_status_bar(self)
        
        # Configurar paneles con parámetros correctos
        setup_import_panel(self, self.left_frame)
        setup_editor_panel(self)  # Sin parámetro parent_frame
        setup_preview_panel(self, self.right_frame)
        
        update_clock(self)
        setup_autosave(self)

        if self.config.get("last_project") and os.path.exists(self.config["last_project"]):
            self.load_project(self.config["last_project"])
        else:
            self.load_initial_project()

    # ========== PROYECTO: NUEVO/ABRIR/GUARDAR ==========

    def new_project(self):
        if self.check_unsaved_changes():
            self.node_data = {}
            self.project_file = None
            self.unsaved_changes = False
            self.load_initial_project()

    def open_project(self):
        if self.check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                title="Abrir Proyecto",
                filetypes=[("Workspace Jumper", "*.wjp"), ("JSON", "*.json"), ("Todos", "*.*")]
            )
            if file_path:
                self.load_project(file_path)

    def save_project(self):
        if self.project_file:
            self._save_to_file(self.project_file)
        else:
            self.save_project_as()

    def save_project_as(self):
        file_path = filedialog.asksaveasfilename(
            title="Guardar Proyecto Como",
            defaultextension=".wjp",
            filetypes=[("Workspace Jumper", "*.wjp"), ("JSON", "*.json"), ("Todos", "*.*")]
        )
        if file_path:
            self._save_to_file(file_path)
            self.project_file = file_path
            self.config["last_project"] = file_path
            self.config_manager.save_config()

    def _save_to_file(self, file_path: str):
        try:
            data = {
                "version": "4.0",
                "modified": datetime.now().isoformat(),
                "node_data": self.node_data
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.unsaved_changes = False
            messagebox.showinfo("Guardado", f"Proyecto guardado en:\n{file_path}")
        except Exception as e:
            logger.exception("Error guardando proyecto")
            messagebox.showerror("Error", f"No se pudo guardar el proyecto:\n{str(e)}")

    def load_project(self, file_path: str):
        """Carga un proyecto desde disco, migrando datos legacy si es necesario."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.node_data = data.get("node_data", {})
            self.project_file = file_path
            self.unsaved_changes = False
            self._migrate_legacy_data()
            self._rebuild_tree()
            messagebox.showinfo("Cargado", f"Proyecto cargado:\n{file_path}")
            if hasattr(self, 'update_status'):
                self.update_status()
            if hasattr(self, 'update_preview'):
                self.update_preview()
        except Exception as e:
            logger.exception("Error cargando proyecto")
            messagebox.showerror("Error", f"No se pudo cargar el proyecto:\n{str(e)}")

    def _migrate_legacy_data(self):
        """Migra datos antiguos a los nuevos campos requeridos para la versión 4.0+."""
        for node_id, node_data in self.node_data.items():
            if "markdown_short" not in node_data:
                content = node_data.get("content", "")
                name = node_data.get("name", "Sin nombre")
                first_line = ""
                if content:
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            first_line = line
                            break
                        elif line.startswith('#'):
                            first_line = line
                            break
                if not first_line:
                    first_line = f"# {name}"
                node_data["markdown_short"] = first_line
                node_data["explanation"] = ""
                node_data["code"] = ""

    def _rebuild_tree(self):
        """Reconstruye el árbol visual basado en node_data."""
        self.tree.delete(*self.tree.get_children())
        for node_id, node_data in self.node_data.items():
            icon = "📁" if node_data["type"] == "folder" else "📄"
            status = node_data.get("status", "")
            if status == "🕓":
                status = "⬜"
                node_data["status"] = "⬜"
            name = node_data['name']
            if node_data["type"] == "folder":
                name += "/"
            label = f"{icon} {name}"
            self.tree.insert("", "end", iid=node_id, text=label, values=[status])

    def load_initial_project(self):
        """Inicializa el proyecto con todos los campos necesarios."""
        if hasattr(self, 'tree'):
            self.tree.delete(*self.tree.get_children())
        self.node_data = {
            "root_folder": {
                "name": "Root",
                "type": "folder",
                "status": "",
                "content": "# Root\n\nCarpeta raíz del proyecto...",
                "markdown_short": "# Root",
                "explanation": "Carpeta raíz del proyecto",
                "code": "",
                "tags": [],
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
        }
        if hasattr(self, 'tree'):
            self.tree.insert("", "end", iid="root_folder", text="📁 Root/", values=[""])
            self.tree.item("root_folder", open=True)
            self.tree.selection_set("root_folder")
            self.current_node = "root_folder"

    def duplicate_node_to_target(self, source_id: str, target_id: Optional[str]):
        """Duplica un nodo a una ubicación específica, generando un nuevo ID."""
        if source_id not in self.node_data:
            return
        import copy
        original = copy.deepcopy(self.node_data[source_id])
        new_name = f"{original['name']} (copia)"
        new_id = f"{original['type']}_{len(self.node_data)}_{new_name}"
        original["name"] = new_name
        original["created"] = datetime.now().isoformat()
        original["modified"] = datetime.now().isoformat()
        self.node_data[new_id] = original
        icon = "📁" if original["type"] == "folder" else "📄"
        display_name = new_name + ("/" if original["type"] == "folder" else "")
        self.tree.insert(target_id or "", "end", iid=new_id,
                        text=f"{icon} {display_name}", values=[original["status"]])
        self.mark_unsaved()

    def check_unsaved_changes(self) -> bool:
        """Advierte si hay cambios sin guardar antes de continuar."""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Cambios sin guardar",
                "Hay cambios sin guardar. ¿Deseas guardar antes de continuar?"
            )
            if result is None:
                return False
            elif result:
                self.save_project()
        return True

    # ========== EXPORTACIÓN Y ESTADÍSTICAS ==========

    def export_html(self):
        if not self.node_data:
            messagebox.showwarning("Advertencia", "No hay contenido para exportar")
            return
        file_path = filedialog.asksaveasfilename(
            title="Exportar como HTML",
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                html_content = generate_html_export(self)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                messagebox.showinfo("Éxito", f"Proyecto exportado a HTML:\n{file_path}")
            except Exception as e:
                logger.exception("Error exportando HTML")
                messagebox.showerror("Error", f"Error al exportar HTML:\n{str(e)}")

    def export_text(self):
        if not self.node_data:
            messagebox.showwarning("Advertencia", "No hay contenido para exportar")
            return
        file_path = filedialog.asksaveasfilename(
            title="Exportar como Texto",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Markdown", "*.md"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                text_content = generate_text_export(self)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                messagebox.showinfo("Éxito", f"Proyecto exportado como texto:\n{file_path}")
            except Exception as e:
                logger.exception("Error exportando texto")
                messagebox.showerror("Error", f"Error al exportar texto:\n{str(e)}")

    def export_node(self):
        export_selected_node(self)

    def show_project_stats(self):
        from dialogs.stats_dialog import show_stats_dialog
        show_stats_dialog(self)

    # ========== BÚSQUEDA, FILTRO Y DIÁLOGOS INSERTAR ==========

    def show_search_dialog(self):
        text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
        if text_widget:
            SearchDialog(self.root, text_widget)

    def insert_link(self):
        show_insert_link(self)

    def insert_table(self):
        show_insert_table(self)

    def insert_image(self):
        show_insert_image(self)

    def filter_tree(self, event=None):
        filter_tree(self)

    # ========== CIERRE Y GUARDADO DEL ESTADO ==========

    def on_closing(self):
        if self.check_unsaved_changes():
            self.config["window_geometry"] = self.root.geometry()
            self.config_manager.save_config()
            self.root.destroy()

    # ========== DESHACER/REHACER, ZEN MODE, STATUS BAR ==========

    def undo(self):
        try:
            text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
            if text_widget:
                text_widget.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
            if text_widget:
                text_widget.edit_redo()
        except tk.TclError:
            pass

    def toggle_zen_mode(self):
        if hasattr(self, 'zen_mode') and self.zen_mode:
            self.main_paned.add(self.left_frame, before=self.center_frame)
            self.main_paned.add(self.right_frame)
            self.zen_mode = False
        else:
            self.main_paned.forget(self.left_frame)
            self.main_paned.forget(self.right_frame)
            self.zen_mode = True

    def toggle_status_bar(self):
        if self.status_frame.winfo_viewable():
            self.status_frame.pack_forget()
        else:
            self.status_frame.pack(side="bottom", fill="x", padx=5, pady=2)

    # ========== AYUDA Y ACERCA DE ==========

    def show_about(self):
        show_about_dialog(self)

    def show_shortcuts(self):
        show_shortcuts_dialog(self)

    def show_markdown_guide(self):
        show_markdown_guide(self)

    # ========== SELECCIÓN DE NODO Y CARGA DE CONTENIDO ==========

    def on_select(self, event=None):
        """Función completa de selección que carga todos los campos en los editores."""
        node_id = self.tree.focus()
        if node_id in self.node_data:
            save_current_content(self)
            self.current_node = node_id
            load_node_content(self, node_id)
            node = self.node_data[node_id]
            
            # Cargar en campo de nombre
            if hasattr(self, 'name_entry'):
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, node.get("name", ""))
            
            # Cargar markdown resumido
            if hasattr(self, 'markdown_short'):
                markdown_short = node.get("markdown_short", "")
                self.markdown_short.delete("1.0", "end")
                self.markdown_short.insert("1.0", markdown_short)
            
            # Cargar explicación extendida
            if hasattr(self, 'explanation_text'):
                explanation = node.get("explanation", "")
                self.explanation_text.delete("1.0", "end")
                self.explanation_text.insert("1.0", explanation)
            
            # Cargar código/notas técnicas
            if hasattr(self, 'code_text'):
                code_content = node.get("code", "")
                self.code_text.delete("1.0", "end")
                self.code_text.insert("1.0", code_content)
                self.text = self.code_text  # compatibilidad legacy
                
                # Actualizar números de línea
                if hasattr(self, 'update_code_line_numbers'):
                    self.root.after_idle(self.update_code_line_numbers)

    # ========== MARCAR CAMBIOS Y VALIDACIONES ==========

    def mark_unsaved(self):
        self.unsaved_changes = True
        if hasattr(self, 'status_saved'):
            self.status_saved.config(text="💾 Sin guardar")

    def validate_links(self):
        messagebox.showinfo("Validador de Enlaces", "Función de validación de enlaces en desarrollo.")

    def show_preferences(self):
        messagebox.showinfo("Configuración", "Panel de configuración en desarrollo.")

    # ========== GESTIÓN DE ARCHIVOS Y CARPETAS ==========

    def add_file(self):
        add_file(self)

    def add_folder(self):
        add_folder(self)

    # ========== TEMAS Y FUENTE ==========

    def on_theme_change(self, event=None):
        new_theme = self.theme_var.get()
        self.config["theme"] = new_theme
        self.config_manager.save_config()
        self.style = ThemedStyle(new_theme, self.config["font_size"])
        self.root.configure(bg=self.style.themes[new_theme]["bg"])

    def change_theme(self, theme_name: str):
        self.config["theme"] = theme_name
        self.style = ThemedStyle(theme_name, self.config["font_size"])
        self.root.configure(bg=self.style.themes[theme_name]["bg"])
        self.config_manager.save_config()

    def change_font_size(self, size: int):
        self.config["font_size"] = size
        self.style = ThemedStyle(self.config["theme"], size)
        font_code = ("Consolas", size)
        font_text = ("Segoe UI", size)
        
        # Actualizar fuentes en TODOS los editores
        widgets_code = ['code_text', 'code_line_numbers', 'text', 'preview_text']
        widgets_text = ['markdown_short', 'explanation_text']
        
        for attr in widgets_code:
            widget = getattr(self, attr, None)
            if widget:
                try:
                    widget.configure(font=font_code)
                except Exception:
                    pass
                    
        for attr in widgets_text:
            widget = getattr(self, attr, None)
            if widget:
                try:
                    widget.configure(font=font_text)
                except Exception:
                    pass
                    
        self.config_manager.save_config()

    # ========== INSERTAR MARKDOWN ==========

    def insert_markdown(self, prefix: str, suffix: str = ""):
        try:
            text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
            if text_widget:
                selection = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                text_widget.insert(tk.INSERT, f"{prefix}{selection}{suffix}")
        except tk.TclError:
            text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
            if text_widget:
                text_widget.insert(tk.INSERT, f"{prefix}{suffix}")

    # ========== ACTUALIZACIÓN DE NOMBRE Y EVENTOS DE TEXTO ==========

    def update_name(self, event=None):
        """Actualizar nombre con formato mejorado"""
        if self.current_node and self.current_node in self.node_data and hasattr(self, 'name_entry'):
            new_name = self.name_entry.get().strip()
            if new_name:
                self.node_data[self.current_node]["name"] = new_name
                self.node_data[self.current_node]["modified"] = datetime.now().isoformat()
                icon = "📁" if self.node_data[self.current_node]["type"] == "folder" else "📄"
                display_name = new_name + ("/" if self.node_data[self.current_node]["type"] == "folder" else "")
                label = f"{icon} {display_name}"
                self.tree.item(self.current_node, text=label)
                self.mark_unsaved()
                self.update_preview()

    def on_text_change(self, event=None):
        if hasattr(self, 'update_line_numbers'):
            self.update_line_numbers()
        self.mark_unsaved()

    def on_mousewheel(self, event):
        if hasattr(self, 'line_numbers'):
            self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

    # ========== SCROLL Y NÚMEROS DE LÍNEA ==========

    def scroll_text(self, *args):
        if hasattr(self, 'text') and hasattr(self, 'line_numbers'):
            self.text.yview(*args)
            self.line_numbers.yview(*args)

    def scrollbar_set(self, *args):
        if hasattr(self, 'text') and hasattr(self, 'line_numbers'):
            self.text.yview_moveto(args[0])
            self.line_numbers.yview_moveto(args[0])

    def update_line_numbers(self):
        if hasattr(self, 'line_numbers') and hasattr(self, 'text'):
            self.line_numbers.config(state='normal')
            self.line_numbers.delete("1.0", "end")
            line_count = int(self.text.index('end').split('.')[0]) - 1
            line_numbers = "\n".join(str(i) for i in range(1, line_count + 1))
            self.line_numbers.insert("1.0", line_numbers)
            self.line_numbers.config(state='disabled')

    # ========== VISTA PREVIA Y STATUS ==========

    def update_preview(self):
        update_preview_improved(self)

    def force_preview_update(self):
        if hasattr(self, 'update_preview'):
            self.root.after_idle(self.update_preview)

    def update_status(self):
        if hasattr(self, "status_stats"):
            files = [n for n in self.node_data.values() if n["type"] == "file"]
            total = len(files)
            done = sum(1 for f in files if f.get("status") == "✅")
            in_progress = sum(1 for f in files if f.get("status") == "⬜")
            self.status_stats.config(
                text=f"Archivos: {total} | Completados: {done} | En proceso: {in_progress}"
            )

    # ========== COPY/CUT/PASTE NODOS ==========

    def copy_node(self):
        self.clipboard_node = self.current_node
        self.clipboard_mode = "copy"

    def cut_node(self):
        self.clipboard_node = self.current_node
        self.clipboard_mode = "cut"

    def paste_node(self):
        if not hasattr(self, "clipboard_node") or not self.clipboard_node:
            messagebox.showwarning("Pegar", "No hay nodo copiado o cortado.")
            return
        import copy
        source_id = self.clipboard_node
        parent = self.tree.focus() or ""
        
        def generate_new_id(base):
            count = 1
            new_id = f"{base}_copy"
            while new_id in self.node_data:
                count += 1
                new_id = f"{base}_copy{count}"
            return new_id
            
        new_id = generate_new_id(source_id)
        node_copy = copy.deepcopy(self.node_data[source_id])
        node_copy["name"] += " (copiado)"
        node_copy["created"] = datetime.now().isoformat()
        node_copy["modified"] = datetime.now().isoformat()
        self.node_data[new_id] = node_copy
        
        icon = "📁" if node_copy["type"] == "folder" else "📄"
        display_name = node_copy["name"] + ("/" if node_copy["type"] == "folder" else "")
        label = f"{icon} {display_name}"
        status = node_copy.get("status", "")
        
        self.tree.insert(parent, "end", iid=new_id, text=label, values=[status])
        
        if self.clipboard_mode == "cut":
            self.tree.delete(source_id)
            del self.node_data[source_id]
            self.clipboard_node = None
            self.clipboard_mode = None
        self.mark_unsaved()

    # ========== RENOMBRAR Y ESTADO DE NODO ==========

    def rename_node(self):
        rename_node_func(self)

    def set_node_status(self, status: str):
        if status == "🕓":
            status = "⬜"
        set_node_status_func(self, status)

    # ========== LIMPIAR EDITORES Y VISTA PREVIA ==========

    def clear_editor(self):
        """Limpiar TODOS los editores"""
        editors = ['name_entry', 'markdown_short', 'explanation_text', 'code_text', 'text']
        for attr in editors:
            widget = getattr(self, attr, None)
            if widget:
                try:
                    if hasattr(widget, "delete"):
                        if attr == 'name_entry':
                            widget.delete(0, "end")
                        else:
                            widget.delete("1.0", "end")
                except Exception:
                    pass
                    
        if hasattr(self, 'preview_text'):
            try:
                self.preview_text.config(state="normal")
                self.preview_text.delete("1.0", "end")
                self.preview_text.config(state="disabled")
            except Exception:
                pass

    # ========== IMPORTAR ESTRUCTURA Y EXPORTAR PREVIEW ==========

    def show_tree_importer(self):
        show_tree_structure_importer(self)

    def export_preview_to_txt(self):
        try:
            if not hasattr(self, 'preview_text'):
                messagebox.showwarning("Exportar", "No hay vista previa disponible")
                return
            content = self.preview_text.get("1.0", "end-1c")
            if not content.strip():
                messagebox.showwarning("Exportar", "No hay contenido en la vista previa para exportar")
                return
            file_path = filedialog.asksaveasfilename(
                title="Exportar Vista Previa",
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Éxito", f"Vista previa exportada a:\n{file_path}")
        except Exception as e:
            logger.exception("Error exportando vista previa")
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def select_all_preview(self):
        try:
            if hasattr(self, 'preview_text'):
                self.preview_text.tag_add(tk.SEL, "1.0", tk.END)
                self.preview_text.mark_set(tk.INSERT, "1.0")
                self.preview_text.see(tk.INSERT)
                self.preview_text.focus_set()
        except Exception:
            pass

    # ========== FUNCIONES AUXILIARES PARA ACTUALIZACIÓN DE DATOS ==========
    
    def update_tree_display_realtime(self, item_id: str):
        """Actualizar la visualización del árbol en tiempo real"""
        if item_id in self.node_data:
            node = self.node_data[item_id]
            icon = "📁" if node["type"] == "folder" else "📄"
            name = node['name'] + ("/" if node["type"] == "folder" else "")
            self.tree.item(item_id, text=f"{icon} {name}")
            self.tree.set(item_id, "status", node.get("status", ""))
        
        # Forzar actualización de vista previa
        self.root.after_idle(self.update_preview)