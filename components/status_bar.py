# carpetatree/components/status_bar.py

from tkinter import ttk
from datetime import datetime

def setup_status_bar(app):
    app.status_frame = ttk.Frame(app.root)
    app.status_frame.pack(side="bottom", fill="x", padx=5, pady=2)

    app.status_project = ttk.Label(app.status_frame, text="Proyecto: Sin título")
    app.status_project.pack(side="left")

    ttk.Separator(app.status_frame, orient="vertical").pack(side="left", padx=10, fill="y")

    app.status_stats = ttk.Label(app.status_frame, text="Archivos: 0 | Completados: 0")
    app.status_stats.pack(side="left")

    ttk.Separator(app.status_frame, orient="vertical").pack(side="left", padx=10, fill="y")

    app.status_editor = ttk.Label(app.status_frame, text="Línea: 1, Col: 1")
    app.status_editor.pack(side="left")

    app.status_saved = ttk.Label(app.status_frame, text="💾 Guardado")
    app.status_saved.pack(side="right")

    app.status_time = ttk.Label(app.status_frame, text="")
    app.status_time.pack(side="right", padx=10)

    update_clock(app)

def update_clock(app):
    current_time = datetime.now().strftime("%H:%M:%S")
    app.status_time.config(text=current_time)
    app.root.after(1000, lambda: update_clock(app))