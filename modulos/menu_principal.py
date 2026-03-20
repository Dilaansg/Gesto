# modulos/menu_principal.py
# menú principal con camino de aprendizaje por secciones
# FRONT: todo lo visual está marcado
# la lógica de navegación y progreso NO se toca

import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import progreso as p

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GESTO")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.5)}x{int(alto * 0.70)}")
        self.resizable(False, False)

        self.seccion_activa = "basico"
        self.btns_tab = {}

        self._build_ui()
        self._mostrar_seccion("basico")

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        # encabezado
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        # FRONT: título y puntaje
        ctk.CTkLabel(
            header, text="GESTO",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")

        self.lbl_puntaje = ctk.CTkLabel(
            header, text=f"Puntaje: {p.cargar()['puntaje_total']}",
            font=ctk.CTkFont(size=14), text_color="gray"
        )
        self.lbl_puntaje.pack(side="right")

        # tabs de secciones
        # FRONT: cambiar colores y estilo
        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", padx=20, pady=(15, 0))

        for seccion_id, seccion in p.CAMINO.items():
            desbloqueada = p.seccion_desbloqueada(seccion_id)
            btn = ctk.CTkButton(
                tabs,
                text=seccion["nombre"],
                font=ctk.CTkFont(size=13),
                height=34, corner_radius=8,
                fg_color=["#3B8ED0", "#1F6AA5"] if seccion_id == "basico" else "transparent",
                border_width=1,
                state="normal" if desbloqueada else "disabled",
                command=lambda s=seccion_id: self._mostrar_seccion(s)  # NO tocar
            )
            btn.pack(side="left", padx=4)
            self.btns_tab[seccion_id] = btn

        # tab próximamente — siempre visible pero bloqueada
        ctk.CTkButton(
            tabs, text="Próximamente",
            font=ctk.CTkFont(size=13),
            height=34, corner_radius=8,
            fg_color="transparent", border_width=1,
            state="disabled"
        ).pack(side="left", padx=4)

        # separador
        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(fill="x", padx=20, pady=(12, 0))

        # área scrolleable con el camino
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # separador pie
        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(fill="x", padx=20)

        # botón modo libre — siempre visible abajo
        # FRONT: cambiar estilo
        ctk.CTkButton(
            self,
            text="Modo libre — Traductor",
            font=ctk.CTkFont(size=13),
            height=38, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=self._abrir_traductor  # NO tocar
        ).pack(padx=20, pady=12, fill="x")

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _mostrar_seccion(self, seccion_id):
        # limpiar scroll
        for widget in self.scroll.winfo_children():
            widget.destroy()

        self.seccion_activa = seccion_id

        # actualizar tab activo
        for sid, btn in self.btns_tab.items():
            if p.seccion_desbloqueada(sid):
                btn.configure(
                    fg_color=["#3B8ED0", "#1F6AA5"] if sid == seccion_id else "transparent"
                )

        seccion = p.CAMINO[seccion_id]
        letras = seccion["letras"]
        progreso = p.cargar()
        todas_lecciones_vistas = all(
            f"leccion_{l}" in progreso.get("lecciones_vistas", []) for l in letras
        )

        # nodos de lecciones
        for i, letra in enumerate(letras):
            leccion_vista = f"leccion_{letra}" in progreso.get("lecciones_vistas", [])

            # la primera lección siempre disponible
            # las siguientes se desbloquean cuando la anterior fue vista
            if i == 0:
                disponible = True
            else:
                letra_anterior = letras[i - 1]
                disponible = f"leccion_{letra_anterior}" in progreso.get("lecciones_vistas", [])

            self._nodo_leccion(letra, disponible, leccion_vista, seccion_id, letras)

            # conector
            ctk.CTkFrame(self.scroll, height=1, fg_color="#333333").pack(fill="x", pady=3)

        # nodo juego 1 — se desbloquea cuando todas las lecciones están vistas
        self._nodo_juego(
            numero=1,
            disponible=todas_lecciones_vistas,
            completado=f"juego1_{seccion_id}" in progreso.get("juegos_completados", []),
            seccion_id=seccion_id,
            letras=letras
        )

        ctk.CTkFrame(self.scroll, height=1, fg_color="#333333").pack(fill="x", pady=3)

        # nodo juego 2 — se desbloquea cuando juego 1 está completado
        self._nodo_juego(
            numero=2,
            disponible=f"juego1_{seccion_id}" in progreso.get("juegos_completados", []),
            completado=f"juego2_{seccion_id}" in progreso.get("juegos_completados", []),
            seccion_id=seccion_id,
            letras=letras
        )

    def _nodo_leccion(self, letra, disponible, vista, seccion_id, letras):
        # FRONT: cambiar estilo del nodo
        nodo = ctk.CTkFrame(self.scroll, corner_radius=10)
        nodo.pack(fill="x", pady=3)

        # color según estado
        # FRONT: cambiar colores
        if vista:
            color = "#00FF99"
            estado_txt = "Vista ✓"
        elif disponible:
            color = "#00CFFF"
            estado_txt = "Disponible"
        else:
            color = "gray"
            estado_txt = "Bloqueada 🔒"

        ctk.CTkLabel(
            nodo, text=letra,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color, width=60
        ).pack(side="left", padx=16, pady=10)

        info = ctk.CTkFrame(nodo, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            info, text=f"Lección {letra} — {estado_txt}",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text="Aprende cómo hacer esta seña",
            font=ctk.CTkFont(size=11), text_color="gray", anchor="w"
        ).pack(anchor="w")

        if disponible:
            texto_btn = "Repasar" if vista else "Empezar"
            fg = "transparent" if vista else ["#3B8ED0", "#1F6AA5"]
            ctk.CTkButton(
                nodo, text=texto_btn,
                font=ctk.CTkFont(size=13),
                width=100, height=34, corner_radius=8,
                fg_color=fg, border_width=1 if vista else 0,
                command=lambda l=letra, s=seccion_id, ls=letras: self._abrir_leccion(l, s, ls)  # NO tocar
            ).pack(side="right", padx=16)

    def _nodo_juego(self, numero, disponible, completado, seccion_id, letras):
        nodo = ctk.CTkFrame(self.scroll, corner_radius=10)
        nodo.pack(fill="x", pady=3)

        if completado:
            color = "#00FF99"
            estado_txt = "Completado ✓"
        elif disponible:
            color = "#FFAA00"
            estado_txt = "Disponible"
        else:
            color = "gray"
            estado_txt = "Bloqueado 🔒"

        # FRONT: ícono del juego
        ctk.CTkLabel(
            nodo, text=f"J{numero}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color, width=60
        ).pack(side="left", padx=16, pady=12)

        info = ctk.CTkFrame(nodo, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=12)

        desc = "Identifica la seña correcta" if numero == 1 else "Haz la seña con tu mano"
        ctk.CTkLabel(
            info, text=f"Juego {numero} — {estado_txt}",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text=desc,
            font=ctk.CTkFont(size=11), text_color="gray", anchor="w"
        ).pack(anchor="w")

        if disponible:
            texto_btn = "Repasar" if completado else "Jugar"
            fg = "transparent" if completado else ["#3B8ED0", "#1F6AA5"]
            comando = (lambda s=seccion_id, ls=letras: self._abrir_juego1(s, ls)) if numero == 1 \
                else (lambda s=seccion_id, ls=letras: self._abrir_juego2(s, ls))
            ctk.CTkButton(
                nodo, text=texto_btn,
                font=ctk.CTkFont(size=13),
                width=100, height=34, corner_radius=8,
                fg_color=fg, border_width=1 if completado else 0,
                command=comando  # NO tocar
            ).pack(side="right", padx=16)

    def _abrir_leccion(self, letra, seccion_id, letras):
        self.withdraw()
        from modulos.leccion import Leccion
        app = Leccion(
            master=self,
            letra=letra,
            seccion_id=seccion_id,
            letras_seccion=letras,
            on_completado=self._on_modulo_cerrado
        )

    def _abrir_juego1(self, seccion_id, letras):
        self.withdraw()
        from modulos.juego1 import JuegoUno
        JuegoUno(
            master=self,    
            letras=letras,
            seccion_id=seccion_id,
            letras_seccion=letras,
            on_completado=self._on_modulo_cerrado
        )

    def _abrir_juego2(self, seccion_id, letras):
        self.withdraw()
        from modulos.juego2 import JuegoDos
        JuegoDos(
            master=self,     
            letras=letras,
            seccion_id=seccion_id,
            letras_seccion=letras,
            on_completado=self._on_modulo_cerrado
        )

    def _abrir_traductor(self):
        self.withdraw()
        from modulos.lsc_traductor import TraductorLSC
        traductor = TraductorLSC(master=self)
        # cuando el traductor se cierre, volver a mostrar el menú
        traductor.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_traductor(traductor))

    def _cerrar_traductor(self, traductor):
        traductor.corriendo = False
        traductor.cap.release()
        traductor.destroy()
        self.deiconify()

    def _on_modulo_cerrado(self):
        progreso = p.cargar()
        self.lbl_puntaje.configure(text=f"Puntaje: {progreso['puntaje_total']}")
        # actualizar tabs por si se desbloqueó una sección nueva
        for seccion_id, btn in self.btns_tab.items():
            if p.seccion_desbloqueada(seccion_id):
                btn.configure(state="normal")
        self._mostrar_seccion(self.seccion_activa)
        self.deiconify()


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()