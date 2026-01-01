import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración y Estilo
st.set_page_config(page_title="Mi Panel Financiero", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #00d1b2; }</style>", unsafe_allow_html=True)

# 2. Enlace de datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    # Limpieza de datos
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df['Importe'] = df['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce').fillna(0)

    # Creamos una columna de color según la categoría
    def asignar_color(cat):
        if cat == 'Ingreso': return '#007BFF'  # AZUL
        if cat == 'Inversion': return '#28A745' # VERDE
        return '#DC3545' # ROJO (para todo lo demás/gastos)

    df['Color'] = df['Categoria'].apply(asignar_color)

    st.title("📊 Mi Salud Financiera")
    st.divider()

    # --- CÁLCULOS ---
    total_ingresos = df[df['Categoria'] == 'Ingreso']['Importe'].sum()
    total_inversiones = df[df['Categoria'] == 'Inversion']['Importe'].sum()
    total_gastos = df[(df['Categoria'] != 'Ingreso') & (df['Categoria'] != 'Inversion')]['Importe'].sum()
    balance = total_ingresos - total_gastos - total_inversiones

    # --- BLOQUE 1: MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos (Azul)", f"{total_ingresos:,.2f} €")
    c2.metric("Gastos (Rojo)", f"{total_gastos:,.2f} €")
    c3.metric("Inversiones (Verde)", f"{total_inversiones:,.2f} €")
    c4.metric("Balance Real", f"{balance:,.2f} €")

    # --- BLOQUE 2: ANÁLISIS VISUAL CON TUS COLORES ---
    st.subheader("Distribución de Movimientos")
    
    # Gráfico de Tarta de Categorías Reales (Conceptos)
    fig_conceptos = px.pie(
        df, 
        values='Importe', 
        names='Concepto', 
        hole=0.5,
        title="Desglose por Concepto (Nómina, Parking, etc.)",
        color='Categoria',
        color_discrete_map={'Ingreso': '#007BFF', 'Inversion': '#28A745', 'Gasto': '#DC3545'}
    )
    st.plotly_chart(fig_conceptos, use_container_width=True)

    # Gráfico de Barras de Comparativa
    st.subheader("Comparativa de Flujos")
    fig_barras = px.bar(
        df, 
        x='Categoria', 
        y='Importe', 
        color='Categoria',
        title="Ingresos vs Gastos vs Inversiones",
        color_discrete_map={'Ingreso': '#007BFF', 'Inversion': '#28A745', 'Gasto': '#DC3545'}
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # --- TABLA DE DATOS ---
    with st.expander("Ver movimientos detallados"):
        st.dataframe(df[['Fecha', 'Concepto', 'Importe', 'Categoria', 'Tipo']], use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar: {e}")
