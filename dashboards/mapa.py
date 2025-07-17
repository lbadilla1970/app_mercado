import plotly.express as px
import altair as alt
import streamlit as st
import numpy as np
import pandas as pd

def mostrar(df):
    st.title("Mapa de Registros (coordenadas aleatorias)")
    # Simular coordenadas geográficas
    mapa = pd.DataFrame({
        'lat': -36.82 + np.random.rand(100) * 0.1,
        'lon': -73.05 + np.random.rand(100) * 0.1,
    })
    st.map(mapa)
    st.markdown("📍 Muestra de coordenadas simuladas cerca de Concepción, Chile")
