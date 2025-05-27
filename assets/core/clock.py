# carpetatree/core/clock.py
from datetime import datetime

def update_clock(app):
    current_time = datetime.now().strftime("%H:%M:%S")
    app.status_time.config(text=current_time)
    app.root.after(1000, lambda: update_clock(app))
