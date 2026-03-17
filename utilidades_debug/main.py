import lsc_traductor as tr
import utilidades_debug.captura_abecedario as ca
import utilidades_debug.entrenar_lsc as en
def menu():
    while True:
        print("="*26)
        print("⚡​MENU PARA EL MODELO⚡​")
        print("="*26)
        print("Oprima [1] para usar el traductor")
        print("Oprima [2] para capturar una nueva letra")
        print("Oprima [3] para entrenar el modelo")
        print("Oprima [0] para salir")
        respuesta = int(input("Seleccione que quiere hacer: "))

        if (respuesta == 1):
            tr.ejecutar_traductor()
        elif (respuesta == 2):
            letra = input("Ingrese la letra a capturar: ").upper()
            if len(letra) == 1:
                ca.ejecutar_capturar(letra)
            else:
                print("X Ingrese solo un carácter.")
        elif (respuesta == 3):
            en.ejecutar_entrenador()
        elif (respuesta == 0):
            break
        else:
            print ("X Opción incorrecta.")

if __name__ == "__main__":
    menu()
