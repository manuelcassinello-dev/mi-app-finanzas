import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de Estilo y Página
st.set_page_config(page_title="Control Patrimonial Total", layout="wide")

# ESTILO CORREGIDO: Eliminamos el fondo blanco fijo para que sea compatible con Modo Oscuro (Móvil)
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
        df_mov = pd.read_csv(URL_MOVIMIENTOS)
        df_inv = pd.read_csv(URL_INVERSIONES)
        for df in [df_mov, df_inv]:
            df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

        df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)
        df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True, errors='coerce')
        df_mov = df_mov.dropna(subset=['Fecha']) 
        df_mov['Año'] = df_mov['Fecha'].dt.year
        df_mov['Mes_Año'] = df_mov['Fecha'].dt.strftime('%Y-%m')

        for col in ['Precio_Compra', 'Valor_Actual']:
            df_inv[col] = df_inv[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)

        st.title("🏛️ Mi Patrimonio Global")
        t_act = df_inv['Valor_Actual'].sum()
        t_inv = df_inv['Precio_Compra'].sum()
        gan = t_act - t_inv
        rent = (gan / t_inv * 100) if t_inv != 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimonio Inversiones", f"{t_act:,.2f} €", f"{gan:,.2f} €")
        c2.metric("Capital Invertido", f"{t_inv:,.2f} €")
        c3.metric("Rentabilidad Media", f"{rent:.2f} %")

        st.divider()
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            st.subheader("🟢 Distribución")
            st.plotly_chart(px.pie(df_inv, values='Valor_Actual', names='Ticket', hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
        with col_inv2:
            st.subheader("📈 Ganancia")
            df_inv['Ganancia'] = df_inv['Valor_Actual'] - df_inv['Precio_Compra']
            st.plotly_chart(px.bar(df_inv, x='Ticket', y='Ganancia', color='Ganancia', color_continuous_scale='Greens'), use_container_width=True)

        st.sidebar.header("🔎 Filtros Personales")
        a_sel = st.sidebar.selectbox("Año (Personal)", sorted(df_mov['Año'].unique(), reverse=True))
        
        df_f = df_mov[df_mov['Año'] == a_sel]
        st.subheader("💸 Ingresos vs Gastos")
        cp1, cp2 = st.columns(2)
        with cp1:
            st.plotly_chart(px.pie(df_f[df_f['Categoria'] == 'Ingreso'], values='Importe', names='Concepto', hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r, title="Ingresos"), use_container_width=True)
        with cp2:
            st.plotly_chart(px.pie(df_f[df_f['Categoria'] == 'Gasto'], values='Importe', names='Concepto', hole=0.5, color_discrete_sequence=px.colors.sequential.Reds_r, title="Gastos"), use_container_width=True)

    except Exception as e:
        st.error(f"Error en Personal: {e}")

with tab_fam:
    try:
        st.title("🏠 Finanzas Familiares")
        df_fam = pd.read_csv(URL_FAMILIAR)
        df_fam.columns = df_fam.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
        
        df_fam['Importe'] = df_fam['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_fam['Importe'] = pd.to_numeric(df_fam['Importe'], errors='coerce').fillna(0)
        df_fam['Fecha'] = pd.to_datetime(df_fam['Fecha'], dayfirst=True, errors='coerce')
        df_fam = df_fam.dropna(subset=['Fecha']) 
        df_fam['Año'] = df_fam['Fecha'].dt.year

        st.sidebar.divider()
        st.sidebar.header("🏠 Filtros Familiares")
        af_sel = st.sidebar.selectbox("Año (Familiar)", sorted(df_fam['Año'].unique(), reverse=True))
        df_ff = df_fam[df_fam['Año'] == af_sel]

        # KPIs
        i_fam = df_ff[df_ff['Categoria'] == 'Ingreso']['Importe'].sum()
        g_fij = df_ff[df_ff['Tipo'] == 'Fijo']['Importe'].sum()
        g_var = df_ff[df_ff['Tipo'] == 'Variable']['Importe'].sum()
        bal = i_fam - (g_fij + g_var)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Ingresos Familia", f"{i_fam:,.2f} €")
        m2.metric("Gastos Fijos", f"{g_fij:,.2f} €")
        m3.metric("Gastos Variables", f"{g_var:,.2f} €")
        m4.metric("Balance Total", f"{bal:,.2f} €")

        st.divider()
        cf1, cf2 = st.columns(2)
        df_sg = df_ff[df_ff['Categoria'] == 'Gasto']
        
        with cf1:
            st
