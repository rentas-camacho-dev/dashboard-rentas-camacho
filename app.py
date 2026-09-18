import streamlit as st
import pandas as pd
import plotly.express as px

from google.oauth2 import service_account
from google.cloud import bigquery


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="FinQuery - Rentas Cortas Camacho",
    page_icon="🏠",
    layout="wide"
)


# ============================================================
# CONEXIÓN A GOOGLE CLOUD
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/drive.readonly",
]

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

conn = bigquery.Client(
    credentials=credentials,
    project="rentascamacho"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("🏠 Portafolio de Inversión Familiar - Camacho")

st.markdown(
    "Dashboard en vivo conectado a Google Cloud BigQuery "
    "(`rentascamacho.rentas_cortas`)"
)


# ============================================================
# CARGA DE DATOS
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

    query_job = conn.query(query)

    df = query_job.result().to_dataframe(
        create_bqstorage_client=False
    )

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    return df


# ============================================================
# EJECUTAR CARGA
# ============================================================

try:

    df_base = load_main_data()

except Exception as e:

    st.error("❌ No fue posible cargar los datos desde BigQuery.")

    st.code(str(e))

    st.stop()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros")

socios = sorted(
    df_base["Nombre_Socio"]
    .dropna()
    .unique()
    .tolist()
)

propiedades = sorted(
    df_base["Nombre_Propiedad"]
    .dropna()
    .unique()
    .tolist()
)


socios_seleccionados = st.sidebar.multiselect(
    "Socio",
    socios,
    default=socios
)


propiedades_seleccionadas = st.sidebar.multiselect(
    "Propiedad",
    propiedades,
    default=propiedades
)


df = df_base.copy()


if socios_seleccionados:

    df = df[
        df["Nombre_Socio"].isin(socios_seleccionados)
    ]


if propiedades_seleccionadas:

    df = df[
        df["Nombre_Propiedad"].isin(propiedades_seleccionadas)
    ]


# ============================================================
# KPIs
# ============================================================

total_ingresos = df["Ingreso"].sum()

total_gastos = df["Gasto"].sum()

utilidad_neta = total_ingresos - total_gastos


if total_ingresos != 0:
    margen = utilidad_neta / total_ingresos
else:
    margen = 0


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "💰 Ingresos",
        f"${total_ingresos:,.0f}"
    )


with col2:

    st.metric(
        "💸 Gastos",
        f"${total_gastos:,.0f}"
    )


with col3:

    st.metric(
        "📈 Utilidad Neta",
        f"${utilidad_neta:,.0f}",
        delta=f"{margen:.1%} margen"
    )


# ============================================================
# SEPARADOR
# ============================================================

st.divider()


# ============================================================
# INGRESOS MENSUALES
# ============================================================

st.subheader("📊 Ingresos mensuales")


df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)


ingresos_mensuales = (
    df.groupby("Mes", as_index=False)["Ingreso"]
    .sum()
)


fig_ingresos = px.bar(
    ingresos_mensuales,
    x="Mes",
    y="Ingreso",
    title="Ingresos por mes",
    labels={
        "Mes": "Mes",
        "Ingreso": "Ingresos"
    }
)


st.plotly_chart(
    fig_ingresos,
    use_container_width=True
)


# ============================================================
# GASTOS POR CATEGORÍA
# ============================================================

st.subheader("🍩 Gastos por categoría")


gastos_categoria = (
    df.groupby(
        "Nombre_Categoria",
        as_index=False
    )["Gasto"]
    .sum()
)


gastos_categoria = gastos_categoria[
    gastos_categoria["Gasto"] > 0
]


if not gastos_categoria.empty:

    fig_gastos = px.pie(
        gastos_categoria,
        names="Nombre_Categoria",
        values="Gasto",
        hole=0.45,
        title="Distribución de gastos"
    )

    st.plotly_chart(
        fig_gastos,
        use_container_width=True
    )

else:

    st.info("No hay gastos para los filtros seleccionados.")


# ============================================================
# ÚLTIMOS MOVIMIENTOS
# ============================================================

st.subheader("🧾 Últimos movimientos")


ultimos = (
    df.sort_values(
        "Fecha",
        ascending=False
    )
    .head(10)
)


st.dataframe(
    ultimos,
    use_container_width=True,
    hide_index=True
)
