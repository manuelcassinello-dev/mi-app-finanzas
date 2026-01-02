import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la Página
st.set_page_config(page_title="Control Financiero Pro", layout="wide")
st.markdown("<style>.stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #28A745; }</style>", unsafe_allow_html=True)

# 2. Configuración de URLs (Google Sheets)
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "Personal": {"mov": "0", "inv": "863168602"},
    "Familiar": {"mov": "23613697", "inv": "863168602"} # He puesto tus inversiones en ambos, cámbialo si tienes una hoja de inv. familiar
}

# 3. Función Maestra de Procesamiento de Datos
def get_data(gid_mov, gid_inv):
    # Carga
    df_m = pd.read_csv(URL_BASE + gid_mov)
    df_i = pd.read_csv(URL_BASE + gid_inv)
    
    # Limpieza básica de columnas
    for df in [df_m, df_i]:
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
    
    # Procesar Movimientos
    df_m['Importe'] = pd.to_numeric(df_m['Importe'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    df_m['Felicidad'] = pd.to_numeric(df_m['Felicidad'], errors='coerce').fillna(0)
    df_m['Fecha'] = pd.to_datetime(df_m['Fecha'], dayfirst=True)
    df_m['Año'] = df_m['Fecha'].dt.year
    df_m['Mes_Año'] = df_m['Fecha'].dt.strftime('%Y-%m')
    
    # Procesar Inversiones
    for col in ['Precio_Compra', 'Valor_Actual']:
        df_i[col] = pd.to_numeric(df_i[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    
    return df_m, df_i

# 4. Función para dibujar la Interfaz de cada pestaña
def draw_dashboard(df_mov, df_inv, titulo):
    st.title(f"🏛️ {titulo}")
    
    # KPIs Inversiones
    val_act = df_inv['Valor_Actual'].sum()
    inv_ini = df_inv['Precio_Compra'].sum()
    rent = ((val_act - inv_ini) / inv_ini * 100) if inv_ini != 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Valor Cartera", f"{val_act:,.2f} €", f"{val_act-inv_ini:,.2f} €")
    c2.metric("Inversión Inicial", f"{inv_ini:,.2f} €")
    c3.metric("Rentabilidad", f"{rent:.2f} %")

    # Gráficos Inversión
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Distribución")
        st.plotly_chart(px.pie(df_inv, values='Valor_Actual', names='Ticket', hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r), use_container_width=True)
    with col2:
        st.subheader("📈 Ganancia")
        df_inv['Ganancia'] = df_inv['Valor_Actual'] - df_inv['Precio_Compra']
        st.plotly_chart(px.bar(df_inv, x='Ticket', y='Ganancia', color='Ganancia', color_continuous_scale='Greens'), use_container_width=True)

    st.divider()

    # Evolución
    st.subheader("📊 Evolución Patrimonio")
    evol = df_mov.groupby('Mes_Año').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Neto')
    evol['Acumulado'] = evol['Neto'].cumsum() + (val_act - df_mov[df_mov['Categoria'] == 'Inversion']['Importe'].sum())
    st.plotly_chart(px.line(evol, x='Mes_Año', y='Acumulado', markers=True, color_discrete_sequence=['#28A745']), use_container_width=True)

    st.divider()

    # Filtros Temporales en Barra Lateral
    anho = st.sidebar.selectbox(f"Año ({titulo})", sorted(df_mov['Año'].unique(), reverse=True), key=f"anho_{titulo}")
    df_f = df_mov[df_mov['Año'] == anho]

    # Felicidad
    st.header("😊 Felicidad Financiera")
    df_gas = df_f[df_f['Categoria'] == 'Gasto']
    if not df_gas.empty:
        f1, f2 = st.columns([2,1])
        with f1:
            st.plotly_chart(px.scatter(df_gas, x="Importe", y="Felicidad", size="Importe", color="Concepto", hover_name="Concepto", title="¿Vale lo que cuesta?"), use_container_width=True)
        with f2:
            df_gas['Ef'] = df_gas['Importe'] / df_gas['Felicidad'].replace(0, 1)
            st.write("**Top Inteligentes**")
            for c, v in df_gas.groupby('Concepto')['Ef'].mean().sort_values().head(3).items():
                st.write(f"✅ {c}: {v:.2f}€/pt")

    # Donuts de Flujo
    st.subheader("💸 Ingresos vs Gastos")
    i1, i2 = st.columns(2)
    with i1:
        st.plotly_chart(px.pie(df_f[df_f['Categoria'] == 'Ingreso'], values='Importe', names='Concepto', hole=0.5, title="Ingresos", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
    with i2:
        st.plotly_chart(px.pie(df_f[df_f['Categoria'] == 'Gasto'], values='Importe', names='Concepto', hole=0.5, title="Gastos", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)

# --- EJECUCIÓN APP ---
tab_pers, tab_fam = st.tabs(["👤 Finanzas Personales", "🏠 Finanzas Familiares"])

with tab_pers:
    df_m_p, df_i_p = get_data(GIDS["Personal"]["mov"], GIDS["Personal"]["inv"])
    draw_dashboard(df_m_p, df_i_p, "Mi Patrimonio Personal")

with tab_fam:
    try:
        df_m_f, df_i_f = get_data(GIDS["Familiar"]["mov"], GIDS["Familiar"]["inv"])
        draw_dashboard(df_m_f, df_i_f, "Cuentas Familiares")
    except:
        st.warning("Asegúrate de que la nueva pestaña del Excel tenga las mismas columnas (Fecha, Concepto, Importe, Categoria, Felicidad).")
