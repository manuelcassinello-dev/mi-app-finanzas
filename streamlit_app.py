import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo
st.set_page_config(page_title="Mi Panel Financiero", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #00d1b2; }</style>", unsafe_allow_html=True)

# 2. Enlace de datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    # Limpieza de nombres de columnas y datos
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df['Importe'] = df['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce').fillna(0)

    st.title("📱 Análisis Total: Ingresos, Gastos e Inversiones")
    st.divider()

    # --- CLASIFICACIÓN DE DATOS ---
    df_ingresos = df[df['Categoria'] == 'Ingreso']
    df_inversiones = df[df['Categoria'] == 'Inversion']
    # Los gastos es todo lo que NO es ingreso ni inversion
    df_gastos = df[(df['Categoria'] != 'Ingreso') & (df['Categoria'] != 'Inversion')]

    # --- CÁLCULOS PARA MÉTRICAS ---
    total_ingresos = df_ingresos['Importe'].sum()
    total_inversiones = df_inversiones['Importe'].sum()
    total_gastos = df_gastos['Importe'].sum()
    balance_final = total_ingresos - total_gastos - total_inversiones

    # --- BLOQUE 1: MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos", f"{total_ingresos:,.2f} €")
    c2.metric("Gastos Totales", f"{total_gastos:,.2f} €", delta_color="inverse")
    c3.metric("Inversiones", f"{total_inversiones:,.2f} €", delta="Ahorro")
    c4.metric("Disponible Real", f"{balance_final:,.2f} €")

    # --- BLOQUE 2: ANÁLISIS VISUAL ---
    st.subheader("Distribución del Capital")
    col_a, col_b = st.columns(2)
    
    with col_a:
        # GRÁFICO 1: ¿A dónde va mi dinero? (Gastos vs Inversiones)
        # Creamos un resumen rápido para este gráfico
        resumen_data = {
            'Concepto': ['Gastos', 'Inversiones'],
            'Total': [total_gastos, total_inversiones]
        }
        df_resumen = pd.DataFrame(resumen_data)
        fig1 = px.pie(df_resumen, values='Total', names='Concepto', hole=0.5,
                      title="Destino del Ingreso (Gastos vs Inversión)",
                      color_discrete_map={'Gastos': '#ff4b4b', 'Inversiones': '#00d1b2'})
        st.plotly_chart(fig1, use_container_width=True)
            
    with col_b:
        # GRÁFICO 2: Detalle de Categorías (Incluye todo para ver pesos relativos)
        fig2 = px.sunburst(df, path=['Categoria', 'Concepto'], values='Importe',
                           title="Mapa Detallado de Movimientos",
                           color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig2, use_container_width=True)

    # --- TABLA ---
    with st.expander("Ver historial de movimientos"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
