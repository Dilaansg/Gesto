# GESTO — Plataforma de Aprendizaje de LSC con IA

Plataforma interactiva para el aprendizaje autónomo de la **Lengua de Señas Colombiana (LSC)** mediante visión artificial en tiempo real.

---

## Opción A — Ejecutar el ejecutable (.exe)

> Para usuarios que solo quieren usar la app sin instalar nada.

1. Descarga el archivo `GESTO.exe` desde la sección de releases del repositorio
2. Ejecuta `GESTO.exe`
3. La primera vez puede tardar unos segundos en cargar — es normal

**Requisitos:**
- Windows 10 o superior
- Webcam (integrada o externa)
- No requiere instalar Python ni ninguna dependencia

---

## Opción B — Ejecutar desde el código fuente

> Para desarrolladores o evaluadores que quieren revisar el código.

### Requisitos previos
- Python **3.10** (versión exacta recomendada)
- Git
- Webcam

### Pasos

**1. Clonar el repositorio**
```bash
git clone https://github.com/Dilaansg/Gesto.git
cd Gesto
```

**2. Crear el entorno virtual**
```bash
python -m venv lsc_env
```

**3. Activar el entorno virtual**

Windows PowerShell:
```bash
.\lsc_env\Scripts\Activate.ps1
```

Windows CMD:
```bash
lsc_env\Scripts\activate
```

Si PowerShell da error de permisos, ejecutar primero:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**4. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**5. Ejecutar la app**
```bash
python main.py
```

---

## Configuración de cámara

Si la cámara no abre correctamente, ve a **Configuración ⚙** dentro de la app y cambia el índice de cámara:
- `0` — cámara integrada del portátil
- `1` — cámara externa USB
- `2` — segunda cámara externa

---

## Estructura del proyecto
```
Gesto/
├── main.py                        # punto de entrada
├── config.py                      # configuración de la app (cámara, modo, etc.)
├── progreso.py                    # gestor de progreso del usuario
├── modelo_lsc.p                   # modelo entrenado (Random Forest, 99.9% precisión)
├── config.json                    # configuración guardada (se crea al correr)
├── progreso.json                  # progreso del usuario (se crea al correr)
│
├── modulos/
│   ├── menu_principal.py          # menú con camino de aprendizaje
│   ├── leccion.py                 # pantalla de lección por letra
│   ├── juego1.py                  # juego: identifica la seña
│   ├── juego2.py                  # juego: haz la seña + mini práctica
│   ├── traductor.py               # modo libre de traducción
│   └── configuracion.py           # pantalla de configuración
│
├── modelo/
│   ├── capturar_datos_v2.py       # script para capturar dataset
│   ├── entrenar_modelo_v2.py      # script para reentrenar el modelo
│   └── dataset_lsc_v2.csv         # dataset con 21 letras (~1300 muestras/letra)
│
└── recursos/
    └── images_database_procesadas/ # fotos de señas por letra para Juego 1
        ├── A/
        ├── B/
        └── ...
```

---

## Módulos de la app

**Menú principal** — camino de aprendizaje por secciones (Básico, Intermedio I, Intermedio II, Avanzado). Cada sección tiene lecciones por letra, Juego 1 y Juego 2.

**Lección** — muestra la imagen de la seña, instrucciones y un tip. Incluye botón "¡Inténtalo!" que abre la cámara para practicar la letra antes de continuar.

**Juego 1** — muestra una fotografía de una seña y el usuario debe seleccionar la letra correcta entre 4 opciones. Se necesita 6/8 aciertos para pasar.

**Juego 2** — el modelo detecta en tiempo real la seña que hace el usuario. Incluye barra de confianza y bloqueo de confirmación si la seña no es clara. Se necesita 4/5 aciertos para pasar.

**Traductor** — modo libre sin lecciones ni puntaje. Detecta señas en tiempo real y acumula el historial de letras.

**Configuración** — selector de cámara con preview en vivo, modo oscuro/claro, resetear progreso, enviar comentarios y enlace al repositorio.

---

## Modelo de detección

- **Algoritmo:** Random Forest (300 árboles)
- **Librería de detección:** MediaPipe Hands (Google) — 21 puntos 3D de la mano
- **Letras soportadas:** A B C D E F I K L M N O P Q R T U V W X Y (21 letras estáticas)
- **Letras no soportadas:** G H J Ñ S Z (requieren movimiento)
- **Precisión en test:** 99.9%
- **Normalización:** coordenadas relativas a la muñeca, invariante a distancia y posición
- **Soporte para zurdos:** dataset aumentado con espejo de coordenadas X
- **Umbral de confianza:** 70% mínimo para aceptar una predicción

---

## Reentrenar el modelo

Si se quieren agregar nuevas letras o mejorar la detección:
```bash
# 1. Capturar nuevos datos
python modelo/capturar_datos_v2.py

# 2. Reentrenar
python modelo/entrenar_modelo_v2.py
```

El nuevo `modelo_lsc.p` reemplaza al anterior automáticamente.

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.10 | Lenguaje principal |
| MediaPipe Hands | Detección de landmarks de la mano |
| scikit-learn | Modelo Random Forest |
| OpenCV | Captura de cámara y procesamiento |
| CustomTkinter | Interfaz gráfica |
| Pillow | Procesamiento de imágenes |

---

## Equipo

Ingeniería de Sistemas — 2026

- Dilan Osorio ⚡︎
- Jhon Oviedo
- Ana Ochoa
- Juan Martínez
- Daniel Ortíz

---
## Herramientas de desarrollo

La lógica avanzada, arquitectura de módulos, pipeline de detección con normalización,
integración de cámara en hilos separados y depuración/optimización general
de la aplicación fueron desarrollados con asistencia de **Claude (Anthropic)**.

*Última actualización: 22 de Marzo 2026*