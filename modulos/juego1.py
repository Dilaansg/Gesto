# juego1/juego1.py
# se unificaron interfaz y logica en un solo archivo
# para que sea mas facil de mantener y no haya problemas con las rutas

import customtkinter as ctk
from PIL import Image
import os
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# aca se define la carpeta del dataset
# cuando reemplacen el dataset ASL por las fotos propias, solo cambien esta ruta
# las subcarpetas tienen que llamarse igual que las letras (A, B, C, etc.)
RUTA_DATASET = "juego1/images_database_procesadas"
LETRAS_VALIDAS = ["A", "B", "C", "D", "E", "I", "L", "O", "U", "V"]

# se define una funcion que toma un png de manos aleatorio
def choise_image() -> str:
    # se crea una lista que guarda todas las carpetas validas
    subcarpetas = [
        f for f in os.listdir(RUTA_DATASET)
        if os.path.isdir(os.path.join(RUTA_DATASET, f))
        and f.upper() in LETRAS_VALIDAS
    ]

    # se elige una sola carpeta al azar
    carpeta_elegida = random.choice(subcarpetas)
    # se construye la ruta de la carpeta elegida
    ruta_carpeta_elegida = os.path.join(RUTA_DATASET, carpeta_elegida)

    # se listan todos los elementos que estan dentro de la carpeta elegida
    imagenes = os.listdir(ruta_carpeta_elegida)

    # al final del proceso se genera una ruta de una de las imagenes
    imagen_seleccionada = random.choice(imagenes)
    ruta_imagen_seleccionada = os.path.join(ruta_carpeta_elegida, imagen_seleccionada)

    return ruta_imagen_seleccionada


ventana_juego1 = ctk.CTk()
ventana_juego1.geometry("600x600")
ventana_juego1.title("Adivina la Seña")
# abajo de la creacion de la ventana se pueden definir otras caracteristicas
# como la dimension de la ventana, los colores, elementos. etc.

# Label para los puntos
label_puntos = ctk.CTkLabel(ventana_juego1, text="Puntos: 0", font=("Arial", 18, "bold"))
label_puntos.pack(pady=10)

# Label para los mensajes (Correcto/Incorrecto)
label_feedback = ctk.CTkLabel(ventana_juego1, text="Selecciona la opcion correcta", font=("Arial", 18))
label_feedback.pack(pady=5)

label_racha = ctk.CTkLabel(ventana_juego1, text="Intenta marcar una racha y no equivocarte!", font=("Arial", 14))
label_racha.pack(pady=5)


# funcion que muestra la imagen que se genero (se ejecuta solamente, pero no retorna nada)
def establecer_juego(label_visor) -> str:
    imagen_generada = choise_image()

    ruta_imagen = os.path.dirname(imagen_generada)
    letra_imagen_generada = os.path.basename(ruta_imagen)

    # se procesa la imagen con pillow
    img_pil = Image.open(imagen_generada)
    # ajuste de tamaño
    img_ajustada = ctk.CTkImage(light_image=img_pil, size=(250, 250))
    # se actualiza el widget que ya existe
    label_visor.configure(image=img_ajustada, text="")
    # evita que python borre la imagen de la ram
    label_visor.image = img_ajustada

    # retorna la letra de la carpeta
    return letra_imagen_generada.upper()


# se crean widgets vacios (es el contenedor en donde se almacena cada elemento, en este caso: la imagen)
label_visualizador = ctk.CTkLabel(ventana_juego1, text="Cargando imagen...")
label_visualizador.pack(pady=30)

letra_correcta = establecer_juego(label_visualizador)


# esta funcion retorna 4 opciones de respuesta (1 correcta y 3 incorrectas)
def obtener_opciones(letra_correcta):
    # se generan las letras distractoras (son diferentes a la letra correcta), en formato de lista
    distractores = random.sample([l for l in LETRAS_VALIDAS if l != letra_correcta], 3)

    # se unen y se mezclan las opciones
    opciones = distractores + [letra_correcta]
    random.shuffle(opciones)
    return opciones


def nueva_ronda():
    # mostramos imagen y capturamos la letra correcta
    correcta = establecer_juego(label_visualizador)

    # generamos las 4 opciones usando esa letra
    opciones = obtener_opciones(correcta)

    # actualizamos los textos de los botones
    for i in range(4):
        letra_boton = opciones[i]
        botones[i].configure(
            text=letra_boton.upper(),
            fg_color=["#3B8ED0", "#1F6AA5"],  # resetea el color del boton
            state="normal",
            command=lambda l=letra_boton: verificar_respuesta(l, correcta)
        )


racha = 0
puntos = 0


def verificar_respuesta(letra_seleccionada, letra_correcta):
    global puntos
    global racha

    # bloquea los botones para que no se pueda clickear mientras se muestra el resultado
    for btn in botones:
        btn.configure(state="disabled")

    if letra_seleccionada == letra_correcta:
        puntos += 10
        racha += 1
        label_puntos.configure(text=f"Puntos: {puntos}")
        label_feedback.configure(text=f"¡Correcto! Efectivamente esa es la '{letra_correcta}'", text_color="green")
        label_racha.configure(text=f"Tu racha es de: {racha}", text_color="green")
    else:
        if puntos != 0:
            puntos -= 10
        racha = 0
        label_puntos.configure(text=f"Puntos: {puntos}")
        label_feedback.configure(text=f"Esa no es, la correcta era la '{letra_correcta}'", text_color="red")
        label_racha.configure(text=f"Has perdido tu racha, intenta hacer una mas grande y no falles!", text_color="red")
        # resalta la correcta en verde para que el jugador aprenda
        for btn in botones:
            if btn.cget("text") == letra_correcta:
                btn.configure(fg_color="#00AA55")

    # siguiente ronda automatica despues de 1.5 segundos
    ventana_juego1.after(1500, nueva_ronda)


# -------------------------------------------------------------------------------------------------

botones = []
frame_btns = ctk.CTkFrame(ventana_juego1)
frame_btns.pack(pady=10)

for i in range(4):
    btn = ctk.CTkButton(frame_btns, text="", width=120, height=60,
                        font=("Arial", 20, "bold"))
    btn.pack(side="left", padx=5)
    botones.append(btn)

nueva_ronda()

# Ejecuta el programa hasta que el usuario lo cierre
ventana_juego1.mainloop()