import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo Fintonic
st.set_page_config(page_title="Mi Fintonic Personal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #00d1b2; }
    h3 { color: #1e293b; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Enlace de Google Sheets (Corregido)
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    # Intento de lectura de datos
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    st.title("📱 Mi Salud Financiera")

    # --- BLOQUE 1: RESUMEN DE GASTOS ---
    st.subheader("Análisis de Gastos")
    col1, col2, col3 = st.columns(3)
    
    # Cálculos dinámicos
    gastos_fijos = df[df['Tipo'] == 'Fijo']['Importe'].sum()
    gastos_variables = df[df['Tipo'] == 'Variable']['Importe'].sum()
    ingresos = df[df['Categoria'] == 'Ingreso']['Importe'].sum()

    col1.metric("Ingresos", f"{ingresos:,.2f} €")
    col2.metric("Gastos Fijos", f"{gastos_fijos:,.2f} €", delta="- Obligación", delta_color="inverse")
    col3.metric("Gastos Variables", f"{gastos_variables:,.2f} €", delta="- Ocio", delta_color="normal")

    # --- BLOQUE 2: GRÁFICOS CIRCULARES ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**Gastos por Categoría**")
        fig_cat = px.pie(df[df['Categoria'] != 'Ingreso'], values='Importe', names='Categoria', hole=0.7,
                         color_discrete_sequence=px.colors.sequential.Mint)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        st.write("**Fijos vs Variables**")
        fig_tipo = px.pie(df[df['Categoria'] != 'Ingreso'], values='Importe', names='Tipo', hole=0.7,
                          color_discrete_map={'Fijo': '#1e293b', 'Variable': '#00d1b2'})
        st.plotly_chart(fig_tipo, use_container_width=True)

    # --- BLOQUE 3: INVERSIONES ---
    st.divider()
    st.subheader("📈 Mis Inversiones")
    
    # Valores de ejemplo (puedes cambiarlos según tu Excel)
    valor_compra = 10000 
    valor_actual = 11500 
    beneficio = valor_actual - valor_compra
    progreso = (beneficio / valor_compra) * 100

    m1, m2 = st.columns(2)
    m1.metric("Patrimonio Invertido", f"{valor_actual:,.2f} €", f"+{beneficio:,.2f} €")
    m2.metric("Rentabilidad", f"{progreso:.2f} %", "Total acumulado")

except Exception as e:
    st.error("⚠️ Error detectado al leer el Google Sheets")
    st.write("Detalle técnico:", e)
    st.info("💡 Consejo: Revisa que tu Google Sheets tenga estas columnas: Fecha, Concepto, Importe, Categoria, Tipo, Felicidad")
