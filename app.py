import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="FinQuery - Vista Nueva",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CONEXIÓN A BIGQUERY
# ============================================================

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/drive.readonly"
    ]
)

client = bigquery.Client(
    credentials=credentials,
    project="rentascamacho"
)


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data(ttl=600)
def cargar_datos():

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

    df = client.query(query).to_dataframe()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    df["Ingreso"] = pd.to_numeric(
        df["Ingreso"], errors="coerce"
    ).fillna(0)

    df["Gasto"] = pd.to_numeric(
        df["Gasto"], errors="coerce"
    ).fillna(0)

    df["Valor_Repartido"] = pd.to_numeric(
        df["Valor_Repartido"], errors="coerce"
    ).fillna(0)

    return df


# ============================================================
# CARGA
# ============================================================

try:

    df = cargar_datos()

except Exception as e:

    st.error("❌ No fue posible cargar los datos desde BigQuery.")
    st.code(str(e))
    st.stop()


# ============================================================
# TÍTULO
# ============================================================

st.title("📊 FinQuery")

st.caption(
    "Vista financiera del portafolio · Datos conectados directamente a BigQuery"
)


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("Filtros")

# Socios
socios = sorted(
    df["Nombre_Socio"]
    .dropna()
    .astype(str)
    .unique()
)

socios_seleccionados = st.sidebar.multiselect(
    "Socio",
    socios,
    default=socios
)


# Propiedades
propiedades = sorted(
    df["Nombre_Propiedad"]
    .dropna()
    .astype(str)
    .unique()
)

propiedades_seleccionadas = st.sidebar.multiselect(
    "Propiedad",
    propiedades,
    default=propiedades
)


# Categorías
categorias = sorted(
    df["Nombre_Categoria"]
    .dropna()
    .astype(str)
    .unique()
)

categorias_seleccionadas = st.sidebar.multiselect(
    "Categoría",
    categorias,
    default=categorias
)


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()

if socios_seleccionados:

    df_filtrado = df_filtrado[
        df_filtrado["Nombre_Socio"]
        .astype(str)
        .isin(socios_seleccionados)
    ]


if propiedades_seleccionadas:

    df_filtrado = df_filtrado[
        df_filtrado["Nombre_Propiedad"]
        .astype(str)
        .isin(propiedades_seleccionadas)
    ]


if categorias_seleccionadas:

    df_filtrado = df_filtrado[
        df_filtrado["Nombre_Categoria"]
        .astype(str)
        .isin(categorias_seleccionadas)
    ]


# ============================================================
# CÁLCULOS
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()

gasto_total = df_filtrado["Gasto"].sum()

flujo_total = ingreso_total - gasto_total

rentabilidad = (
    flujo_total / ingreso_total
    if ingreso_total != 0
    else 0
)


# ============================================================
# KPI
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Ingreso Total",
        f"${ingreso_total:,.0f}"
    )


with col2:

    st.metric(
        "Gasto",
        f"${gasto_total:,.0f}"
    )


with col3:

    st.metric(
        "Flujo",
        f"${flujo_total:,.0f}"
    )


with col4:

    st.metric(
        "Rentabilidad",
        f"{rentabilidad:.1%}"
    )


st.divider()


# ============================================================
# RESUMEN POR PROPIEDAD
# ============================================================

st.subheader("🏠 Resumen por propiedad")


df_propiedades = (
    df_filtrado
    .groupby("Nombre_Propiedad", dropna=False)
    .agg(
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
    .reset_index()
)


df_propiedades["Flujo"] = (
    df_propiedades["Ingreso"]
    - df_propiedades["Gasto"]
)


df_propiedades["%"] = df_propiedades.apply(
    lambda row:
        row["Flujo"] / row["Ingreso"]
        if row["Ingreso"] != 0
        else 0,
    axis=1
)


# Ordenar por ingreso
df_propiedades = df_propiedades.sort_values(
    "Ingreso",
    ascending=False
)


# ============================================================
# FORMATO PARA MOSTRAR
# ============================================================

tabla = df_propiedades.copy()

tabla["Ingreso"] = tabla["Ingreso"].apply(
    lambda x: f"${x:,.0f}"
)

tabla["Gasto"] = tabla["Gasto"].apply(
    lambda x: f"${x:,.0f}"
)

tabla["Flujo"] = tabla["Flujo"].apply(
    lambda x: f"${x:,.0f}"
)

tabla["%"] = tabla["%"].apply(
    lambda x: f"{x:.1%}"
)


tabla = tabla.rename(
    columns={
        "Nombre_Propiedad": "Propiedad"
    }
)


st.dataframe(
    tabla[
        [
            "Propiedad",
            "Ingreso",
            "Gasto",
            "Flujo",
            "%"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# INFORMACIÓN
# ============================================================

st.caption(
    f"Registros utilizados: {len(df_filtrado):,}"
)
