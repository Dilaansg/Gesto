import cv2
import mediapipe as mp
import pickle
import numpy as np
import random
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
from collections import Counter

# ─────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

model = pickle.load(open('./modelo_lsc.p', 'rb'))

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.7)

LETRAS = ["A", "B", "C", "E", "I", "O", "U", "L"]

# ─────────────────────────────────────────
# APLICACIÓN
# ─────────────────────────────────────────
class JuegoLSC(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Juego LSC - Lengua de Señas Colombiana")
        self.geometry("1000x680")
        self.resizable(False, False)

        # Estado del juego
        self.target = random.choice(LETRAS)
        self.letra_detectada = "..."
        self.mensaje = "Haz el gesto y presiona ENTER"
        self.color_mensaje = "#FFFFFF"
        self.puntaje = 0
        self.intentos = 0
        self.corriendo = True

        # Historial para estabilidad
        self.historial = []
        self.frames_estabilidad = 15

        self._build_ui()
        self._start_camera()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ──────────────────────────────────────
    def _build_ui(self):
        # ── Panel izquierdo: cámara ──
        self.cam_label = ctk.CTkLabel(self, text="", width=640, height=480)
        self.cam_label.grid(row=0, column=0, rowspan=6, padx=20, pady=20)

        # ── Panel derecho ──
        panel = ctk.CTkFrame(self, width=280, corner_radius=15)
        panel.grid(row=0, column=1, rowspan=6, padx=(0, 20), pady=20, sticky="nsew")
        panel.grid_propagate(False)

        # Título
        ctk.CTkLabel(
            panel, text="🤟 Juego LSC", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            panel, text="Lengua de Señas Colombiana",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(pady=(0, 20))

        # Letra objetivo
        ctk.CTkLabel(panel, text="OBJETIVO", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="gray").pack()
        self.lbl_target = ctk.CTkLabel(
            panel, text=self.target,
            font=ctk.CTkFont(size=90, weight="bold"),
            text_color="#00CFFF"
        )
        self.lbl_target.pack(pady=(0, 10))

        # Letra detectada
        ctk.CTkLabel(panel, text="DETECTADO", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="gray").pack()
        self.lbl_detectado = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=55, weight="bold"),
            text_color="#AAAAAA"
        )
        self.lbl_detectado.pack(pady=(0, 10))

        # Mensaje feedback
        self.lbl_mensaje = ctk.CTkLabel(
            panel, text=self.mensaje,
            font=ctk.CTkFont(size=13),
            text_color=self.color_mensaje,
            wraplength=240
        )
        self.lbl_mensaje.pack(pady=(0, 15))

        # Puntaje
        score_frame = ctk.CTkFrame(panel, corner_radius=10)
        score_frame.pack(padx=20, fill="x", pady=(0, 20))

        ctk.CTkLabel(score_frame, text="✅ Correctas",
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=20, pady=8)
        ctk.CTkLabel(score_frame, text="📝 Intentos",
                     font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=20, pady=8)

        self.lbl_puntaje = ctk.CTkLabel(
            score_frame, text="0", font=ctk.CTkFont(size=22, weight="bold"), text_color="#00FF99"
        )
        self.lbl_puntaje.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.lbl_intentos = ctk.CTkLabel(
            score_frame, text="0", font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFAA00"
        )
        self.lbl_intentos.grid(row=1, column=1, padx=20, pady=(0, 10))

        # Botón confirmar
        self.btn_confirmar = ctk.CTkButton(
            panel, text="✔ CONFIRMAR (Enter)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45, corner_radius=10,
            command=self._confirmar
        )
        self.btn_confirmar.pack(padx=20, fill="x", pady=(0, 10))

        # Botón saltar
        ctk.CTkButton(
            panel, text="⏭ Saltar letra",
            font=ctk.CTkFont(size=13),
            height=38, corner_radius=10,
            fg_color="transparent", border_width=2,
            command=self._saltar
        ).pack(padx=20, fill="x")

        # Bind teclado
        self.bind("<Return>", lambda e: self._confirmar())

    # ──────────────────────────────────────
    # LÓGICA DEL JUEGO
    # ──────────────────────────────────────
    def _confirmar(self):
        self.intentos += 1
        if self.letra_detectada == self.target:
            self.puntaje += 1
            self.mensaje = "¡CORRECTO! 🎉"
            self.color_mensaje = "#00FF99"
            self.target = random.choice(LETRAS)
            self.lbl_target.configure(text=self.target)
            self.historial.clear()
        else:
            self.mensaje = f"Incorrecto ❌  (era {self.target}... o sigue intentando)"
            self.color_mensaje = "#FF4444"

        self.lbl_mensaje.configure(text=self.mensaje, text_color=self.color_mensaje)
        self.lbl_puntaje.configure(text=str(self.puntaje))
        self.lbl_intentos.configure(text=str(self.intentos))

    def _saltar(self):
        self.target = random.choice(LETRAS)
        self.lbl_target.configure(text=self.target)
        self.mensaje = "Letra cambiada. ¡Haz el gesto!"
        self.color_mensaje = "#FFFFFF"
        self.lbl_mensaje.configure(text=self.mensaje, text_color=self.color_mensaje)
        self.historial.clear()

    # ──────────────────────────────────────
    # CÁMARA EN HILO SEPARADO
    # ──────────────────────────────────────
    def _start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.thread.start()
        self._update_frame()  # Inicia el ciclo de refresco en el hilo principal

    def _camera_loop(self):
        """Corre en hilo separado: captura y procesa frames."""
        while self.corriendo:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                data_aux = []
                for lm in hand_landmarks.landmark:
                    data_aux.append(lm.x)
                    data_aux.append(lm.y)

                pred = model.predict([np.asarray(data_aux)])[0]
                self.historial.append(pred)
                if len(self.historial) > self.frames_estabilidad:
                    self.historial.pop(0)

                conteo = Counter(self.historial)
                letra_freq, reps = conteo.most_common(1)[0]
                if reps > self.frames_estabilidad * 0.7:
                    self.letra_detectada = letra_freq

            else:
                if self.historial:
                    self.historial.pop(0)
                self.letra_detectada = "..."

            # Guardar frame procesado para mostrarlo
            self._current_frame = frame

    def _update_frame(self):
        """Corre en el hilo principal: actualiza el Label de la cámara."""
        if hasattr(self, '_current_frame'):
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk  # Evita que el GC lo elimine

            # Actualizar letra detectada en UI
            color = "#00CFFF" if self.letra_detectada == self.target else "#FFFFFF"
            self.lbl_detectado.configure(text=self.letra_detectada, text_color=color)

        self.after(30, self._update_frame)  # ~33 fps

    # ──────────────────────────────────────
    # CIERRE LIMPIO
    # ──────────────────────────────────────
    def _on_close(self):
        self.corriendo = False
        self.cap.release()
        self.destroy()


# ─────────────────────────────────────────
if __name__ == "__main__":
    app = JuegoLSC()
    app.mainloop()