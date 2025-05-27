# carpetatree/components/layout.py

import tkinter as tk
from tkinter import ttk

def setup_main_layout(app):
    app.main_paned = tk.PanedWindow(app.root, sashwidth=6, sashrelief="ridge",
                                     showhandle=True, orient="horizontal")
    app.main_paned.pack(fill="both", expand=True, padx=5, pady=5)

    app.left_frame = ttk.Frame(app.main_paned)
    app.center_frame = ttk.Frame(app.main_paned)
    app.right_frame = ttk.Frame(app.main_paned)

    app.main_paned.add(app.left_frame, minsize=200)
    app.main_paned.add(app.center_frame, minsize=400)
    app.main_paned.add(app.right_frame, minsize=300)

    weights = app.config.get("panel_weights", [300, 600, 500])
    app.root.after(100, lambda: apply_panel_weights(app, weights))

def apply_panel_weights(app, weights):
    try:
        total_width = app.root.winfo_width()
        if total_width > 100:
            pos1 = weights[0]
            pos2 = weights[0] + weights[1]
            app.main_paned.sash_place(0, pos1, 0)
            app.main_paned.sash_place(1, pos2, 0)
    except:
        pass