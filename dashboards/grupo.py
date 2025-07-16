import plotly.express as px
import altair as alt
import streamlit as st

def mostrar(df):
    st.title("Análisis Detallado por Grupo")

    grupo = st.selectbox("Selecciona un Grupo", df['Grupo'].unique())
    filtro = df[df['Grupo'] == grupo]

    st.write(f"Datos filtrados por Grupo: {grupo}")
    st.dataframe(filtro.head(10))

    fig = px.histogram(filtro, x='Valor', nbins=20, color='Categoría')
    st.plotly_chart(fig, use_container_width=True)

    st.line_chart(filtro.groupby('Fecha')['Valor'].mean())
