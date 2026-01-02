import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de Estilo y Página
st.set_page_config(page_title="Control Patrimonial Total", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Conexión a Datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"
URL_FAMILIAR = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=23613697"

# Creamos las pestañas
tab1, tab2 = st.tabs(["👤 Finanzas Personales", "🏠 Finanzas Familiares"])

with tab1:
    try:
        # --- CARGA Y LIMPIEZA (TU CÓDIGO ORIGINAL) ---
        df_mov = pd.read_csv(URL_MOVIMIENTOS)
        df_inv = pd.read_csv(URL_INVERSIONES)
        for df in [df_mov, df_inv]:
            df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

        df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)
        df_mov['Felicidad'] = pd.to_numeric(df_mov['Felicidad'], errors='coerce').fillna(0)
        df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True)
        df_mov['Año'] = df_mov['Fecha'].dt.year
        df_mov['Mes_Año'] = df_mov['Fecha'].dt.strftime('%Y-%m')

        for col in ['Precio_Compra', 'Valor_Actual']:
            df_inv[col] = df_inv[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)

        # --- SECCIÓN 1: MI PATRIMONIO GLOBAL ---
        st.title("🏛️ Mi Patrimonio Global")
        total_inv_actual = df_inv['Valor_Actual'].sum()
        total_invertido = df_inv['Precio_Compra'].sum()
        ganancia_total = total_inv_actual - total_invertido
        rent_pct = (ganancia_total / total_invertido * 100) if total_invertido != 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimonio en Inversiones", f"{total_inv_actual:,.2f} €", f"{ganancia_total:,.2f} €")
        c2.metric("Capital Invertido", f"{total_invertido:,.2f} €")
        c3.metric("Rentabilidad Media", f"{rent_pct:.2f} %")

        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            st.subheader("🟢 Distribución por Activo")
            fig_inv = px.pie(df_inv, values='Valor_Actual', names
