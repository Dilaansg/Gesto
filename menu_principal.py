import customtkinter as ctk
import subprocess
import sys
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GESTO")
        self.geometry("600x500")
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)  # empieza transparente

        self._build_ui()
        self.after(100, self._fade_in)  # animacion al iniciar
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ─────────────────────────────────────────────────
    # INTERFAZ (acá pueden modificar)
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        ctk.CTkLabel(
            self, text="GESTO",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#00CFFF"
        ).pack(pady=(40, 0))

        ctk.CTkLabel(
            self, text="Lengua de Señas Colombiana",
            font=ctk.CTkFont(size=14), text_color="gray"
        ).pack(pady=(0, 40))

        # acá pueden modificar los botones — cambiar texto, colores, íconos. hay que buscar una organización
        # y minimalista, procuremos que se sienta como una aplicación moderna.
        # NO tocar command=
        self.btn_j1 = ctk.CTkButton(
            self, text="Juego 1",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55, corner_radius=12,
            command=lambda: self._lanzar("juego1\juego_1\interfaz_juego1.py", self.btn_j1, "Juego 1")
        )
        self.btn_j1.pack(padx=80, fill="x", pady=8)

        self.btn_j2 = ctk.CTkButton(
            self, text="Juego 2",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55, corner_radius=12,
            command=lambda: self._lanzar("juego2\juego2.py", self.btn_j2, "Juego 2")
        )
        self.btn_j2.pack(padx=80, fill="x", pady=8)
        #Hay que implementar nombres creativos para los juegos, por el momento lo dejo como juego1 y juego2.

        self.btn_tr = ctk.CTkButton(
            self, text="Traductor LSC",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55, corner_radius=12,
            command=lambda: self._lanzar("lsc_traductor.py", self.btn_tr, "Traductor LSC")
        )
        self.btn_tr.pack(padx=80, fill="x", pady=8)


        #Este es el pie de pagina, diría que esto está bien, aunque se puede quitar jaajaj
        ctk.CTkLabel(
            self, text="GESTO 2026",
            font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(side="bottom", pady=15)

    # ─────────────────────────────────────────────────
    # ANIMACIONES (se pueden mejorar, se ven económicas, solo que por practicidad son así.)
    # ─────────────────────────────────────────────────
    def _fade_in(self, alpha=0.0):
        """Aumenta la opacidad de 0 a 1 gradualmente."""
        alpha += 0.05  # velocidad de la animación, entre mas alta más rápida
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(20, lambda: self._fade_in(alpha))  # intervalo de la "animación"

    def _fade_out(self, callback, alpha=1.0):
        """Reduce la opacidad de 1 a 0 y ejecuta callback al terminar."""
        alpha -= 0.05  
        self.attributes("-alpha", alpha)
        if alpha > 0:
            self.after(20, lambda: self._fade_out(callback, alpha))  # intervalo de la "animación"
        else:
            callback()

    def _cerrar(self):
        """Fade out antes de cerrar la app."""
        self._fade_out(self.destroy)

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _lanzar(self, archivo, boton, texto_original):
        """Bloquea botones, fade out, abre módulo, fade in al volver."""
        self._bloquear_botones()
        boton.configure(text="Abriendo")
        self._fade_out(lambda: self._abrir_modulo(boton, archivo, texto_original))

    def _abrir_modulo(self, boton, archivo, texto_original):
        self.withdraw()
        self.attributes("-alpha", 1.0)  # Reset alpha para cuando vuelva

        def correr():
            proceso = subprocess.Popen([sys.executable, archivo])
            proceso.wait()
            self.after(0, lambda: self._volver(boton, texto_original))

        threading.Thread(target=correr, daemon=True).start()

    def _volver(self, boton, texto_original):
        """Restaura botón, muestra menú con fade in."""
        boton.configure(text=texto_original)
        self._desbloquear_botones()
        self.deiconify()
        self.attributes("-alpha", 0.0)
        self._fade_in()

    def _bloquear_botones(self):
        for btn in [self.btn_j1, self.btn_j2, self.btn_tr]:
            btn.configure(state="disabled")

    def _desbloquear_botones(self):
        for btn in [self.btn_j1, self.btn_j2, self.btn_tr]:
            btn.configure(state="normal")


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()

