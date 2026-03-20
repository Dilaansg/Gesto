# modulos/juego1.py
# juego 1 — identifica la seña
# recibe TODAS las letras de la sección, no una sola
# FRONT: todo lo visual está marcado

import customtkinter as ctk
from PIL import Image
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import progreso as p

RUTA_IMAGENES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recursos", "images_database_procesadas"
)

PREGUNTAS_PARA_PASAR = 8
ACIERTOS_PARA_PASAR = 6

class JuegoUno(ctk.CTkToplevel):
    def __init__(self, master, letras, seccion_id, letras_seccion, on_completado):
        super().__init__(master)
        self.title("Juego 1 — Identifica la seña")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.5)}x{int(alto * 0.85)}")
        self.resizable(False, False)

        # ── estado (NO tocar) ──
        self.letras = letras
        self.seccion_id = seccion_id
        self.letras_seccion = letras_seccion
        self.on_completado = on_completado
        self.aciertos = 0
        self.preguntas_hechas = 0
        self.letra_actual = None
        self.letra_anterior = None  # evita repetir la misma letra dos veces seguidas
        self.botones = []
        # ──────────────────────

        self._build_ui()
        self._nueva_pregunta()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(
            header, text=f"Juego 1 — {p.CAMINO[self.seccion_id]['nombre']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        self.lbl_progreso = ctk.CTkLabel(
            header, text=f"0 / {PREGUNTAS_PARA_PASAR}",
            font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.lbl_progreso.pack(side="right")

        self.barra = ctk.CTkProgressBar(self, height=6, corner_radius=4)
        self.barra.set(0)
        self.barra.pack(fill="x", padx=20, pady=(8, 0))

        self.lbl_feedback = ctk.CTkLabel(
            self, text="¿Qué letra es esta seña?",
            font=ctk.CTkFont(size=15)
        )
        self.lbl_feedback.pack(pady=(15, 5))

        self.lbl_imagen = ctk.CTkLabel(self, text="", width=240, height=240)
        self.lbl_imagen.pack(pady=(0, 15))

        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(padx=20, fill="x")

        for i in range(4):
            btn = ctk.CTkButton(
                frame_btns, text="",
                font=ctk.CTkFont(size=22, weight="bold"),
                height=60, corner_radius=10,
                command=lambda idx=i: self._verificar(idx)  # NO tocar
            )
            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            self.botones.append(btn)

        frame_btns.grid_columnconfigure(0, weight=1)
        frame_btns.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            self, text="← Volver al menú",
            font=ctk.CTkFont(size=12),
            height=32, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=self._cerrar  # NO tocar
        ).pack(pady=(15, 0))

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _nueva_pregunta(self):
        # elegir letra distinta a la anterior
        opciones_disponibles = [l for l in self.letras if l != self.letra_anterior]
        self.letra_actual = random.choice(opciones_disponibles)
        self.letra_anterior = self.letra_actual

        # distractores
        pool = [l for l in self.letras if l != self.letra_actual]
        distractores = random.sample(pool, min(3, len(pool)))

        # completar distractores con letras de otras secciones si hacen falta
        if len(distractores) < 3:
            todas = [l for sec in p.CAMINO.values() for l in sec["letras"]
                     if l != self.letra_actual and l not in distractores]
            distractores += random.sample(todas, 3 - len(distractores))

        opciones = distractores + [self.letra_actual]
        random.shuffle(opciones)

        self._cargar_imagen(self.letra_actual)

        for i, btn in enumerate(self.botones):
            btn.configure(
                text=opciones[i],
                state="normal",
                fg_color=["#3B8ED0", "#1F6AA5"]
            )
            btn._letra = opciones[i]

        self.lbl_feedback.configure(
            text="¿Qué letra es esta seña?",
            text_color="#FFFFFF"
        )

    def _cargar_imagen(self, letra):
        ruta_carpeta = os.path.join(RUTA_IMAGENES, letra)
        if not os.path.exists(ruta_carpeta):
            self.lbl_imagen.configure(text=f"Sin imagen\npara {letra}", text_color="gray")
            return
        imagenes = [f for f in os.listdir(ruta_carpeta)
                    if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not imagenes:
            self.lbl_imagen.configure(text=f"Sin imagen\npara {letra}", text_color="gray")
            return
        ruta = os.path.join(ruta_carpeta, random.choice(imagenes))
        img = Image.open(ruta).resize((240, 240))
        img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 240))
        self.lbl_imagen.configure(image=img_ctk)
        self.lbl_imagen.image = img_ctk

    def _verificar(self, idx):
        for btn in self.botones:
            btn.configure(state="disabled")

        letra_sel = self.botones[idx]._letra
        self.preguntas_hechas += 1

        if letra_sel == self.letra_actual:
            self.aciertos += 1
            self.botones[idx].configure(fg_color="#00AA55")
            self.lbl_feedback.configure(text="¡Correcto!", text_color="#00FF99")
        else:
            self.botones[idx].configure(fg_color="#AA2222")
            for btn in self.botones:
                if btn._letra == self.letra_actual:
                    btn.configure(fg_color="#00AA55")
            self.lbl_feedback.configure(
                text=f"Era la '{self.letra_actual}'", text_color="#FF4444"
            )

        self.lbl_progreso.configure(text=f"{self.preguntas_hechas} / {PREGUNTAS_PARA_PASAR}")
        self.barra.set(self.preguntas_hechas / PREGUNTAS_PARA_PASAR)

        if self.preguntas_hechas >= PREGUNTAS_PARA_PASAR:
            self.after(1200, self._fin_ronda)
        else:
            self.after(1200, self._nueva_pregunta)

    def _fin_ronda(self):
        aprobado = self.aciertos >= ACIERTOS_PARA_PASAR
        if aprobado:
            p.completar_juego(self.seccion_id, 1)
            self.lbl_feedback.configure(
                text=f"¡Aprobado! {self.aciertos}/{PREGUNTAS_PARA_PASAR} — pasando al Juego 2...",
                text_color="#00FF99"
            )
            self.after(1500, self._ir_juego2)
        else:
            self.lbl_feedback.configure(
                text=f"Necesitas {ACIERTOS_PARA_PASAR}/{PREGUNTAS_PARA_PASAR} — intentá de nuevo",
                text_color="#FF4444"
            )
            # resetear contadores y letra anterior para nueva ronda
            self.aciertos = 0
            self.preguntas_hechas = 0
            self.letra_anterior = None
            self.barra.set(0)
            self.after(2000, self._nueva_pregunta)

    def _ir_juego2(self):
        from modulos.juego2 import JuegoDos
        JuegoDos(
            master=self.master,
            letras=self.letras,
            seccion_id=self.seccion_id,
            letras_seccion=self.letras_seccion,
            on_completado=self.on_completado
        )
        self.destroy()

    def _cerrar(self):
        self.destroy()
        self.on_completado()


if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.withdraw()
    def dummy(): pass
    app = JuegoUno(
        master=raiz,
        letras=["A", "E", "I", "O", "U"],
        seccion_id="basico",
        letras_seccion=["A", "E", "I", "O", "U"],
        on_completado=dummy
    )
    raiz.mainloop()