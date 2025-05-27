# carpetatree/dialogs/tree_structure_importer.py

import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime

class TreeStructureImporter:
    """Diálogo para importar estructura de carpetas y archivos desde texto"""
    
    def __init__(self, parent, app):
        self.app = app
        self.parent_node = app.tree.focus() or ""
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Importar Estructura de Árbol")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350)
        y = (self.dialog.winfo_screenheight() // 2) - (250)
        self.dialog.geometry(f"700x500+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        
        # Header
        header_frame = ttk.Frame(self.dialog)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(header_frame, text="🌳 Importar Estructura de Árbol", 
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        # Información
        info_frame = ttk.LabelFrame(self.dialog, text="Instrucciones")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        info_text = """Pega aquí la estructura de carpetas y archivos en formato de árbol.
Formatos soportados:
• Formato Windows (tree /f): +---carpeta  |   archivo.txt
• Formato ASCII: └──carpeta/  │   └──archivo.txt
• Formato simple: carpeta/  archivo.txt (con indentación)
• Formato con comentarios: archivo.py # Comentario descriptivo

Ejemplo:
+---AdaptiveStrategyLayer
|   |   AdaptiveStrategyLayer.txt
|   +---evolution-engine
|   +---feedback-loops
└───ClientInterface
    |   ClientInterface.txt
    +---frontend"""
        
        ttk.Label(info_frame, text=info_text, justify="left", 
                 wraplength=650).pack(padx=10, pady=5)
        
        # Área de texto para pegar estructura
        text_frame = ttk.LabelFrame(self.dialog, text="Estructura de Árbol")
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Texto con scrollbar
        text_container = tk.Frame(text_frame)
        text_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_area = tk.Text(text_container, wrap="none", 
                                font=("Consolas", 9))
        self.text_area.pack(side="left", fill="both", expand=True)
        
        text_scrollbar_v = ttk.Scrollbar(text_container, orient="vertical", 
                                        command=self.text_area.yview)
        text_scrollbar_v.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=text_scrollbar_v.set)
        
        text_scrollbar_h = ttk.Scrollbar(text_frame, orient="horizontal", 
                                        command=self.text_area.xview)
        text_scrollbar_h.pack(side="bottom", fill="x")
        self.text_area.config(xscrollcommand=text_scrollbar_h.set)
        
        # Botones
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="📋 Ejemplo", 
                  command=self.load_example).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="🔍 Vista Previa", 
                  command=self.preview_structure).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="✅ Importar", 
                  command=self.import_structure).pack(side="right", padx=5)
        
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self.dialog.destroy).pack(side="right", padx=5)
        
        # Foco inicial
        self.text_area.focus()
        
    def load_example(self):
        """Cargar ejemplo de estructura"""
        example = """AdaptiveStrategyLayer/
|   AdaptiveStrategyLayer.txt # Documentación principal del sistema
|   
+---evolution-engine/ # Motor de evolución de estrategias
+---feedback-loops/ # Bucles de retroalimentación
+---interfaces/ # Interfaces del sistema
+---model-training/ # Entrenamiento de modelos
+---mutation-orchestrator/ # Orquestador de mutaciones
+---visualization/ # Herramientas de visualización
CI/
ClientInterface/
|   ClientInterface.txt # Interfaz principal del cliente
|   
+---frontend/
|   +---assets/ # Recursos estáticos
|   +---components/ # Componentes reutilizables
|   +---modules/
|   |   +---runtime-control/ # Control de ejecución
|   |   +---visual-programming/ # Programación visual
|   +---services/ # Servicios del frontend
|   +---src/ # Código fuente
|   +---utils/ # Utilidades
|   +---views/ # Vistas de la aplicación
+---frontend-engine/ # Motor del frontend"""
        
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", example)
        
    def preview_structure(self):
        """Vista previa de la estructura a importar"""
        content = self.text_area.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Vista Previa", "No hay contenido para previsualizar")
            return
            
        try:
            structure = self.parse_tree_structure(content)
            preview_text = self.format_preview(structure)
            
            # Ventana de vista previa
            preview_dialog = tk.Toplevel(self.dialog)
            preview_dialog.title("Vista Previa - Estructura a Importar")
            preview_dialog.geometry("600x400")
            preview_dialog.transient(self.dialog)
            
            # Área de texto para vista previa
            preview_frame = tk.Frame(preview_dialog)
            preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            preview_text_widget = tk.Text(preview_frame, wrap="none", 
                                         font=("Consolas", 9), state="disabled")
            preview_text_widget.pack(side="left", fill="both", expand=True)
            
            preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", 
                                            command=preview_text_widget.yview)
            preview_scrollbar.pack(side="right", fill="y")
            preview_text_widget.config(yscrollcommand=preview_scrollbar.set)
            
            # Mostrar vista previa
            preview_text_widget.config(state="normal")
            preview_text_widget.insert("1.0", preview_text)
            preview_text_widget.config(state="disabled")
            
            # Botón cerrar
            ttk.Button(preview_dialog, text="Cerrar", 
                      command=preview_dialog.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar estructura:\n{str(e)}")
    
    def format_preview(self, structure, indent=0):
        """Formatear estructura para vista previa"""
        result = ""
        for item in structure:
            name = item['name']
            item_type = item['type']
            icon = "📁" if item_type == "folder" else "📄"
            
            result += "  " * indent + f"{icon} {name}"
            if item_type == "folder":
                result += "/"
            
            # Mostrar comentario si existe
            if item.get('markdown'):
                result += f" # {item['markdown']}"
            
            result += "\n"
            
            if 'children' in item:
                result += self.format_preview(item['children'], indent + 1)
        
        return result
    
    def import_structure(self):
        """Importar la estructura al árbol"""
        content = self.text_area.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("Importar", "No hay contenido para importar")
            return
            
        try:
            structure = self.parse_tree_structure(content)
            
            if not structure:
                messagebox.showwarning("Importar", "No se pudo interpretar la estructura")
                return
            
            # Confirmar importación
            count = self.count_items(structure)
            result = messagebox.askyesno(
                "Confirmar Importación", 
                f"Se van a crear {count['folders']} carpetas y {count['files']} archivos.\n¿Continuar?"
            )
            
            if result:
                self.create_structure(structure, self.parent_node)
                self.app.mark_unsaved()
                self.app.update_preview()
                messagebox.showinfo("Éxito", "Estructura importada correctamente")
                self.dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar estructura:\n{str(e)}")
    
    def count_items(self, structure):
        """Contar elementos en la estructura"""
        count = {"folders": 0, "files": 0}
        
        for item in structure:
            if item['type'] == "folder":
                count["folders"] += 1
                if 'children' in item:
                    child_count = self.count_items(item['children'])
                    count["folders"] += child_count["folders"]
                    count["files"] += child_count["files"]
            else:
                count["files"] += 1
        
        return count
    
    def parse_tree_structure(self, content):
        """Parsear estructura de árbol desde texto - VERSIÓN UNIFICADA"""
        lines = content.split('\n')
        structure = []
        stack = [{"children": structure, "level": -1}]
        
        for line in lines:
            if not line.strip():
                continue
                
            # Determinar nivel de indentación y limpiar línea
            cleaned_line, level, markdown = self.parse_line_advanced(line)
            
            if not cleaned_line:
                continue
                
            # Determinar si es carpeta o archivo con MÚLTIPLES CRITERIOS
            is_folder = self.detect_folder_vs_file(cleaned_line, line)
            
            item = {
                "name": cleaned_line.rstrip('/'),
                "type": "folder" if is_folder else "file",
                "markdown": markdown  # Agregar markdown detectado
            }
            
            if is_folder:
                item["children"] = []
            
            # Encontrar el padre correcto según el nivel
            while len(stack) > 1 and stack[-1]["level"] >= level:
                stack.pop()
            
            # Agregar item al padre actual
            stack[-1]["children"].append(item)
            
            # Si es carpeta, agregar al stack
            if is_folder:
                stack.append({"children": item["children"], "level": level})
        
        return structure
    
    def detect_folder_vs_file(self, cleaned_name, original_line):
        """Detectar si es carpeta o archivo usando múltiples criterios"""
        
        # CRITERIO 1: Termina con "/"
        if cleaned_name.endswith('/'):
            return True
            
        # CRITERIO 2: Tiene extensión típica de archivo
        file_extensions = ['.ts', '.rs', '.js', '.py', '.txt', '.md', '.json', '.html', '.css', '.jsx', '.tsx', '.vue', '.php', '.java', '.cpp', '.c', '.h']
        if any(cleaned_name.lower().endswith(ext) for ext in file_extensions):
            return False
            
        # CRITERIO 3: Contiene punto en el nombre (probablemente archivo)
        if '.' in cleaned_name and not cleaned_name.startswith('.'):
            return False
            
        # CRITERIO 4: Línea contiene marcadores de carpeta
        folder_markers = ['├──', '└──', '+---', '\\---']
        if any(marker in original_line for marker in folder_markers) and not any(ext in cleaned_name.lower() for ext in ['.txt', '.md', '.js', '.ts', '.py']):
            return True
            
        # CRITERIO 5: Si no tiene extensión y no termina con "/", asumir carpeta
        if '.' not in cleaned_name:
            return True
            
        # Por defecto, asumir archivo
        return False
    
    def parse_line_advanced(self, line):
        """Parsear línea con detección de markdown y nivel avanzado"""
        original_line = line
        markdown = ""
        
        # NUEVO: Detectar nivel por cantidad de # al inicio
        level_from_hash = 0
        stripped = line.lstrip()
        if stripped.startswith('#'):
            level_from_hash = 0
            for char in stripped:
                if char == '#':
                    level_from_hash += 1
                else:
                    break
            # Remover los # del inicio
            line = stripped[level_from_hash:].strip()
            level_from_hash -= 1  # Ajustar porque empezamos en 0
        
        # Extraer comentario markdown (después de # en la línea)
        if '#' in line and not line.startswith('#'):
            parts = line.split('#', 1)
            line = parts[0]  # Parte antes del #
            if len(parts) > 1:
                markdown = parts[1].strip()  # Comentario después del #
        
        # Contar indentación inicial
        level = 0
        for char in line:
            if char in [' ', '\t', '|', '│']:
                level += 1
            else:
                break
        
        # Usar nivel por # si se detectó
        if level_from_hash > 0:
            level = level_from_hash
        
        # Limpiar caracteres especiales del formato tree
        cleaned = line.strip()
        
        # Remover caracteres de formato tree AVANZADO
        tree_chars = ['├──', '└──', '+---', '\\---', '│', '|', '+', '\\', '├', '└', '─', '┌', '┐', '┘', '┌', '┤', '┬', '┴', '┼']
        for char in tree_chars:
            cleaned = cleaned.replace(char, '')
        
        # Limpiar espacios adicionales
        cleaned = cleaned.strip()
        
        # Si la línea tiene solo caracteres de formato, ignorar
        if not cleaned or all(c in '│├└─+\\|-  \t┌┐┘┤┬┴┼' for c in cleaned):
            return "", level, markdown
        
        # Ajustar nivel basado en caracteres especiales si no hay #
        if level_from_hash == 0 and any(marker in original_line for marker in ['├──', '└──', '+---', '\\---']):
            level = len(original_line) - len(original_line.lstrip('│ \t|'))
        
        return cleaned, level // 4 if level_from_hash == 0 else level, markdown
    
    def create_structure(self, structure, parent_id):
        """Crear estructura en el árbol con TODOS los campos necesarios"""
        for item in structure:
            # Generar ID único
            new_id = f"{item['type']}_{len(self.app.node_data)}_{item['name']}_{datetime.now().strftime('%H%M%S%f')}"
            
            # Crear contenido inicial con markdown detectado
            name_part = item['name'].split('.')[0] if '.' in item['name'] else item['name']
            
            # Definir contenido base
            if item.get('markdown'):
                content = f"# {name_part}\n\n{item['markdown']}"
                markdown_short = f"# {name_part}"
                explanation = item['markdown']
            else:
                if item['type'] == "folder":
                    content = f"# {name_part}\n\nCarpeta creada automáticamente..."
                    markdown_short = f"# {name_part}"
                    explanation = "Carpeta creada automáticamente desde importación de estructura"
                else:
                    content = f"# {name_part}\n\nArchivo creado automáticamente..."
                    markdown_short = f"# {name_part}"
                    explanation = "Archivo creado automáticamente desde importación de estructura"
            
            # 🔥 CREAR NODO CON TODOS LOS CAMPOS NECESARIOS
            self.app.node_data[new_id] = {
                "name": item['name'],
                "type": item['type'],
                "status": "",
                "content": content,                    # Campo legacy
                "markdown_short": markdown_short,     # NUEVO: Campo para markdown resumido
                "explanation": explanation,           # NUEVO: Campo para explicaciones
                "code": "",                          # NUEVO: Campo para código
                "tags": [],
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
            
            # Insertar en el árbol
            icon = "📁" if item['type'] == "folder" else "📄"
            display_name = item['name'] + ("/" if item['type'] == "folder" else "")
            
            self.app.tree.insert(parent_id, "end", iid=new_id, 
                               text=f"{icon} {display_name}", values=[""])
            
            # Si es carpeta y tiene hijos, crear recursivamente
            if item['type'] == "folder" and 'children' in item:
                self.create_structure(item['children'], new_id)

def show_tree_structure_importer(app):
    """Mostrar diálogo de importación de estructura"""
    TreeStructureImporter(app.root, app)