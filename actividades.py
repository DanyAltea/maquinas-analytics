import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px



### Cargar el set de datos

url = "https://drive.google.com/uc?export=download&id=1w41dVQb-O7tfgtl40Do8h6PMhu3Lgamt"
df = pd.read_excel(url)
print(df)

# Convertir las fechas manejando el formato día/mes/año
df['Registrationdate'] = pd.to_datetime(df['Registrationdate'], dayfirst=True, errors='coerce')

# Crear un contenedor horizontal para la selección de máquina y fechas
col1, col2, col3 = st.columns(3)

# Selección de la máquina (en la primera columna)
with col1:
    maquinas_disponibles = df['equipo'].unique()  # Obtener todas las máquinas únicas
    maquina_seleccionada = st.selectbox("Selecciona la máquina", options=maquinas_disponibles)

# Filtrar los datos por la máquina seleccionada
df_maquina = df[df['equipo'] == maquina_seleccionada]

# Filtro de fecha en Streamlit (en las otras columnas)
fecha_min = pd.to_datetime('2024-01-01')  # Definir la fecha mínima como 2024/01/01
fecha_max = df_maquina['Registrationdate'].max()

with col2:
    fecha_inicio = st.date_input("Fecha de inicio", value=fecha_min.date(), min_value=fecha_min.date(), max_value=fecha_max.date())

with col3:
    fecha_fin = st.date_input("Fecha de fin", value=fecha_max.date(), min_value=fecha_min.date(), max_value=fecha_max.date())

# Filtrar los datos según las fechas seleccionadas
df_filtrado = df_maquina[(df_maquina['Registrationdate'].dt.date >= fecha_inicio) & (df_maquina['Registrationdate'].dt.date <= fecha_fin)]

# Excluir los tipos de tiempo 'TNP'
df_filtrado = df_filtrado[df_filtrado['tipoTiempo'] != 'TNP']

# Agrupar los datos por tipoTiempo y sumar los minutos
data_agrupada = df_filtrado.groupby('tipoTiempo')['minutos'].sum()

# Colores asignados a cada tipoTiempo
colores = {'UPDT': 'red', 'Planned': 'yellow', 'Run': 'green', 'Otros': 'blue', 'R': 'purple'}

# Crear un gráfico de pastel
fig, ax = plt.subplots(figsize=(2, 2))

# Función para mostrar los minutos y el porcentaje en el gráfico de pastel
def func(pct, allval):
    absolute = int(pct / 100.*allval)  # Calcular el valor absoluto de minutos
    return f"{absolute} min\n({pct:.1f}%)"

# Crear el gráfico de pastel
ax.pie(data_agrupada, labels=data_agrupada.index, autopct=lambda pct: func(pct, sum(data_agrupada)),
       colors=[colores.get(x, 'gray') for x in data_agrupada.index], startangle=90, wedgeprops={'edgecolor': 'black'},
       textprops={'fontsize': 5})  # Cambiar el tamaño de letra

# Añadir un título
ax.set_title(f"Distribución de tiempo para {maquina_seleccionada}", fontsize = 8)

# Mostrar el gráfico
plt.tight_layout()
st.pyplot(fig)

# Mostrar la tabla debajo del gráfico
st.write("### Causales de tiempo UPDT")
st.write("La siguiente tabla muestra las órdenes, productos, causales y minutos filtrados para la máquina y el rango de fechas seleccionados:")

# Filtrar por tipoTiempo 'UPDT'
df_updt = df_filtrado[df_filtrado['tipoTiempo'] == 'UPDT']
# Seleccionar columnas relevantes
columnas_mostrar = ['orden', 'producto', 'justificacion', 'HoraInicial', 'minutos']
tabla_detalle = df_updt[columnas_mostrar]
df['orden'] = df['orden'].fillna(0).astype(int)
st.dataframe(tabla_detalle.style.format({"orden": "{:.0f}", "minutos": "{:.1f}"}), width=800)