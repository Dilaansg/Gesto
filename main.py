# main.py
import customtkinter as ctk
import sys
import os

def resource_path(relative_path):
    """Obtiene la ruta correcta tanto en desarrollo como en .exe"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)                       #esto es para empaquetar los .py y que funcione en .exe

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    from modulos.menu_principal import MenuPrincipal
    app = MenuPrincipal()
    app.mainloop()