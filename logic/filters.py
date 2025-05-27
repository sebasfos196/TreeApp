# carpetatree/logic/filters.py

def filter_tree(app):
    filter_text = app.filter_var.get().lower()
    status_filter = app.status_filter.get()

    for node_id in app.tree.get_children():
        apply_filter_recursive(app, node_id, filter_text, status_filter)

def apply_filter_recursive(app, node_id, filter_text, status_filter):
    if node_id not in app.node_data:
        return False

    data = app.node_data[node_id]
    name_match = filter_text in data["name"].lower()
    content_match = filter_text in data["content"].lower()
    tag_match = any(filter_text in tag.lower() for tag in data.get("tags", []))

    status_match = (status_filter == "Todos" or
                    status_filter.endswith(data["status"]))

    text_match = name_match or content_match or tag_match

    has_matching_child = False
    for child in app.tree.get_children(node_id):
        if apply_filter_recursive(app, child, filter_text, status_filter):
            has_matching_child = True

    show_node = (text_match and status_match) or has_matching_child

    if show_node:
        app.tree.reattach(node_id, '', 'end')
    else:
        app.tree.detach(node_id)

    return show_node
