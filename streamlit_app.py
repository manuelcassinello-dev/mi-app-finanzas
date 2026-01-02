import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuracion base
st.set_page_config(page_title="Control Financiero Pro", layout="wide")

# URLs de Google Sheets
URL_BASE = "https://docs.google.com/spreadsheets/d/1LRG_a5JYm78tAYVR2qhiZNqNLXGe9WRTLKMnpk8jdOg/export?format=csv&gid="
GIDS = {
    "p_mov": "0",
    "p_inv": "863168602",
    "f_mov": "23613697"
}

# 2. Funcion de carga limpia
def cargar_limpio(gid):
    try:
        df = pd.read_csv(URL_BASE + gid)
        df.columns = df.columns.str.strip().str.replace('í', 'i').str.replace('ó', 'o')
        # Limpieza de numeros para evitar ValueErrors
        for c in ['Importe', 'Precio_Compra', 'Valor_Actual', 'Felicidad']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
        # Gestion de fechas
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
            df['Anio'] = df['Fecha'].dt.year
            df['Mes_Anio'] = df['Fecha'].dt.strftime('%Y-%m')
        return df
    except:
        return pd.DataFrame()

# --- INTERFAZ DE PESTAÑAS ---
t_pers, t_fam = st.tabs(["Mis Finanzas", "Finanzas Familiares"])

with t_pers:
    st.title("Mi Patrimonio Personal")
    df_m = cargar_limpio(GIDS["p_mov"])
    df_i = cargar_limpio(GIDS["p_inv"])

    # KPIs Inversion
    if not df_i.empty:
        v_act = df_i['Valor_Actual'].sum()
        v_ini = df_i['Precio_Compra'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Valor Cartera", f"{v_act:,.2f} EUR", f"{v_act-v_ini:,.2f} EUR")
        c2.metric("Inversion Inicial", f"{v_ini:,.2f} EUR")
        c3.metric("Rentabilidad", f"{((v_act-v_ini)/v_ini*100):.2f} %" if v_ini != 0 else "0%")

    # Evolucion Patrimonial (LA LINEA)
    if not df_m.empty:
        st.subheader("Evolucion del Patrimonio")
        v_total = df_i['Valor_Actual'].sum() if not df_i.empty else 0
        evol = df_m.groupby('Mes_Anio').apply(lambda x: x[x['Categoria'] == 'Ingreso']['Importe'].sum() - x[x['Categoria'] == 'Gasto']['Importe'].sum()).reset_index(name='Neto')
        evol['Acumulado'] = evol['Neto'].cumsum() + (v_total - df_m[df_m['Categoria'] == 'Inversion']['Importe'].sum())
        st.plotly_chart(px.line(evol, x='Mes_Anio', y='Acumulado', markers=True, color_discrete_sequence=['#28A745']), use_container_width=True)

    # Filtro Año y Felicidad
    st.divider()
    lista_anios = sorted(df_m['Anio'].unique(), reverse=True) if not df_m.empty else [2026]
    anio_p = st.sidebar.selectbox("Año (Personal)", lista_anios, key="sel_p")
    df_p_f = df_m[df_m['Anio'] == anio_p] if not df_m.empty else pd.DataFrame()

    if not df_p_f.empty:
        st.subheader("Felicidad Financiera")
        df_gas_p = df_p_f[df_p_f['Categoria'] == 'Gasto']
        if not df_gas_p.empty:
            f1, f2 = st.columns([2,1])
            with f1:
                st.plotly_chart(px.scatter(df_gas_p, x="Importe", y="Felicidad", size="Importe", color="Concepto", hover_name="Concepto"), use_container_width=True)
            with f2:
                df_gas_p['Ef'] = df_gas_p['Importe'] / df_gas_p['Felicidad'].replace(0, 1)
                st.write("**Eficiencia (Menos EUR/pt mejor)**")
                for c, v in df_gas_p.groupby('Concepto')['Ef'].mean().sort_values().head(3).items():
                    st.write(f"- {c}: {v:.2f} EUR/pt")

    # Donuts Personales
    st.subheader("Ingresos y Gastos Personales")
    d1, d2 = st.columns(2)
    with d1:
        st.plotly_chart(px.pie(df_p_f[df_p_f['Categoria']=='Ingreso'], values='Importe', names='Concepto', hole=0.5, title="Ingresos", color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
    with d2:
        st.plotly_chart(px.pie(df_p_f[df_p_f['Categoria']=='Gasto'], values='Importe', names='Concepto', hole=0.5, title="Gastos", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)

with t_fam:
    st.title("Cuentas Familiares")
    df_f = cargar_limpio(GIDS["f_mov"])
    
    if not df_f.empty:
        anio_f = st.sidebar.selectbox("Año (Familiar)", sorted(df_f['Anio'].unique(), reverse=True), key="sel_f")
        df_f_f = df_f[df_f['Anio'] == anio_f]

        # KPIs Familia
        inf = df_f_f[df_f_f['
