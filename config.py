# config.py — en la raíz del proyecto
# maneja toda la configuración persistente de la app
# NO tocar la estructura del JSON

import json
import os
import subprocess
import sys

def _ruta_datos(nombre_archivo):
    """Devuelve la ruta correcta tanto en desarrollo como en el .exe"""
    if getattr(sys, 'frozen', False):
        # corriendo como .exe — guardar junto al ejecutable
        base = os.path.dirname(sys.executable)
    else:
        # corriendo como script — guardar en la raíz del proyecto
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, nombre_archivo)

ARCHIVO = _ruta_datos("config.json")



CONFIG_INICIAL = {
    "camara": 0,              # índice de la cámara (0 = integrada, 1 = externa)
    "modo_oscuro": True,      # tema de la app
    "version": "1.0.0"
}

def cargar():
    """Carga la configuración. Si no existe, crea una nueva."""
    if not os.path.exists(ARCHIVO):
        guardar(CONFIG_INICIAL.copy())
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)
    if "camara" not in config:
        config["camara"] = 0
        guardar(config)
    return config

def guardar(config):
    """Guarda la configuración."""
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_camara():
    """Retorna el índice de cámara configurado."""
    return cargar().get("camara", 1)

def get_modo_oscuro():
    """Retorna si el modo oscuro está activo."""
    return cargar().get("modo_oscuro", True)

def set_camara(indice):
    config = cargar()
    config["camara"] = indice
    guardar(config)

def set_modo_oscuro(valor):
    config = cargar()
    config["modo_oscuro"] = valor
    guardar(config)

def guardar_comentario(texto):
    """Agrega un comentario al archivo comentarios.txt con fecha y hora."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}]\n{texto}\n{'-'*50}\n"
    with open("comentarios.txt", "a", encoding="utf-8") as f:
        f.write(linea)

def abrir_repositorio():
    """Abre el repositorio en el navegador."""
    url = "https://github.com/Dilaansg/Gesto"
    if sys.platform == "win32":
        os.startfile(url)
    else:
        subprocess.Popen(["open", url])


# en config.py agregar al final:

# en config.py reemplazar las paletas por estas:

PALETA_OSCURA = {
    # fondos
    "fondo":            "#0f0a1e",   # fondo principal de la app
    "fondo_card":       "#1a1333",   # fondo de tarjetas/paneles
    "fondo_muted":      "#2d1b69",   # fondo de elementos secundarios

    # texto
    "texto_principal":  "#f3f0ff",   # texto principal
    "texto_secundario": "#9ca3af",   # texto gris/muted
    "texto_bloqueado":  "#4b5563",   # texto de elementos bloqueados

    # colores de acción
    "primario":         "#a78bfa",   # botones primarios, tabs activos
    "primario_fondo":   "#1a1333",   # fondo de botones primarios
    "secundario":       "#2d1b69",   # botones secundarios
    "acento":           "#7c3aed",   # acentos, bordes activos

    # bordes
    "borde":            "#2d1b69",   # borde general
    "borde_activo":     "#7c3aed",   # borde de elementos activos

    # estados de lección
    "completado":       "#34d399",   # verde — lección completada
    "disponible":       "#a78bfa",   # morado — lección disponible
    "bloqueado":        "#4b5563",   # gris — lección bloqueada

    # feedback
    "error":            "#C0392B",
    "advertencia":      "#E8A020",
}

PALETA_CLARA = {
    # fondos
    "fondo":            "#f8f7fc",   # fondo principal
    "fondo_card":       "#ffffff",   # fondo de tarjetas
    "fondo_muted":      "#f3f4f6",   # fondo de elementos secundarios

    # texto
    "texto_principal":  "#1a1625",   # texto principal
    "texto_secundario": "#6b7280",   # texto gris/muted
    "texto_bloqueado":  "#9ca3af",   # texto de elementos bloqueados

    # colores de acción
    "primario":         "#7c3aed",   # botones primarios, tabs activos
    "primario_fondo":   "#ffffff",   # fondo de botones primarios
    "secundario":       "#e9d5ff",   # botones secundarios
    "acento":           "#a78bfa",   # acentos, bordes activos

    # bordes
    "borde":            "#e5e7eb",   # borde general
    "borde_activo":     "#ac4dff",   # borde de elementos activos

    # estados de lección
    "completado":       "#10b981",   # verde — lección completada
    "disponible":       "#7c3aed",   # morado — lección disponible
    "bloqueado":        "#9ca3af",   # gris — lección bloqueada

    # feedback
    "error":            "#d4183d",
    "advertencia":      "#E8A020",
}

def get_paleta():
    return PALETA_OSCURA if get_modo_oscuro() else PALETA_CLARA

