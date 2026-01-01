import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de estilo
st.set_page_config(page_title="Mi Salud Financiera Integral", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Enlaces a las pestañas (Asegúrate de que los GID coincidan con tus pestañas)
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"

try:
    # CARGA DE DATOS
    df_mov = pd.read_csv(URL_MOVIMIENTOS)
    df_inv = pd.read_csv(URL_INVERSIONES)
    
    # Limpieza de nombres de columnas
    df_mov.columns = df_mov.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    df_inv.columns = df_inv.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

    # LIMPIEZA DE NÚMEROS (Pestaña Movimientos)
    df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)

    # LIMPIEZA DE NÚMEROS (Pestaña Inversiones)
    for col in ['Precio_Compra', 'Valor_Actual']:
        df_inv[col] = df_inv[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)

    # --- CÁLCULOS DE CARTERA ---
    # En tus fondos (Indexa/Groupama), la cantidad suele ser 1 si pones el total directamente
    # Si pones participaciones, cámbialo aquí
    df_inv['Ganancia'] = df_inv['Valor_Actual'] - df_inv['Precio_Compra']
    df_inv['Rentabilidad_Pct'] = (df_inv['Ganancia'] / df_inv['Precio_Compra']) * 100
    
    total_invertido = df_inv['Precio_Compra'].sum()
    valor_total_hoy = df_inv['Valor_Actual'].sum()
    ganancia_total = valor_total_hoy - total_invertido

    # --- PANEL DE CONTROL ---
    st.title("🏛️ Mi Patrimonio Global")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Patrimonio en Inversiones", f"{valor_total_hoy:,.2f} €", f"{ganancia_total:,.2f} €")
    m2.metric("Capital Invertido", f"{total_invertido:,.2f} €")
    m3.metric("Rentabilidad Media", f"{(ganancia_total/total_invertido*100) if total_invertido !=0 else 0:.2f} %")

    st.divider()

    # --- ANÁLISIS VISUAL DE INVERSIONES ---
    col_inv1, col_inv2 = st.columns(2)
    
    with col_inv1:
        st.subheader("🟢 Distribución por Activo")
        fig_inv_pie = px.pie(df_inv, values='Valor_Actual', names='Ticket', hole=0.5,
                             color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_inv_pie, use_container_width=True)

    with col_inv2:
        st.subheader("📈 Ganancia Realizada por Fondo")
        fig_inv_bar = px.bar(df_inv, x='Ticket', y='Ganancia', color='Ganancia',
                             color_continuous_scale=['#DC3545', '#28A745'],
                             title="Evolución en Euros")
        st.plotly_chart(fig_inv_bar, use_container_width=True)

    # --- ANÁLISIS DE GASTOS (Lo que ya tenías) ---
    st.divider()
    st.subheader("💸 Flujo de Caja (Gastos e Ingresos)")
    
    df_ingresos = df_mov[df_mov['Categoria'] == 'Ingreso']
    df_gastos = df_mov[df_mov['Categoria'] == 'Gasto']
    
    c1, c2 = st.columns(2)
    with c1:
        fig_ing = px.pie(df_ingresos, values='Importe', names='Concepto', hole=0.5, title="🔵 Ingresos",
                         color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_ing, use_container_width=True)
    with c2:
        fig_gas = px.pie(df_gastos, values='Importe', names='Concepto', hole=0.5, title="🔴 Gastos",
                         color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig_gas, use_container_width=True)

except Exception as e:
    st.error(f"Revisa el formato de tu Excel: {e}")
