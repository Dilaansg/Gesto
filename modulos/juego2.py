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
import config as cfg

def _get_ruta_modelo():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "modelo_lsc.p")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelo_lsc.p")

RUTA_MODELO = _get_ruta_modelo()
UMBRAL = 0.70
FRAMES_ESTABILIDAD = 15
ACIERTOS_PARA_PASAR = 4
PREGUNTAS_PARA_PASAR = 5

model = pickle.load(open(RUTA_MODELO, 'rb'))
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def normalizar(hand_landmarks):
    coords = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
    base_x, base_y, base_z = coords[0]
    coords = [(x - base_x, y - base_y, z - base_z) for x, y, z in coords]
    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in coords)
    if max_val > 0:
        coords = [(x/max_val, y/max_val, z/max_val) for x, y, z in coords]
    return [v for triplet in coords for v in triplet]


class BaseCamera:
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
        self.cap = cv2.VideoCapture(cfg.get_camara(), cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(cfg.get_camara())
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
# MINI PRÁCTICA
# ═══════════════════════════════════════════════════════
class MiniPractica(ctk.CTkToplevel, BaseCamera):
    def __init__(self, master, letra, on_exitoso):
        super().__init__(master)
        self.title(f"¡Inténtalo! — {letra}")
        ancho = self.winfo_screenwidth()
        alto  = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.7)}x{int(alto * 0.68)}")
        self.resizable(False, False)
        self.grab_set()

        C = cfg.get_paleta()
        self.configure(fg_color=C["fondo"])

        self.letra     = letra
        self.on_exitoso= on_exitoso
        self.validado  = False

        self._build_ui()
        self._iniciar_camara()
        self._update_frame()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # FRONT: modificar libremente
    def _build_ui(self):
        C = cfg.get_paleta()

        self.ancho_cam = int(self.winfo_screenwidth() * 0.7 * 0.62)
        self.alto_cam  = int(self.ancho_cam * 0.72)
        ancho_panel    = int(self.winfo_screenwidth() * 0.7 * 0.33)

        # cámara con borde redondeado
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
        self.cam_label.pack(padx=8, pady=8)

        # panel derecho
        panel = ctk.CTkFrame(
            self, width=ancho_panel, corner_radius=16,
            fg_color=C["fondo_card"],
            border_width=1, border_color=C["borde"]
        )
        panel.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        panel.grid_propagate(False)

        # FRONT: título
        ctk.CTkLabel(
            panel, text="¡Inténtalo!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(pady=(25, 4))

        ctk.CTkLabel(
            panel, text="Haz esta seña:",
            font=ctk.CTkFont(size=13),
            text_color=C["texto_secundario"]
        ).pack()

        # FRONT: recuadro letra objetivo
        letra_frame = ctk.CTkFrame(
            panel, width=90, height=90,
            corner_radius=18,
            fg_color=C["primario"], border_width=0
        )
        letra_frame.pack(pady=(12, 12))
        letra_frame.pack_propagate(False)
        ctk.CTkLabel(
            letra_frame, text=self.letra,
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # letra detectada
        ctk.CTkLabel(
            panel, text="DETECTADO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        self.lbl_detectado = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=50, weight="bold"),
            text_color=C["texto_secundario"]
        )
        self.lbl_detectado.pack(pady=(0, 8))

        # barra de confianza
        ctk.CTkLabel(
            panel, text="CONFIANZA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        self.barra_confianza = ctk.CTkProgressBar(
            panel, width=200, height=10, corner_radius=5,
            progress_color=C["completado"],
            fg_color=C["fondo_muted"]
        )
        self.barra_confianza.set(0)
        self.barra_confianza.pack(pady=(4, 4))

        self.lbl_confianza_pct = ctk.CTkLabel(
            panel, text="0%",
            font=ctk.CTkFont(size=11),
            text_color=C["texto_secundario"]
        )
        self.lbl_confianza_pct.pack(pady=(0, 12))

        # feedback
        self.lbl_feedback = ctk.CTkLabel(
            panel, text="",
            font=ctk.CTkFont(size=13), wraplength=220,
            text_color=C["texto_principal"]
        )
        self.lbl_feedback.pack(pady=(0, 12))

        # FRONT: botón cerrar
        ctk.CTkButton(
            panel, text="Cerrar",
            font=ctk.CTkFont(size=13), height=38, corner_radius=20,
            fg_color="transparent",
            border_width=1, border_color=C["borde"],
            text_color=C["texto_secundario"],
            hover_color=C["fondo_muted"],
            command=self._cerrar
        ).pack(padx=20, fill="x")

    def _update_frame(self):
        if not self.corriendo: return
        C = cfg.get_paleta()
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(self.ancho_cam, self.alto_cam))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk

            color = C["completado"] if self.letra_detectada == self.letra else C["texto_principal"]
            self.lbl_detectado.configure(text=self.letra_detectada, text_color=color)
            self.barra_confianza.set(self.confianza_actual)
            self.lbl_confianza_pct.configure(text=f"{int(self.confianza_actual * 100)}%")

            if self.confianza_actual >= UMBRAL:
                self.barra_confianza.configure(progress_color=C["completado"])
            elif self.confianza_actual >= 0.5:
                self.barra_confianza.configure(progress_color=C["advertencia"])
            else:
                self.barra_confianza.configure(progress_color=C["error"])

            if self.letra_detectada == self.letra and not self.validado:
                self.validado = True
                self.lbl_feedback.configure(
                    text="¡Correcto! Muy bien 🎉",
                    text_color=C["completado"]
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
# JUEGO 2 COMPLETO
# ═══════════════════════════════════════════════════════
class JuegoDos(ctk.CTkToplevel, BaseCamera):
    def __init__(self, master, letras, seccion_id, letras_seccion, on_completado):
        super().__init__(master)
        self.title("Juego 2 — Haz la seña")
        self.update_idletasks()
        ancho = self.winfo_screenwidth()
        alto  = self.winfo_screenheight()
        self.geometry(f"{int(ancho * 0.75)}x{int(alto * 0.85)}")
        self.resizable(False, False)

        C = cfg.get_paleta()
        self.configure(fg_color=C["fondo"])
        self.target_anterior = None #para que no muestre dos veces seguidas la misma letra.
        self.letras        = letras
        self.seccion_id    = seccion_id
        self.letras_seccion= letras_seccion
        self.on_completado = on_completado
        self.target        = random.choice(self.letras)
        self.puntaje       = 0
        self.intentos      = 0
        self.aciertos_ronda= 0
        self.mensaje       = "Haz el gesto y presiona ESPACIO"
        self._current_frame= None

        self._build_ui()
        self._iniciar_camara()
        self._update_frame()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # FRONT: modificar libremente
    def _build_ui(self):
        C = cfg.get_paleta()

        self.ancho_cam = int(self.winfo_screenwidth() * 0.75 * 0.58)
        self.alto_cam  = int(self.winfo_screenheight() * 0.80 * 0.85)
        ancho_panel    = int(self.winfo_screenwidth() * 0.75 * 0.36)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # cámara con borde redondeado
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

        instr_frame = ctk.CTkFrame(
            cam_frame,
            corner_radius=10,
            fg_color=C["fondo_muted"],
            border_width=0
        )
        instr_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            instr_frame,
            text="Muestra la mano y presiona ESPACIO",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(pady=8)

        # panel derecho scrolleable
        panel = ctk.CTkScrollableFrame(
            self, width=ancho_panel, corner_radius=16,
            fg_color=C["fondo_card"],
            scrollbar_button_color=C["borde_activo"],
            scrollbar_button_hover_color=C["primario"]
        )
        panel.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

        # FRONT: título
        ctk.CTkLabel(
            panel, text="Juego 2",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=C["texto_principal"]
        ).pack(pady=(25, 4))

        ctk.CTkLabel(
            panel, text="Haz la seña correcta",
            font=ctk.CTkFont(size=12),
            text_color=C["texto_secundario"]
        ).pack(pady=(0, 16))

        # FRONT: letra objetivo en recuadro
        ctk.CTkLabel(
            panel, text="OBJETIVO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        letra_frame = ctk.CTkFrame(
            panel, width=100, height=100,
            corner_radius=20,
            fg_color=C["primario"], border_width=0
        )
        letra_frame.pack(pady=(8, 16))
        letra_frame.pack_propagate(False)
        self.lbl_target = ctk.CTkLabel(
            letra_frame, text=self.target,
            font=ctk.CTkFont(size=52, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_target.place(relx=0.5, rely=0.5, anchor="center")

        # detectado
        ctk.CTkLabel(
            panel, text="DETECTADO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["texto_secundario"]
        ).pack()

        self.lbl_detectado = ctk.CTkLabel(
            panel, text="...",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=C["texto_secundario"]
        )
        self.lbl_detectado.pack(pady=(4, 12))

        # barra confianza
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
        self.lbl_confianza_pct.pack(pady=(0, 12))

        # mensaje feedback
        self.lbl_mensaje = ctk.CTkLabel(
            panel, text=self.mensaje,
            font=ctk.CTkFont(size=13),
            text_color=C["texto_secundario"], wraplength=240
        )
        self.lbl_mensaje.pack(pady=(0, 12))

        # puntaje
        score_frame = ctk.CTkFrame(
            panel, corner_radius=12,
            fg_color=C["fondo_muted"],
            border_width=0
        )
        score_frame.pack(padx=20, fill="x", pady=(0, 16))

        ctk.CTkLabel(
            score_frame, text="✅ Correctas",
            font=ctk.CTkFont(size=12),
            text_color=C["texto_secundario"]
        ).grid(row=0, column=0, padx=20, pady=8)

        ctk.CTkLabel(
            score_frame, text="📝 Intentos",
            font=ctk.CTkFont(size=12),
            text_color=C["texto_secundario"]
        ).grid(row=0, column=1, padx=20, pady=8)

        self.lbl_puntaje = ctk.CTkLabel(
            score_frame, text="0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C["completado"]
        )
        self.lbl_puntaje.grid(row=1, column=0, padx=20, pady=(0, 12))

        self.lbl_intentos = ctk.CTkLabel(
            score_frame, text="0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C["advertencia"]
        )
        self.lbl_intentos.grid(row=1, column=1, padx=20, pady=(0, 12))

        # FRONT: botones — NO tocar command=
        ctk.CTkButton(
            panel, text="✔ CONFIRMAR",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46, corner_radius=22,
            fg_color=C["primario"],
            text_color="#ffffff",
            hover_color=C["acento"],
            command=self._confirmar
        ).pack(padx=20, fill="x", pady=(0, 10))

        ctk.CTkButton(
            panel, text="⏭ Saltar letra",
            font=ctk.CTkFont(size=13), height=38, corner_radius=22,
            fg_color="transparent",
            border_width=1, border_color=C["borde"],
            text_color=C["texto_secundario"],
            hover_color=C["fondo_muted"],
            command=self._saltar
        ).pack(padx=20, fill="x")

        self.bind("<space>", lambda e: self._confirmar())

    # ── lógica — NO tocar ──
    def _confirmar(self):
        C = cfg.get_paleta()
        if self.confianza_actual < UMBRAL and self.letra_detectada != "...":
            self.lbl_mensaje.configure(
                text="⚠️ Seña poco clara, ajusta la mano",
                text_color=C["advertencia"]
            )
            return

        self.intentos += 1
        if self.letra_detectada == self.target:
            self.puntaje += 1
            self.aciertos_ronda += 1
            self.lbl_mensaje.configure(text="¡CORRECTO! 🎉", text_color=C["completado"])
            opciones = [l for l in self.letras if l != self.target] #para que no muestre la misma anterior
            self.target_anterior = self.target
            self.target = random.choice(opciones)
            self.lbl_target.configure(text=self.target)
            self.lbl_target.configure(text=self.target)
            self.historial.clear()
            if self.intentos >= PREGUNTAS_PARA_PASAR:
                self.after(800, self._fin_ronda)
                return
        else:
            self.lbl_mensaje.configure(text="Incorrecto ❌", text_color=C["error"])
            if self.intentos >= PREGUNTAS_PARA_PASAR:
                self.after(800, self._fin_ronda)
                return

        self.lbl_puntaje.configure(text=str(self.puntaje))
        self.lbl_intentos.configure(text=str(self.intentos))

    def _saltar(self):
        opciones = [l for l in self.letras if l != self.target]
        self.target_anterior = self.target
        self.target = random.choice(opciones)
        self.lbl_target.configure(text=self.target)
        self.lbl_target.configure(text=self.target)
        C = cfg.get_paleta()
        self.lbl_mensaje.configure(text="Letra cambiada", text_color=C["texto_secundario"])
        self.historial.clear()

    def _fin_ronda(self):
        C = cfg.get_paleta()
        aprobado = self.aciertos_ronda >= ACIERTOS_PARA_PASAR
        if aprobado:
            p.completar_juego(self.seccion_id, 2)
            p.completar_seccion(self.seccion_id)
            self.lbl_mensaje.configure(
                text=f"¡Sección completada! 🎉",
                text_color=C["completado"]
            )
            self.after(2000, self._cerrar)
        else:
            self.lbl_mensaje.configure(
                text=f"Necesitas {ACIERTOS_PARA_PASAR}/{PREGUNTAS_PARA_PASAR} — intentá de nuevo",
                text_color=C["error"]
            )
            self.aciertos_ronda = 0
            self.intentos = 0
            self.puntaje = 0
            self.lbl_puntaje.configure(text="0")
            self.lbl_intentos.configure(text="0")

    def _update_frame(self):
        if not self.corriendo: return
        C = cfg.get_paleta()
        if self._current_frame is not None:
            img = Image.fromarray(cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB))
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(self.ancho_cam, self.alto_cam))
            self.cam_label.configure(image=imgtk)
            self.cam_label.image = imgtk

            color = C["completado"] if self.letra_detectada == self.target else C["texto_principal"]
            self.lbl_detectado.configure(text=self.letra_detectada, text_color=color)
            self.barra_confianza.set(self.confianza_actual)
            self.lbl_confianza_pct.configure(text=f"{int(self.confianza_actual * 100)}%")

            if self.confianza_actual >= UMBRAL:
                self.barra_confianza.configure(progress_color=C["completado"])
            elif self.confianza_actual >= 0.5:
                self.barra_confianza.configure(progress_color=C["advertencia"])
            else:
                self.barra_confianza.configure(progress_color=C["error"])

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