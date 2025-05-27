import tkinter as tk
from tkinter import ttk

class StatusSelector:
    """Widget personalizado para seleccionar estados con iconos centrados."""
    def __init__(self, parent, callback):
        self.frame = ttk.Frame(parent)
        self.callback = callback
        self.current_status = ""
        self.statuses = {
            "✅": {"color": "#4CAF50", "name": "Completado"},
            "⬜": {"color": "#FF9800", "name": "En Proceso"},
            "❌": {"color": "#F44336", "name": "Pendiente"}
        }
        self.buttons = {}
        for status, info in self.statuses.items():
            btn = tk.Label(self.frame, text=status, cursor="hand2",
                           fg="gray", font=("Segoe UI", 12))
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, s=status: self.select_status(s))
            self.buttons[status] = btn

    def select_status(self, status):
        for btn in self.buttons.values():
            btn.config(fg="gray")
        if status == self.current_status:
            self.current_status = ""
        else:
            self.current_status = status
            self.buttons[status].config(fg=self.statuses[status]["color"])
        self.callback(self.current_status)

    def set_status(self, status):
        for btn in self.buttons.values():
            btn.config(fg="gray")
        if status in self.buttons:
            self.current_status = status
            self.buttons[status].config(fg=self.statuses[status]["color"])