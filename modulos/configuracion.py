# modulos/configuracion.py
# pantalla de configuración general
# FRONT: modificar libremente la sección visual

import customtkinter as ctk
import cv2
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
import progreso as p

INTEGRANTES = [
    "DILAN OSORIO",   # FRONT: reemplazar con nombres reales
    "JHON OVIEDO",
    "ANA OCHOA",
    "JUAN MARTÍNEZ",
    "DANIEL ORTÍZ",
]

class Configuracion(ctk.CTkToplevel):
    def __init__(self, master, on_cerrar):
        super().__init__(master)
        self.title("Configuración")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.45)}x{int(alto * 0.70)}")
        self.resizable(False, False)

        self.on_cerrar = on_cerrar
        self.cap_preview = None
        self.preview_corriendo = False
        self._current_frame = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        # scroll general
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ── PERFIL ──────────────────────────────────
        self._seccion(scroll, "👤 PERFIL")

        progreso = p.cargar()
        ctk.CTkLabel(
            scroll,
            text=f"Puntaje actual: {progreso['puntaje_total']} pts  |  "
                 f"Lecciones vistas: {len(progreso.get('lecciones_vistas', []))}  |  "
                 f"Secciones completadas: {len(progreso.get('secciones_completadas', []))}",
            font=ctk.CTkFont(size=14), text_color="gray"
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(
            scroll, text="RESETEAR PROGRESO",
            font=ctk.CTkFont(size=13), height=36, corner_radius=8,
            fg_color="#AA2222", hover_color="#881111",
            command=self._confirmar_reset  # NO tocar
        ).pack(anchor="w", pady=(0, 20))

        # ── APARIENCIA ──────────────────────────────
        self._seccion(scroll, "APARIENCIA")

        modo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        modo_frame.pack(fill="x", pady=(0, 20))
        modo_actual = cfg.get_modo_oscuro()

        self.lbl_modo = ctk.CTkLabel(
            modo_frame, 
            text="Modo oscuro" if modo_actual else "Modo claro",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_modo.pack(side="left")
        

        self.switch_modo = ctk.CTkSwitch(
            modo_frame, text="",
            onvalue=True, offvalue=False,
            command = self._actualizar_label_modo
        )
        self.switch_modo.pack(side="right")

        
        if modo_actual:
            self.switch_modo.select()
        else:
            self.switch_modo.deselect()

        # ── CÁMARA ──────────────────────────────────
        self._seccion(scroll, "CÁMARA")

        cam_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cam_frame.pack(fill="x", pady=(0, 8))


        self.cam_var = ctk.StringVar(value=str(cfg.get_camara()))
        ctk.CTkSegmentedButton(
            cam_frame, values=["0", "1", "2"],
            variable=self.cam_var,
            command=self._cambiar_camara  # NO tocar
        ).pack(side="left")

        # preview de la cámara
        # FRONT: ajustar tamaño
        self.lbl_preview = ctk.CTkLabel(
            scroll, text="Presiona 'Ver preview' para verificar la cámara",
            width=320, height=180,
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.lbl_preview.pack(pady=(0, 8))

        btns_cam = ctk.CTkFrame(scroll, fg_color="transparent")
        btns_cam.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            btns_cam, text="▶ Ver preview",
            font=ctk.CTkFont(size=12), height=32, corner_radius=8,
            command=self._iniciar_preview  # NO tocar
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns_cam, text="⏹ Detener",
            font=ctk.CTkFont(size=12), height=32, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=self._detener_preview  # NO tocar
        ).pack(side="left")

        # ── COMENTARIOS ─────────────────────────────
        self._seccion(scroll, "COMENTARIOS Y FEEDBACK")

        ctk.CTkLabel(
            scroll,
            text="Escribe sugerencias, errores o ideas. Se guardaran para próximas actualizaciones.",
            font=ctk.CTkFont(size=12), text_color="gray", wraplength=380, justify="left"
        ).pack(anchor="w", pady=(0, 8))

        self.txt_comentario = ctk.CTkTextbox(
            scroll, height=100, corner_radius=8
        )
        self.txt_comentario.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            scroll, text="💾 Guardar comentario",
            font=ctk.CTkFont(size=13), height=36, corner_radius=8,
            command=self._guardar_comentario  # NO tocar
        ).pack(anchor="w", pady=(0, 20))

        # ── ACERCA DE ───────────────────────────────
        self._seccion(scroll, "Acerca de")

        ctk.CTkLabel(
            scroll, text="GESTO — Plataforma de aprendizaje de LSC",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")

        config = cfg.cargar()
        # version
        ctk.CTkLabel(
            scroll, text=f"Versión {config.get('version', '1.0.0')}",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(anchor="w", pady=(2, 10))

        # integrantes
        ctk.CTkLabel(
            scroll, text="Equipo:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")

        for nombre in INTEGRANTES:
            ctk.CTkLabel(
                scroll, text=f"  - {nombre}",
                font=ctk.CTkFont(size=12), text_color="gray"
            ).pack(anchor="w")

        ctk.CTkButton(
            scroll, text="🔗 Ver repositorio en GitHub",
            font=ctk.CTkFont(size=13), height=36, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=cfg.abrir_repositorio  # NO tocar
        ).pack(anchor="w", pady=(15, 0))

    # ─────────────────────────────────────────────────
    # UTILIDAD UI
    # ─────────────────────────────────────────────────
    def _seccion(self, parent, titulo):
        """Crea un separador de sección con título."""
        # FRONT: cambiar estilo de los separadores
        ctk.CTkLabel(
            parent, text=titulo,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", pady=(10, 4))
        ctk.CTkFrame(parent, height=1, fg_color="#444444").pack(fill="x", pady=(0, 10))

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _confirmar_reset(self):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar")
        dialogo.geometry("340x160")
        dialogo.resizable(False, False)
        dialogo.grab_set()

        ctk.CTkLabel(
            dialogo,
            text="¿Estás seguro?\nEsto borrará todo tu progreso.",
            font=ctk.CTkFont(size=14), justify="center"
        ).pack(pady=(25, 15))

        btns = ctk.CTkFrame(dialogo, fg_color="transparent")
        btns.pack()

        ctk.CTkButton(
            btns, text="Cancelar",
            width=120, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=dialogo.destroy
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btns, text="Sí, resetear",
            width=120, corner_radius=8,
            fg_color="#AA2222", hover_color="#881111",
            command=lambda: self._ejecutar_reset(dialogo)
        ).pack(side="left", padx=8)

    def _ejecutar_reset(self, dialogo):
        dialogo.destroy()
        p.resetear()
        self.on_cerrar()
        self._cerrar()

    def _cambiar_modo(self):
        pass

    def _actualizar_label_modo(self):
        modo = self.switch_modo.get()
        self.lbl_modo.configure(text = "Modo Oscuro" if modo else "Modo claro") 

    def _cambiar_camara(self, valor):
        cfg.set_camara(int(valor))
        self._detener_preview()

    def _iniciar_preview(self):
        self._detener_preview()
        indice = cfg.get_camara()
        cap_test = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
        if not cap_test.isOpened():
                cap_test.release()
                self.lbl_preview.configure(
                    text=f"Cámara {indice} no disponible.\nCambia el índice e intenta de nuevo.",
                    image=None
                )
                return
        cap_test.release()
        self.preview_corriendo = True
        self.cap_preview = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
        threading.Thread(target=self._preview_loop, daemon=True).start()
        self._update_preview()

    def _preview_loop(self):
        while self.preview_corriendo:
            if not self.cap_preview: break
            ret, frame = self.cap_preview.read()
            if not ret: continue
            self._current_frame = cv2.flip(frame, 1)

    def _update_preview(self):
        if not self.preview_corriendo: return
        if self._current_frame is not None:
            from PIL import Image
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(320, 180))
            self.lbl_preview.configure(image=imgtk, text="")
            self.lbl_preview.image = imgtk
        self.after(30, self._update_preview)

    def _detener_preview(self):
        self.preview_corriendo = False
        if self.cap_preview:
            self.cap_preview.release()
            self.cap_preview = None
        self.lbl_preview.configure(image=None, text="Preview detenido")

    def _guardar_comentario(self):
        texto = self.txt_comentario.get("1.0", "end").strip()
        if not texto:
            return
        cfg.guardar_comentario(texto)
        self.txt_comentario.delete("1.0", "end")
        self.txt_comentario.insert("1.0", "✅ Comentario guardado")
        self.after(2000, lambda: self.txt_comentario.delete("1.0", "end"))

    def _cerrar(self):
        modo = self.switch_modo.get()
        cfg.set_modo_oscuro(modo)
        ctk.set_appearance_mode("dark" if modo else "light")
        self._detener_preview()
        self.destroy()
        self.on_cerrar() 


if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.withdraw()
    def dummy(): pass
    app = Configuracion(master=raiz, on_cerrar=dummy)
    try:
        raiz.mainloop()
    except KeyboardInterrupt:
        raiz.destroy()