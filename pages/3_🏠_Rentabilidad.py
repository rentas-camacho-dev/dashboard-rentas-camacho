import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(
    page_title="Rentabilidad por Propiedad",
    page_icon="🏠",
    layout="wide"
)

# ============================================================
# CONEXIÓN BIGQUERY
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

@st.cache_data(ttl=300)
def cargar_datos():

    query = """
    SELECT
        Fecha,
        Nombre_Propiedad,
        Ciudad,
        Nombre_Socio,
        Ingreso,
        Gasto

    FROM
        `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`

    WHERE
        LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
    """

    return client.query(query).to_dataframe()


df = cargar_datos()


# ============================================================
# VALIDACIÓN
# ============================================================

if df.empty:

    st.warning("No se encontraron datos de Airbnb.")
    st.stop()


# ============================================================
# LIMPIEZA
# ============================================================

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    errors="coerce"
)

df["Ingreso"] = pd.to_numeric(
    df["Ingreso"],
    errors="coerce"
).fillna(0)

df["Gasto"] = pd.to_numeric(
    df["Gasto"],
    errors="coerce"
).fillna(0)

df = df.dropna(
    subset=["Fecha"]
)


# ============================================================
# TÍTULO
# ============================================================

st.title("🏠 Rentabilidad por Propiedad")

st.write(
    "Vista ejecutiva de rentabilidad de las propiedades Airbnb"
)


# ============================================================
# PRUEBA
# ============================================================

st.success(
    f"Conexión a BigQuery funcionando — "
    f"{len(df):,} registros cargados"
)

st.dataframe(
    df.head(20),
    use_container_width=True
)
