import pandas as pd
import os

def analizar_dataset(file_path='modelo\dataset_lsc_v3.csv', minimo_muestras=300):
    if not os.path.exists(file_path):
        print(f"No se encontró el archivo {file_path}")
        return

    # Leer el dataset
    df = pd.read_csv(file_path)
    
    # Suponiendo que la columna de la letra se llama 'label' o es la última columna
    # Ajusta 'label' al nombre real de tu columna de etiquetas
    columna_etiqueta = df.columns[-1] 
    
    conteos = df[columna_etiqueta].value_counts()
    promedio = conteos.mean()

    print("=== 📊 REPORTE DE DATASET ===")
    print(f"Total de registros: {len(df)}")
    print(f"Promedio de muestras por letra: {promedio:.2f}")
    print("-" * 30)

    letras_faltantes = []

    for letra, cantidad in conteos.items():
        estado = "✅ OK" if cantidad >= minimo_muestras else "⚠️ INSUFICIENTE"
        print(f"Letra {letra}: {cantidad} muestras -> {estado}")
        if cantidad < minimo_muestras:
            letras_faltantes.append(letra)

    print("-" * 30)
    if letras_faltantes:
        print(f"🚩 ALERTA: Necesitas capturar más datos para: {', '.join(map(str, letras_faltantes))}")
        print(f"Objetivo recomendado: {minimo_muestras} por letra.")
    else:
        print("🚀 ¡Dataset balanceado! Estás listo para entrenar.")

if __name__ == "__main__":
    analizar_dataset()