import customtkinter as ctk
import styles


class ManualMenu(ctk.CTkFrame):
    def __init__(self, master, back_command):
        # Set the frame to cover the entire container
        super().__init__(master, fg_color="transparent")

        # 1. Title
        self.title_label = ctk.CTkLabel(
            self,
            text="MANUAL SETTINGS",
            font=styles.FONT_IMPACT_LG,
            text_color=styles.VALO_RED
        )
        self.title_label.pack(pady=(40, 20))

        # 2. Button Container
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # NVIDIA Button
        self.create_menu_button(
            self.button_frame, "NVIDIA Control Panel", "#76B900")

        # Windows Button
        self.create_menu_button(self.button_frame, "WINDOWS", "#808080")

        # In Game Button
        self.create_menu_button(self.button_frame, "IN GAME", styles.VALO_RED)

        # 3. PROMINENT BACK BUTTON
        self.back_btn = ctk.CTkLabel(
            self,
            text="[ BACK TO HOME ]",
            font=("Arial", 16, "bold"),     # Made larger and bold
            text_color="#FF4655",           # High-visibility Valorant Red
            cursor="hand2"
        )
        self.back_btn.pack(side="bottom", pady=40)

        # Link the click to the back_command
        self.back_btn.bind("<Button-1>", lambda e: self.on_back(back_command))

    def create_menu_button(self, parent, text, color):
        btn = ctk.CTkButton(
            parent,
            text=text,
            width=500,
            height=70,
            fg_color="transparent",
            border_color=color,
            border_width=2,
            text_color="white",
            font=styles.FONT_IMPACT_SM if hasattr(
                styles, 'FONT_IMPACT_SM') else ("Impact", 24),
            hover_color="#1a1a1a"
        )
        btn.pack(pady=10)

    def on_back(self, back_command):
        """Clears this menu and runs the back function"""
        self.destroy()  # Removes the manual menu frame
        back_command()  # Calls the function to rebuild the main optimize menu
