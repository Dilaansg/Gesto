# progreso.py
# este archivo maneja todo el estado del usuario
# si algo falla aqui, falla todo, para FRONT END: 
# no hay que tocar esto, skip jajajaj
import json
import os

ARCHIVO = "progreso.json"

# estructura completa del camino de aprendizaje
# el orden importa — es el orden en que se desbloquean
CAMINO = {
    "basico": {
        "nombre": "Básico",
        "letras": ["A", "E", "I", "O", "U"],
        "tiene_final": False
    },
    "intermedio_1": {
        "nombre": "Intermedio I",
        "letras": ["B", "C", "D", "F", "L", "V"],
        "tiene_final": True
    },
    "intermedio_2": {
        "nombre": "Intermedio II",
        "letras": ["K", "R", "T", "Q", "W", "X", "Y"],
        "tiene_final": True
    },
    "avanzado": {
        "nombre": "Avanzado",
        "letras": ["M", "N", "P"],
        "tiene_final": True
    }
}

PROXIMO = ["G", "H", "Ñ", "S", "Z"]

# estado base para un usuario nuevo
PROGRESO_INICIAL = {
    "seccion_actual": "basico",
    "letras_completadas": [],
    "secciones_completadas": [],
    "puntaje_total": 0
}


def cargar():
    # carga el progreso desde el archivo. Si no existe, crea uno nuevo
    if not os.path.exists(ARCHIVO):
        guardar(PROGRESO_INICIAL.copy())
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar(progreso):
    #guardar el progreso
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(progreso, f, ensure_ascii=False, indent=2)


def completar_letra(letra, puntos=10):
    # suma puntos si la letra está completada
    progreso = cargar()
    if letra not in progreso["letras_completadas"]:
        progreso["letras_completadas"].append(letra)
    progreso["puntaje_total"] += puntos
    guardar(progreso)


def completar_seccion(seccion):
    #desbloquea la siguiente sección si la anterior ya se completó
    progreso = cargar()
    if seccion not in progreso["secciones_completadas"]:
        progreso["secciones_completadas"].append(seccion)

    # desbloquear la siguiente sección
    secciones = list(CAMINO.keys())
    idx = secciones.index(seccion)
    if idx + 1 < len(secciones):
        progreso["seccion_actual"] = secciones[idx + 1]

    guardar(progreso)


def letra_disponible(letra):
   #comprueba si la letra está disponible para el usuario
    progreso = cargar()
    secciones = list(CAMINO.keys())

    for seccion_id, seccion in CAMINO.items():
        if letra in seccion["letras"]:
            idx_seccion = secciones.index(seccion_id)
            seccion_actual_idx = secciones.index(progreso["seccion_actual"])

            # disponible si es la sección actual o una anterior
            if idx_seccion <= seccion_actual_idx:
                return True
            return False
    return False


def letra_completada(letra):
    #comprueba si ya se completo la letra
    progreso = cargar()
    return letra in progreso["letras_completadas"]


def seccion_desbloqueada(seccion_id):
    #comprueba si ya se puede jugar la sección
    progreso = cargar()
    secciones = list(CAMINO.keys())
    idx_seccion = secciones.index(seccion_id)
    idx_actual = secciones.index(progreso["seccion_actual"])
    return idx_seccion <= idx_actual


def seccion_completada_check(seccion_id):
    #comprueba si todas las letras de la sección están completadas.
    progreso = cargar()
    letras = CAMINO[seccion_id]["letras"]
    return all(l in progreso["letras_completadas"] for l in letras)


def resetear():
    #borrar el progreso
    guardar(PROGRESO_INICIAL.copy())


def reporte():
    progreso = cargar()
    print("\n=== PROGRESO DEL USUARIO ===")
    print(f"Sección actual: {progreso['seccion_actual']}")
    print(f"Letras completadas: {progreso['letras_completadas']}")
    print(f"Secciones completadas: {progreso['secciones_completadas']}")
    print(f"Puntaje total: {progreso['puntaje_total']}")


if __name__ == "__main__":
    reporte()