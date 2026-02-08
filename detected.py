import customtkinter as ctk
import engine
import ux


class DetectedScreen(ctk.CTkFrame):
    def __init__(self, master_app, on_click):
        super().__init__(master_app, fg_color="#0f1923")
        self.on_click = on_click
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        game_found = engine.check_valorant_presence()
        status_text = "VALORANT DETECTED" if game_found else "VALORANT NOT FOUND"
        status_color = "#00ff7f" if game_found else "#ff4655"

        self.lbl = ctk.CTkLabel(self, text=status_text,
                                font=ux.get_font(50), text_color=status_color)
        self.lbl.pack(pady=(350, 10))

        self.sub = ctk.CTkLabel(
            self, text="CLICK ANYWHERE TO CONTINUE", font=ux.get_font(18), text_color="white")
        self.sub.pack()

        # Bind clicks to progress to dashboard
        self.bind("<Button-1>", lambda e: self.on_click())
        self.lbl.bind("<Button-1>", lambda e: self.on_click())
        self.sub.bind("<Button-1>", lambda e: self.on_click())
