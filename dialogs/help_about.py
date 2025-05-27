# carpetatree/dialogs/help_about.py

from tkinter import Toplevel, Text, messagebox

def show_shortcuts_dialog(app):
    shortcuts_text = """🔧 ATAJOS DE TECLADO

Archivo:
• Ctrl+N - Nuevo archivo
• Ctrl+S - Guardar proyecto
• Ctrl+O - Abrir proyecto
• Ctrl+Shift+S - Guardar como

Edición:
• Ctrl+Z - Deshacer
• Ctrl+Y - Rehacer
• Ctrl+F - Buscar y reemplazar

Vista:
• F11 - Modo zen
• Ctrl+Shift+N - Nueva carpeta

Navegación:
• Click derecho - Menú contextual
• Doble click - Expandir/contraer
"""

    window = Toplevel(app.root)
    window.title("⌨️ Atajos de Teclado")
    window.geometry("400x300")
    text = Text(window, wrap="word", font=("Consolas", 10))
    text.pack(fill="both", expand=True, padx=10, pady=10)
    text.insert("1.0", shortcuts_text)
    text.config(state="disabled")

def show_markdown_guide(app):
    guide_text = """📝 GUÍA MARKDOWN

Encabezados:
# Encabezado 1
## Encabezado 2
### Encabezado 3

Formato:
**negrita**, *cursiva*, `código`

Enlaces:
[Texto](https://url)

Imágenes:
![desc](ruta.jpg)

Listas:
- Elemento
1. Numerado

Tablas:
| A | B |
|---|---|
| x | y |

Código:

Citas:
> texto citado
"""

    window = Toplevel(app.root)
    window.title("📝 Guía Markdown")
    window.geometry("500x400")
    text = Text(window, wrap="word", font=("Consolas", 10))
    text.pack(fill="both", expand=True, padx=10, pady=10)
    text.insert("1.0", guide_text)
    text.config(state="disabled")

def show_about_dialog(app):
    about_text = """🚀 WORKSPACE JUMPER v4 PRO

Organizador visual con editor Markdown integrado.

Características:
• Árbol de proyecto
• Editor Markdown
• Estados de avance
• Tags por nodo
• Vista previa integrada
• Exportación a HTML y TXT
• Auto-guardado

Versión: 4.0
Hecho en Python + Tkinter

¡Gracias por usar Workspace Jumper!
"""
    messagebox.showinfo("Acerca de", about_text)
