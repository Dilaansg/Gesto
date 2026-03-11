import cv2
import mediapipe as mp
import pickle   
import numpy as np  
from collections import Counter
def ejecutar_traductor():
    # 1. Cargar el modelo entrenado
    modelo_dict = pickle.load(open('modelo_lsc.p', 'rb'))   
    model = modelo_dict 

    # --- VARIABLES DE ESTABILIDAD ---
    historial_predicciones = []
    letra_estable = "..." # Lo que se muestra finalmente
    frames_estabilidad = 15 # Aumenté a 15 para que sea aún más fluido
    # --------------------------------

    # 2. Configurar MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        data_aux = []
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar malla
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extraer coordenadas
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x)
                    data_aux.append(y)

                # 1. Predicción cruda (puede ser inestable)
                prediccion_raw = model.predict([np.asarray(data_aux)])[0]
                
                # 2. Guardar en el historial
                historial_predicciones.append(prediccion_raw)
                
                # 3. Mantener el tamaño del historial fijo
                if len(historial_predicciones) > frames_estabilidad:
                    historial_predicciones.pop(0)
                
                # 4. Calcular la letra más frecuente (la moda)
                conteo = Counter(historial_predicciones)
                # Solo cambiamos la letra_estable si una letra domina el historial
                letra_frecuente, repeticiones = conteo.most_common(1)[0]
                
                # Umbral de confianza: si aparece en más del 70% de los frames guardados
                if repeticiones > (frames_estabilidad * 0.7):
                    letra_estable = letra_frecuente

                # Mostrar resultado ESTABLE en pantalla
                cv2.rectangle(frame, (0,0), (450, 110), (0,0,0), -1) # Fondo negro para que se lea mejor
                cv2.putText(frame, f"LSC: {letra_estable}", (20, 75), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        else:
            # Si no hay mano, limpiamos el historial poco a poco
            if len(historial_predicciones) > 0:
                historial_predicciones.pop(0)
            letra_estable = "..."

        cv2.imshow('Traductor LSC con Estabilidad', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return  

