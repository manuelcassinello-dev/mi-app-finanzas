import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de Estilo y Página
st.set_page_config(page_title="Control Patrimonial Total", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetric"] {
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-top: 4px solid #28A745;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión a Datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"
URL_FAMILIAR = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=23613697"

# --- CREACIÓN DE PESTAÑAS ---
tab_pers, tab_fam = st.tabs(["👤 Finanzas Personales", "🏠 Finanzas Familiares"])

with tab_pers:
    try:
        # Carga Personal
        df_mov = pd.read_csv(URL_MOVIMIENTOS)
        df_inv = pd.read_csv(URL_INVERSIONES)
        
        for df in [df_mov, df_inv]:
            df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

        df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)
        df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True, errors='coerce')
        df_mov = df_mov.dropna(subset=['Fecha']) 
        df_mov['Año'] = df_mov['Fecha'].dt.year

        for col in ['Precio_Compra', 'Valor_Actual']:
            df_inv[col] = df_inv[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)

        # Filtros Personal en Sidebar
        with st.sidebar:
            st.header("🔎 Filtros Personales")
            a_p = st.selectbox("Año (Personal)", sorted(df_mov['Año'].unique(), reverse=True), key="filter_p")

        st.title("🏛️ Mi Patrimonio Personal")
        
        t_act = df_inv['Valor_Actual'].sum()
        t_inv = df_inv['Precio_Compra'].sum()
        gan = t_act - t_inv
        rent = (gan / t_inv * 100) if t_inv != 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimonio Inversiones", f"{t_act:,.2f} €", f"{gan:,.2f} €")
        c2.metric("Inversión Inicial", f"{t_inv:,.2f} €")
        c3.metric("Rentabilidad Media", f"{rent:.2f} %")

        # Proyección
        with st.expander("🔮 Ver Proyección a 12 meses"):
            df_f_p = df_mov[df_mov['Año'] == a_p]
            ahorro = df_f_p[df_f_p['Categoria'] == 'Ingreso']['Importe'].sum() - df_f_p[df_f_p['Categoria'] == 'Gasto']['Importe'].sum()
            a_medio = ahorro / 12
            proy = pd.DataFrame([{"Mes": f"Mes +{i}", "Patrimonio Est.": t_act + (a_medio * i)} for i in range
