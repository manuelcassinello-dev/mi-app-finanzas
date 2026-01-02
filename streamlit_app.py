import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de Estilo y Página
st.set_page_config(page_title="Control Patrimonial Total", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Conexión a Datos (Tus 3 hojas de Google Sheets)
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"
URL_FAMILIAR = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=23613697"

# --- ESTRUCTURA DE PESTAÑAS ---
tab_p, tab_f = st.tabs(["👤 Mis Finanzas", "🏠 Finanzas Familiares"])

# ==========================================
# PESTAÑA 1: TU CÓDIGO ORIGINAL (TAL CUAL)
# ==========================================
with tab_p:
    try:
        # --- CARGA Y LIMPIEZA ---
        df_mov = pd.read_csv(URL_MOVIMIENTOS)
        df_inv = pd.read_csv(URL_INVERSIONES)
        for df in [df_mov, df_inv]:
            df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

        # Limpieza numérica de Movimientos
        df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)
        df_mov['Felicidad'] = pd.to_numeric(df_mov['Felicidad'], errors='coerce').fillna(0)
        df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True)
        df_mov['Año'] = df_mov['Fecha'].dt.year
        df_mov['Mes_Año'] = df_mov['Fecha'].dt.strftime('%Y-%m')

        # Limpieza numérica de Inversiones
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
            fig_inv = px.pie(df_inv, values='Valor_Actual', names='Ticket', hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig_inv, use_container_width=True)
        with col_inv2:
            st.subheader("📈 Ganancia Realizada por Fondo")
            df_inv['Ganancia'] = df_inv['Valor_Actual'] - df_inv['Precio_Compra']
            fig_bar = px.bar(df_inv, x='Ticket', y='Ganancia', color='Ganancia', color_continuous_scale='Greens')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # --- SECCIÓN 2: EVOLUCIÓN HISTÓRICA ---
        st.subheader("📈 Evolución del Patrimonio Neto")
        evol_m = df_mov.groupby('Mes_Año').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Ahorro')
        punto_partida = total_inv_actual - evol_m['Ahorro'].sum()
        evol_m['Acumulado'] = evol_m['Ahorro'].cumsum() + punto_partida
        
        fig_evol = px.line(evol_m, x='Mes_Año', y='Acumulado', markers=True, line_shape="spline", color_discrete_sequence=['#28A745'])
        st.plotly_chart(fig_evol, use_container_width=True)

        st.divider()

        # --- SECCIÓN 3: FILTROS Y FLUJO DE CAJA ---
        st.sidebar.header("🔎 Filtros Personales")
        anho_sel = st.sidebar.selectbox("Selecciona Año", sorted(df_mov['Año'].unique(), reverse=True))
        mes_sel = st.sidebar.selectbox("Selecciona Mes", ["Todos"] + sorted(df_mov[df_mov['Año'] == anho_sel]['Mes_Año'].unique()))

        df_f = df_mov[df_mov['Año'] == anho_sel]
        if mes_sel != "Todos": df_f = df_f[df_f['Mes_Año'] == mes_sel]

        # --- MÓDULO FELICIDAD FINANCIERA ---
        st.header("😊 Felicidad Financiera")
        df_gastos_f = df_f[df_f['Categoria'] == 'Gasto']
        
        if not df_gastos_f.empty:
            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                fig_h = px.scatter(df_gastos_f, x="Importe", y="Felicidad", size="Importe", color="Concepto",
                                   hover_name="Concepto", title="¿Vale lo que cuesta?")
                st.plotly_chart(fig_h, use_container_width=True)
            with col_f2:
                df_gastos_f['Eficiencia'] = df_gastos_f['Importe'] / df_gastos_f['Felicidad'].replace(0, 1)
                top_ef = df_gastos_f.groupby('Concepto')['
