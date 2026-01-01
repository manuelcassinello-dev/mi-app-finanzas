import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo
st.set_page_config(page_title="Patrimonio y Evolución Pro", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Enlaces (Asegúrate de que los GID sean correctos)
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"

try:
    # CARGA Y LIMPIEZA
    df_mov = pd.read_csv(URL_MOVIMIENTOS)
    df_inv = pd.read_csv(URL_INVERSIONES)
    
    for df in [df_mov, df_inv]:
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

    # Procesar Importes
    df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)

    # Procesar Fechas para evolución temporal
    df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True)
    df_mov['Año'] = df_mov['Fecha'].dt.year
    df_mov['Mes_Nombre'] = df_mov['Fecha'].dt.strftime('%b')
    df_mov['Mes_Año'] = df_mov['Fecha'].dt.strftime('%Y-%m')

    # Procesar Inversiones (Estado actual)
    for col in ['Precio_Compra', 'Valor_Actual']:
        df_inv[col] = df_inv[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)
    
    valor_cartera_hoy = df_inv['Valor_Actual'].sum()

    # --- SIDEBAR: FILTROS TEMPORALES ---
    st.sidebar.header("📅 Filtros de Tiempo")
    anhos = sorted(df_mov['Año'].unique(), reverse=True)
    anho_sel = st.sidebar.selectbox("Selecciona el Año", anhos)
    
    meses = sorted(df_mov[df_mov['Año'] == anho_sel]['Mes_Año'].unique())
    mes_sel = st.sidebar.selectbox("Selecciona el Mes (opcional)", ["Todos"] + meses)

    # Filtrar datos de movimientos
    df_filtrado = df_mov[df_mov['Año'] == anho_sel]
    if mes_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Mes_Año'] == mes_sel]

    # --- CÁLCULOS ---
    ingresos = df_filtrado[df_filtrado['Categoria'] == 'Ingreso']['Importe'].sum()
    gastos_fijos = df_filtrado[df_filtrado['Tipo'] == 'Fijo']['Importe'].sum()
    gastos_var = df_filtrado[df_filtrado['Tipo'] == 'Variable']['Importe'].sum()
    balance = ingresos - gastos_fijos - gastos_var

    # --- BLOQUE 1: RESUMEN TEMPORAL ---
    st.title(f"📊 Análisis de {mes_sel if mes_sel != 'Todos' else anho_sel}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos", f"{ingresos:,.2f} €")
    c2.metric("Gastos Fijos", f"{gastos_fijos:,.2f} €")
    c3.metric("Gastos Variables", f"{gastos_var:,.2f} €")
    c4.metric("Balance Neto", f"{balance:,.2f} €", delta=f"{balance/ingresos*100:.1f}%" if ingresos > 0 else None)

    # --- BLOQUE 2: EVOLUCIÓN HISTÓRICA ---
    st.divider()
    st.subheader("📈 Evolución del Patrimonio Neto")
    
    # Calculamos el acumulado mes a mes de (Ingresos - Gastos)
    evolucion_mensual = df_mov.groupby('Mes_Año').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Ahorro_Mes')
    evolucion_mensual['Patrimonio_Acumulado'] = evolucion_mensual['Ahorro_Mes'].cumsum() + valor_cartera_hoy - (df_mov[df_mov['Categoria'] == 'Inversion']['Importe'].sum())
    
    fig_evol = px.line(evolucion_mensual, x='Mes_Año', y='Patrimonio_Acumulado', 
                        title="Crecimiento de tu Patrimonio", markers=True,
                        line_shape="spline", color_discrete_sequence=['#28A745'])
    st.plotly_chart(fig_evol, use_container_width=True)

    # --- BLOQUE 3: DESGLOSE DE GASTOS E INGRESOS ---
    st.subheader("🔍 Detalle de Conceptos")
    col_izq, col_der = st.columns(2)

    with col_izq:
        fig_ing = px.pie(df_filtrado[df_filtrado['Categoria'] == 'Ingreso'], values='Importe', names='Concepto', 
                         title="🔵 Origen de Ingresos", hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_ing, use_container_width=True)

    with col_der:
        fig_gas = px.pie(df_filtrado[df_filtrado['Categoria'] == 'Gasto'], values='Importe', names='Concepto', 
                         title="🔴 Destino de Gastos", hole=0.5, color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig_gas, use_container_width=True)

    # --- BLOQUE 4: ESTADO DE INVERSIONES (SIEMPRE VISIBLE) ---
    st.divider()
    st.subheader("🏛️ Estado Actual de Inversiones")
    st.table(df_inv[['Ticket', 'Precio_Compra', 'Valor_Actual', 'Categoria']])

except Exception as e:
    st.error(f"Error técnico: {e}")
