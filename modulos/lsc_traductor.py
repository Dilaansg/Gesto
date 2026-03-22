# modulos/lsc_traductor.py
import cv2
import mediapipe as mp
import pickle
import numpy as np
from collections import Counter
import customtkinter as ctk
from PIL import Image
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg

def _get_ruta_modelo():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "modelo_lsc.p")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelo_lsc.p")

RUTA_MODELO = _get_ruta_modelo()

class TraductorLSC(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Traductor LSC")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto  = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.75)}x{int(alto * 0.80)}")
        self.resizable(False, False)

        C = cfg.get_paleta()
        self.configure(fg_color=C["fondo"])

        # ── Lógica (NO tocar) ──
        self.model = pickle.load(open(RUTA_MODELO, 'rb'))
        self.historial = []
        self.frames_estabilidad = 15
        self.letra_estable = "..."
        self.confianza_actual = 0.0
        self.corriendo = True
        self._current_frame = None
        self.UMBRAL = 0.70

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        # ──────────────────────

        self._build_ui()
        self._start_camera()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente
    # ─────────────────────────────────────────────────
    def _build_ui(self):
        C = cfg.get_paleta()

        self.ancho_cam = int(self.winfo_screenwidth() * 0.75 * 0.58)
        self.alto_cam  = int(self.winfo_screenheight() * 0.80 * 0.85)
        ancho_panel    = int(self.winfo_screenwidth() * 0.75 * 0.36)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── cámara con borde redondeado ──────────────
        cam_frame = ctk.CTkFrame(
            self, corner_radius=16,
            fg_color=C["fondo_card"],
            border_width=1, border_color=C["borde"]
        )
        cam_frame.grid(row=0, column=0, padx=15, pady=15, sticky="n")

        self.cam_label = ctk.CTkLabel(
            cam_frame, text="",
            width=self.ancho_cam, height=self.alto_cam
        )
        self.cam_label.pack(padx=8, pady=(8, 4))

        # instrucción debajo de la cámara
        instr_frame = ctk.CTkFrame(
            cam_frame, corner_radius=10,
            fg_color=C["fondo_muted"], border_width=0
        )
        instr_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            instr_frame,
            text="Muestra una mano a la cámara para traducir",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(pady=8)

        # ── panel derecho ────────────────────────────
        panel = ctk.CTkFrame(
            self, width=ancho_panel, corner_radius=16,
            fg_color=C["fondo_card"],
            border_width=1, border_color=C["borde"]
        )
        panel.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        panel.grid_propagate(False)

        # FRONT: título
        ctk.CTkLabel(
            panel, text="Traductor LSC",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(pady=(25, 4))

        ctk.CTkLabel(
            panel, text="Lengua de Señas Colombiana",
            font=ctk.CTkFont(size=12),
            text_color=C["texto_secundario"]
        ).pack(pady=(0, 16))

        # FRONT: recuadro letra detectada
        ctk.CTkLabel(
            panel, text="DETECTANDO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        letra_frame = ctk.CTkFrame(
            panel, width=110, height=110,
            corner_radius=20,
            fg_color=C["primario"], border_width=0
        )
        letra_frame.pack(pady=(8, 8))
        letra_frame.pack_propagate(False)

        self.lbl_letra = ctk.CTkLabel(
            letra_frame, text="...",
            font=ctk.CTkFont(size=58, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_letra.place(relx=0.5, rely=0.5, anchor="center")

        # estado
        self.lbl_estado = ctk.CTkLabel(
            panel, text="Muestra una mano a la cámara",
            font=ctk.CTkFont(size=12),
            text_color=C["texto_secundario"], wraplength=240
        )
        self.lbl_estado.pack(pady=(0, 16))

        # barra de confianza
        ctk.CTkLabel(
            panel, text="CONFIANZA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        self.barra_confianza = ctk.CTkProgressBar(
            panel, height=10, corner_radius=5,
            progress_color=C["completado"],
            fg_color=C["fondo_muted"]
        )
        self.barra_confianza.set(0)
        self.barra_confianza.pack(fill="x", padx=20, pady=(4, 2))

        self.lbl_confianza_pct = ctk.CTkLabel(
            panel, text="0%",
            font=ctk.CTkFont(size=11),
            text_color=C["texto_secundario"]
        )
        self.lbl_confianza_pct.pack(pady=(0, 16))

        # separador
        ctk.CTkFrame(
            panel, height=1, fg_color=C["borde"]
        ).pack(fill="x", padx=20, pady=(0, 16))

        # historial
        ctk.CTkLabel(
            panel, text="HISTORIAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        # recuadro historial
        historial_frame = ctk.CTkFrame(
            panel, corner_radius=12,
            fg_color=C["fondo_muted"], border_width=0
        )
        historial_frame.pack(fill="x", padx=20, pady=(8, 16))

        self.lbl_historial = ctk.CTkLabel(
            historial_frame, text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=C["texto_principal"],
            wraplength=200
        )
        self.lbl_historial.pack(pady=12, padx=12)

        # botón limpiar
        ctk.CTkButton(
            panel, text="🗑 Limpiar historial",
            font=ctk.CTkFont(size=13), height=38, corner_radius=20,
            fg_color="transparent",
            border_width=1, border_color=C["borde"],
            text_color=C["texto_secundario"],
            hover_color=C["fondo_muted"],
            command=self._limpiar_historial  # NO tocar
        ).pack(padx=20, fill="x")

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar
    # ─────────────────────────────────────────────────
    def _normalizar(self, hand_landmarks):
        coords = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
        base_x, base_y, base_z = coords[0]
        coords = [(x - base_x, y - base_y, z - base_z) for x, y, z in coords]
        max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in coords)
        if max_val > 0:
            coords = [(x/max_val, y/max_val, z/max_val) for x, y, z in coords]
        return [v for triplet in coords for v in triplet]

    def _limpiar_historial(self):
        self.texto_acumulado = ""
        self.lbl_historial.configure(text="")

    def _start_camera(self):
        self.texto_acumulado = ""
        self.ultima_letra_guardada = ""
        self.cap = cv2.VideoCapture(cfg.get_camara(), cv2.CAP_DSHOW)
        threading.Thread(target=self._camera_loop, daemon=True).start()
        self._update_frame()

    def _camera_loop(self):
        while self.corriendo:
            ret, frame = self.cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                data_aux = self._normalizar(hand_landmarks)
                pred_proba = self.model.predict_proba([np.asarray(data_aux)])[0]
                confianza = max(pred_proba)
                letra = self.model.classes_[np.argmax(pred_proba)]
                self.confianza_actual = confianza
                if confianza >= self.UMBRAL:
                    self.historial.append(letra)
                if len(self.historial) > self.frames_estabilidad:
                    self.historial.pop(0)
                if self.historial:
                    conteo = Counter(self.historial)
                    letra_freq, reps = conteo.most_common(1)[0]
                    if reps > self.frames_estabilidad * 0.7:
                        self.letra_estable = letra_freq
                        if letra_freq != self.ultima_letra_guardada:
                            self.ultima_letra_guardada = letra_freq
                            self.texto_acumulado += letra_freq
            else:
                if self.historial: self.historial.pop(0)
                self.letra_estable = "..."
                self.confianza_actual = 0.0
            self._current_frame = frame

    def _update_frame(self):
        if not self.corriendo: return
        C = cfg.get_paleta()
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(self.ancho_cam, self.alto_cam))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk

            # actualizar letra en el recuadro
            self.lbl_letra.configure(text=self.letra_estable)

            if self.letra_estable == "...":
                self.lbl_estado.configure(
                    text="Muestra una mano a la cámara",
                    text_color=C["texto_secundario"]
                )
            else:
                self.lbl_estado.configure(
                    text="Seña detectada ✅",
                    text_color=C["completado"]
                )

            self.barra_confianza.set(self.confianza_actual)
            self.lbl_confianza_pct.configure(text=f"{int(self.confianza_actual * 100)}%")

            if self.confianza_actual >= self.UMBRAL:
                self.barra_confianza.configure(progress_color=C["completado"])
            elif self.confianza_actual >= 0.5:
                self.barra_confianza.configure(progress_color=C["advertencia"])
            else:
                self.barra_confianza.configure(progress_color=C["error"])

            self.lbl_historial.configure(text=self.texto_acumulado[-20:])

        self.after(30, self._update_frame)

    def _on_close(self):
        self.corriendo = False
        self.cap.release()
        self.destroy()


if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.withdraw()
    app = TraductorLSC(master=raiz)
    try:
        raiz.mainloop()
    except KeyboardInterrupt:
        raiz.destroy()