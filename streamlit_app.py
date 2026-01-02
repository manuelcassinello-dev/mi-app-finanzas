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

# --- ESTRUCTURA DE PESTAÑAS ---
t1, t2 = st.tabs(["👤 Mis Finanzas", "🏠 Finanzas Familiares"])

with t1:
    try:
        # --- CARGA Y LIMPIEZA ORIGINAL ---
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

        # --- SECCIÓN 1: PATRIMONIO ---
        st.title("🏛️ Mi Patrimonio Personal")
        
        t_inv_act = df_inv['Valor_Actual'].sum()
        t_inv_ini = df_inv['Precio_Compra'].sum()
        ganancia = t_inv_act - t_inv_ini
        rent = (ganancia / t_inv_ini * 100) if t_inv_ini != 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Patrimonio en Inversiones", f"{t_inv_act:,.2f} €", f"{ganancia:,.2f} €")
        c2.metric("Capital Invertido", f"{t_inv_ini:,.2f} €")
        c3.metric("Rentabilidad Media", f"{rent:.2f} %")

        col_i1, col_i2 = st.columns(2)
        with col_i1:
            st.subheader("🟢 Distribución por Activo")
            st.plotly_chart(px.pie(df_inv, values='Valor_Actual', names='Ticket', hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
        with col_i2:
            st.subheader("📈 Ganancia por Fondo")
            df_inv['Ganancia'] = df_inv['Valor_Actual'] - df_inv['Precio_Compra']
            st.plotly_chart(px.bar(df_inv, x='Ticket', y='Ganancia', color='Ganancia', color_continuous_scale='Greens'), use_container_width=True)

        st.divider()

        # --- SECCIÓN 2: EVOLUCIÓN ---
        st.subheader("📈 Evolución del Patrimonio Neto")
        evol_m = df_mov.groupby('Mes_Año').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Ahorro')
        punto_p = t_inv_act - evol_m['Ahorro'].sum()
        evol_m['Acumulado'] = evol_m['Ahorro'].cumsum() + punto_p
        st.plotly_chart(px.line(evol_m, x='Mes_Año', y='Acumulado', markers=True, line_shape="spline", color_discrete_sequence=['#28A745']), use_container_width=True)

        # --- SECCIÓN 3: FILTROS Y FLUJO ---
        st.sidebar.header("🔎 Filtros Personales")
        a_sel = st.sidebar.selectbox("Año (Personal)", sorted(df_mov['Año'].unique(), reverse=True))
        m_sel = st.sidebar.selectbox("Mes (Personal)", ["Todos"] + sorted(df_mov[df_mov['Año'] == a_sel]['Mes_Año'].unique()))

        df_f = df_mov[df_mov['Año'] == a_sel]
        if m_sel != "Todos": df_f = df_f[df_f['Mes_Año'] == m_sel]

        st.header("😊 Felicidad Financiera")
        df_g_f = df_f[df_f['Categoria'] == 'Gasto']
        if not df_g_f.empty:
            f1, f2 = st.columns([2, 1])
            with f1:
                st.plotly_chart(px.scatter(df_g_f, x="Importe", y="Felicidad", size="Importe", color="Concepto", hover_name="Concepto"), use_container_width=True)
            with f2:
                df_g_f['Ef'] = df_g_f['Importe'] / df_g_f['Felicidad'].replace(0, 1)
                st.write("🚀 **Top Gastos Inteligentes**")
                for c, v in df_g_f.groupby('Concepto')['Ef'].mean().sort_values().head(3).items():
                    st.write(f"**{c}**: {v:.2f}€ / punto")

        st.subheader("💸 Flujo de Caja")
        d1, d2 = st.columns(2)
        with d1:
            st.plotly_chart(px.pie(df_f[df_f['Categoria'] == 'Ingreso'], values='Importe', names='Concepto', hole=0.5, title="Ingresos"), use_container_width=True)
        with d2:
            st.plotly_chart(px.pie(df_f[df_f['Categoria'] == 'Gasto'], values='Importe', names='Concepto', hole
