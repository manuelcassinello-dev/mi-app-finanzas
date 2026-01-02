import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración
st.set_page_config(page_title="Control Financiero Pro", layout="wide")

# URLs de Google Sheets
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GID_MIS_MOV = "0"
GID_MIS_INV = "863168602"
GID_FAM_MOV = "23613697"

# 2. Función para limpiar y procesar datos
def procesar_datos(gid):
    df_temp = pd.read_csv(URL_BASE + gid)
    df_temp.columns = df_temp.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    if 'Importe' in df_temp.columns:
        df_temp['Importe'] = pd.to_numeric(df_temp['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    if 'Felicidad' in df_temp.columns:
        df_temp['Felicidad'] = pd.to_numeric(df_temp['Felicidad'], errors='coerce').fillna(0)
    if 'Fecha' in df_temp.columns:
        df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha'], dayfirst=True)
        df_temp['Año'] = df_temp['Fecha'].dt.year
        df_temp['Mes_Año'] = df_temp['Fecha'].dt.strftime('%Y-%m')
    return df_temp

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["👤 Mis Finanzas", "🏠 Finanzas Familiares"])

with tab1:
    st.title("Mi Patrimonio Personal")
    # Carga datos personales
    df_m = procesar_datos(GID_MIS_MOV)
    df_i = procesar_datos(GID_MIS_INV)
    
    # KPIs Verdes (Inversiones)
    val_act = df_i['Valor_Actual'].sum()
    inv_ini = df_i['Precio_Compra'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Patrimonio en Inversiones", f"{val_act:,.2f} €", f"{val_act-inv_ini:,.2f} €")
    c2.metric("Capital Invertido", f"{inv_ini:,.2f} €")
    c3.metric("Rentabilidad Media", f"{(val_act-inv_ini)/inv_ini*100:.2f} %" if inv_ini != 0 else "0%")

    # Gráficos Inversión
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.plotly_chart(px.pie(df_i, values='Valor_Actual', names='Ticket', hole=0.5, title="Distribución por Activo", color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
    with col_inv2:
        df_i['Ganancia'] = df_i['Valor_Actual'] - df_i['Precio_Compra']
        st.plotly_chart(px.bar(df_i, x='Ticket', y='Ganancia', color='Ganancia', title="Ganancia por Fondo", color_continuous_scale='Greens'), use_container_width=True)

    # Donuts de Gastos/Ingresos Personales
    st.divider()
    anho_p = st.sidebar.selectbox("Año (Personal)", sorted(df_m['Año'].unique(), reverse=True), key="ap")
    df_p_filt = df_m[df_m['Año'] == anho_p]
    
    cp1, cp2 = st.columns(2)
    with cp1:
        st.plotly_chart(px.pie(df_p_filt[df_p_filt['Categoria']=='Ingreso'], values='Importe', names='Concepto', hole=0.5, title="Ingresos Personales", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
    with cp2:
        st.plotly_chart(px.pie(df_p_filt[df_p_filt['Categoria']=='Gasto'], values='Importe', names='Concepto', hole=0.5, title="Gastos Personales", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)

with tab2:
    st.title("Cuentas Familiares")
    # Carga SOLO datos familiares
    df_f = procesar_datos(GID_FAM_MOV)
    
    # Filtro año familiar
    anho_f = st.sidebar.selectbox("Año (Familiar)", sorted(df_f['Año'].unique(), reverse=True), key="af")
    df_f_filt = df_f[df_f['Año'] == anho_f]
    
    # KPIs Familiares (Sin inversiones)
    ing_f = df_f_filt[df_f_filt['Categoria'] == 'Ingreso']['Importe'].sum()
    gas_f = df_f_filt[df_f_filt['Categoria'] == 'Gasto']['Importe'].sum()
    
    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("Ingresos Familiares", f"{ing_f:,.2f} €")
    cf2.metric("Gastos Familiares", f"{gas_f:,.2f} €")
    cf3.metric("Ahorro Familiar", f"{ing_f - gas_f:,.2f} €")

    # Donuts Familiares
    st.divider()
    colf1, colf2 = st.columns(2)
    with colf1:
        st.plotly_chart(px.pie(df_f_filt[df_f_filt['Categoria']=='Ingreso'], values='Importe', names='Concepto', hole=0.5, title="Origen Ingresos Familia", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
    with colf2:
        st.plotly_chart(px.pie(df_f_filt[df_f_filt['Categoria']=='Gasto'], values='Importe', names='Concepto', hole=0.5, title="Destino Gastos Familia", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)
