# carpetatree/dialogs/stats_dialog.py

import tkinter as tk
from tkinter import ttk
from logic.stats_generator import generate_project_stats

def show_stats_dialog(app):
    stats_window = tk.Toplevel(app.root)
    stats_window.title("📊 Estadísticas del Proyecto")
    stats_window.geometry("500x400")
    stats_window.transient(app.root)

    text_widget = tk.Text(stats_window, wrap="word", font=("Consolas", 10))
    scrollbar = ttk.Scrollbar(stats_window, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    stats = generate_project_stats(app)
    text_widget.insert("1.0", stats)
    text_widget.config(state="disabled")
