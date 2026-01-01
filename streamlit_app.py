import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo
st.set_page_config(page_title="Mi Panel Financiero", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #00d1b2; }</style>", unsafe_allow_html=True)

# 2. Enlace de datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv"

try:
    df = pd.read_csv(URL_MOVIMIENTOS)
    
    # Limpieza profesional de datos
    df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df['Importe'] = df['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce').fillna(0)

    st.title("📊 Análisis de Ingresos, Gastos e Inversiones")
    st.divider()

    # --- CÁLCULOS ---
    total_ingresos = df[df['Categoria'] == 'Ingreso']['Importe'].sum()
    total_inversiones = df[df['Categoria'] == 'Inversion']['Importe'].sum()
    # Gastos es todo lo que no sea Ingreso ni Inversion
    df_solo_gastos = df[(df['Categoria'] != 'Ingreso') & (df['Categoria'] != 'Inversion')]
    total_gastos = df_solo_gastos['Importe'].sum()
    disponible = total_ingresos - total_gastos - total_inversiones

    # --- BLOQUE 1: MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos Totales", f"{total_ingresos:,.2f} €")
    c2.metric("Gastos Totales", f"{total_gastos:,.2f} €")
    c3.metric("Inversiones", f"{total_inversiones:,.2f} €")
    c4.metric("Disponible Real", f"{disponible:,.2f} €")

    # --- BLOQUE 2: ANÁLISIS VISUAL DETALLADO ---
    st.subheader("¿En qué se va el dinero realmente?")
    col_izq, col_der = st.columns(2)

    with col_izq:
        # GRÁFICO 1: El gran reparto (Ingreso vs Gasto vs Inversión)
        resumen = pd.DataFrame({
            'Tipo': ['Gastos', 'Inversiones', 'Disponible'],
            'Valor': [total_gastos, total_inversiones, max(0, disponible)]
        })
        fig_reparto = px.pie(resumen, values='Valor', names='Tipo', hole=0.6,
                             title="Distribución del Ingreso",
                             color_discrete_map={'Gastos': '#FF6384', 'Inversiones': '#36A2EB', 'Disponible': '#4BC0C0'})
        st.plotly_chart(fig_reparto, use_container_width=True)

    with col_der:
        # GRÁFICO 2: ¡Aquí está el detalle! (Usa el CONCEPTO para las categorías)
        # Mostramos los gastos desglosados por lo que escribes en la columna Concepto
        fig_detalle = px.bar(df_solo_gastos, x='Concepto', y='Importe', color='Tipo',
                             title="Desglose de Gastos por Concepto",
                             color_discrete_map={'Fijo': '#1e293b', 'Variable': '#00d1b2'})
        st.plotly_chart(fig_detalle, use_container_width=True)

    # --- BLOQUE 3: MAPA TOTAL ---
    st.subheader("Mapa Jerárquico de Movimientos")
    # Este gráfico permite ver Categoria -> Concepto de un vistazo
    fig_sun = px.sunburst(df, path=['Categoria', 'Concepto'], values='Importe',
                          color='Categoria', 
                          color_discrete_map={'Ingreso': '#4BC0C0', 'Inversion': '#36A2EB', 'Gasto': '#FF6384'})
    st.plotly_chart(fig_sun, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
