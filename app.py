import streamlit as st
import pandas as pd
import plotly.express as px

from google.oauth2 import service_account
from google.cloud import bigquery


# ============================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="FinQuery - Rentas Cortas Camacho",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Portafolio de Inversión Familiar - Camacho")

st.markdown(
    "Dashboard en vivo conectado a Google Cloud BigQuery "
    "(`rentascamacho.rentas_cortas`)"
)


# ============================================================
# 2. CONEXIÓN A BIGQUERY
# ============================================================

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

conn = bigquery.Client(
    credentials=credentials,
    project="rentascamacho"
)


# ============================================================
# 3. CARGAR DATOS DESDE BIGQUERY
# ============================================================

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

    df = conn.query(query).to_dataframe()

    df["Fecha"] = pd.to_datetime(df["Fecha"])

    return df


df_base = load_main_data()


# ============================================================
# 4. FILTROS
# ============================================================

st.sidebar.header("🔍 Filtros Globales")

socios_disponibles = (
    ["Todos"]
    + sorted(
        df_base["Nombre_Socio"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
)

socio_seleccionado = st.sidebar.selectbox(
    "Seleccionar Socio",
    socios_disponibles
)


propiedades_disponibles = (
    ["Todas"]
    + sorted(
        df_base["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
)

propiedad_seleccionada = st.sidebar.selectbox(
    "Seleccionar Propiedad",
    propiedades_disponibles
)


df_filtered = df_base.copy()


if socio_seleccionado != "Todos":

    df_filtered = df_filtered[
        df_filtered["Nombre_Socio"] == socio_seleccionado
    ]


if propiedad_seleccionada != "Todas":

    df_filtered = df_filtered[
        df_filtered["Nombre_Propiedad"] == propiedad_seleccionada
    ]


# ============================================================
# 5. KPIs
# ============================================================

total_ingresos = df_filtered["Ingreso"].sum()

total_gastos = df_filtered["Gasto"].sum()

utilidad_neta = total_ingresos - total_gastos

margen = (
    utilidad_neta / total_ingresos * 100
    if total_ingresos > 0
    else 0
)


col1, col2, col3 = st.columns(3)


col1.metric(
    "💰 Total Ingresos",
    f"${total_ingresos:,.0f}"
)


col2.metric(
    "📉 Total Gastos",
    f"${total_gastos:,.0f}"
)


col3.metric(
    "📈 Utilidad Neta",
    f"${utilidad_neta:,.0f}",
    delta=f"{margen:.1f}%"
)


st.divider()


# ============================================================
# 6. GRÁFICOS
# ============================================================

col_graf1, col_graf2 = st.columns(2)


# ------------------------------------------------------------
# INGRESOS MENSUALES
# ------------------------------------------------------------

with col_graf1:

    st.subheader("📊 Ingresos Mensuales")

    if not df_filtered.empty:

        df_grafico = df_filtered.copy()

        df_grafico["Mes"] = (
            df_grafico["Fecha"]
            .dt.to_period("M")
            .astype(str)
        )

        df_mensual = (
            df_grafico
            .groupby("Mes", as_index=False)["Ingreso"]
            .sum()
        )

        fig_bar = px.bar(
            df_mensual,
            x="Mes",
            y="Ingreso",
            text_auto=".2s",
            labels={
                "Mes": "Mes",
                "Ingreso": "Ingresos"
            }
        )

        fig_bar.update_layout(
            xaxis_title="",
            yaxis_title="Ingresos",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    else:

        st.warning(
            "No hay datos con los filtros seleccionados."
        )


# ------------------------------------------------------------
# GASTOS POR CATEGORÍA
# ------------------------------------------------------------

with col_graf2:

    st.subheader("🍩 Gastos por Categoría")

    if not df_filtered.empty:

        df_gastos = (
            df_filtered
            .groupby(
                "Nombre_Categoria",
                as_index=False
            )["Gasto"]
            .sum()
        )

        df_gastos = df_gastos[
            df_gastos["Gasto"] > 0
        ]

        fig_pie = px.pie(
            df_gastos,
            names="Nombre_Categoria",
            values="Gasto",
            hole=0.4
        )

        fig_pie.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            )
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    else:

        st.warning(
            "No hay datos de gastos."
        )


st.divider()


# ============================================================
# 7. TABLA DE MOVIMIENTOS
# ============================================================

st.subheader("📋 Últimos Movimientos Detallados")


df_tabla = (
    df_filtered[
        [
            "Fecha",
            "Nombre_Propiedad",
            "Nombre_Socio",
            "Ingreso",
            "Gasto",
            "Nombre_Categoria",
            "Nombre_Cuenta"
        ]
    ]
    .sort_values(
        by="Fecha",
        ascending=False
    )
    .head(10)
)


st.dataframe(
    df_tabla,
    use_container_width=True,
    hide_index=True
)
