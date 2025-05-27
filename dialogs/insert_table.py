# carpetatree/dialogs/insert_table.py

import tkinter as tk

def show_insert_table(app):
    dialog = tk.Toplevel(app.root)
    dialog.title("Insertar Tabla")
    dialog.geometry("300x150")
    dialog.transient(app.root)
    dialog.grab_set()

    tk.Label(dialog, text="Filas:").pack(anchor="w", padx=10, pady=5)
    row_spin = tk.Spinbox(dialog, from_=2, to=10, value=3, width=10)
    row_spin.pack(padx=10, pady=5)

    tk.Label(dialog, text="Columnas:").pack(anchor="w", padx=10, pady=5)
    col_spin = tk.Spinbox(dialog, from_=2, to=10, value=3, width=10)
    col_spin.pack(padx=10, pady=5)

    def insert():
        rows, cols = int(row_spin.get()), int(col_spin.get())
        header = "| " + " | ".join([f"Columna {i+1}" for i in range(cols)]) + " |\n"
        separator = "| " + " | ".join(["---"] * cols) + " |\n"
        body = ""
        for i in range(rows - 1):
            body += "| " + " | ".join([f"Dato {i+1}.{j+1}" for j in range(cols)]) + " |\n"
        app.text.insert(tk.INSERT, header + separator + body)
        dialog.destroy()

    tk.Button(dialog, text="Crear Tabla", command=insert).pack(pady=10)
