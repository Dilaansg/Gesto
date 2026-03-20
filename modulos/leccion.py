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
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.5)}x{int(alto * 0.70)}")
        self.resizable(False, False)

        # ── estado (NO tocar) ──
        self.letra = letra
        self.seccion_id = seccion_id
        self.letras_seccion = letras_seccion
        self.on_completado = on_completado
        self.mini_exitoso = False
        # ──────────────────────

        self._build_ui()
        self._marcar_vista()  # marcar como vista al abrir
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        # encabezado con progreso de la sección
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(
            header, text=f"Sección: {p.CAMINO[self.seccion_id]['nombre']}",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(side="left")

        pos = self.letras_seccion.index(self.letra) + 1
        total = len(self.letras_seccion)
        ctk.CTkLabel(
            header, text=f"Letra {pos} de {total}",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(side="right")

        # FRONT: letra grande
        ctk.CTkLabel(
            self, text=self.letra,
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color="#00CFFF"
        ).pack(pady=(10, 5))

        # contenido principal — imagen + explicación lado a lado
        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=20, pady=5)

        # imagen de la seña
        self.lbl_imagen = ctk.CTkLabel(contenido, text="", width=220, height=220)
        self.lbl_imagen.pack(side="left", padx=(0, 20))
        self._cargar_imagen()

        # panel de explicación
        panel = ctk.CTkFrame(contenido, fg_color="transparent")
        panel.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            panel, text="Cómo hacer esta seña",
            font=ctk.CTkFont(size=16, weight="bold"), anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        descripcion = self._get_descripcion(self.letra)
        ctk.CTkLabel(
            panel, text=descripcion,
            font=ctk.CTkFont(size=13), text_color="gray",
            wraplength=280, justify="left", anchor="w"
        ).pack(anchor="w")

        # FRONT: tip
        ctk.CTkLabel(
            panel, text="Tip",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFAA00", anchor="w"
        ).pack(anchor="w", pady=(12, 4))

        tip = self._get_tip(self.letra)
        ctk.CTkLabel(
            panel, text=tip,
            font=ctk.CTkFont(size=12), text_color="gray",
            wraplength=280, justify="left", anchor="w"
        ).pack(anchor="w")

        # separador
        ctk.CTkFrame(self, height=1, fg_color="#333333").pack(fill="x", padx=20, pady=(10, 0))

        # botones de navegación
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=12)

        ctk.CTkButton(
            btn_frame, text="← Volver",
            font=ctk.CTkFont(size=13),
            width=100, height=38, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=self._cerrar  # NO tocar
        ).pack(side="left")

        # botón INTÉNTALO — abre mini práctica con cámara
        # FRONT: cambiar estilo
        self.btn_intentalo = ctk.CTkButton(
            btn_frame, text="¡Inténtalo! 📷",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150, height=38, corner_radius=8,
            fg_color="#FFAA00", text_color="black",
            command=self._abrir_mini_practica  # NO tocar
        )
        self.btn_intentalo.pack(side="right", padx=(10, 0))

        # botón siguiente letra — siempre visible
        # FRONT: cambiar estilo
        self.btn_siguiente = ctk.CTkButton(
            btn_frame, text="Siguiente →",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38, corner_radius=8,
            command=self._siguiente  # NO tocar
        )
        self.btn_siguiente.pack(side="right")

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
            progreso["puntaje_total"] += 5  # puntos por ver la lección
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
        # FRONT: cambiar estilo del botón cuando el usuario ya lo logró
        self.btn_intentalo.configure(
            text="¡Logrado! ✓",
            fg_color="#00AA55",
            text_color="white",
            state="disabled"
        )

    def _siguiente(self):
        idx_actual = self.letras_seccion.index(self.letra)
        hay_siguiente = idx_actual + 1 < len(self.letras_seccion)

        if hay_siguiente:
            # actualizar estado
            self.letra = self.letras_seccion[idx_actual + 1]
            self.title(f"Lección — Letra {self.letra}")
            self.mini_exitoso = False
            self._marcar_vista()
            # limpiar y reconstruir sin destruir la ventana
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
        img = Image.open(ruta).resize((220, 220))
        img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(220, 220))
        self.lbl_imagen.configure(image=img_ctk)
        self.lbl_imagen.image = img_ctk

    # ─────────────────────────────────────────────────
    # CONTENIDO — FRONT: pueden ampliar las descripciones o mejorarlas
    # ─────────────────────────────────────────────────
    def _get_descripcion(self, letra):
        descripciones = {
            "A": "Cierra el puño con el pulgar apoyado sobre los dedos.",
            "B": "Extiende todos los dedos juntos hacia arriba. El pulgar se dobla hacia la palma.",
            "C": "Dobla todos los dedos formando una C. La palma queda mirando hacia un lado.",
            "D": "El índice apunta hacia arriba y el resto forma un círculo con el pulgar.",
            "E": "Dobla todos los dedos hacia la palma. El pulgar queda debajo de los dedos.",
            "F": "Une el índice y el pulgar formando un círculo. Los otros tres dedos extendidos.",
            "I": "Cierra el puño y levanta solo el meñique.",
            "K": "Índice y medio extendidos en V, el pulgar entre ellos.",
            "L": "Extiende el índice hacia arriba y el pulgar hacia el lado. Forma una L.",
            "M": "Los tres dedos centrales doblados sobre el pulgar.",
            "N": "El índice y el medio doblados sobre el pulgar.",
            "O": "Une todos los dedos con el pulgar formando una O.",
            "P": "El índice apunta hacia abajo y el pulgar hacia el lado.",
            "Q": "El índice y el pulgar apuntan hacia abajo formando una Q.",
            "R": "El índice y el medio extendidos y cruzados entre sí.",
            "T": "El pulgar queda entre el índice y el medio, los otros dedos cerrados.",
            "U": "El índice y el medio extendidos juntos hacia arriba.",
            "V": "El índice y el medio extendidos en forma de V, separados.",
            "W": "El índice, medio y anular extendidos y separados.",
            "X": "El índice doblado en forma de gancho.",
            "Y": "El pulgar y el meñique extendidos. Los otros tres dedos cerrados.",
        }
        return descripciones.get(letra, "Observa la imagen y replica la posición de la mano.")

    def _get_tip(self, letra):
        tips = { #diccionario para tips
            "A": "Asegúrate de que el pulgar no quede escondido detrás del puño.",
            "B": "Los cuatro dedos deben estar completamente extendidos y juntos.",
            "C": "La curvatura debe ser suave, no demasiado cerrada ni abierta.",
            "D": "El círculo que forman los dedos debe quedar visible de frente.",
            "E": "Los dedos deben estar bien doblados, casi tocando la palma.",
            "F": "El círculo del índice y pulgar debe ser claro y visible.",
            "I": "El meñique debe estar completamente extendido y recto.",
            "K": "El pulgar debe quedar entre los dos dedos, no debajo.",
            "L": "El ángulo entre el índice y el pulgar debe ser de 90 grados.",
            "M": "Los tres dedos deben cubrir el pulgar completamente.",
            "N": "Solo dos dedos cubren el pulgar, a diferencia de la M.",
            "O": "Todos los dedos deben unirse con el pulgar formando un círculo cerrado.",
            "P": "Esta seña puede ser complicada — practica el ángulo de rotación.",
            "Q": "El índice y el pulgar apuntan hacia el suelo, no hacia el frente.",
            "R": "El cruce de los dedos debe ser claro y visible.",
            "T": "El pulgar debe asomar entre los dos dedos, no quedar oculto.",
            "U": "Los dos dedos deben estar completamente juntos, sin separación.",
            "V": "La separación entre los dos dedos debe ser clara y simétrica.",
            "W": "Los tres dedos deben estar bien separados entre sí.",
            "X": "El gancho del índice debe ser pronunciado y claro.",
            "Y": "El pulgar y el meñique deben estar completamente extendidos.",
        }
        return tips.get(letra, "Mira la imagen de referencia y compara con tu mano.")


if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.withdraw()  # ocultar ventana raíz
    def dummy(): pass
    app = Leccion(
        master=raiz,
        letra="A",
        seccion_id="basico",
        letras_seccion=["A", "E", "I", "O", "U"],
        on_completado=dummy
    )
    raiz.mainloop()