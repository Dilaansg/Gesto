#traductor.py
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

RUTA_MODELO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelo_lsc.p"
)

class TraductorLSC(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Traductor LSC")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.7)}x{int(alto * 0.75)}")
        self.resizable(False, False)

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
        self.cam_label = ctk.CTkLabel(self, text="", width=640, height=480)
        self.cam_label.grid(row=0, column=0, rowspan=4, padx=20, pady=20)

        panel = ctk.CTkFrame(self, width=280)
        panel.grid(row=0, column=1, rowspan=4, padx=(0, 20), pady=20, sticky="nsew")
        panel.grid_propagate(False)

        ctk.CTkLabel(
            panel, text="TRADUCTOR",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(30, 4))

        ctk.CTkLabel(
            panel, text="DETECTANDO",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="white"
        ).pack()

        self.lbl_letra = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=110, weight="bold"), text_color="#00CFFF"
        )
        self.lbl_letra.pack(pady=(0, 5))

        self.lbl_estado = ctk.CTkLabel(
            panel, text="Muestra una mano a la cámara",
            font=ctk.CTkFont(size=12), text_color="gray", wraplength=240
        )
        self.lbl_estado.pack(pady=(0, 10))

        ctk.CTkLabel(
            panel, text="CONFIANZA",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray"
        ).pack()

        self.barra_confianza = ctk.CTkProgressBar(
            panel, width=220, height=12, corner_radius=6,
            progress_color="#00FF99", fg_color="#333333"
        )
        self.barra_confianza.set(0)
        self.barra_confianza.pack(pady=(4, 4))

        self.lbl_confianza_pct = ctk.CTkLabel(
            panel, text="0%", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.lbl_confianza_pct.pack(pady=(0, 15))

        ctk.CTkFrame(panel, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            panel, text="HISTORIAL",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray"
        ).pack()

        self.lbl_historial = ctk.CTkLabel(
            panel, text="",
            font=ctk.CTkFont(size=16), text_color="#FFFFFF", wraplength=240
        )
        self.lbl_historial.pack(pady=(5, 15))

        ctk.CTkButton(
            panel, text="Limpiar",
            font=ctk.CTkFont(size=13), height=38, corner_radius=10,
            fg_color="transparent", border_width=2,
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
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
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
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk
            self.lbl_letra.configure(text=self.letra_estable)
            if self.letra_estable == "...":
                self.lbl_estado.configure(text="Muestra una mano a la cámara", text_color="gray")
            else:
                self.lbl_estado.configure(text="Seña detectada ✅", text_color="#00FF99")
            self.barra_confianza.set(self.confianza_actual)
            self.lbl_confianza_pct.configure(text=f"{int(self.confianza_actual * 100)}%")
            if self.confianza_actual >= self.UMBRAL:
                self.barra_confianza.configure(progress_color="#00FF99")
            elif self.confianza_actual >= 0.5:
                self.barra_confianza.configure(progress_color="#FFAA00")
            else:
                self.barra_confianza.configure(progress_color="#FF4444")
            self.lbl_historial.configure(text=self.texto_acumulado[-30:])
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