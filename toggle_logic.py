def toggle_specs(dashboard):
    if not dashboard.is_revealed:
        # --- GO TO SPECS VIEW ---
        # 1. Hide the entire Home button group (Play, Reveal, Optimize)
        dashboard.home_controls.pack_forget()

        # 2. Show the hardware cards
        dashboard.grid_container.pack(expand=True, fill="both", padx=50)
        for card in dashboard.node_widgets.values():
            card.grid()

        # 3. Show ONLY the Hide button at the bottom
        dashboard.specs_controls.pack(side="bottom", pady=20)

        dashboard.is_revealed = True
    else:
        # --- GO BACK TO HOME VIEW ---
        # 1. Hide the specs and the single Hide button
        dashboard.grid_container.pack_forget()
        dashboard.specs_controls.pack_forget()

        # 2. Bring back the entire Home group
        dashboard.home_controls.pack(expand=True)

        dashboard.is_revealed = False
