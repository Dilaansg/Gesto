# modulos/leccion.py
# pantalla de aprendizaje — muestra la imagen de la seña y explica cómo hacerla
# FRONT: todo lo visual está marcado

import customtkinter as ctk
from PIL import Image
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import progreso as p
import config as cfg

RUTA_IMAGENES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recursos", "images_database_procesadas"
)

class Leccion(ctk.CTkToplevel):
    def __init__(self, master, letra, seccion_id, letras_seccion, on_completado):
        super().__init__(master)
        self.title(f"Lección — Letra {letra}")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto  = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.55)}x{int(alto * 0.85)}")
        self.resizable(False, False)

        # ── estado (NO tocar) ──
        self.letra          = letra
        self.seccion_id     = seccion_id
        self.letras_seccion = letras_seccion
        self.on_completado  = on_completado
        self.mini_exitoso   = False
        # ──────────────────────

        C = cfg.get_paleta()
        self.configure(fg_color=C["fondo"])

        self._build_ui()
        self._marcar_vista()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        C = cfg.get_paleta()

        pos   = self.letras_seccion.index(self.letra) + 1
        total = len(self.letras_seccion)

        # ── encabezado ──────────────────────────────
        header = ctk.CTkFrame(self, fg_color=C["fondo"])
        header.pack(fill="x", padx=24, pady=(18, 0))

        # FRONT: nombre de la sección
        ctk.CTkLabel(
            header,
            text=f"{p.CAMINO[self.seccion_id]['nombre']}",
            font=ctk.CTkFont(size=13),
            text_color=C["texto_secundario"]
        ).pack(side="left")

        # FRONT: posición en la sección
        ctk.CTkLabel(
            header,
            text=f"{pos} / {total}",
            font=ctk.CTkFont(size=13),
            text_color=C["texto_secundario"]
        ).pack(side="right")

        # ── barra de progreso de la sección ─────────
        # FRONT: cambiar colores de la barra
        barra_prog = ctk.CTkProgressBar(
            self, height=6, corner_radius=4,
            progress_color=C["primario"],
            fg_color=C["fondo_muted"]
        )
        barra_prog.set(pos / total)
        barra_prog.pack(fill="x", padx=24, pady=(8, 16))

        # ── letra centrada arriba ────────────────────
        letra_frame = ctk.CTkFrame(
            self,
            width=90, height=90,
            corner_radius=18,
            fg_color=C["primario"],
            border_width=0
        )
        letra_frame.pack(pady=(0, 16))
        letra_frame.pack_propagate(False)
        ctk.CTkLabel(
            letra_frame, text=self.letra,
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self,
            text="¿Cómo hacer esta seña?",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(pady=(0, 16))

        # ── contenido central: imagen izquierda, recuadros derecha ──
        contenido = ctk.CTkFrame(self, fg_color=C["fondo"])
        contenido.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        # columna izquierda — imagen con borde redondeado
        col_izq = ctk.CTkFrame(
            contenido,
            corner_radius=16,
            fg_color=C["fondo_card"],
            border_width=2,
            border_color=C["borde_activo"]
        )
        col_izq.pack(side="left", padx=(0, 16), pady=4, fill="y")

        self.lbl_imagen = ctk.CTkLabel(col_izq, text="", width=260, height=280)
        self.lbl_imagen.pack(padx=16, pady=16)
        self._cargar_imagen()

        # columna derecha — instrucciones + tip apilados
        col_der = ctk.CTkFrame(contenido, fg_color=C["fondo"], width=370)
        col_der.pack(side="left", fill="y", pady=4)
        col_der.pack_propagate(False)

        # recuadro instrucciones
        frame_instrucciones = ctk.CTkFrame(
            col_der,
            corner_radius=14,
            fg_color=C["fondo_card"],
            border_width=2,
            border_color=C["borde"]
        )
        frame_instrucciones.pack(fill="both", expand= True, pady=(0, 12))

        ctk.CTkLabel(
            frame_instrucciones,
            text="Instrucciones",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=C["texto_principal"], anchor="w"
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            frame_instrucciones,
            text=self._get_descripcion(self.letra),
            font=ctk.CTkFont(size=15),
            text_color=C["texto_secundario"],
            wraplength=240, justify="left", anchor="w"
        ).pack(anchor="w", padx=16, pady=(0, 14))

        # recuadro tip
        frame_tip = ctk.CTkFrame(
            col_der,
            corner_radius=14,
            fg_color="#FFCF4B",
            border_width=2,
            border_color=C["advertencia"],
            height=40
        )
        frame_tip.pack(fill="x")

        tip_header = ctk.CTkFrame(frame_tip, fg_color="transparent")
        tip_header.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            tip_header, text="⚠️ Consejo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(side="left")

        ctk.CTkLabel(
            frame_tip,
            text=self._get_tip(self.letra),
            font=ctk.CTkFont(size=12),
            text_color=C["texto_principal"],
            wraplength=240, justify="left", anchor="w"
        ).pack(anchor="w", padx=16, pady=(0, 14))

        # ── barra inferior con botones ───────────────
        ctk.CTkFrame(
            self, height=1, fg_color=C["borde"]
        ).pack(fill="x", side = "bottom")

        btn_frame = ctk.CTkFrame(self, fg_color=C["fondo"])
        btn_frame.pack(side="bottom", fill="x", padx=24, pady=14)

        # columna izquierda — botón anterior
        idx_actual   = self.letras_seccion.index(self.letra)
        hay_anterior = idx_actual > 0

        ctk.CTkButton(
            btn_frame, text="‹  Anterior",
            font=ctk.CTkFont(size=13),
            width=130, height=48, corner_radius=22,
            fg_color="transparent",
            border_width=1, border_color=C["borde"],
            text_color=C["texto_secundario"] if hay_anterior else C["texto_bloqueado"],
            hover_color=C["fondo_muted"],
            state="normal" if hay_anterior else "disabled",
            command=self._anterior  # NO tocar
        ).pack(side="left")

        # centro — botón INTÉNTALO
        self.btn_intentalo = ctk.CTkButton(
            btn_frame, text="¡Inténtalo!",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48, corner_radius=22, width=200,
            fg_color=C["completado"],
            text_color="#ffffff",
            hover_color=C["primario"],
            command=self._abrir_mini_practica  # NO tocar
        )
        self.btn_intentalo.pack(side="left", expand=True)

        # derecha — botón siguiente
        hay_siguiente = idx_actual + 1 < len(self.letras_seccion)
        texto_sig = "Siguiente  ›" if hay_siguiente else "Finalizar  ✓"
        ctk.CTkButton(
            btn_frame, text=texto_sig,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130, height=48, corner_radius=22,
            fg_color=C["primario"],
            text_color="#ffffff",
            hover_color=C["acento"],
            command=self._siguiente  # NO tocar
        ).pack(side="right")
    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _marcar_vista(self):
        progreso = p.cargar()
        clave = f"leccion_{self.letra}"
        if "lecciones_vistas" not in progreso:
            progreso["lecciones_vistas"] = []
        if clave not in progreso["lecciones_vistas"]:
            progreso["lecciones_vistas"].append(clave)
            progreso["puntaje_total"] += 5
            p.guardar(progreso)

    def _abrir_mini_practica(self):
        from modulos.juego2 import MiniPractica
        MiniPractica(
            master=self,
            letra=self.letra,
            on_exitoso=self._mini_practica_exitosa
        )

    def _mini_practica_exitosa(self):
        self.mini_exitoso = True
        C = cfg.get_paleta()
        self.btn_intentalo.configure(
            text="¡Logrado! ✓",
            fg_color=C["completado"],
            text_color="white",
            state="disabled"
        )

    def _anterior(self):
        idx = self.letras_seccion.index(self.letra)
        if idx > 0:
            self.letra = self.letras_seccion[idx - 1]
            self.title(f"Lección — Letra {self.letra}")
            self.mini_exitoso = False
            self._marcar_vista()
            for widget in self.winfo_children():
                widget.destroy()
            self._build_ui()

    def _siguiente(self):
        idx_actual    = self.letras_seccion.index(self.letra)
        hay_siguiente = idx_actual + 1 < len(self.letras_seccion)
        if hay_siguiente:
            self.letra = self.letras_seccion[idx_actual + 1]
            self.title(f"Lección — Letra {self.letra}")
            self.mini_exitoso = False
            self._marcar_vista()
            for widget in self.winfo_children():
                widget.destroy()
            self._build_ui()
        else:
            self.destroy()
            self.on_completado()

    def _cerrar(self):
        self.destroy()
        self.on_completado()

    def _cargar_imagen(self):
        ruta_carpeta = os.path.join(RUTA_IMAGENES, self.letra)
        if not os.path.exists(ruta_carpeta):
            self.lbl_imagen.configure(
                text=f"Sin imagen\npara {self.letra}", text_color="gray"
            )
            return
        imagenes = [f for f in os.listdir(ruta_carpeta)
                    if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not imagenes:
            self.lbl_imagen.configure(
                text=f"Sin imagen\npara {self.letra}", text_color="gray"
            )
            return
        ruta = os.path.join(ruta_carpeta, random.choice(imagenes))
        img  = Image.open(ruta).resize((260, 280))
        img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(260, 280))
        self.lbl_imagen.configure(image=img_ctk)
        self.lbl_imagen.image = img_ctk

    # ─────────────────────────────────────────────────
    # CONTENIDO — FRONT: ampliar descripciones y tips
    # ─────────────────────────────────────────────────
    def _get_descripcion(self, letra):
        descripciones = {
            "A": "Cierra el puño con el pulgar apoyado sobre los dedos.",
            "B": "Extiende todos los dedos juntos hacia arriba. El pulgar se dobla hacia la palma.",
            "C": "Dobla todos los dedos formando una C. La palma queda mirando hacia un lado.",
            "D": "El índice apunta hacia arriba y el resto forma un círculo con el pulgar.",
            "E": "Dobla todos los dedos hacia la palma. El pulgar queda debajo de los dedos.",
            "F": "Extiende el índice hacia arriba y el pulgar también, con un poco de separación entre sí.",
            "I": "Cierra el puño y levanta solo el meñique.",
            "K": "Índice y medio extendidos en V, el pulgar entre ellos.",
            "L": "Extiende el índice hacia arriba y el pulgar hacia el lado. Forma una L.",
            "M": "Los tres dedos centrales doblados sobre el pulgar.",
            "N": "El índice y el medio doblados sobre el pulgar.",
            "O": "Une todos los dedos con el pulgar formando una O.",
            "P": "El índice apunta hacia abajo y el pulgar hacia el lado.",
            "Q": "Encoge los dedos alrededor de el pulgar.",
            "R": "El índice y el medio extendidos y cruzados entre sí.",
            "T": "Une el índice y el pulgar formando un círculo. Los otros tres dedos extendidos.",
            "U": "El índice y el meñique extendidos hacia arriba.",
            "V": "El índice y el medio extendidos en forma de V, separados.",
            "W": "El índice, medio y anular extendidos y separados.",
            "X": "El índice doblado en forma de gancho.",
            "Y": "El pulgar y el meñique extendidos. Los otros tres dedos cerrados.",
        }
        return descripciones.get(letra, "Observa la imagen y replica la posición de la mano.")

    def _get_tip(self, letra):
        tips = {
            "A": "Asegúrate de que el pulgar no quede escondido detrás del puño.",
            "B": "Los cuatro dedos deben estar completamente extendidos y juntos.",
            "C": "La curvatura debe ser suave, no demasiado cerrada ni abierta.",
            "D": "El círculo que forman los dedos debe quedar visible de frente.",
            "E": "Los dedos deben estar bien doblados, casi tocando la palma.",
            "F": "No separes mucho el índice y el pulgar, puede confundirse con la L",
            "I": "El meñique debe estar completamente extendido y recto.",
            "K": "El pulgar debe quedar entre los dos dedos, no debajo.",
            "L": "El ángulo entre el índice y el pulgar debe ser de 90 grados.",
            "M": "Los tres dedos deben cubrir el pulgar completamente.",
            "N": "Solo dos dedos cubren el pulgar, a diferencia de la M.",
            "O": "Todos los dedos deben unirse con el pulgar formando un círculo cerrado.",
            "P": "Esta seña puede ser complicada — practica el ángulo de rotación.",
            "Q": "Cubre el pulgar con los otros dedos.",
            "R": "El cruce de los dedos debe ser claro y visible.",
            "T": "El círculo del índice y pulgar debe ser claro y visible.",
            "U": "Pose de rock :p",
            "V": "La separación entre los dos dedos debe ser clara y simétrica.",
            "W": "Los tres dedos deben estar bien separados entre sí.",
            "X": "El gancho del índice debe ser pronunciado y claro.",
            "Y": "El pulgar y el meñique deben estar completamente extendidos.",
        }
        return tips.get(letra, "Mira la imagen de referencia y compara con tu mano.")


if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.withdraw()
    def dummy(): pass
    app = Leccion(
        master=raiz,
        letra="A",
        seccion_id="basico",
        letras_seccion=["A", "E", "I", "O", "U"],
        on_completado=dummy
    )
    raiz.mainloop()