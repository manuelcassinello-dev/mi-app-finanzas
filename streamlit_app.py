import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuracion de pagina
st.set_page_config(page_title="Control Financiero", layout="wide")

# URLs de Google Sheets
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "p_mov": "0",
    "p_inv": "863168602",
    "f_mov": "23613697"
}

# 2. Funcion de carga de datos sin caracteres especiales
def cargar_datos(gid):
    try:
        df = pd.read_csv(URL_BASE + gid)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip().str.replace('i', 'i').str.replace('o', 'o')
        
        # Convertir numeros
        for col in ['Importe', 'Precio_Compra', 'Valor_Actual', 'Felicidad']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
        
        # Procesar fechas
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
            df['Anio'] = df['Fecha'].dt.year
            df['Mes_Anio'] = df['Fecha'].dt.strftime('%Y-%m')
        return df
    except:
        return pd.DataFrame()

# --- INTERFAZ ---
t_p, t_f = st.tabs(["Mis Finanzas", "Finanzas Familiares"])

with t_p:
    st.title("Mi Patrimonio Personal")
    df_m = cargar_datos(GIDS["p_mov"])
    df_i = cargar_datos(GIDS["p_inv"])

    # Metricas de Inversion
    if not df_i.empty:
        v_act = df_i['Valor_Actual'].sum()
        v_ini = df_i['Precio_Compra'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Valor Cartera", f"{v_act:,.2f} EUR", f"{v_act-v_ini:,.2f} EUR")
        c2.metric("Inversion Inicial", f"{v_ini:,.2f} EUR")
        c3.metric("Rentabilidad", f"{((v_act-v_ini)/v_ini*100):.2f} %" if v_ini != 0 else "0%")

        # Graficos Inversion
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.pie(df_i, values='Valor_Actual', names='Ticket', hole=0.5, title="Distribucion"), use_container_width=True)
        with g2:
            df_i['Ganancia'] = df_i['Valor_Actual'] - df_i['Precio_Compra']
            st.plotly_chart(px.bar(df_i, x='Ticket', y='Ganancia', color='Ganancia', title="Ganancia por Fondo", color_continuous_scale='Greens'), use_container_width=True)

    # Evolucion Patrimonial (Recuperada)
    if not df_m.empty:
        st.subheader("Evolucion del Patrimonio")
        v_inv_total = df_i['Valor_Actual'].sum() if not df_i.empty else 0
        evol = df_m.groupby('Mes_Anio').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Neto')
        evol['Acumulado'] = evol['Neto'].cumsum() + (v_inv_total - df_m[df_m['Categoria'] == 'Inversion']['Importe'].sum())
        st.plotly_chart(px.line(evol, x='Mes_Anio', y='Acumulado', markers=True, title="Patrimonio Neto Total"), use_container_width=True)

    # Felicidad y Analisis
    st.divider()
    anios_p = sorted(df_m['Anio'].unique(), reverse=True) if not df_m.empty else [2026]
    sel_anio_p = st.sidebar.selectbox("Filtro Anio Personal", anios_p, key="sp")
    df_
