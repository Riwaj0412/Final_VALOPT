def toggle_specs(dashboard):
    """
    Handles the logic for showing and hiding the hardware specifications grid.
    
    Args:
        dashboard: The DashboardHUD instance containing the widgets and state.
    """
    # Check if the specs are currently hidden
    if not dashboard.is_revealed:
        # PHASE 1: REVEAL
        # Loop through all cards stored in the dictionary and bring them onto the grid
        for card_key in dashboard.node_widgets:
            card = dashboard.node_widgets[card_key]
            # .grid() restores the widget to its assigned row/column position
            card.grid() 
        
        # Update the button text to reflect the next possible action
        dashboard.reveal_btn.configure(text="[ HIDE SPECS ]")
        
        # Update the state tracker
        dashboard.is_revealed = True
        
    else:
        # PHASE 2: HIDE
        # Loop through all cards and remove them from the visual layout
        for card_key in dashboard.node_widgets:
            card = dashboard.node_widgets[card_key]
            # .grid_remove() hides the widget but remembers its grid settings
            card.grid_remove()
            
        # Update the button text back to the original state
        dashboard.reveal_btn.configure(text="[ REVEAL SPECS ]")
        
        # Update the state tracker
        dashboard.is_revealed = False

# This logic ensures that the 'node_widgets' dictionary created in 
# specs_factory.py is the single source of truth for what gets toggled.