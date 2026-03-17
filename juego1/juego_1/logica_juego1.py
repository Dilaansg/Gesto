# LIBRERIAS

import os
import random


# se define una funcion que toma un png de manos aelatorio que recibe:

def choise_image()->str:

    # se crea una tupla que guarda todas las carpetas
    subcarpetas = [f for f in os.listdir("juego1/asl_dataset") if os.path.isdir(os.path.join("juego1/asl_dataset", f))]

    # se elige una sola carpeta al azar
    carpeta_elegida = random.choice(subcarpetas)
    # se construye la ruta de la carpeta elegida
    ruta_carpeta_elegida = os.path.join("juego1/asl_dataset", carpeta_elegida)

    # se listan todos los elementos que estan dentro de la carpeta elegida
    imagenes = os.listdir(ruta_carpeta_elegida)

    # al final del proceso se genera una ruta de una de las imagenes
    imagen_seleccionada = random.choice(imagenes)
    ruta_imagen_seleccionada = os.path.join(ruta_carpeta_elegida, imagen_seleccionada)
    
    return ruta_imagen_seleccionada

# guarda la ruta de la imagen en una variable
ruta_imagen_escojida = choise_image()




