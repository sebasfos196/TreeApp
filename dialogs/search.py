# carpetatree/dialogs/search.py

import tkinter as tk

class SearchDialog:
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.text_widget = text_widget
        self.create_dialog()

    def create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Buscar y Reemplazar")
        self.dialog.geometry("400x150")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        tk.Label(self.dialog, text="Buscar:").pack(anchor="w", padx=10, pady=5)
        self.search_entry = tk.Entry(self.dialog, width=50)
        self.search_entry.pack(padx=10, pady=5)

        tk.Label(self.dialog, text="Reemplazar:").pack(anchor="w", padx=10, pady=5)
        self.replace_entry = tk.Entry(self.dialog, width=50)
        self.replace_entry.pack(padx=10, pady=5)

        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Buscar", command=self.find_text).pack(side="left", padx=5)
        tk.Button(button_frame, text="Reemplazar", command=self.replace_text).pack(side="left", padx=5)
        tk.Button(button_frame, text="Reemplazar todo", command=self.replace_all).pack(side="left", padx=5)

        self.search_entry.focus()
        self.search_entry.bind("<Return>", lambda e: self.find_text())

    def find_text(self):
        term = self.search_entry.get()
        if term:
            pos = self.text_widget.search(term, tk.INSERT, tk.END)
            if pos:
                end_pos = f"{pos}+{len(term)}c"
                self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
                self.text_widget.tag_add(tk.SEL, pos, end_pos)
                self.text_widget.mark_set(tk.INSERT, pos)
                self.text_widget.see(pos)

    def replace_text(self):
        if self.text_widget.tag_ranges(tk.SEL):
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_widget.insert(tk.INSERT, self.replace_entry.get())

    def replace_all(self):
        term = self.search_entry.get()
        repl = self.replace_entry.get()
        if term:
            content = self.text_widget.get("1.0", tk.END)
            new = content.replace(term, repl)
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", new)
