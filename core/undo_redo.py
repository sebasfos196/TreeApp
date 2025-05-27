# carpetatree/core/undo_redo.py

def undo(app):
    try:
        app.text.edit_undo()
    except:
        pass

def redo(app):
    try:
        app.text.edit_redo()
    except:
        pass
