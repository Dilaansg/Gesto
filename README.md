# Proyecto Gesto - Traductor de Lengua de Señas Colombiana (LSC)

### CONFIGURACION INICIAL (LEER ANTES DE EMPEZAR)
Para mantener el repositorio ligero y evitar errores de compatibilidad, NO se subió la carpeta lsc_env. Cada integrante debe crear su propio entorno virtual:

### Clonar el repositorio:
git clone https://github.com/Dilaansg/Gesto.git
cd Gesto

### Crear el Entorno Virtual (venv):
python -m venv lsc_env

### Activar el Entorno:

Windows (PowerShell): .\lsc_env\Scripts\Activate.ps1

Windows (CMD): lsc_env\Scripts\activate

Mac/Linux: source lsc_env/bin/activate

### Instalar Dependencias:
Una vez activado el entorno (veras el nombre lsc_env en la terminal), ejecuta:
pip install -r requirements.txt

NOTA: Se usa mediapipe==0.10.11 por estabilidad. No actualizarlo.

### COMO EJECUTAR EL SISTEMA
Ejecuta el menu principal con:
python main.py

Opciones:

Traductor: Abre la camara y traduce en tiempo real.

Captura: Recolecta datos para nuevas señas.

Entrenar: Actualiza el archivo modelo_lsc.p con los nuevos datos.

### REGLAS DE ORO
NO SUBIR la carpeta lsc_env al repositorio.

Si instalas una libreria nueva, corre: pip freeze > requirements.txt

Haz un 'git pull' siempre antes de empezar a trabajar.

Evita trabajar dentro de carpetas de OneDrive para prevenir errores de permisos.

Ultima actualizacion: 11 / 03 / 2026