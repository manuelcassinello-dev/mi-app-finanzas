import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo
st.set_page_config(page_title="Mi Salud Financiera", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #007BFF; }</style>", unsafe_allow_html=True)

# 2. Enlace de datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    # Limpieza de datos
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df['Importe'] = df['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce').fillna(0)

    st.title("📊 Análisis de Flujos: Ingresos vs Gastos")
    st.divider()

    # --- SEPARACIÓN DE DATOS ---
    df_ingresos = df[df['Categoria'] == 'Ingreso']
    df_gastos = df[df['Categoria'] == 'Gasto']
    df_inversiones = df[df['Categoria'] == 'Inversion']

    # --- MÉTRICAS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Ingresos", f"{df_ingresos['Importe'].sum():,.2f} €")
    c2.metric("Total Gastos", f"{df_gastos['Importe'].sum():,.2f} €")
    c3.metric("Total Inversiones", f"{df_inversiones['Importe'].sum():,.2f} €")

    # --- BLOQUE VISUAL: LOS DOS GRÁFICOS ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("🔵 Origen de Ingresos")
        if not df_ingresos.empty:
            fig_ing = px.pie(
                df_ingresos, 
                values='Importe', 
                names='Concepto', 
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Blues_r # Tonos azules
            )
            st.plotly_chart(fig_ing, use_container_width=True)
        else:
            st.info("No hay datos de ingresos")

    with col_der:
        st.subheader("🔴 Destino de Gastos")
        if not df_gastos.empty:
            fig_gas = px.pie(
                df_gastos, 
                values='Importe', 
                names='Concepto', 
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Reds_r # Tonos rojos
            )
            st.plotly_chart(fig_gas, use_container_width=True)
        else:
            st.info("No hay datos de gastos")

    # --- GRÁFICO DE INVERSIONES (Si existen) ---
    if not df_inversiones.empty:
        st.subheader("🟢 Detalle de Inversiones")
        fig_inv = px.bar(
            df_inversiones, x='Concepto', y='Importe',
            color_discrete_sequence=['#28A745']
        )
        st.plotly_chart(fig_inv, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
