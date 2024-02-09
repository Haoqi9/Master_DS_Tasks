# Librerías
from getpass import getpass
import matplotlib.pyplot as plt
import pandas as pd
import random as rd

plt.style.use('ggplot')


def mostrar_menu():
    """
    Muestra el menú principal del juego por pantalla.
    """
    print('1. Partida modo solitario')
    print('2. Partida 2 jugadores')
    print('3. Estadística')
    print('4. Salir')

def mostrar_sub_menu():
    """
    Muestra el menú de las opciones de dificultad por pantalla.
    """
    print('1. Fácil(20 intentos)')
    print('2. Medio(12 intentos)')
    print('3. Difícil(5 intentos)')

def validar_num(minimo, maximo):
    """
    Devuelve el número (no negativo) seleccionado que esté en el intervalo dado.
    """
    while True:
        numero = input(f'Introduzca un número entre {minimo} y {maximo}: ')
        if numero.isdigit() and (minimo <= int(numero) <= maximo):
            return int(numero)

def obtener_numero_solitario(minimo, maximo):
    """
    Devuelve un número aletario dentro del intervalo dado.
    """
    return rd.randint(minimo, maximo)

def obtener_numero_2jugadores(minimo, maximo):
    """
    Devuelve un número oculto dentro del intervalo dado.
    """
    while True:
        numero = getpass(f'Introduzca un número entre {minimo} y {maximo}: ')
        if numero.isdigit() and (minimo <= int(numero) <= maximo):
            return int(numero)

def obtener_numero_intentos(opcion_dificultad):
    """
    Devuelve el número de intentos según la dificultad elejida.
    """
    if opcion_dificultad == 1:
        return 20
    elif opcion_dificultad == 2:
        return 12
    elif opcion_dificultad == 3:
        return 5

def obtener_respuesta():
    """
    Devuelve un string 'yes' o 'no' según la elección del jugador.
    """
    respuesta = input('¿Quieres volver al menú principal? (yes or no): ').lower()
    while respuesta not in ['yes', 'no']:
        respuesta = input("Introduzca 'yes' o 'no': ").lower()
    return respuesta

def obtener_numero_adivinado(minimo, maximo, num_intento, total_intentos):
    """
    Devuelve el número seleccionado que esté en el intervalo dado 
    y un mensaje que indica el número de intento/turno actual.
    """
    while True:
        numero = input(f'El número secreto está entre el {minimo} y {maximo} (intento número {num_intento} de {total_intentos}): ')
        if numero.isdigit() and (minimo <= int(numero) <= maximo):
            return int(numero)

def crear_estructura_hoja_inicial(objeto_workbook, nombre_hoja):
    """
    Crea la estructura inicial de una hoja de excel con zeros como valores iniciales:
    * 2 filas: 'Jugadas', 'Ganadas'.
    * 4 columnas: 'Fácil', 'Medio', 'Difícil', 'All'.
    """
    objeto_workbook[nombre_hoja]['A2'] = 'Jugadas'
    objeto_workbook[nombre_hoja]['A3'] = 'Ganadas'
    
    objeto_workbook[nombre_hoja]['B1'] = 'Fácil'
    objeto_workbook[nombre_hoja]['C1'] = 'Medio'
    objeto_workbook[nombre_hoja]['D1'] = 'Difícil'
    objeto_workbook[nombre_hoja]['E1'] = 'All'
    
    objeto_workbook[nombre_hoja]['B2'].value = 0  # facil jugadas
    objeto_workbook[nombre_hoja]['B3'].value = 0  # facil ganadas

    objeto_workbook[nombre_hoja]['C2'].value = 0  # medio jugadas
    objeto_workbook[nombre_hoja]['C3'].value = 0  # medio ganadas

    objeto_workbook[nombre_hoja]['D2'].value = 0  # dificil jugadas
    objeto_workbook[nombre_hoja]['D3'].value = 0  # dificil ganadas
    
    objeto_workbook[nombre_hoja]['E2'].value = 0  # All jugadas
    objeto_workbook[nombre_hoja]['E3'].value = 0  # All ganadas

def actualizar_estadisticas(objeto_workbook, nombre_hoja, opcion_dificultad, ganada = True):
    """
    Actualiza los datos de las hojas de excel correspondientes al nombre del jugador y
    la hoja 'total' según la dificultad del juego y de si la partida ha sido ganada o perdida.
    """
    if opcion_dificultad == 1:
        objeto_workbook[nombre_hoja]['B2'].value += 1      # facil jugadas
        objeto_workbook['total']['B2'].value += 1          # total facil jugadas
        if ganada is True:
            objeto_workbook[nombre_hoja]['B3'].value += 1  # facil ganadas
            objeto_workbook['total']['B3'].value += 1      # total facil ganadas
    
    elif opcion_dificultad == 2:
        objeto_workbook[nombre_hoja]['C2'].value += 1      # medio jugadas
        objeto_workbook['total']['C2'].value += 1          # total medio jugadas
        if ganada is True:
            objeto_workbook[nombre_hoja]['C3'].value += 1  # medio ganadas
            objeto_workbook['total']['C3'].value += 1      # total medio ganadas
            
    elif opcion_dificultad == 3:
        objeto_workbook[nombre_hoja]['D2'].value += 1      # dificil jugadas
        objeto_workbook['total']['D2'].value += 1          # total dificil jugadas
        if ganada is True:
            objeto_workbook[nombre_hoja]['D3'].value += 1  # dificil ganadas
            objeto_workbook['total']['D3'].value += 1      # total dificil ganadas
            
    objeto_workbook[nombre_hoja]['E2'].value += 1          # All jugadas
    objeto_workbook['total']['E2'].value += 1              # total All jugadas
    if ganada is True:
        objeto_workbook[nombre_hoja]['E3'].value += 1      # All ganadas
        objeto_workbook['total']['E3'].value += 1          # total All ganadas

def mostrar_menu_estadisticas():
    """
    Muestra el menú de las opciones de visualización de las estadísticas por pantalla.
    """
    print('1. Visualizar estadísticas de forma descriptiva.')
    print('2. Visualizar estadísticas de forma gráfica.')

def visualizar_estadisticas_descriptivas(objeto_workbook, nombre_hoja):
    """
    Muestra las estadísticas totales del jugador/'total' de forma descriptiva (en texto) por la pantalla.
    """
    print("Jugador: ".rjust(9), nombre_hoja)
    print("Fácil: ".rjust(9), "Del total de", objeto_workbook[nombre_hoja]['B2'].value, "partida/s, se ha/n ganado", objeto_workbook[nombre_hoja]['B3'].value)
    print("Medio: ".rjust(9), "Del total de", objeto_workbook[nombre_hoja]['C2'].value, "partida/s, se ha/n ganado", objeto_workbook[nombre_hoja]['C3'].value)
    print("Difícil: ".rjust(9), "Del total de", objeto_workbook[nombre_hoja]['D2'].value, "partida/s, se ha/n ganado", objeto_workbook[nombre_hoja]['D3'].value)
    print("All: ".rjust(9), "Del total de", objeto_workbook[nombre_hoja]['E2'].value, "partida/s, se ha/n ganado", objeto_workbook[nombre_hoja]['E3'].value)

def visualizar_estadisticas_graficas(objeto_workbook, nombre_jugador):
    """
    Muestra las estadísticas totales del jugador/'total' por medio de un gráfico de barras horizontales por la pantalla.
    """
    df = pd.DataFrame({
                        nombre_jugador + ': ' + objeto_workbook[nombre_jugador]['B1'].value: [objeto_workbook[nombre_jugador]['B3'].value, objeto_workbook[nombre_jugador]['B2'].value],
                        nombre_jugador + ': ' + objeto_workbook[nombre_jugador]['C1'].value: [objeto_workbook[nombre_jugador]['C3'].value, objeto_workbook[nombre_jugador]['C2'].value],
                        nombre_jugador + ': ' + objeto_workbook[nombre_jugador]['D1'].value: [objeto_workbook[nombre_jugador]['D3'].value, objeto_workbook[nombre_jugador]['D2'].value],
                        nombre_jugador + ': ' + objeto_workbook[nombre_jugador]['E1'].value: [objeto_workbook[nombre_jugador]['E3'].value, objeto_workbook[nombre_jugador]['E2'].value]
                        },
                        index=[objeto_workbook[nombre_jugador]['A3'].value, objeto_workbook[nombre_jugador]['A2'].value])
    
    df.plot.barh(subplots=True,
                figsize=(8, 6),
                alpha=0.6,
                cmap='viridis')
    
    plt.tight_layout()
    plt.show()