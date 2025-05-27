# carpetatree/utils/markdown_highlighter.py

import re

class MarkdownHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()

    def setup_tags(self):
        self.text_widget.tag_configure("header", foreground="#569cd6", font=("Segoe UI", 12, "bold"))
        self.text_widget.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.text_widget.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        self.text_widget.tag_configure("code", background="#2d2d30", foreground="#ce9178", font=("Consolas", 9))
        self.text_widget.tag_configure("link", foreground="#4fc3f7", underline=True)
        self.text_widget.tag_configure("list", foreground="#dcdcaa")

    def highlight(self):
        content = self.text_widget.get("1.0", "end")
        for tag in ["header", "bold", "italic", "code", "link", "list"]:
            self.text_widget.tag_remove(tag, "1.0", "end")

        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"

            if line.startswith('#'):
                self.text_widget.tag_add("header", line_start, line_end)

            for match in re.finditer(r'\*\*(.*?)\*\*', line):
                self.text_widget.tag_add("bold", f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
            for match in re.finditer(r'\*(.*?)\*', line):
                self.text_widget.tag_add("italic", f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
            for match in re.finditer(r'`(.*?)`', line):
                self.text_widget.tag_add("code", f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
            for match in re.finditer(r'\[([^\]]+)\]\([^)]+\)', line):
                self.text_widget.tag_add("link", f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
            if line.strip().startswith(('-', '*', '+')):
                self.text_widget.tag_add("list", line_start, line_end)