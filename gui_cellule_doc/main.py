import customtkinter as ctk
from Controller.Controller import Controller


if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("green")
    app = Controller()
    app.run()
