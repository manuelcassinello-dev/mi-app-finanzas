import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Mi App de Libertad Financiera", layout="wide")

# Estilos CSS para que se parezca a Fintonic
st.markdown("""
    <style>
    .stApp { background-color: #f8fafd; }
    div.stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e6ed; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Mi Dashboard de Felicidad y Libertad")

# --- SIMULACIÓN DE DATOS (Para que veas cómo queda) ---
# En el futuro, estos datos vendrán de tu Excel o base de datos
datos_demo = pd.DataFrame([
    {"Concepto": "Alquiler", "Importe": 800, "Regla": "50% (Fijos)", "Sentimiento": "Obligación"},
    {"Concepto": "Suscripción Gym", "Importe": 50, "Regla": "30% (Variable)", "Sentimiento": "Felicidad"},
    {"Concepto": "Cena Amigos", "Importe": 60, "Regla": "30% (Variable)", "Sentimiento": "Felicidad"},
    {"Concepto": "Luz y Agua", "Importe": 120, "Regla": "50% (Fijos)", "Sentimiento": "Obligación"},
    {"Concepto": "Ahorro Indexados", "Importe": 400, "Regla": "20% (Ahorro)", "Sentimiento": "Felicidad"},
    {"Concepto": "Seguro Coche", "Importe": 40, "Regla": "50% (Fijos)", "Sentimiento": "Obligación"},
])

# --- MÉTRICAS SUPERIORES ---
col1, col2, col3 = st.columns(3)
total_gastos = datos_demo[datos_demo["Regla"] != "20% (Ahorro)"]["Importe"].sum()
felicidad_neta = datos_demo[datos_demo["Sentimiento"] == "Felicidad"]["Importe"].sum()

with col1:
    st.metric("Gasto Total", f"{total_gastos} €")
with col2:
    st.metric("Inversión en Felicidad", f"{felicidad_neta} €", "¡Sigue así!")
with col3:
    st.metric("Ratio de Ahorro", "22%", "Objetivo 20%")

st.divider()

# --- FILAS DE GRÁFICOS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Regla 50 / 20 / 30")
    # Calculamos cuánto hay en cada categoría de la regla
    fig_regla = px.pie(datos_demo, values='Importe', names='Regla', 
                       color_discrete_sequence=["#2ECC71", "#3498DB", "#E74C3C"],
                       hole=0.6)
    st.plotly_chart(fig_regla, use_container_width=True)

with c2:
    st.subheader("Gastos: ¿Obligación o Disfrute?")
    # Gráfico para ver el sentimiento del gasto
    fig_sentimiento = px.bar(datos_demo, x='Sentimiento', y='Importe', color='Sentimiento',
                             color_discrete_map={"Felicidad": "#00D1B2", "Obligación": "#FF3860"})
    st.plotly_chart(fig_sentimiento, use_container_width=True)

# --- FORMULARIO PARA AÑADIR DATOS ---
st.sidebar.header("📝 Registrar Nuevo Gasto")
with st.sidebar:
    nuevo_concepto = st.text_input("Concepto (Ej: Supermercado)")
    nuevo_importe = st.number_input("Importe (€)", min_value=0.0)
    nueva_regla = st.selectbox("Categoría Regla", ["50% (Fijos)", "30% (Variable)", "20% (Ahorro)"])
    nuevo_sentimiento = st.radio("¿Cómo te hace sentir?", ["Obligación", "Felicidad"])
    
    if st.button("Guardar Movimiento"):
        st.success(f"Registrado: {nuevo_concepto} por {nuevo_importe}€")
        st.info("Nota: En el siguiente paso haremos que esto se guarde de verdad.")
