import plotly.express as px
import altair as alt
import streamlit as st

def mostrar(df):
    st.title("Dashboard General")
    st.dataframe(df.head(10))

    st.subheader("Gráfico de Barras - Promedio por Categoría (Altair)")
    chart = alt.Chart(df).mark_bar().encode(
        x='Categoría:N',
        y='mean(Valor):Q',
        color='Categoría:N'
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Distribución por Categoría - Plotly")
    fig = px.box(df, x='Categoría', y='Valor', color='Categoría')
    st.plotly_chart(fig, use_container_width=True)