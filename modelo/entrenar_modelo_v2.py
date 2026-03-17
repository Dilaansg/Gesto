# entrenar_modelo_v2.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

def ejecutar_entrenador():
    # 1. Cargar dataset v2 (normalizado)
    df = pd.read_csv('modelo\dataset_lsc_v2.csv', header=None)
    print(f"Total muestras: {len(df)}")
    print(f"Dimensiones del vector: {df.shape[1] - 1} features")  # debe ser 63
    print(f"\nMuestras por letra:\n{df.iloc[:, -1].value_counts().sort_index()}")

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    # 2. Split estratificado
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"\nEntrenamiento: {len(X_train)} | Test: {len(X_test)}")

    # 3. Entrenar Random Forest mejorado
    print("\nEntrenando Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=25,
        min_samples_split=3,
        random_state=42,
        n_jobs=-1  # usa todos los núcleos disponibles
    )
    rf.fit(X_train, y_train)
    acc_rf = accuracy_score(y_test, rf.predict(X_test))
    print(f"Random Forest: {acc_rf * 100:.2f}%")

    # 4. Entrenar SVM
    print("Entrenando SVM...")
    svm = SVC(
        kernel='rbf', C=10, gamma='scale',
        probability=True, random_state=42
    )
    svm.fit(X_train, y_train)
    acc_svm = accuracy_score(y_test, svm.predict(X_test))
    print(f"SVM:           {acc_svm * 100:.2f}%")

    # 5. Elegir el mejor
    if acc_rf >= acc_svm:
        mejor = rf
        nombre = "Random Forest"
        acc_final = acc_rf
    else:
        mejor = svm
        nombre = "SVM"
        acc_final = acc_svm

    print(f"\n✅ Ganador: {nombre} — {acc_final * 100:.2f}%")

    # 6. Reporte detallado
    y_pred = mejor.predict(X_test)
    print("\n--- Precisión por letra ---")
    print(classification_report(y_test, y_pred))

    # 7. Matriz de confusión
    clases = sorted(set(y))
    cm = confusion_matrix(y_test, y_pred, labels=clases)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d',
                xticklabels=clases, yticklabels=clases, cmap='Blues')
    plt.title(f'Matriz de Confusión — {nombre} ({acc_final*100:.1f}%)')
    plt.ylabel('Real')
    plt.xlabel('Predicho')
    plt.tight_layout()
    plt.savefig('matriz_confusion_v2.png')
    plt.show()
    print("Matriz guardada como 'matriz_confusion_v2.png'")

    # 8. Guardar modelo
    with open('modelo_lsc.p', 'wb') as f:
        pickle.dump(mejor, f)
    print("✅ Modelo guardado como 'modelo_lsc.p'")


if __name__ == "__main__":
    ejecutar_entrenador()