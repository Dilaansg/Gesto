import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
def ejecutar_entrenador():
    # 1. Cargar los datos
    df = pd.read_csv('dataset_lsc.csv', header=None)

    # 2. Dividir en X (puntos) y y (la letra)
    X = df.iloc[:, :-1]  # Todas las columnas excepto la última
    y = df.iloc[:, -1]   # La última columna (la etiqueta/letra)

    # 3. Dividir datos para entrenamiento y prueba (80% entrena, 20% evalúa)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)

    # 4. Crear y entrenar el modelo
    print("Entrenando la red neuronal...")
    modelo = RandomForestClassifier(n_estimators=100)
    modelo.fit(X_train, y_train)

    # 5. Porcentaje de precisión del modelo
    y_pred = modelo.predict(X_test)
    precision = accuracy_score(y_test, y_pred)
    print(f"⚡​Entrenamiento completado. Precisión: {precision * 100:.2f}%")

    # 6. Guardar el modelo 
    with open('modelo_lsc.p', 'wb') as f:
        pickle.dump(modelo, f)
    print("⚡​Modelo guardado como 'modelo_lsc.p'")