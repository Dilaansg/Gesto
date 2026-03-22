# modulos/menu_principal.py
# menú principal con camino de aprendizaje por secciones
# FRONT: todo lo visual está marcado — usar siempre C["clave"] para colores
# la lógica de navegación y progreso NO se toca

import customtkinter as ctk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import progreso as p
import config as cfg

ctk.set_appearance_mode("dark" if cfg.get_modo_oscuro() else "light")
ctk.set_default_color_theme("blue")

class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GESTO")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto  = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.55)}x{int(alto * 0.85)}")
        self.resizable(False, False)

        # paleta activa — se recarga cada vez que se abre el menú
        C = cfg.get_paleta()
        self.configure(fg_color=C["fondo"])

        self.seccion_activa = "basico"
        self.btns_tab = {}

        self._build_ui()
        self._mostrar_seccion("basico")

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        C = cfg.get_paleta()

        # ── encabezado ──────────────────────────────
        header = ctk.CTkFrame(self, fg_color=C["fondo"])
        header.pack(fill="x", padx=24, pady=(20, 0))

        # FRONT: título
        ctk.CTkLabel(
            header, text="GESTO",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=C["texto_principal"] if C["texto_principal"] != C["fondo"] else "#1a1625" #corregir color de fondo
        ).pack(side="left")

        # FRONT: botón configuración
        ctk.CTkButton(
            header, text="⚙",
            font=ctk.CTkFont(size=16),
            width=36, height=36, corner_radius=8,
            fg_color="transparent",
            border_width=1, border_color=C["borde"],
            text_color=C["acento"],
            hover_color=C["fondo_muted"],
            command=self._abrir_configuracion  # NO tocar
        ).pack(side="right")

        # FRONT: puntaje
        self.lbl_puntaje = ctk.CTkLabel(
            header,
            text=f"✦ {p.cargar()['puntaje_total']} pts",
            font=ctk.CTkFont(size=13),
            text_color=C["texto_secundario"]
        )
        self.lbl_puntaje.pack(side="right", padx=(0, 12))

        # ── tabs ────────────────────────────────────
        # FRONT: cambiar height y corner_radius para ajustar forma de las pills
        tabs = ctk.CTkFrame(self, fg_color=C["fondo"])
        tabs.pack(fill="x", padx=24, pady=(14, 0))

        for seccion_id, seccion in p.CAMINO.items():
            desbloqueada = p.seccion_desbloqueada(seccion_id)
            es_activa = seccion_id == "basico"
            btn = ctk.CTkButton(
                tabs,
                text=seccion["nombre"],
                font=ctk.CTkFont(size=12),
                height=32, corner_radius=20,
                width= 0,
                fg_color=C["primario"] if es_activa else "transparent",
                border_width=2,
                border_color=C["primario"] if desbloqueada else C["borde"],
                text_color=C["primario_fondo"] if es_activa else (C["primario"] if desbloqueada else C["texto_bloqueado"]),
                hover_color=C["fondo_muted"],
                state="normal" if desbloqueada else "disabled",
                command=lambda s=seccion_id: self._mostrar_seccion(s)  # NO tocar
            )
            btn.pack(side="left", padx=3)
            self.btns_tab[seccion_id] = btn

        # tab próximamente
        ctk.CTkButton(
            tabs, text="Próximamente",
            font=ctk.CTkFont(size=12),
            height=32, corner_radius=20,
            width=0,
            fg_color="transparent",
            border_width=2, border_color=C["borde"],
            text_color=C["texto_bloqueado"],
            state="disabled"
        ).pack(side="left", padx=3)

        # ── separador ───────────────────────────────
        ctk.CTkFrame(
            self, height=1, fg_color=C["borde_activo"]
        ).pack(fill="x", padx=24, pady=(14, 0))

        # ── área scrolleable ────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=C["fondo"],
            scrollbar_button_color=C["borde_activo"],
            scrollbar_button_hover_color=C["primario"]
        )
        self.scroll.pack(fill="both", expand=True, padx=24, pady=10)

        # ── pie ─────────────────────────────────────
        ctk.CTkFrame(
            self, height=1, fg_color=C["borde"]
        ).pack(fill="x", padx=24)

        # FRONT: botón traductor
        ctk.CTkButton(
            self,
            text="Modo libre — Traductor",
            font=ctk.CTkFont(size=13),
            height=40, corner_radius=5,
            fg_color="#7c3aed",
            text_color="#ffffff",
            hover_color="#4d12b3",
            command=self._abrir_traductor  # NO tocar
        ).pack(padx=24, pady=10, fill="x")

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _mostrar_seccion(self, seccion_id):
        C = cfg.get_paleta()

        for widget in self.scroll.winfo_children():
            widget.destroy()

        self.seccion_activa = seccion_id

        for sid, btn in self.btns_tab.items():
            if p.seccion_desbloqueada(sid):
                if sid == seccion_id:
                    btn.configure(
                        fg_color=C["primario"],
                        text_color=C["primario_fondo"],
                        border_color=C["primario"]
                    )
                else:
                    btn.configure(
                        fg_color="transparent",
                        text_color=C["primario"],
                        border_color=C["primario"]
                    )

        seccion = p.CAMINO[seccion_id]
        letras   = seccion["letras"]
        progreso = p.cargar()
        todas_lecciones_vistas = all(
            f"leccion_{l}" in progreso.get("lecciones_vistas", []) for l in letras
        )

        for i, letra in enumerate(letras):
            leccion_vista = f"leccion_{letra}" in progreso.get("lecciones_vistas", [])
            if i == 0:
                disponible = True
            else:
                disponible = f"leccion_{letras[i-1]}" in progreso.get("lecciones_vistas", [])

            self._nodo_leccion(letra, disponible, leccion_vista, seccion_id, letras)
            ctk.CTkFrame(
                self.scroll, height=1, fg_color=C["borde"]
            ).pack(fill="x", pady=2)

        self._nodo_juego(
            numero=1,
            disponible=todas_lecciones_vistas,
            completado=f"juego1_{seccion_id}" in progreso.get("juegos_completados", []),
            seccion_id=seccion_id, letras=letras
        )
        ctk.CTkFrame(
            self.scroll, height=1, fg_color=C["borde"]
        ).pack(fill="x", pady=2)
        self._nodo_juego(
            numero=2,
            disponible=f"juego1_{seccion_id}" in progreso.get("juegos_completados", []),
            completado=f"juego2_{seccion_id}" in progreso.get("juegos_completados", []),
            seccion_id=seccion_id, letras=letras
        )

    def _nodo_leccion(self, letra, disponible, vista, seccion_id, letras):
        C = cfg.get_paleta()

        # FRONT: borde de color según estado
        borde = C["completado"] if vista else (C["borde_activo"] if disponible else C["borde"])
        fondo = C["fondo_card"] if disponible else C["fondo_muted"]

        nodo = ctk.CTkFrame(
            self.scroll, corner_radius=12,
            fg_color=fondo,
            border_width=2, border_color=borde
        )
        nodo.pack(fill="x", pady=3)

        # FRONT: color de la letra según estado
        letra_frame = ctk.CTkFrame(
            nodo,
            width=48, height=48,
            corner_radius=10,
            fg_color=C["completado"] if vista else (C["disponible"] if disponible else C["bloqueado"]),
            border_width=0
         )
        letra_frame.pack(side="left", padx=14, pady=14)
        letra_frame.pack_propagate(False)  # evita que el frame se encoja

        ctk.CTkLabel(
            letra_frame, text=letra,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f3f0ff"  # blanco sobre el fondo de color
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(nodo, fg_color=fondo, border_width=0)
        info.pack(side="left", fill="both", expand=True, pady=10)

        estado_txt = "Vista ✓" if vista else ("Disponible" if disponible else "Bloqueada 🔒")
        ctk.CTkLabel(
            info, text=f"Lección {letra} — {estado_txt}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["texto_principal"] if disponible else C["texto_bloqueado"],
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text="Aprende cómo hacer esta seña",
            font=ctk.CTkFont(size=11),
            text_color=C["texto_secundario"] if disponible else C["texto_bloqueado"],
            anchor="w"
        ).pack(anchor="w")

        if disponible:
            texto_btn = "Repasar" if vista else "Empezar"
            ctk.CTkButton(
                nodo, text=texto_btn,
                font=ctk.CTkFont(size=12),
                width=90, height=32, corner_radius=20,
                fg_color="transparent" if vista else C["primario"],
                border_width=2 if vista else 0,
                border_color=C["primario"],
                text_color=C["primario"] if vista else C["primario_fondo"],
                hover_color=C["fondo_muted"],
                command=lambda l=letra, s=seccion_id, ls=letras: self._abrir_leccion(l, s, ls)  # NO tocar
            ).pack(side="right", padx=16)

    def _nodo_juego(self, numero, disponible, completado, seccion_id, letras):
        C = cfg.get_paleta()

        borde = C["completado"] if completado else (C["advertencia"] if disponible else C["borde"])
        fondo = C["fondo_card"] if disponible else C["fondo_muted"]

        nodo = ctk.CTkFrame(
            self.scroll, corner_radius=12,
            fg_color=fondo,
            border_width=1, border_color=borde
        )
        nodo.pack(fill="x", pady=3)

        iconos = {1: "🎮", 2: "🤟"}
        color  = C["completado"] if completado else (C["advertencia"] if disponible else C["bloqueado"])

        icono_frame = ctk.CTkFrame(
            nodo,
            width=48, height=48,
            corner_radius=10,
            fg_color=C["completado"] if completado else (C["advertencia"] if disponible else C["bloqueado"]),
        )
        icono_frame.pack(side="left", padx=14, pady=14)
        icono_frame.pack_propagate(False)

        ctk.CTkLabel(
            icono_frame, text=iconos[numero],
            font=ctk.CTkFont(size=24),
            text_color="#f3f0ff"
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(nodo, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=12)

        estado_txt = "Completado ✓" if completado else ("Disponible" if disponible else "Bloqueado 🔒")
        desc = "Identifica la seña correcta" if numero == 1 else "Haz la seña con tu mano"

        ctk.CTkLabel(
            info, text=f"Juego {numero} — {estado_txt}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["texto_principal"] if disponible else C["texto_bloqueado"],
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text=desc,
            font=ctk.CTkFont(size=11),
            text_color=C["texto_secundario"] if disponible else C["texto_bloqueado"],
            anchor="w"
        ).pack(anchor="w")

        if disponible:
            texto_btn = "Repasar" if completado else "Jugar"
            comando = (
                lambda s=seccion_id, ls=letras: self._abrir_juego1(s, ls)
            ) if numero == 1 else (
                lambda s=seccion_id, ls=letras: self._abrir_juego2(s, ls)
            )
            ctk.CTkButton(
                nodo, text=texto_btn,
                font=ctk.CTkFont(size=12),
                width=90, height=32, corner_radius=20,
                fg_color="transparent" if completado else C["primario"],
                border_width=1 if completado else 0,
                border_color=C["primario"],
                text_color=C["primario"] if completado else C["primario_fondo"],
                hover_color=C["fondo_muted"],
                command=comando  # NO tocar
            ).pack(side="right", padx=16)

    def _abrir_configuracion(self):
        self.withdraw()
        from modulos.configuracion import Configuracion
        Configuracion(master=self, on_cerrar=self._on_modulo_cerrado)

    def _abrir_leccion(self, letra, seccion_id, letras):
        self.withdraw()
        from modulos.leccion import Leccion
        Leccion(master=self, letra=letra, seccion_id=seccion_id,
                letras_seccion=letras, on_completado=self._on_modulo_cerrado)

    def _abrir_juego1(self, seccion_id, letras):
        self.withdraw()
        from modulos.juego1 import JuegoUno
        JuegoUno(master=self, letras=letras, seccion_id=seccion_id,
                 letras_seccion=letras, on_completado=self._on_modulo_cerrado)

    def _abrir_juego2(self, seccion_id, letras):
        self.withdraw()
        from modulos.juego2 import JuegoDos
        JuegoDos(master=self, letras=letras, seccion_id=seccion_id,
                 letras_seccion=letras, on_completado=self._on_modulo_cerrado)

    def _abrir_traductor(self):
        self.withdraw()
        from modulos.lsc_traductor import TraductorLSC
        traductor = TraductorLSC(master=self)
        traductor.protocol("WM_DELETE_WINDOW",
                           lambda: self._cerrar_traductor(traductor))

    def _cerrar_traductor(self, traductor):
        traductor.corriendo = False
        traductor.cap.release()
        traductor.destroy()
        self.deiconify()

    def _on_modulo_cerrado(self):
        C = cfg.get_paleta()
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=C["fondo"])
        self.btns_tab = {}
        self._build_ui()
        progreso = p.cargar()
        self.lbl_puntaje.configure(text=f"✦ {progreso['puntaje_total']} pts")
        self.configure(fg_color=C["fondo"])
        for seccion_id, btn in self.btns_tab.items():
            if p.seccion_desbloqueada(seccion_id):
                btn.configure(state="normal")
        self._mostrar_seccion(self.seccion_activa)
        self.deiconify()


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()