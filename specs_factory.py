import ux
import engine


def build_specs_grid(parent, node_dict):
    report = engine.get_system_report()

    nodes = [
        ("CORE PROCESSOR", "🖥️", report['cpu']),
        ("SYSTEM MEMORY", "⚡", report['ram']),
        ("GRAPHICS CARD", "🎮", report['gpu']),
        ("DISPLAY MONITOR", "📺", engine.get_monitor_specs()),
        ("ENGINE STATUS", "🚀", "ACTIVE")
    ]

    parent.grid_columnconfigure((0, 1), weight=1)

    for i, (title, icon, value) in enumerate(nodes):
        node = ux.SpecNode(parent, title, icon, value)
        node.grid(row=i//2, column=i % 2, padx=10, pady=8, sticky="nsew")
        node_dict[title] = node
