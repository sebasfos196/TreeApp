# carpetatree/core/theme.py

from tkinter import ttk

class ThemedStyle(ttk.Style):
    def __init__(self, theme="dark", font_size=10):
        super().__init__()
        self.theme = theme
        self.font_size = font_size
        self.themes = {
            "dark": {
                "bg": "#1e1e1e", "fg": "#d4d4d4", "select_bg": "#264f78",
                "entry_bg": "#2d2d30", "button_bg": "#0e639c", "accent": "#007acc"
            },
            "light": {
                "bg": "#ffffff", "fg": "#000000", "select_bg": "#add6ff",
                "entry_bg": "#ffffff", "button_bg": "#e1e1e1", "accent": "#0066cc"
            },
            "soft": {
                "bg": "#f5f5f5", "fg": "#333333", "select_bg": "#c8e6c9",
                "entry_bg": "#ffffff", "button_bg": "#e8f5e8", "accent": "#4caf50"
            },
            "github": {
                "bg": "#0d1117", "fg": "#c9d1d9", "select_bg": "#21262d",
                "entry_bg": "#21262d", "button_bg": "#238636", "accent": "#58a6ff"
            },
            "vscode": {
                "bg": "#1e1e1e", "fg": "#cccccc", "select_bg": "#094771",
                "entry_bg": "#2d2d30", "button_bg": "#0e639c", "accent": "#007acc"
            }
        }
        self.configure_style()

    def configure_style(self):
        colors = self.themes.get(self.theme, self.themes["dark"])

        self.configure("TFrame", background=colors["bg"])
        self.configure("TLabel", background=colors["bg"], foreground=colors["fg"],
                       font=("Segoe UI", self.font_size))
        self.configure("Treeview", background=colors["bg"], foreground=colors["fg"],
                       fieldbackground=colors["bg"], font=("Segoe UI", self.font_size))
        self.map("Treeview", background=[("selected", colors["select_bg"])])
        self.configure("TButton", background=colors["button_bg"], foreground=colors["fg"])
        self.configure("TEntry", fieldbackground=colors["entry_bg"],
                       foreground=colors["fg"], insertcolor=colors["fg"])
        self.configure("TCombobox", fieldbackground=colors["entry_bg"],
                       background=colors["bg"], foreground=colors["fg"])
