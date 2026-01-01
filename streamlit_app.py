import streamlit as st
import pandas as pd
import plotly.express as px

# Forzar que la app se vea limpia
st.set_page_config(page_title="Mi Libertad Financiera", layout="wide")

# Estilo para asegurar que el texto sea visible (Negro)
st.markdown("""
    <style>
    h1, h2, h3, p, span, .stMetric label { color: #1a1a1a !important; font-weight: bold !important; }
    .stMetric { background-color: #ffffff !important; border: 2px solid #00d1b2 !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Mi Panel de Libertad Financiera")

# --- BLOQUE 1: TUS DATOS REALES (Cámbialos aquí abajo) ---
# Aquí es donde tú mismo puedes actualizar tus números cada mes
ingresos_trabajo = 2500
ingresos_pasivos = 350 # Dividendos, alquileres...
gastos_fijos = 1200
gastos_disfrute = 400
ahorro_mes = 1250

patrimonio_total = 55000 
objetivo_libertad = 100000

# --- CÁLCULOS AUTOMÁTICOS ---
libertad_por_ahorro = (patrimonio_total / (gastos_fijos + gastos_disfrute)) if (gastos_fijos + gastos_disfrute) > 0 else 0
porcentaje_pasivos = (ingresos_pasivos / gastos_fijos) * 100 if gastos_fijos > 0 else 0

# --- INTERFAZ VISUAL ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Patrimonio Neto", f"{patrimonio_total} €")
with col2:
    st.metric("Meses de Libertad (Ahorro)", f"{libertad_por_ahorro:.1f} meses")
with col3:
    st.metric("% Libertad (Vía Pasivos)", f"{porcentaje_pasivos:.1f}%")

st.divider()

# --- GRÁFICOS ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Distribución de Patrimonio")
    df_patrimonio = pd.DataFrame({
        "Activo": ["Vivienda", "Fondos Indexados", "Efectivo", "Cripto/Otros"],
        "Valor": [30000, 15000, 7000, 3000]
    })
    fig1 = px.pie(df_patrimonio, values='Valor', names='Activo', hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Felicidad vs Obligación")
    df_gastos = pd.DataFrame({
        "Tipo": ["Obligación (Fijos)", "Felicidad (Variables)"],
        "Euros": [gastos_fijos, gastos_disfrute]
    })
    fig2 = px.bar(df_gastos, x='Tipo', y='Euros', color='Tipo', color_discrete_map={"Obligación (Fijos)": "#ff4b4b", "Felicidad (Variables)": "#00d1b2"})
    st.plotly_chart(fig2, use_container_width=True)
