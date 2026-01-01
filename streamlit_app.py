import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración General
st.set_page_config(page_title="Control Patrimonial Total", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Conexión a datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"

try:
    # Carga y limpieza de datos
    df_mov = pd.read_csv(URL_MOVIMIENTOS)
    df_inv = pd.read_csv(URL_INVERSIONES)
    for df in [df_mov, df_inv]:
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

    # Limpieza numérica Movimientos
    df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)
    df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True)
    df_mov['Año'] = df_mov['Fecha'].dt.year
    df_mov['Mes_Año'] = df_mov['Fecha'].dt.strftime('%Y-%m')

    # Limpieza numérica Inversiones
    for col in ['Precio_Compra', 'Valor_Actual']:
        df_inv[col] = df_inv[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)

    # --- SECCIÓN 1: PATRIMONIO ACTUAL (INVERSIONES) ---
    st.title("🏛️ Mi Patrimonio Global")
    
    total_invertido = df_inv['Precio_Compra'].sum()
    valor_actual_inv = df_inv['Valor_Actual'].sum()
    plusvalia = valor_actual_inv - total_invertido
    rent_pct = (plusvalia / total_invertido * 100) if total_invertido != 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Valor Cartera Hoy", f"{valor_actual_inv:,.2f} €", f"{plusvalia:,.2f} €")
    m2.metric("Capital Invertido", f"{total_invertido:,.2f} €")
    m3.metric("Rentabilidad Total", f"{rent_pct:.2f} %")

    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.subheader("🟢 Distribución de Inversiones")
        fig_inv = px.pie(df_inv, values='Valor_Actual', names='Ticket', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_inv, use_container_width=True)
    with col_inv2:
        st.subheader("📈 Ganancia por Activo (€)")
        df_inv['Ganancia'] = df_inv['Valor_Actual'] - df_inv['Precio_Compra']
        fig_gan = px.bar(df_inv, x='Ticket', y='Ganancia', color='Ganancia',
                         color_continuous_scale=['#DC3545', '#28A745'])
        st.plotly_chart(fig_gan, use_container_width=True)

    st.divider()

    # --- SECCIÓN 2: EVOLUCIÓN HISTÓRICA ---
    st.subheader("📉 Evolución del Patrimonio Neto")
    # Cálculo de ahorro acumulado + valor inicial inversiones
    evol_ahorro = df_mov.groupby('Mes_Año').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Mensual')
    evol_ahorro['Acumulado'] = evol_ahorro['Mensual'].cumsum() + valor_actual_inv - (df_mov[df_mov['Categoria'] == 'Inversion']['Importe'].sum())
    
    fig_linea = px.line(evol_ahorro, x='Mes_Año', y='Acumulado', markers=True, 
                        line_shape="spline", color_discrete_sequence=['#28A745'])
    st.plotly_chart(fig_linea, use_container_width=True)

    st.divider()

    # --- SECCIÓN 3: FILTROS Y FLUJO MENSUAL (GASTOS/INGRESOS) ---
    st.sidebar.header("🔎 Explorador Temporal")
    anho_sel = st.sidebar.selectbox("Año", sorted(df_mov['Año'].unique(), reverse=True))
    mes_sel = st.sidebar.selectbox("Mes", ["Todos"] + sorted(df_mov[df_mov['Año'] == anho_sel]['Mes_Año'].unique()))

    df_f = df_mov[df_mov['Año'] == anho_sel]
    if mes_sel != "Todos": df_f = df_f[df_f['Mes_Año'] == mes_sel]

    st.subheader(f"💸 Análisis de Flujos: {mes_sel if mes_sel != 'Todos' else anho_sel}")
    
    c_ing, c_gas = st.columns(2)
    with c_ing:
        st.markdown("### 🔵 Ingresos")
        fig_i = px.pie(df_f[df_f['Categoria'] == 'Ingreso'], values='Importe', names='Concepto', hole=0.5,
                       color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_i, use_container_width=True)
    with c_gas:
        st.markdown("### 🔴 Gastos")
        fig_g = px.pie(df_f[df_f['Categoria'] == 'Gasto'], values='Importe', names='Concepto', hole=0.5,
                       color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig_g, use_container_width=True)

    # Tabla resumen al final
    with st.expander("Ver detalle de movimientos filtrados"):
        st.dataframe(df_f[['Fecha', 'Concepto', 'Importe', 'Categoria', 'Tipo']], use_container_width=True)

except Exception as e:
    st.error(f"Error en la fusión de datos: {e}")
