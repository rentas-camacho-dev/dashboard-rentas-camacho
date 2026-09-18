import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración general de la página
st.set_page_config(
    page_title="FinQuery - Rentas Cortas Camacho",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Portafolio de Inversión Familiar - Camacho")
st.markdown("Dashboard en vivo conectado a Google Cloud BigQuery (`rentascamacho.rentas_cortas`)")

# 2. Conexión nativa a BigQuery
conn = st.connection("bigquery", type="bigquery")

# 3. Cargar datos principales desde la vista maestra
@st.cache_data(ttl=600)
def load_main_data():
    query = """
        SELECT 
            ID_Movimiento,
            Fecha,
            Nombre_Propiedad,
            Nombre_Socio,
            Valor_Repartido,
            Ingreso,
            Gasto,
            Nombre_Categoria,
            Nombre_Subcategoria,
            Nombre_Cuenta
        FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    """
    df = conn.query(query)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

df_base = load_main_data()

# 4. Barra Lateral - Filtros Dinámicos
st.sidebar.header("🔍 Filtros Globales")

socios_disponibles = ["Todos"] + list(df_base['Nombre_Socio'].dropna().unique())
socio_seleccionado = st.sidebar.selectbox("Seleccionar Socio", socios_disponibles)

propiedades_disponibles = ["Todas"] + list(df_base['Nombre_Propiedad'].dropna().unique())
propiedad_seleccionada = st.sidebar.selectbox("Seleccionar Propiedad", propiedades_disponibles)

df_filtered = df_base.copy()
if socio_seleccionado != "Todos":
    df_filtered = df_filtered[df_filtered['Nombre_Socio'] == socio_seleccionado]
if propiedad_seleccionada != "Todas":
    df_filtered = df_filtered[df_filtered['Nombre_Propiedad'] == propiedad_seleccionada]

# 5. Cálculo de KPIs Principales
total_ingresos = df_filtered['Ingreso'].sum()
total_gastos = df_filtered['Gasto'].sum()
utilidad_neta = total_ingresos - total_gastos

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Ingresos", f"${total_ingresos:,.0f}")
col2.metric("📉 Total Gastos", f"${total_gastos:,.0f}")
col3.metric("📈 Utilidad Neta", f"${utilidad_neta:,.0f}", delta=f"{(utilidad_neta/total_ingresos*100) if total_ingresos > 0 else 0:.1f}%")

st.divider()

# 6. Gráficos Interactivos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Ingresos Mensuales")
    if not df_filtered.empty:
        df_filtered['Mes'] = df_filtered['Fecha'].dt.to_period('M').astype(str)
        df_mensual = df_filtered.groupby('Mes')[['Ingreso']].sum().reset_index()
        fig_bar = px.bar(df_mensual, x='Mes', y='Ingreso', text_auto='.2s', color_discrete_sequence=['#0E86D4'])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No hay datos con los filtros seleccionados.")

with col_graf2:
    st.subheader("🍩 Gastos por Categoría")
    if not df_filtered.empty:
        df_gastos = df_filtered.groupby('Nombre_Categoria')[['Gasto']].sum().reset_index()
        df_gastos = df_gastos[df_gastos['Gasto'] > 0]
        fig_pie = px.pie(df_gastos, names='Nombre_Categoria', values='Gasto', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No hay datos de gastos.")

st.divider()

# 7. Tabla Detallada
st.subheader("📋 Últimos Movimientos Detallados")
st.dataframe(
    df_filtered[['Fecha', 'Nombre_Propiedad', 'Nombre_Socio', 'Ingreso', 'Gasto', 'Nombre_Categoria', 'Nombre_Cuenta']]
    .sort_values(by='Fecha', ascending=False)
    .head(10),
    use_container_width=True
)
