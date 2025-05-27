# carpetatree/core/tree_app.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

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
    set_node_status as set_node_status_func
)

class TreeAppV4:
    def __init__(self, root):
        self.root = root
        self.root.title("Workspace Interactivo Jumper v4 Pro")
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config

        self.node_data = {}
        self.current_node = None
        self.project_file = None
        self.unsaved_changes = False
        self.history = []
        self.history_index = -1

        self.style = ThemedStyle(self.config["theme"], self.config["font_size"])
        self.root.configure(bg=self.style.themes[self.config["theme"]]["bg"])

        self.root.geometry(self.config["window_geometry"])
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        setup_menu_bar(self)
        setup_toolbar(self)
        setup_main_layout(self)
        setup_tree_panel(self)
        setup_editor_panel(self)
        setup_preview_panel(self)
        setup_status_bar(self)

        update_clock(self)
        setup_autosave(self)

        if self.config["last_project"] and os.path.exists(self.config["last_project"]):
            self.load_project(self.config["last_project"])
        else:
            self.load_initial_project()

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

    def _save_to_file(self, file_path):
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
            messagebox.showerror("Error", f"No se pudo guardar el proyecto:\n{str(e)}")

    def load_project(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.node_data = data.get("node_data", {})
            self.project_file = file_path
            self.unsaved_changes = False
            
            # 🔥 MIGRAR DATOS ANTIGUOS A NUEVOS CAMPOS
            self._migrate_legacy_data()
            
            # Reconstruir árbol
            self._rebuild_tree()
            
            messagebox.showinfo("Cargado", f"Proyecto cargado:\n{file_path}")
            if hasattr(self, 'update_status'):
                self.update_status()
            if hasattr(self, 'update_preview'):
                self.update_preview()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el proyecto:\n{str(e)}")

    def _migrate_legacy_data(self):
        """Migrar datos de proyectos antiguos a nuevos campos"""
        for node_id, node_data in self.node_data.items():
            # Si no tiene los nuevos campos, crearlos desde content
            if "markdown_short" not in node_data:
                content = node_data.get("content", "")
                name = node_data.get("name", "Sin nombre")
                
                # Extraer primera línea como markdown resumido
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
                
                # Establecer nuevos campos
                node_data["markdown_short"] = first_line
                node_data["explanation"] = ""
                node_data["code"] = ""

    def _rebuild_tree(self):
        """Reconstruir árbol con formato mejorado"""
        self.tree.delete(*self.tree.get_children())

        for node_id, node_data in self.node_data.items():
            icon = "📁" if node_data["type"] == "folder" else "📄"
            status = node_data.get("status", "")
            # Cambiar 🕓 por ⬜ al cargar
            if status == "🕓":
                status = "⬜"
                node_data["status"] = "⬜"  # Actualizar en los datos también
            
            name = node_data['name']
            # Mostrar carpetas con "/" al final
            if node_data["type"] == "folder":
                name += "/"
            
            label = f"{icon} {name}"
            self.tree.insert("", "end", iid=node_id, text=label, values=[status])

    def load_initial_project(self):
        """Inicializar proyecto con TODOS los campos necesarios"""
        if hasattr(self, 'tree'):
            self.tree.delete(*self.tree.get_children())

        # 🔥 CREAR NODO RAÍZ CON TODOS LOS CAMPOS NECESARIOS
        self.node_data = {
            "root_folder": {
                "name": "Root",
                "type": "folder",
                "status": "",
                "content": "# Root\n\nCarpeta raíz del proyecto...",  # Campo legacy
                "markdown_short": "# Root",                              # NUEVO: Campo para markdown resumido
                "explanation": "Carpeta raíz del proyecto",              # NUEVO: Campo para explicaciones
                "code": "",                                              # NUEVO: Campo para código
                "tags": [],
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
        }

        # Insertar solo la carpeta Root con formato mejorado
        if hasattr(self, 'tree'):
            self.tree.insert("", "end", iid="root_folder", text="📁 Root/", values=[""])
            self.tree.item("root_folder", open=True)
            self.tree.selection_set("root_folder")
            self.current_node = "root_folder"

    def duplicate_node_to_target(self, source_id, target_id):
        """Duplicar nodo a ubicación específica"""
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
        # Mostrar carpetas con "/" al final
        display_name = new_name + ("/" if original["type"] == "folder" else "")
        self.tree.insert(target_id, "end", iid=new_id,
                       text=f"{icon} {display_name}",
                       values=[original["status"]])
        self.mark_unsaved()

    def check_unsaved_changes(self):
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
                messagebox.showerror("Error", f"Error al exportar texto:\n{str(e)}")

    def export_node(self):
        export_selected_node(self)

    def show_project_stats(self):
        from dialogs.stats_dialog import show_stats_dialog
        show_stats_dialog(self)

    def show_search_dialog(self):
        # 🔥 BUSCAR EN EL EDITOR CORRECTO
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

    def on_closing(self):
        if self.check_unsaved_changes():
            self.config["window_geometry"] = self.root.geometry()
            self.config_manager.save_config()
            self.root.destroy()

    def undo(self):
        try:
            # 🔥 USAR EL EDITOR ACTIVO
            text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
            if text_widget:
                text_widget.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            # 🔥 USAR EL EDITOR ACTIVO
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

    def show_about(self):
        show_about_dialog(self)

    def show_shortcuts(self):
        show_shortcuts_dialog(self)

    def show_markdown_guide(self):
        show_markdown_guide(self)

    def on_select(self, event):
        """Función COMPLETA de selección con carga de TODOS los campos"""
        node_id = self.tree.focus()
        if node_id in self.node_data:
            # Guardar contenido actual antes de cambiar
            save_current_content(self)
            
            # Establecer nuevo nodo actual
            self.current_node = node_id
            
            # Cargar contenido legacy (para compatibilidad)
            load_node_content(self, node_id)
            
            # 🔥 CARGAR CONTENIDO EN LOS NUEVOS EDITORES MÚLTIPLES
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
                
                # 🔥 COMPATIBILIDAD: Asegurar que text apunte a code_text
                self.text = self.code_text
                
                # Actualizar números de línea del código
                if hasattr(self, 'update_code_line_numbers'):
                    self.root.after_idle(self.update_code_line_numbers)

    def mark_unsaved(self):
        self.unsaved_changes = True
        if hasattr(self, 'status_saved'):
            self.status_saved.config(text="💾 Sin guardar")
    
    def validate_links(self):
        messagebox.showinfo("Validador de Enlaces", "Función de validación de enlaces en desarrollo.")

    def show_preferences(self):
        messagebox.showinfo("Configuración", "Panel de configuración en desarrollo.")

    def add_file(self):
        from logic.node_manager import add_file
        add_file(self)

    def add_folder(self):
        from logic.node_manager import add_folder
        add_folder(self)

    def on_theme_change(self, event=None):
        new_theme = self.theme_var.get()
        self.config["theme"] = new_theme
        self.config_manager.save_config()
        self.style = ThemedStyle(new_theme, self.config["font_size"])
        self.root.configure(bg=self.style.themes[new_theme]["bg"])

    def insert_markdown(self, prefix, suffix=""):
        try:
            # 🔥 USAR EL EDITOR ACTIVO (código por defecto)
            text_widget = getattr(self, 'code_text', getattr(self, 'text', None))
            if text_widget:
                selection = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                text_widget.insert(tk.INSERT, f"{prefix}{selection}{suffix}")
        except tk.TclError:
            if hasattr(self, 'code_text'):
                self.code_text.insert(tk.INSERT, f"{prefix}{suffix}")

    def update_name(self, event=None):
        """Actualizar nombre con formato mejorado"""
        if self.current_node and self.current_node in self.node_data:
            new_name = self.name_entry.get().strip()
            if new_name:
                self.node_data[self.current_node]["name"] = new_name
                self.node_data[self.current_node]["modified"] = datetime.now().isoformat()
                
                icon = "📁" if self.node_data[self.current_node]["type"] == "folder" else "📄"
                # Mostrar carpetas con "/" al final
                display_name = new_name + ("/" if self.node_data[self.current_node]["type"] == "folder" else "")
                label = f"{icon} {display_name}"
                
                self.tree.item(self.current_node, text=label)
                self.mark_unsaved()
                
                # Actualizar vista previa inmediatamente
                self.update_preview()

    def on_text_change(self, event=None):
        """Manejar cambios de texto en editores legacy"""
        if hasattr(self, 'update_line_numbers'):
            self.update_line_numbers()
        self.mark_unsaved()

    def on_mousewheel(self, event):
        """Manejar scroll del mouse en editores legacy"""
        if hasattr(self, 'line_numbers'):
            self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

    def scroll_text(self, *args):
        """Scroll sincronizado legacy"""
        if hasattr(self, 'text') and hasattr(self, 'line_numbers'):
            self.text.yview(*args)
            self.line_numbers.yview(*args)

    def scrollbar_set(self, *args):
        """Configurar scrollbar legacy"""
        if hasattr(self, 'text') and hasattr(self, 'line_numbers'):
            self.text.yview_moveto(args[0])
            self.line_numbers.yview_moveto(args[0])

    def update_line_numbers(self):
        """Actualizar números de línea legacy"""
        if hasattr(self, 'line_numbers') and hasattr(self, 'text'):
            self.line_numbers.config(state='normal')
            self.line_numbers.delete("1.0", "end")
            line_count = int(self.text.index('end').split('.')[0]) - 1
            line_numbers = "\n".join(str(i) for i in range(1, line_count + 1))
            self.line_numbers.insert("1.0", line_numbers)
            self.line_numbers.config(state='disabled')

    def update_preview(self):
        """Usar la nueva función mejorada de vista previa"""
        update_preview_improved(self)

    def update_status(self):
        if hasattr(self, "status_stats"):
            files = [n for n in self.node_data.values() if n["type"] == "file"]
            total = len(files)
            done = sum(1 for f in files if f.get("status") == "✅")
            in_progress = sum(1 for f in files if f.get("status") == "⬜")  # Cambiar 🕓 por ⬜
            self.status_stats.config(text=f"Archivos: {total} | Completados: {done} | En proceso: {in_progress}")

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
        # Mostrar carpetas con "/" al final
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
    
    def rename_node(self):
        rename_node_func(self)

    def set_node_status(self, status):
        # Cambiar 🕓 por ⬜ antes de establecer
        if status == "🕓":
            status = "⬜"
        set_node_status_func(self, status)

    def clear_editor(self):
        """Limpiar TODOS los editores"""
        if hasattr(self, 'name_entry'):
            self.name_entry.delete(0, "end")
        
        # Limpiar editores múltiples
        if hasattr(self, 'markdown_short'):
            self.markdown_short.delete("1.0", "end")
        if hasattr(self, 'explanation_text'):
            self.explanation_text.delete("1.0", "end")
        if hasattr(self, 'code_text'):
            self.code_text.delete("1.0", "end")
            
        # Limpiar editor legacy
        if hasattr(self, 'text'):
            self.text.delete("1.0", "end")
            
        # Limpiar vista previa
        if hasattr(self, 'preview_text'):
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.config(state="disabled")

    def change_theme(self, theme_name):
        self.config["theme"] = theme_name
        self.style = ThemedStyle(theme_name, self.config["font_size"])
        self.root.configure(bg=self.style.themes[theme_name]["bg"])
        self.config_manager.save_config()

    def change_font_size(self, size):
        self.config["font_size"] = size
        self.style = ThemedStyle(self.config["theme"], size)

        # Actualizar fuentes en TODOS los editores
        font_code = ("Consolas", size)
        font_text = ("Segoe UI", size)
        
        if hasattr(self, 'code_text'):
            self.code_text.configure(font=font_code)
        if hasattr(self, 'code_line_numbers'):
            self.code_line_numbers.configure(font=font_code)
        if hasattr(self, 'markdown_short'):
            self.markdown_short.configure(font=font_text)
        if hasattr(self, 'explanation_text'):
            self.explanation_text.configure(font=font_text)
        if hasattr(self, 'preview_text'):
            self.preview_text.configure(font=font_code)
            
        # Legacy
        if hasattr(self, 'text'):
            self.text.configure(font=font_code)
        if hasattr(self, 'line_numbers'):
            self.line_numbers.configure(font=font_code)

        self.config_manager.save_config()

    def force_preview_update(self):
        """Forzar actualización inmediata de la vista previa"""
        if hasattr(self, 'update_preview'):
            self.root.after_idle(self.update_preview)

    def show_tree_importer(self):
        """Mostrar diálogo de importación de estructura de árbol"""
        show_tree_structure_importer(self)

    def export_preview_to_txt(self):
        """Exportar vista previa a archivo TXT"""
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
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def select_all_preview(self):
        """Seleccionar todo el contenido de la vista previa"""
        try:
            if hasattr(self, 'preview_text'):
                self.preview_text.tag_add(tk.SEL, "1.0", tk.END)
                self.preview_text.mark_set(tk.INSERT, "1.0")
                self.preview_text.see(tk.INSERT)
                self.preview_text.focus_set()
        except:
            pass