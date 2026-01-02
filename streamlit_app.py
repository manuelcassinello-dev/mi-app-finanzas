import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuracion de pagina
st.set_page_config(page_title="Control Financiero", layout="wide")

# URLs de Google Sheets (GIDs verificados)
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "p_mov": "0",
    "p_inv": "863168602",
    "f_mov": "23613697"
}

# 2. Funcion de carga ultra-robusta
def cargar_datos(gid):
    try:
        df = pd.read_csv(URL_BASE + gid)
        # Limpiar nombres de columnas (quitar espacios y tildes para evitar errores)
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o').str.replace('ñ', 'n')
        
        # Convertir numeros (maneja formato europeo 1.234,56)
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

    # KPIs Inversiones (Solo en Personal)
    if not df_i.empty:
        v_act = df_i['Valor_Actual'].sum()
        v_ini = df_i['Precio_Compra'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Valor Cartera", f"{v_act:,.2f} EUR", f"{v_act-v_ini:,.2f} EUR")
        c2.metric("Capital Invertido", f"{v_ini:,.2f} EUR")
        c3.metric("Rentabilidad", f"{((v_act-v_ini)/v_ini*100):.2f} %" if v_ini != 0 else "0%")

        # Graficos Inversion
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.pie(df_i, values='Valor_Actual', names='Ticket', hole=0.5, title="Distribucion Activos"), use_container_width=True)
        with g2:
            df_i['Ganancia'] = df_i['Valor_Actual'] - df_i['Precio_Compra']
            st.plotly_chart(px.bar(df_i, x='Ticket', y='Ganancia', color='Ganancia', title="Ganancia por Fondo", color_continuous_scale='Greens'), use_container_width=True)

    # Linea de Evolucion Patrimonial
    if not df_m.empty:
        st.subheader("Evolucion del Patrimonio Neto")
        v_inv_total = df_i['Valor_Actual'].sum() if not df_i.empty else 0
        evol = df_m.groupby('Mes_Anio').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Neto')
        evol['Acumulado'] = evol['Neto'].cumsum() + (v_inv_total - df_m[df_m['Categoria'] == 'Inversion']['Importe'].sum())
        st.plotly_chart(px.line(evol, x='Mes_Anio', y='Acumulado', markers=True, title="Crecimiento Total"), use_container_width=True)

    # Filtros y Felicidad
    st.divider()
    anios = sorted(df_m['Anio'].unique(), reverse=True) if not df_m.empty else [2026]
    sel_anio = st.sidebar.selectbox("Filtro Anio (Personal)", anios, key="sp")
    df_p_f = df_m[df_m['Anio'] == sel_anio] if not df_m.empty else pd.DataFrame()

    if not df_p_f.empty:
        st.subheader("Analisis de Gastos y Felicidad")
        df_gas = df_p_f[df_p_f['Categoria'] == 'Gasto']
        if not df_gas.empty:
            f1, f2 = st.columns([2,1])
            with f1:
                st.plotly_chart(px.scatter(df_gas, x="Importe", y="Felicidad", size="Importe", color="Concepto", hover_name="Concepto", title="¿Vale lo que cuesta?"), use_container_width=True)
            with f2:
                df_gas['Ef'] = df_gas['Importe'] / df_gas['Felicidad'].replace(0, 1
