import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de pantalla
st.set_page_config(page_title="Mi Fintonic Personal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stMetric"] { 
        background-color: #ffffff; border-radius: 12px; padding: 20px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #00d1b2; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Enlace de datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    # LEER SIN SALTAR FILAS (Tus títulos están en la fila 1 según tu imagen)
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    # LIMPIEZA TOTAL: Quita espacios, tildes y pone todo en minúsculas para comparar mejor
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    
    # Aseguramos que los nombres de las columnas sean los correctos internamente
    columnas_necesarias = ['Fecha', 'Concepto', 'Importe', 'Categoria', 'Tipo']
    
    st.title("📱 Mi Panel Financiero")
    st.divider()

    # --- PROCESAMIENTO ---
    # Convertimos Importe a número por si acaso
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce').fillna(0)
    
    # Quitamos filas que no tengan datos esenciales
    df = df.dropna(subset=['Importe', 'Categoria'])

    # Cálculos
    ingresos = df[df['Categoria'].str.contains('Ingreso|Nomina', case=False, na=False)]['Importe'].sum()
    gastos_fijos = df[df['Tipo'].str.contains('Fijo', case=False, na=False)]['Importe'].sum()
    gastos_variables = df[df['Tipo'].str.contains('Variable', case=False, na=False)]['Importe'].sum()
    ahorro = ingresos - (gastos_fijos + gastos_variables)

    # --- MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", f"{ingresos:,.2f} €")
    col2.metric("Gastos Fijos", f"{gastos_fijos:,.2f} €")
    col3.metric("Gastos Variables", f"{gastos_variables:,.2f} €")
    col4.metric("Balance Neto", f"{ahorro:,.2f} €")

    # --- GRÁFICOS ---
    st.subheader("Análisis Visual")
    c1, c2 = st.columns(2)
    
    with c1:
        df_gastos = df[~df['Categoria'].str.contains('Ingreso|Nomina', case=False, na=False)]
        fig_cat = px.pie(df_gastos, values='Importe', names='Categoria', hole=0.6, title="Categorías")
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        fig_tipo = px.pie(df_gastos, values='Importe', names='Tipo', hole=0.6, title="Fijo vs Variable")
        st.plotly_chart(fig_tipo, use_container_width=True)

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("⚠️ Error de lectura")
    st.write("Asegúrate de que en la FILA 1 de tu Excel los títulos sean: **Fecha, Concepto, Importe, Categoria, Tipo, Felicidad**")
    st.write("Detalle técnico:", e)
