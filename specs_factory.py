import ux
import engine


def build_specs_grid(parent, node_dict):
    # Fetch LIVE data (Now includes the 'os' key)
    report = engine.get_system_report()

    # Integrated list with your emojis + dynamic OS
    nodes = [
        ("CORE PROCESSOR", "🖥️", report['cpu']),
        ("SYSTEM MEMORY", "⚡", report['ram']),
        ("GRAPHICS CARD", "🎮", report['gpu']),
        ("OS KERNEL", "💻", report['os']),
        ("DISPLAY MONITOR", "📺", engine.get_monitor_specs()),
        ("ENGINE STATUS", "🚀", "ACTIVE")
    ]

    parent.grid_columnconfigure((0, 1), weight=1)

    for i, (title, icon, value) in enumerate(nodes):
        # Uses your custom SpecNode class from ux.py
        node = ux.SpecNode(parent, title, icon, value)
        node.grid(row=i//2, column=i % 2, padx=20, pady=15, sticky="nsew")

        # IMPORTANT: Hide nodes initially so the [ REVEAL ] button works
        node.grid_remove()
        node_dict[title] = node
