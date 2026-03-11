import cv2
import mediapipe as mp
import pandas as pd
import os
import time
from collections import Counter
def ejecutar_capturar(letra):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    archivo_datos = "dataset_lsc.csv"
    letra_actual = letra
    rafaga_objetivo = 10 # Número de capturas por ráfaga

    cap = cv2.VideoCapture(0)
    contador_total = 0

    print(f"Capturando letra: {letra_actual}. Presiona 'S' para ráfaga de {rafaga_objetivo}.")

    while cap.isOpened():
        success, img = cap.read()
        if not success: break
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        key = cv2.waitKey(1) & 0xFF
        
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
                
                if key == ord('s'):
                    print(f"Iniciando ráfaga para {letra_actual}...")
                    for i in range(rafaga_objetivo):
                        # Volvemos a procesar para capturar movimiento real
                        success, img_rafaga = cap.read()
                        img_rafaga = cv2.flip(img_rafaga, 1)
                        res_rafaga = hands.process(cv2.cvtColor(img_rafaga, cv2.COLOR_BGR2RGB))
                        
                        if res_rafaga.multi_hand_landmarks:
                            lms = res_rafaga.multi_hand_landmarks[0]
                            data = []
                            for lm in lms.landmark:
                                data.extend([lm.x, lm.y])
                            data.append(letra_actual)
                            
                            df = pd.DataFrame([data])
                            df.to_csv(archivo_datos, mode='a', index=False, header=False)
                            contador_total += 1
                        time.sleep(0.05) # Pequeña pausa para capturar variaciones
                    print(f"Ráfaga completada. Total muestras: {contador_total}")

        cv2.putText(img, f"Letra: {letra_actual} | Total: {contador_total}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("Capturador Optimizado LSC", img)
        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    

    """if nombre.archivo ==  opcion selecccionada
        corecto, siguiente nivel

        else:
        error, siguiente """