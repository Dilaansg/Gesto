# capturar_datos_v2.py
import cv2
import mediapipe as mp
import pandas as pd
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

ARCHIVO = "modelo\dataset_lsc_v2.csv"
LETRAS = ["A", "B", "C", "D", "E", "F", "I", "K", "L", 
          "M", "N", "O", "P", "Q", "R", "T", "U", "V", "W", "X", "Y"]
RAFAGA = 30  # capturas por ráfaga — puedes subir a 50 si tienes tiempo

# ─────────────────────────────────────────
# NORMALIZACIÓN — NO tocar
# Esta función debe ser idéntica en el traductor y juego2
# ─────────────────────────────────────────
def normalizar(hand_landmarks):
    coords = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
    base_x, base_y, base_z = coords[0]  # muñeca como origen

    coords = [(x - base_x, y - base_y, z - base_z) for x, y, z in coords]

    max_val = max(max(abs(x), abs(y), abs(z)) for x, y, z in coords)
    if max_val > 0:
        coords = [(x/max_val, y/max_val, z/max_val) for x, y, z in coords]

    return [v for triplet in coords for v in triplet]  # 63 valores


def capturar(letra):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    contador = 0

    # Contar muestras existentes de esta letra
    try:
        df_existente = pd.read_csv(ARCHIVO, header=None)
        existentes = len(df_existente[df_existente.iloc[:, -1] == letra])
    except FileNotFoundError:
        existentes = 0

    print(f"\nLetra '{letra}' — ya tiene {existentes} muestras.")
    print(f"Presiona S para ráfaga de {RAFAGA}. Q para pasar a la siguiente letra.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: continue

        frame = cv2.flip(frame, 1)
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        key = cv2.waitKey(1) & 0xFF

        if results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

            if key == ord('s'):
                print(f"Capturando ráfaga...")
                capturadas = 0

                while capturadas < RAFAGA:
                    ret, img = cap.read()
                    if not ret: continue
                    img = cv2.flip(img, 1)
                    res = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

                    if res.multi_hand_landmarks:
                        data = normalizar(res.multi_hand_landmarks[0])
                        data.append(letra)
                        pd.DataFrame([data]).to_csv(ARCHIVO, mode='a', index=False, header=False)
                        contador += 1
                        capturadas += 1

                    time.sleep(0.03)

                print(f"Ráfaga lista. Total esta sesión: {contador}")

        # UI en cámara
        cv2.rectangle(frame, (0, 0), (640, 60), (0, 0, 0), -1)
        cv2.putText(frame, f"Letra: {letra} | Sesion: {contador} | Total: {existentes + contador}",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, "S = rafaga  |  Q = siguiente letra",
                    (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
        cv2.imshow(f"Capturando: {letra}", frame)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return contador


def reporte():
    try:
        df = pd.read_csv(ARCHIVO, header=None)
        print(f"\n=== REPORTE DATASET V2 ===")
        print(f"Total registros: {len(df)}")
        for letra in sorted(LETRAS):
            n = len(df[df.iloc[:, -1] == letra])
            estado = "✅" if n >= 300 else "⚠️ necesita más"
            print(f"  {letra}: {n} muestras {estado}")
    except FileNotFoundError:
        print("Dataset vacío aún.")


if __name__ == "__main__":
    print("=== CAPTURADOR LSC V2 — CON NORMALIZACIÓN ===")
    print(f"Letras a capturar: {LETRAS}")
    print(f"Apunta a mínimo 300 muestras por letra (idealmente 400+)")
    print(f"Varía: distancia, iluminación, ángulo de la mano\n")

    for letra in LETRAS:
        reporte()
        input(f"\nPresiona ENTER para empezar con la letra '{letra}'...")
        capturar(letra)

    reporte()
    print("\n✅ Captura completa. Corre entrenar_modelo.py para reentrenar.")