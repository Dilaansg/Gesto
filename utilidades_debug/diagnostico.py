# diagnostico.py
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Cargar modelo
modelo = pickle.load(open('modelo_lsc.p', 'rb'))

# 2. Cargar dataset y recrear el split exacto
df = pd.read_csv('modelo\dataset_lsc_v3.csv', header=None)
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

# random_state=42 garantiza el mismo split que cuando entrenaste
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 3. Reporte por letra
y_pred = modelo.predict(X_test)
print("--- Precisión por letra ---")
print(classification_report(y_test, y_pred))

# 4. Matriz de confusión
clases = sorted(set(y))
cm = confusion_matrix(y_test, y_pred, labels=clases)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=clases, yticklabels=clases, cmap='Blues')
plt.title('Matriz de Confusión — modelo actual')
plt.ylabel('Real')
plt.xlabel('Predicho')
plt.tight_layout()
plt.savefig('matriz_confusion.png')
plt.show()
print("Matriz guardada como 'matriz_confusion.png'")