import pandas as pd
import numpy as np

def espejar_muestras(archivo_entrada, archivo_salida):
    df = pd.read_csv(archivo_entrada, header=None)
    
    nuevas_filas = []
    for _, fila in df.iterrows():
        datos = fila[:-1].values  # 63 valores (x, y, z por cada landmark)
        letra = fila.iloc[-1]
        
        # espejar coordenada X — invertir el signo de cada X
        # los datos están como x0,y0,z0,x1,y1,z1...
        datos_espejo = datos.copy()
        for i in range(0, len(datos), 3):  # cada 3 valores hay una X
            datos_espejo[i] = -datos_espejo[i]
        
        nueva_fila = list(datos_espejo) + [letra]
        nuevas_filas.append(nueva_fila)
    
    df_espejo = pd.DataFrame(nuevas_filas)
    df_combinado = pd.concat([df, df_espejo], ignore_index=True)
    df_combinado = df_combinado.sample(frac=1).reset_index(drop=True)
    df_combinado.to_csv(archivo_salida, index=False, header=False)
    
    print(f"Original: {len(df)} muestras")
    print(f"Con espejo: {len(df_combinado)} muestras")

if __name__ == "__main__":
    espejar_muestras("modelo/dataset_lsc_v2.csv", "modelo/dataset_lsc_v3.csv")