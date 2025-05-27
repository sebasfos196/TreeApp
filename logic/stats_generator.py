# carpetatree/logic/stats_generator.py

from collections import Counter

def generate_project_stats(app):
    total = len(app.node_data)
    files = [n for n in app.node_data.values() if n["type"] == "file"]
    folders = [n for n in app.node_data.values() if n["type"] == "folder"]

    status_counter = Counter(f["status"] or "—" for f in files)
    tag_counter = Counter(tag for f in files for tag in f.get("tags", []))
    avg_length = sum(len(f["content"]) for f in files) / len(files) if files else 0

    lines = [
        "📊 ESTADÍSTICAS DEL PROYECTO",
        "=============================",
        f"Total de nodos: {total}",
        f"Total archivos: {len(files)}",
        f"Total carpetas: {len(folders)}",
        "",
        "📌 Estados:",
    ]
    for status, count in status_counter.items():
        label = {
            "✅": "Completado",
            "🕓": "En Proceso",
            "❌": "Pendiente",
            "—": "Sin Estado"
        }.get(status, status)
        lines.append(f"  {label:12}: {count}")

    lines.append("")
    lines.append("🏷️  Tags más usados:")
    for tag, count in tag_counter.most_common(10):
        lines.append(f"  #{tag:<15}: {count} vez{'' if count == 1 else 'es'}")

    lines.append("")
    lines.append(f"📝 Longitud media de archivos: {avg_length:.1f} caracteres")
    return "\n".join(lines)
