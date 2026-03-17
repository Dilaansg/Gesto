# se importan las funciones definidas anteriormente para 
# implementarlas en la interfaz de customthinker
import customtkinter as ctk
import logica_juego1 as l1
from PIL import Image
import os
import random


ventana_juego1 = ctk.CTk()
ventana_juego1.geometry("600x600")
ventana_juego1.title("Visor de Señas Aleatorio")
# abajo de la creacion de la ventana se pueden definir otras caracteristicas como la dimension de la ventana, los colores, elementos. etc.

# Label para los puntos (con una fuente más grande)
label_puntos = ctk.CTkLabel(ventana_juego1, text="Puntos: 0", font=("Arial", 18, "bold"))
label_puntos.pack(pady=10)

# Label para los mensajes (Correcto/Incorrecto)
label_feedback = ctk.CTkLabel(ventana_juego1, text="Selecciona la opccion correcta", font=("Arial", 18))
label_feedback.pack(pady=5)

label_racha = ctk.CTkLabel(ventana_juego1, text="Intenta marcar una racha y no equivocarte!", font=("Arial", 14))
label_racha.pack(pady=5)


# funcion que muestra la imagen que se genero (se ejecuta solamente, pero no retorna nada)
def establecer_juego(label_visor)->str:
    imagen_generada = l1.choise_image()

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

    # retorna la carpeta
    return letra_imagen_generada

# se crean widgets vacios (es el contenedor en donde se almacena cada elemento, en este caso: la imagen)
label_visualizador = ctk.CTkLabel(ventana_juego1, text="Presiona el botón para cargar")
label_visualizador.pack(pady=30)

letra_correcta = establecer_juego(label_visualizador)

# esta funcion retorna 4 opcciones de respuesta (1 correcta y 3 incorrectas)
def obtener_opcciones(letra_correcta):
    # se traen todos las subcarpetas
    subcarpetas = [f for f in os.listdir("juego1/asl_dataset") if os.path.isdir(os.path.join("juego1/asl_dataset", f))]

    # se generan las letras distractoras (son diferentes a la letra correcta), en formato de lista
    distractores = random.sample([l for l in subcarpetas if l != letra_correcta], 3)

    # se unen y se mezclan las tres opcciones incorrectas
    opcciones = distractores + [letra_correcta]
    random.shuffle(opcciones)
    return opcciones

def nueva_ronda():
    # Mostramos imagen y CAPTURAMOS la letra correcta
    correcta = establecer_juego(label_visualizador)
    
    # Generamos las 4 opciones usando esa letra
    opciones = obtener_opcciones(correcta)
    
    # 3. Actualizamos los textos de los botones (suponiendo que tienes una lista de botones)
    for i in range(4):
         letra_boton = opciones[i]

         botones[i].configure(
            text=letra_boton.upper(),
            command=lambda l=letra_boton: verificar_respuesta(l, correcta)
        )

racha = 0
puntos = 0

def verificar_respuesta(letra_seleccionada, letra_correcta):
    global puntos # Para poder modificar la variable de afuera
    global racha
    
    if letra_seleccionada == letra_correcta:
        puntos += 10
        label_puntos.configure(text=f"Puntos: {puntos}")
        label_feedback.configure(text=f"¡Correcto! Efectivamente esa es la '{letra_correcta.upper()}'", text_color="green")
        racha += 1
        label_racha.configure(text=f"Tu racha es de: '{racha}' puntos", text_color="green")
        # Al acertar, se inicia automaticamente la siguiente ronda
        nueva_ronda()

    else:
        if puntos != 0:
            puntos -= 10
        label_puntos.configure(text=f"Puntos: {puntos}")
        label_feedback.configure(text=f"Esa no es, la correcta era la '{letra_correcta.upper()}'", text_color="red")
        if racha != 0:
            label_racha.configure(text=f"Has perdido tu racha, intenta hacer una mas grande y no falles!", text_color="red")
            racha = 0
        nueva_ronda()

# -------------------------------------------------------------------------------------------------




botones = [] 
frame_btns = ctk.CTkFrame(ventana_juego1)
frame_btns.pack(pady=10)

for i in range(4):
    btn = ctk.CTkButton(frame_btns, text="", width=150, height=200)
    btn.pack(side="left", padx=5)
    botones.append(btn)

nueva_ronda()


# Ejecuta el programa hasta que el usuario lo cierre
ventana_juego1.mainloop()

# letras = ["A", "e", "i"]

#    i  = 0
#    for i < 3:
