import cv2
import mediapipe as mp
import pickle
import numpy as np
import random

# 1. Cargar el modelo que ya entrenaste
model_dict = pickle.load(open('./modelo_lsc.p', 'rb'))
model = pickle.load(open('./modelo_lsc.p', 'rb'))

# 2. Configuración de MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.7)

# 3. Variables del Juego
letras_disponibles = ["A", "B", "C", "E", "I", "O", "U", "L"] # Asegúrate que coincidan con tu modelo
target = random.choice(letras_disponibles)
mensaje = "Haz el gesto:"
color_mensaje = (255, 255, 255) # Blanco

cap = cv2.VideoCapture(0)

print(f"Objetivo inicial: {target}")

while True:
    data_aux = []
    x_ = []
    y_ = []
    
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Dibujar interfaz del juego
    cv2.rectangle(frame, (0, 0), (W, 80), (50, 50, 50), -1) # Barra superior
    cv2.putText(frame, f"OBJETIVO: {target}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
    cv2.putText(frame, mensaje, (W-300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_mensaje, 2)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        data_aux = []

        # ✅ IGUAL que el código 1: coordenadas crudas, sin normalizar
        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            data_aux.append(x)
            data_aux.append(y)

        # Predicción
        prediction = model.predict([np.asarray(data_aux)])
        letra_detectada = prediction[0]
        

        

        # --- Interfaz del Juego ---
        cv2.putText(frame, f"Detectado: {letra_detectada}", (20, H-20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        key = cv2.waitKey(1)
        if key == 13: # Tecla Enter
            if letra_detectada == target:
                mensaje = "CORRECTO!"
                color_mensaje = (0, 255, 0) # Verde
                target = random.choice(letras_disponibles)
            else:
                mensaje = "INCORRECTO"
                color_mensaje = (0, 0, 255) # Rojo

    # Mostrar la ventana siempre
    cv2.imshow('Juego LSC - Pon a prueba tu conocimiento', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break