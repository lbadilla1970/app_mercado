import streamlit as st
import pandas as pd
import numpy as np
from dashboards import general, grupo, mapa
from utils.calculos import calculo_1
from utils.charts import kpi_card

st.set_page_config(layout="wide")

# Simula o carga los datos
np.random.seed(42)
df = pd.DataFrame({
    'Categoría': np.random.choice(['A', 'B', 'C', 'D'], size=200),
    'Valor': np.random.randint(10, 100, size=200),
    'Fecha': pd.date_range(start='2023-01-01', periods=200, freq='D'),
    'Grupo': np.random.choice(['X', 'Y'], size=200)
})

# Sidebar para navegación
pagina = st.sidebar.selectbox("Seleccione una vista", [
    "Resumen General", 
    "Análisis por Grupo", 
    "Mapa"
])


# Lógica de navegación
if pagina == "Resumen General":
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Dotación", value="250", delta="+10 respecto al mes anterior", color="#1f77b4", width=200, height=100)
    with col2:
        kpi_card("Sueldo Promedio", "$1.200.000", "-2%", "#2ca02c", width=200, height=100)
    with col3:
        kpi_card("Rotación Mensual", "3.2%", "+0.4%", "#d62728", width=200, height=100)
        
    general.mostrar(df)
elif pagina == "Análisis por Grupo":
    grupo.mostrar(df)
elif pagina == "Mapa":
    mapa.mostrar(df)

