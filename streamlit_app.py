import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Control Financiero Pro", layout="wide")

# URLs de Google Sheets
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "personal_mov": "0",
    "personal_inv": "863168602",
    "familiar_mov": "23613697"
}

# 2. Función de procesamiento segura
def procesar_datos(gid):
    try:
        df = pd.read_csv(URL_BASE + gid)
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
        
        # Limpieza de números
        for col in ['Importe', 'Precio_Compra', 'Valor_Actual', 'Felicidad']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
        
        # Fechas
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['Fecha'])
            df['Año'] = df['Fecha'].dt.year
        return df
    except Exception as e:
        st.error(f"Error al cargar la hoja {gid}: {e}")
        return pd.DataFrame()

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["👤 Mis Finanzas", "🏠 Finanzas Familiares"])

with tab1:
    st.header("Mi Patrimonio Personal")
    df_m = procesar_datos(GIDS["personal_mov"])
    df_i = procesar_datos(GIDS["personal_inv"])

    # KPIs de Inversión Seguros
    if not df_i.empty:
        val_act = df_i['Valor_Actual'].sum()
        inv_ini = df_i['Precio_Compra'].sum()
        ganancia = val_act - inv_ini
        rent = (ganancia / inv_ini * 100) if inv_ini != 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimonio Inversiones", f"{val_act:,.2f} €", f"{ganancia:,.2f} €")
        c2.metric("Inversión Inicial", f"{inv_ini:,.2f} €")
        c3.metric("Rentabilidad Media", f"{rent:.2f} %")
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df_i, values='Valor_Actual', names='Ticket', hole=0.5, title="Distribución", color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
        with col2:
            df_i['Ganancia_Ind'] = df_i['Valor_Actual'] - df_i['Precio_Compra']
            st.plotly_chart(px.bar(df_i, x='Ticket', y='Ganancia_Ind', color='Ganancia_Ind', title="Ganancia por Fondo", color_continuous_scale='Greens'), use_container_width=True)
    else:
        st.info("No se detectaron datos de inversiones.")

with tab2:
    st.header("Cuentas Familiares")
    df_f = procesar_datos(GIDS["familiar_mov"])

    if not df_f.empty:
        # Selector de Año
        anho_f = st.selectbox("Selecciona el Año", sorted(df_f['Año'].unique(), reverse=True), key="sel_f")
        df_f_filt = df_f[df_f['Año'] == anho_f]
        
        # Totales
        ing_f = df_f_filt[df_f_filt['Categoria'] == 'Ingreso']['Importe'].sum()
        gas_f = df_f_filt[df_f_filt['Categoria'] == 'Gasto']['Importe'].sum()
        
        cf1, cf2, cf3 = st.columns(3)
        cf1.metric("Ingresos Familiares", f"{ing_f:,.2f} €")
        cf2.metric("Gastos Familiares", f"{gas_f:,.2f} €")
        cf3.metric("Balance / Ahorro", f"{ing_f - gas_f:,.2f} €")

        # Gráficos de Flujo
        colf1, colf2 = st.columns(2)
        with colf1:
            st.plotly_chart(px.pie(df_f_filt[df_f_filt['Categoria']=='Ingreso'], values='Importe', names='Concepto', hole=0.5, title="Ingresos", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
        with colf2:
            st.plotly_chart(px.pie(df_f_filt[df_f_filt['Categoria']=='Gasto'], values='Importe', names='Concepto', hole=0.5, title="Gastos", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)
    else:
        st.warning("La pestaña familiar del Excel parece estar vacía o mal configurada.")
