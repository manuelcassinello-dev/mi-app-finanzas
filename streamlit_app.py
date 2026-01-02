import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(page_title="Control Financiero Pro", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Configuración de URLs
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "Personal": {"mov": "0", "inv": "863168602"},
    "Familiar": {"mov": "23613697"} 
}

# 3. Función de Carga de Datos
def get_data(gid):
    df = pd.read_csv(URL_BASE + gid)
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df['Importe'] = pd.to_numeric(df['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    if 'Felicidad' in df.columns:
        df['Felicidad'] = pd.to_numeric(df['Felicidad'], errors='coerce').fillna(0)
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
    df['Año'] = df['Fecha'].dt.year
    df['Mes_Año'] = df['Fecha'].dt.strftime('%Y-%m')
    return df

# 4. Función Interfaz Familiar (Solo Gastos/Ingresos)
def draw_family_dashboard(df_mov):
    st.title("🏠 Cuentas Familiares")
    
    # Filtro de tiempo
    anho = st.sidebar.selectbox("Año (Familiar)", sorted(df_mov['Año'].unique(), reverse=True))
    df_f = df_mov[df_mov['Año'] == anho]
    
    # KPIs de Balance
    ingresos = df_f[df_f['Categoria'] == 'Ingreso']['Importe'].sum()
    gastos = df_f[df_f['Categoria'] == 'Gasto']['Importe'].sum()
    balance = ingresos - gastos
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Totales", f"{ingresos:,.2f} €")
    c2.metric("Gastos Totales", f"{gastos:,.2f} €", delta=f"{-gastos:,.2f} €", delta_color="inverse")
    c3.metric("Balance Mensual", f"{balance:,.2f} €", delta=f"{(balance/ingresos*100) if ingresos>0 else 0:.1f}% Ahorro")

    st.divider()

    # Gráficos Circulares
    st.subheader("📊 Distribución de Gastos e Ingresos")
    col1, col2 = st.columns(2)
    
    with col1:
        df_ing = df_f[df_f['Categoria'] == 'Ingreso']
        if not df_ing.empty:
            fig_i = px.pie(df_ing, values='Importe', names='Concepto', hole=0.5, title="Origen de Ingresos", color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig_i, use_container_width=True)
    
    with col2:
        df_gas = df_f[df_f['Categoria'] == 'Gasto']
        if not df_gas.empty:
            fig_g = px.pie(df_gas, values='Importe', names='Concepto', hole=0.5, title="Destino de Gastos", color_discrete_sequence=px.colors.sequential.Reds_r)
            st.plotly_chart(fig_g, use_container_width=True)

    # Detalle de categorías (Fijos vs Variables si usas la columna Tipo)
    if 'Tipo' in df_f.columns:
        st.divider()
        st.subheader("📉 Análisis por Tipo de Gasto")
        df_tipo = df_f[df_f['Categoria'] == 'Gasto'].groupby('Tipo')['Importe'].sum().reset_index()
        fig_tipo = px.bar(df_tipo, x='Tipo', y='Importe', color='Tipo', title="Fijos vs Variables", color_discrete_map={'Fijo': '#E74C3C', 'Variable': '#F39C12'})
        st.plotly_chart(fig_tipo, use_container_width=True)

# 5. Función Interfaz Personal (Completa)
def draw_personal_dashboard(df_mov, df_inv):
    st.title("👤 Mi Patrimonio Personal")
    # ... (Aquí va tu código de inversiones y felicidad que ya funcionaba) ...
    # Nota: Por brevedad no lo repito todo, pero mantén la lógica que ya tenías.

# --- EJECUCIÓN APP ---
tab_pers, tab_fam = st.tabs(["👤 Mis Finanzas", "🏠 Finanzas Familiares"])

with tab_pers:
    # Carga datos personales (Mov + Inv)
    df
