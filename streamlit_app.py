import streamlit as st
import pandas as pd
import plotly.express as px

# 1. FORZAR COLORES LEGIBLES
st.set_page_config(page_title="Mi Libertad", layout="wide")

st.markdown("""
    <style>
    /* Forzamos que todo el texto sea negro carbón para que se vea bien */
    .stApp { background-color: white; }
    h1, h2, h3, p, span, label, .stMetric { color: #000000 !important; }
    div[data-testid="stMetricValue"] { color: #000000 !important; font-weight: bold; }
    .stMetric { border: 2px solid #00d1b2; padding: 15px; border-radius: 10px; background-color: #f0fdfa; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Mi Panel de Control")

# 2. PANEL LATERAL PARA METER TUS DATOS
st.sidebar.header("📝 Actualiza tus Cifras")
patrimonio = st.sidebar.number_input("Tu Patrimonio Total (€)", value=55000)
gastos_mes = st.sidebar.number_input("Tus Gastos Mensuales (€)", value=1500)
pasivos_mes = st.sidebar.number_input("Ingresos Pasivos (€)", value=300)

# 3. CÁLCULOS
meses_libertad = patrimonio / gastos_mes if gastos_mes > 0 else 0
porcentaje_libertad = (pasivos_mes / gastos_mes) * 100 if gastos_mes > 0 else 0

# 4. MOSTRAR RESULTADOS
col1, col2 = st.columns(2)
with col1:
    st.metric("Meses de ahorro", f"{meses_libertad:.1f} meses")
with col2:
    st.metric("Libertad Financiera", f"{porcentaje_libertad:.1f}%")

st.divider()

# 5. GRÁFICO DE DISTRIBUCIÓN (Configurable)
st.subheader("¿En qué tienes invertido tu dinero?")
# Aquí simulamos unos datos, pero pronto los leeremos de tu lista
datos = pd.DataFrame({
    "Activo": ["Vivienda", "Fondos", "Efectivo"],
    "Valor": [patrimonio*0.6, patrimonio*0.3, patrimonio*0.1]
})
fig = px.pie(datos, values='Valor', names='Activo', hole=0.5, color_discrete_sequence=["#00d1b2", "#1f2937", "#94a3b8"])
st.plotly_chart(fig, use_container_width=True)
