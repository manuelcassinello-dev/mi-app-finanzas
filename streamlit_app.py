import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de pantalla
st.set_page_config(page_title="Mi Fintonic Personal", layout="wide")

# Estilo visual profesional
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stMetric"] { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border-top: 4px solid #00d1b2; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Enlace de datos (Formato exportación CSV)
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    # Leemos saltando la primera fila (skiprows=1) porque tus títulos están en la fila 2
    df = pd.read_csv(URL_MOVIMIENTOS, skiprows=1)
    
    # Limpieza automática: quita espacios y tildes de los nombres de las columnas
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

    st.title("📱 Mi Panel Financiero")
    st.divider()

    # --- CÁLCULOS PRINCIPALES ---
    # Filtramos para evitar errores si hay filas vacías
    df = df.dropna(subset=['Importe', 'Tipo', 'Categoria'])
    
    ingresos = df[df['Categoria'].str.contains('Ingreso', case=False, na=False)]['Importe'].sum()
    gastos_fijos = df[df['Tipo'].str.contains('Fijo', case=False, na=False)]['Importe'].sum()
    gastos_variables = df[df['Tipo'].str.contains('Variable', case=False, na=False)]['Importe'].sum()
    ahorro = ingresos - (gastos_fijos + gastos_variables)

    # --- BLOQUE 1: MÉTRICAS TOP ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", f"{ingresos:,.2f} €")
    col2.metric("Gastos Fijos", f"{gastos_fijos:,.2f} €")
    col3.metric("Gastos Variables", f"{gastos_variables:,.2f} €")
    col4.metric("Ahorro Neto", f"{ahorro:,.2f} €", delta=f"{(ahorro/ingresos*100) if ingresos>0 else 0:.1f}%")

    # --- BLOQUE 2: GRÁFICOS ---
    st.subheader("Análisis Visual")
    c1, c2 = st.columns(2)
    
    with c1:
        # Gráfico de gastos por categoría (excluyendo ingresos)
        df_gastos = df[~df['Categoria'].str.contains('Ingreso', case=False, na=False)]
        fig_cat = px.pie(df_gastos, values='Importe', names='Categoria', hole=0.6,
                         title="Distribución por Categoría",
                         color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        # Gráfico Fijo vs Variable
        fig_tipo = px.pie(df_gastos, values='Importe', names='Tipo', hole=0.6,
                          title="Fijos vs Variables",
                          color_discrete_map={'Fijo': '#1e293b', 'Variable': '#00d1b2'})
        st.plotly_chart(fig_tipo, use_container_width=True)

    # --- BLOQUE 3: TABLA DE DATOS ---
    with st.expander("Ver movimientos recientes"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("⚠️ Error de conexión o formato")
    st.info("Asegúrate de que en la FILA 2 de tu Excel tienes exactamente estos títulos: Fecha, Concepto, Importe, Categoria, Tipo, Felicidad")
    st.write("Detalle del error para soporte:", e)
