import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo
st.set_page_config(page_title="Gestión Patrimonial Pro", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #007BFF; }</style>", unsafe_allow_html=True)

# 2. Enlace de datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    # Limpieza y preparación de fechas
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df['Importe'] = df['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce').fillna(0)
    
    # Convertimos la fecha a formato real para poder agrupar por mes/año
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
    df['Año'] = df['Fecha'].dt.year
    df['Mes'] = df['Fecha'].dt.strftime('%Y-%m')

    st.title("🏛️ Mi Patrimonio y Evolución")
    
    # --- FILTRO TEMPORAL ---
    años_disponibles = sorted(df['Año'].unique().tolist(), reverse=True)
    seleccion_año = st.sidebar.selectbox("Selecciona el Año", años_disponibles)
    df_filtrado = df[df['Año'] == seleccion_año]

    # --- CÁLCULOS ---
    ingresos = df_filtrado[df_filtrado['Categoria'] == 'Ingreso']['Importe'].sum()
    fijos = df_filtrado[df_filtrado['Tipo'] == 'Fijo']['Importe'].sum()
    variables = df_filtrado[df_filtrado['Tipo'] == 'Variable']['Importe'].sum()
    inversiones = df_filtrado[df_filtrado['Categoria'] == 'Inversion']['Importe'].sum()
    ahorro_puro = ingresos - fijos - variables - inversiones

    # --- MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Ingresos {seleccion_año}", f"{ingresos:,.2f} €")
    c2.metric("Gastos Fijos", f"{fijos:,.2f} €")
    c3.metric("Gastos Variables", f"{variables:,.2f} €")
    c4.metric("Patrimonio Neto", f"{df['Importe'][df['Categoria']=='Ingreso'].sum() - df['Importe'][df['Categoria']!='Ingreso'].sum():,.2f} €")

    st.divider()

    # --- BLOQUE 1: EVOLUCIÓN TEMPORAL ---
    st.subheader("📈 Evolución de mi Patrimonio")
    # Agrupamos por mes para ver la tendencia
    evolucion = df.groupby(['Mes', 'Categoria'])['Importe'].sum().unstack().fillna(0)
    if 'Ingreso' in evolucion:
        fig_linea = px.line(evolucion, y='Ingreso', title="Tendencia Mensual de Ingresos", line_shape="spline", render_mode="svg")
        fig_linea.update_traces(line_color='#007BFF')
        st.plotly_chart(fig_linea, use_container_width=True)

    # --- BLOQUE 2: PORCENTAJES DE GASTO Y AHORRO ---
    st.subheader("🎯 Análisis de Regla de Ahorro")
    col_a, col_b = st.columns(2)

    with col_a:
        # Gráfico circular de porcentajes reales sobre el ingreso
        datos_queso = pd.DataFrame({
            'Concepto': ['Fijos', 'Variables', 'Inversión/Ahorro'],
            'Valor': [fijos, variables, (inversiones + ahorro_puro)]
        })
        fig_reparto = px.pie(datos_queso, values='Valor', names='Concepto', hole=0.5,
                             color_discrete_map={'Fijos': '#DC3545', 'Variables': '#FFC107', 'Inversión/Ahorro': '#28A745'},
                             title="% del Ingreso destinado a:")
        st.plotly_chart(fig_reparto, use_container_width=True)

    with col_b:
        # Desglose detallado de los gastos actuales
        df_gastos_solo = df_filtrado[df_filtrado['Categoria'] == 'Gasto']
        fig_barras = px.bar(df_gastos_solo, x='Concepto', y='Importe', color='Tipo',
                            title="Detalle de Gastos por Concepto",
                            color_discrete_map={'Fijo': '#DC3545', 'Variable': '#007BFF'})
        st.plotly_chart(fig_barras, use_container_width=True)

except Exception as e:
    st.error(f"Error en el análisis: {e}")
