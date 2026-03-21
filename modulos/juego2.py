# modulos/juego2.py
# contiene la lógica de detección reutilizable, el mini práctica y el juego 2 completo
# FRONT: todo lo visual está marcado

import cv2
import mediapipe as mp
import pickle
import numpy as np
import random
import customtkinter as ctk
from PIL import Image
import threading
from collections import Counter
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import progreso as p

# ─────────────────────────────────────────
# CONFIGURACIÓN — NO tocar
# ─────────────────────────────────────────
RUTA_MODELO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelo_lsc.p")
UMBRAL = 0.80
FRAMES_ESTABILIDAD = 15
ACIERTOS_PARA_PASAR = 4
PREGUNTAS_PARA_PASAR = 5

model = pickle.load(open(RUTA_MODELO, 'rb'))
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# ─────────────────────────────────────────
# FUNCIÓN REUTILIZABLE DE NORMALIZACIÓN — NO tocar
# debe ser idéntica a capturar_datos_v2.py
# ─────────────────────────────────────────
def normalizar(hand_landmarks):
    coords = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
    base_x, base_y, base_z = coords[0]
    coords = [(x - base_x, y - base_y, z - base_z) for x, y, z in coords]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in coords)
    if max_val > 0:
        coords = [(x/max_val, y/max_val, z/max_val) for x, y, z in coords]
    return [v for triplet in coords for v in triplet]


# ─────────────────────────────────────────
# CLASE BASE DE CÁMARA — NO tocar
# MiniPractica y JuegoDos heredan de esta
# ─────────────────────────────────────────
class BaseCamera:
    """Maneja la cámara y la detección en hilo separado."""

    def _iniciar_camara(self):
        self.corriendo = True
        self._current_frame = None
        self.letra_detectada = "..."
        self.confianza_actual = 0.0
        self.historial = []
        self.hands_detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) #CAMBIAR POR 0 O 1 DEPENDIENDO SI NO INICIA LA CAMARA CORRECTAMENTE 
        threading.Thread(target=self._camera_loop, daemon=True).start()

    def _detener_camara(self):
        self.corriendo = False
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()

    def _camera_loop(self):
        while self.corriendo:
            if not self.cap: break
            ret, frame = self.cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            results = self.hands_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                hl = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
                data_aux = normalizar(hl)
                pred_proba = model.predict_proba([np.asarray(data_aux)])[0]
                confianza = max(pred_proba)
                letra = model.classes_[np.argmax(pred_proba)]
                self.confianza_actual = confianza
                if confianza >= UMBRAL:
                    self.historial.append(letra)
                if len(self.historial) > FRAMES_ESTABILIDAD:
                    self.historial.pop(0)
                if self.historial:
                    letra_freq, reps = Counter(self.historial).most_common(1)[0]
                    if reps > FRAMES_ESTABILIDAD * 0.7:
                        self.letra_detectada = letra_freq
            else:
                if self.historial: self.historial.pop(0)
                self.letra_detectada = "..."
                self.confianza_actual = 0.0
            self._current_frame = frame


# ═══════════════════════════════════════════════════════
# MINI PRÁCTICA — se abre encima de la lección
# recibe una sola letra y valida que el usuario la haga
# ═══════════════════════════════════════════════════════
class MiniPractica(ctk.CTkToplevel, BaseCamera):
    def __init__(self, master, letra, on_exitoso):
        super().__init__(master)
        self.title(f"¡Inténtalo! — {letra}")
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.7)}x{int(alto * 0.68)}")
        self.resizable(False, False)
        self.grab_set()  # bloquea la ventana de atrás

        # ── estado (NO tocar) ──
        self.letra = letra
        self.on_exitoso = on_exitoso
        self.validado = False
        # ──────────────────────

        self._build_ui()
        self._iniciar_camara()
        self._update_frame()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # FRONT: modificar libremente
    def _build_ui(self):
        # cámara izquierda  
        self.ancho_cam = int(self.winfo_screenwidth() * 0.7 * 0.65)
        self.alto_cam = int(self.ancho_cam * 0.75)
        self.cam_label = ctk.CTkLabel(self, text="", width=self.ancho_cam, height=self.alto_cam)
        self.cam_label.grid(row=0, column=0, rowspan=3, padx=15, pady=15)
        # panel derecho
        ancho_panel = int(self.winfo_screenwidth() * 0.7 * 0.35)
        panel = ctk.CTkFrame(self, width=ancho_panel, corner_radius=15)
        panel.grid(row=0, column=1, rowspan=6, padx=(0, 15), pady=15, sticky="nsew")
        panel.grid_propagate(False)

        # FRONT: título
        ctk.CTkLabel(
            panel, text="¡Inténtalo!",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            panel, text="Haz esta seña:",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack()

        # FRONT: letra objetivo grande
        ctk.CTkLabel(
            panel, text=self.letra,
            font=ctk.CTkFont(size=90, weight="bold"),
            text_color="#00CFFF"
        ).pack(pady=(5, 10))

        # letra detectada
        ctk.CTkLabel(
            panel, text="DETECTADO",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray"
        ).pack()

        self.lbl_detectado = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=50, weight="bold"), text_color="#AAAAAA"
        )
        self.lbl_detectado.pack(pady=(0, 8))

        # barra de confianza
        ctk.CTkLabel(
            panel, text="CONFIANZA",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray"
        ).pack()

        self.barra_confianza = ctk.CTkProgressBar(
            panel, width=200, height=10, corner_radius=5,
            progress_color="#00FF99", fg_color="#333333"
        )
        self.barra_confianza.set(0)
        self.barra_confianza.pack(pady=(4, 4))

        self.lbl_confianza_pct = ctk.CTkLabel(
            panel, text="0%",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.lbl_confianza_pct.pack(pady=(0, 15))

        # feedback
        self.lbl_feedback = ctk.CTkLabel(
            panel, text="",
            font=ctk.CTkFont(size=13), wraplength=220
        )
        self.lbl_feedback.pack(pady=(0, 10))

        # botón cerrar
        ctk.CTkButton(
            panel, text="Cerrar",
            font=ctk.CTkFont(size=13), height=36, corner_radius=8,
            fg_color="transparent", border_width=1,
            command=self._cerrar  # NO tocar
        ).pack(padx=20, fill="x")

    # ── lógica — NO tocar ──
    def _update_frame(self):
        if not self.corriendo: return
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(self.ancho_cam, self.alto_cam))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk

            color = "#00CFFF" if self.letra_detectada == self.letra else "#FFFFFF"
            self.lbl_detectado.configure(text=self.letra_detectada, text_color=color)

            self.barra_confianza.set(self.confianza_actual)
            self.lbl_confianza_pct.configure(text=f"{int(self.confianza_actual * 100)}%")

            if self.confianza_actual >= UMBRAL:
                self.barra_confianza.configure(progress_color="#00FF99")
            elif self.confianza_actual >= 0.5:
                self.barra_confianza.configure(progress_color="#FFAA00")
            else:
                self.barra_confianza.configure(progress_color="#FF4444")

            # detección exitosa automática
            if self.letra_detectada == self.letra and not self.validado:
                self.validado = True
                self.lbl_feedback.configure(
                    text="¡Correcto! Muy bien 🎉", text_color="#00FF99"
                )
                self.after(1500, self._exito)

        self.after(30, self._update_frame)

    def _exito(self):
        self._detener_camara()
        self.destroy()
        self.on_exitoso()

    def _cerrar(self):
        self._detener_camara()
        self.destroy()


# ═══════════════════════════════════════════════════════
# JUEGO 2 COMPLETO — usa todas las letras de la sección
# ═══════════════════════════════════════════════════════
class JuegoDos(ctk.CTkToplevel, BaseCamera):
    def __init__(self, master, letras, seccion_id, letras_seccion, on_completado):
        super().__init__(master)
        self.title("Juego 2 — Haz la seña")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.7)}x{int(alto * 0.68)}")
        self.resizable(False, False)

        # ── estado (NO tocar) ──
        self.letras = letras
        self.seccion_id = seccion_id
        self.letras_seccion = letras_seccion
        self.on_completado = on_completado
        self.target = random.choice(self.letras)
        self.puntaje = 0
        self.intentos = 0
        self.aciertos_ronda = 0
        self.mensaje = "Haz el gesto y presiona CONFIRMAR"
        self.color_mensaje = "#FFFFFF"
        self._current_frame = None
        # ──────────────────────

        self._build_ui()
        self._iniciar_camara()
        self._update_frame()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # FRONT: modificar libremente
    def _build_ui(self):
        self.ancho_cam = int(self.winfo_screenwidth() * 0.7 * 0.60)
        self.alto_cam = int(self.winfo_screenheight() * 0.68 * 0.90)
        ancho_panel = int(self.winfo_screenwidth() * 0.7 * 0.35)

        self.cam_label = ctk.CTkLabel(self, text="", width=self.ancho_cam, height=self.alto_cam)
        self.cam_label.grid(row=0, column=0, padx=10, pady=5, sticky="n")  # sticky="n" pega arriba

        panel = ctk.CTkScrollableFrame(self, width=ancho_panel, corner_radius=15)
        panel.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="nsew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Juego 2",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            panel, text="Haz la seña correcta",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(pady=(0, 15))

        ctk.CTkLabel(panel, text="OBJETIVO",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="gray").pack()
        self.lbl_target = ctk.CTkLabel(
            panel, text=self.target,
            font=ctk.CTkFont(size=90, weight="bold"), text_color="#00CFFF"
        )
        self.lbl_target.pack(pady=(0, 5))

        ctk.CTkLabel(panel, text="DETECTADO",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="gray").pack()
        self.lbl_detectado = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=55, weight="bold"), text_color="#AAAAAA"
        )
        self.lbl_detectado.pack(pady=(0, 5))

        ctk.CTkLabel(panel, text="CONFIANZA",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack()
        self.barra_confianza = ctk.CTkProgressBar(
            panel, width=220, height=12, corner_radius=6,
            progress_color="#00FF99", fg_color="#333333"
        )
        self.barra_confianza.set(0)
        self.barra_confianza.pack(pady=(4, 2))
        self.lbl_confianza_pct = ctk.CTkLabel(
            panel, text="0%",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.lbl_confianza_pct.pack(pady=(0, 8))

        self.lbl_mensaje = ctk.CTkLabel(
            panel, text=self.mensaje,
            font=ctk.CTkFont(size=13),
            text_color=self.color_mensaje, wraplength=240
        )
        self.lbl_mensaje.pack(pady=(0, 10))

        score_frame = ctk.CTkFrame(panel, corner_radius=10)
        score_frame.pack(padx=20, fill="x", pady=(0, 13))
        ctk.CTkLabel(score_frame, text="✅ Correctas",
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=20, pady=8)
        ctk.CTkLabel(score_frame, text="📝 Intentos",
                     font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=20, pady=8)
        self.lbl_puntaje = ctk.CTkLabel(
            score_frame, text="0",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#00FF99"
        )
        self.lbl_puntaje.grid(row=1, column=0, padx=20, pady=(0, 10))
        self.lbl_intentos = ctk.CTkLabel(
            score_frame, text="0",
            font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFAA00"
        )
        self.lbl_intentos.grid(row=1, column=1, padx=20, pady=(0, 10))

        # NO tocar command=
        ctk.CTkButton(
            panel, text="✔ CONFIRMAR",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45, corner_radius=10,
            command=self._confirmar
        ).pack(padx=20, fill="x", pady=(0, 10))

        ctk.CTkButton(
            panel, text="⏭ Saltar letra",
            font=ctk.CTkFont(size=13), height=38, corner_radius=10,
            fg_color="transparent", border_width=2,
            command=self._saltar
        ).pack(padx=20, fill="x")

        self.bind("<Return>", lambda e: self._confirmar())

    # ── lógica — NO tocar ──
    def _confirmar(self):
        if self.confianza_actual < UMBRAL and self.letra_detectada != "...":
            self.lbl_mensaje.configure(
                text="⚠️ Seña poco clara, ajusta la mano",
                text_color="#FFAA00"
            )
            return

        self.intentos += 1
        if self.letra_detectada == self.target:
            self.puntaje += 1
            self.aciertos_ronda += 1
            self.mensaje = "¡CORRECTO! 🎉"
            self.color_mensaje = "#00FF99"
            self.target = random.choice(self.letras)
            self.lbl_target.configure(text=self.target)
            self.historial.clear()

            # verificar si completó la ronda
            if self.intentos >= PREGUNTAS_PARA_PASAR:
                self.after(800, self._fin_ronda)
                return
        else:
            self.mensaje = "Incorrecto ❌"
            self.color_mensaje = "#FF4444"

            if self.intentos >= PREGUNTAS_PARA_PASAR:
                self.after(800, self._fin_ronda)
                return

        self.lbl_mensaje.configure(text=self.mensaje, text_color=self.color_mensaje)
        self.lbl_puntaje.configure(text=str(self.puntaje))
        self.lbl_intentos.configure(text=str(self.intentos))

    def _saltar(self):
        self.target = random.choice(self.letras)
        self.lbl_target.configure(text=self.target)
        self.lbl_mensaje.configure(text="Letra cambiada", text_color="#FFFFFF")
        self.historial.clear()

    def _fin_ronda(self):
        aprobado = self.aciertos_ronda >= ACIERTOS_PARA_PASAR
        if aprobado:
            p.completar_juego(self.seccion_id, 2)
            p.completar_seccion(self.seccion_id)
            self.lbl_mensaje.configure(
                text=f"¡Sección completada! {self.aciertos_ronda}/{PREGUNTAS_PARA_PASAR}",
                text_color="#00FF99"
            )
            self.after(2000, self._cerrar)
        else:
            self.lbl_mensaje.configure(
                text=f"Necesitas {ACIERTOS_PARA_PASAR}/{PREGUNTAS_PARA_PASAR} — intentá de nuevo",
                text_color="#FF4444"
            )
            self.aciertos_ronda = 0
            self.intentos = 0
            self.puntaje = 0
            self.lbl_puntaje.configure(text="0")
            self.lbl_intentos.configure(text="0")

    def _update_frame(self):
        if not self.corriendo: return
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(self.ancho_cam, self.alto_cam))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk

            color = "#00CFFF" if self.letra_detectada == self.target else "#FFFFFF"
            self.lbl_detectado.configure(text=self.letra_detectada, text_color=color)
            self.barra_confianza.set(self.confianza_actual)
            self.lbl_confianza_pct.configure(text=f"{int(self.confianza_actual * 100)}%")

            if self.confianza_actual >= UMBRAL:
                self.barra_confianza.configure(progress_color="#00FF99")
            elif self.confianza_actual >= 0.5:
                self.barra_confianza.configure(progress_color="#FFAA00")
            else:
                self.barra_confianza.configure(progress_color="#FF4444")

        self.after(30, self._update_frame)

    def _cerrar(self):
        self._detener_camara()
        self.destroy()
        self.on_completado()


if __name__ == "__main__":
    raiz = ctk.CTk()
    raiz.withdraw()
    def dummy(): pass
    app = JuegoDos(
        master=raiz,
        letras=["A", "E", "I", "O", "U"],
        seccion_id="basico",
        letras_seccion=["A", "E", "I", "O", "U"],
        on_completado=dummy
    )
    raiz.mainloop()