import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración General
st.set_page_config(page_title="Patrimonio y Felicidad Financiera", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Conexión a datos
URL_MOVIMIENTOS = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=0"
URL_INVERSIONES = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid=863168602"

try:
    df_mov = pd.read_csv(URL_MOVIMIENTOS)
    df_inv = pd.read_csv(URL_INVERSIONES)
    for df in [df_mov, df_inv]:
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')

    # Limpieza numérica
    df_mov['Importe'] = df_mov['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df_mov['Importe'] = pd.to_numeric(df_mov['Importe'], errors='coerce').fillna(0)
    df_mov['Felicidad'] = pd.to_numeric(df_mov['Felicidad'], errors='coerce').fillna(0)
    df_mov['Fecha'] = pd.to_datetime(df_mov['Fecha'], dayfirst=True)
    df_mov['Año'] = df_mov['Fecha'].dt.year
    df_mov['Mes_Año'] = df_mov['Fecha'].dt.strftime('%Y-%m')

    # --- SECCIÓN 1: PATRIMONIO ACTUAL ---
    st.title("🏛️ Mi Patrimonio Global")
    valor_actual_inv = pd.to_numeric(df_inv['Valor_Actual'].astype(str).str.replace(',', '.'), errors='coerce').sum()
    st.metric("Valor Cartera Hoy", f"{valor_actual_inv:,.2f} €")
    
    # (Mantenemos los gráficos de inversiones que ya tenías...)
    st.divider()

    # --- SECCIÓN 2: FILTROS TEMPORALES ---
    st.sidebar.header("🔎 Explorador")
    anho_sel = st.sidebar.selectbox("Año", sorted(df_mov['Año'].unique(), reverse=True))
    df_f = df_mov[df_mov['Año'] == anho_sel]

    # --- SECCIÓN 3: FELICIDAD FINANCIERA (EL NUEVO MÓDULO) ---
    st.header("😊 Felicidad Financiera")
    st.write("Analizamos si tus gastos están alineados con lo que te hace feliz.")

    # Filtramos solo gastos para este análisis
    df_gastos_fel = df_f[df_f['Categoria'] == 'Gasto']

    if not df_gastos_fel.empty:
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            # Gráfico de Dispersión: Importe vs Felicidad
            fig_happy = px.scatter(df_gastos_fel, x="Importe", y="Felicidad", 
                                   size="Importe", color="Concepto",
                                   hover_name="Concepto", title="¿Vale lo que cuesta?",
                                   labels={"Felicidad": "Nivel de Felicidad (1-5)", "Importe": "Gasto (€)"})
            st.plotly_chart(fig_happy, use_container_width=True)
            st.info("💡 Los puntos arriba a la izquierda son tus 'Joyas': cuestan poco y te hacen muy feliz.")

        with col_f2:
            # Promedio de felicidad por Concepto
            fel_media = df_gastos_fel.groupby('Concepto')['Felicidad'].mean().sort_values(ascending=False).reset_index()
            fig_bar_fel = px.bar(fel_media, x='Felicidad', y='Concepto', orientation='h',
                                 title="Ranking de Felicidad por Gasto",
                                 color='Felicidad', color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar_fel, use_container_width=True)

        # MÉTRICA DE EFICIENCIA EMOCIONAL
        # Calculamos cuánto pagas por cada punto de felicidad
        df_gastos_fel['Coste_por_Punto'] = df_gastos_fel['Importe'] / df_gastos_fel['Felicidad'].replace(0, 1)
        eficiencia = df_gastos_fel.groupby('Concepto')['Coste_por_Punto'].mean().sort_values().head(5)
        
        st.subheader("🚀 Top 5 Gastos más eficientes (Más felicidad por menos dinero)")
        st.write("Estos son los gastos que deberías proteger o potenciar:")
        cols = st.columns(5)
        for i, (concepto, coste) in enumerate(eficiencia.items()):
            cols[i].metric(concepto, f"{coste:.2f} €/pt")

    else:
        st.warning("Añade valores del 1 al 5 en la columna 'Felicidad' de tu Excel para ver este análisis.")

    # (Aquí seguirían tus gráficos de ingresos y gastos de antes...)

except Exception as e:
    st.error(f"Error en el módulo de felicidad: {e}")
