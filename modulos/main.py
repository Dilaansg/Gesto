# main.py
import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    from modulos.menu_principal import MenuPrincipal
    app = MenuPrincipal()
    app.mainloop()