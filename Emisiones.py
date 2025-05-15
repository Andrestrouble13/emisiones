import pandas as pd
import numpy as np
from datetime import datetime

# Paso 1: Cargar los archivos desde 2017 en adelante
def cargar_datos():
    archivos = [
        'emisiones-2019.csv.csv',
        'emisiones-2018.csv.csv',
        'emisiones-2017.csv.csv'
        'emisiones-2016.csv.csv'
    ]
    df_list = []
    for archivo in archivos:
        try:
            df = pd.read_csv(archivo, sep=';', encoding='latin1')
            df_list.append(df)
        except FileNotFoundError:
            print(f"Archivo no encontrado: {archivo}")
    return pd.concat(df_list, ignore_index=True)

# Paso 2: Filtrar columnas relevantes
def filtrar_columnas(df):
    columnas_base = ['ESTACION', 'MAGNITUD', 'ANO', 'MES']
    columnas_dias = [col for col in df.columns if col.startswith('D')]
    return df[columnas_base + columnas_dias]

# Paso 3: Reestructurar el DataFrame (melt)
def reestructurar(df):
    df_melted = df.melt(id_vars=['ESTACION', 'MAGNITUD', 'ANO', 'MES'],
                        value_vars=[col for col in df.columns if col.startswith('D')],
                        var_name='DIA',
                        value_name='VALOR')
    df_melted['DIA'] = df_melted['DIA'].str.extract('D(\d+)', expand=False).astype(int)
    return df_melted

# Paso 4: Crear columna de fecha y limpiar
def crear_fecha(df):
    df['FECHA'] = pd.to_datetime(dict(year=df['ANO'], month=df['MES'], day=df['DIA']), errors='coerce')
    df = df[~df['FECHA'].isna()]
    df = df.sort_values(['ESTACION', 'MAGNITUD', 'FECHA'])
    return df

# Paso 5: Mostrar estaciones y contaminantes disponibles
def mostrar_estaciones_y_contaminantes(df):
    print("Estaciones disponibles:", sorted(df['ESTACION'].unique()))
    print("Contaminantes disponibles:", sorted(df['MAGNITUD'].unique()))

# Paso 6: Función para emisiones por estación, contaminante y fechas
def emisiones_por_estacion_contaminante(df, estacion, contaminante, fecha_inicio, fecha_fin):
    mask = (
        (df['ESTACION'] == estacion) &
        (df['MAGNITUD'] == contaminante) &
        (df['FECHA'] >= fecha_inicio) &
        (df['FECHA'] <= fecha_fin)
    )
    return df.loc[mask, ['FECHA', 'VALOR']].set_index('FECHA').squeeze()

# Paso 7: Resumen descriptivo por contaminante
def resumen_por_contaminante(df):
    return df.groupby('MAGNITUD')['VALOR'].describe()

# Paso 8: Resumen por estación y contaminante
def resumen_por_distrito(df):
    return df.groupby(['ESTACION', 'MAGNITUD'])['VALOR'].describe()

# Paso 9: Resumen de una estación y contaminante específico
def resumen_estacion_contaminante(df, estacion, contaminante):
    df_filtrado = df[(df['ESTACION'] == estacion) & (df['MAGNITUD'] == contaminante)]
    return df_filtrado['VALOR'].describe()

# Paso 10: Medias mensuales para un contaminante y un año
def medias_mensuales_contaminante(df, contaminante, anio):
    df_filtrado = df[(df['MAGNITUD'] == contaminante) & (df['FECHA'].dt.year == anio)]
    return df_filtrado.groupby(['ESTACION', df_filtrado['FECHA'].dt.month])['VALOR'].mean().unstack()

# Paso 11: Medias mensuales por estación para todos los contaminantes
def medias_mensuales_por_estacion(df, estacion):
    df_filtrado = df[df['ESTACION'] == estacion]
    return df_filtrado.groupby([df_filtrado['FECHA'].dt.month, 'MAGNITUD'])['VALOR'].mean().unstack()

# MAIN
def main():
    df = cargar_datos()
    df = filtrar_columnas(df)
    df = reestructurar(df)
    df = crear_fecha(df)
    
    mostrar_estaciones_y_contaminantes(df)

    # Ejemplo de uso:
    print("\n--- Resumen general por contaminante ---")
    print(resumen_por_contaminante(df))

    print("\n--- Resumen estación 4 y contaminante 8 ---")
    print(resumen_estacion_contaminante(df, estacion=4, contaminante=8))

    print("\n--- Medias mensuales del contaminante 8 en 2019 ---")
    print(medias_mensuales_contaminante(df, contaminante=8, anio=2019))

    print("\n--- Medias mensuales por contaminante en estación 4 ---")
    print(medias_mensuales_por_estacion(df, estacion=4))

if __name__ == '__main__':
    main()