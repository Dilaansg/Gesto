import cv2
import mediapipe as mp
import pickle
import numpy as np
from collections import Counter
import customtkinter as ctk
from PIL import Image
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TraductorLSC(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Traductor")
        self.geometry("1000x620")  # FRONT: ajustar tamaño de la ventana
        self.resizable(False, False)

        # ── Lógica (NO tocar) ──
        self.model = pickle.load(open('modelo_lsc.p', 'rb'))
        self.historial = []
        self.frames_estabilidad = 15
        self.letra_estable = "..."
        self.corriendo = True
        self._current_frame = None

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        # ──────────────────────

        self._build_ui()
        self._start_camera()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────────
    # INTERFAZ — FRONT: modificar libremente esta sección
    # ─────────────────────────────────────────────────
    def _build_ui(self):

        # ── Cámara (izquierda) ──────────────────────
        # FRONT: ajustar tamaño con el parámetro size en _update_frame
        self.cam_label = ctk.CTkLabel(self, text="", width=640, height=480)
        self.cam_label.grid(row=0, column=0, rowspan=4, padx=20, pady=20)

        # ── Panel derecho ───────────────────────────
        # FRONT: este frame es todo el panel de info — cambiar colores, padding, etc.
        panel = ctk.CTkFrame(self, width=280)
        panel.grid(row=0, column=1, rowspan=4, padx=(0, 20), pady=20, sticky="nsew")
        panel.grid_propagate(False)

        # FRONT: título
        ctk.CTkLabel(
            panel, text="TRADUCTOR",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(30, 4))

        # FRONT: etiqueta "DETECTANDO"
        ctk.CTkLabel(
            panel, text="DETECTANDO",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack()

        # FRONT: letra grande — ajustar tamaño de fuente y color
        self.lbl_letra = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=110, weight="bold"),
            text_color="#00CFFF"
        )
        self.lbl_letra.pack(pady=(0, 10))

        # FRONT: mensaje de estado debajo de la letra
        self.lbl_estado = ctk.CTkLabel(
            panel, text="Muestra una mano a la cámara",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=240
        )
        self.lbl_estado.pack(pady=(0, 30))

        # separador visual — pueden reemplazar por una imagen o ícono
        ctk.CTkFrame(panel, height=2, fg_color="#333333").pack(fill="x", padx=20, pady=(0, 20))

        # historial de letras — caja donde se acumulan las detectadas
        ctk.CTkLabel(
            panel, text="HISTORIAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        ).pack()

        self.lbl_historial = ctk.CTkLabel(
            panel, text="",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF",
            wraplength=240
        )
        self.lbl_historial.pack(pady=(5, 20))

        # botón limpiar historial — ajustar estilo
        ctk.CTkButton(
            panel,
            text="Limpiar",
            font=ctk.CTkFont(size=13),
            height=38, corner_radius=10,
            fg_color="transparent", border_width=2,
            command=self._limpiar_historial   # NO tocar command
        ).pack(padx=20, fill="x")

    # ─────────────────────────────────────────────────
    # LÓGICA — NO tocar nada debajo de esta línea
    # ─────────────────────────────────────────────────
    def _limpiar_historial(self):
        self.texto_acumulado = ""
        self.lbl_historial.configure(text="")

    def _start_camera(self):
        self.texto_acumulado = ""
        self.ultima_letra_guardada = ""
        self.cap = cv2.VideoCapture(0)
        t = threading.Thread(target=self._camera_loop, daemon=True)
        t.start()
        self._update_frame()

    def _camera_loop(self):
        while self.corriendo:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                data_aux = []
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                    for lm in hand_landmarks.landmark:
                        data_aux.append(lm.x)
                        data_aux.append(lm.y)

                pred = self.model.predict([np.asarray(data_aux)])[0]
                self.historial.append(pred)
                if len(self.historial) > self.frames_estabilidad:
                    self.historial.pop(0)

                conteo = Counter(self.historial)
                letra_freq, reps = conteo.most_common(1)[0]
                if reps > self.frames_estabilidad * 0.7:
                    self.letra_estable = letra_freq
                    # Acumular en historial solo si cambió
                    if letra_freq != self.ultima_letra_guardada:
                        self.ultima_letra_guardada = letra_freq
                        self.texto_acumulado += letra_freq
            else:
                if self.historial:
                    self.historial.pop(0)
                self.letra_estable = "..."

            self._current_frame = frame

    def _update_frame(self):
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            #cambiar size para ajustar el tamaño del video en pantalla
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk

            # Actualizar letra y estado
            self.lbl_letra.configure(text=self.letra_estable)
            if self.letra_estable == "...":
                self.lbl_estado.configure(text="Muestra una mano a la cámara", text_color="gray")
            else:
                self.lbl_estado.configure(text="Seña detectada ✅", text_color="#00FF99")

            # Actualizar historial visible
            self.lbl_historial.configure(text=self.texto_acumulado[-30:])  # últimos 30 chars

        self.after(30, self._update_frame)

    def _on_close(self):
        self.corriendo = False
        self.cap.release()
        self.destroy()


if __name__ == "__main__":
    app = TraductorLSC()
    app.mainloop()