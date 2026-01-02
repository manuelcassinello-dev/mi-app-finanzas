import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página y Estilo
st.set_page_config(page_title="Control Financiero Pro", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. URLs de Google Sheets
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "pers_mov": "0",
    "pers_inv": "863168602",
    "fam_mov": "23613697"
}

# 3. Función de procesamiento de datos
def cargar(gid):
    df = pd.read_csv(URL_BASE + gid)
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    # Limpieza de números
    for col in ['Importe', 'Precio_Compra', 'Valor_Actual', 'Felicidad']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    # Fechas y Tiempo
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
        df['Año'] = df['Fecha'].dt.year
        df['Mes_Año'] = df['Fecha'].dt.strftime('%Y-%m')
    return df

# --- INTERFAZ ---
tab_p, tab_f = st.tabs(["👤 Mis Finanzas", "🏠 Finanzas Familiares"])

with tab_p:
    st.title("Mi Patrimonio Personal")
    df_m = cargar(GIDS["pers_mov"])
    df_i = cargar(GIDS["pers_inv"])

    # KPIs de Inversión (Los cuadros verdes)
    v_act = df_i['Valor_Actual'].sum()
    v_ini = df_i['Precio_Compra'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor Cartera", f"{v_act:,.2f} €", f"{v_act-v_ini:,.2f} €")
    c2.metric("Inversión Inicial", f"{v_ini:,.2f} €")
    c3.metric("Rentabilidad", f"{((v_act-v_ini)/v_ini*100):.2f} %" if v_ini != 0 else "0%")

    # Gráficos Inversión
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(px.pie(df_i, values='Valor_Actual', names='Ticket', hole=0.5, title="Distribución"), use_container_width=True)
    with g2:
        df_i['Ganancia'] = df_i['Valor_Actual'] - df_i['Precio_Compra']
        st.plotly_chart(px.bar(df_i, x='Ticket', y='Gan
