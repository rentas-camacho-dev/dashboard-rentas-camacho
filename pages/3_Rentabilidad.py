import streamlit as st
import pandas as pd
import html
import textwrap

from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Airbnb Financial Hub",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML SEGURO
# ============================================================

def render_html(contenido):
    st.markdown(
        textwrap.dedent(contenido).strip(),
        unsafe_allow_html=True
    )


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

/* ------------------------------------------------------------
   GENERAL
------------------------------------------------------------ */

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1500px !important;
}


/* ------------------------------------------------------------
   HEADER
------------------------------------------------------------ */

.app-header {
    background: white;
    border-radius: 18px;
    border: 1px solid #E3E8EF;
    padding: 16px 22px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
}

.app-icon {
    width: 54px;
    height: 54px;
    min-width: 54px;
    border-radius: 15px;
    background: linear-gradient(
        135deg,
        #FF385C,
        #FF0A45
    );
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 27px;
}

.app-name {
    color: #172B4D;
    font-size: 24px;
    font-weight: 700;
    line-height: 1.05;
}

.app-name span {
    color: #FF385C;
}

.app-subtitle {
    color: #6B778C;
    font-size: 13px;
    margin-top: 4px;
}


/* ------------------------------------------------------------
   FILTROS
------------------------------------------------------------ */

.filter-title {
    color: #172B4D;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 2px;
}


/* ------------------------------------------------------------
   KPI
------------------------------------------------------------ */

.kpi-card {
    background: white;
    border: 1px solid #E3E8EF;
    border-radius: 16px;
    padding: 16px 18px;
    min-height: 112px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.035);
}

.kpi-label {
    color: #6B778C;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 7px;
}

.kpi-value {
    color: #172B4D;
    font-size: 25px;
    font-weight: 700;
    line-height: 1.1;
}

.kpi-sub {
    color: #8A94A6;
    font-size: 11px;
    margin-top: 7px;
}

.kpi-positive {
    color: #00875A;
}

.kpi-negative {
    color: #DE350B;
}


/* ------------------------------------------------------------
   SECCIÓN
------------------------------------------------------------ */

.section-title {
    color: #172B4D;
    font-size: 22px;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 2px;
}

.section-subtitle {
    color: #6B778C;
    font-size: 13px;
    margin-bottom: 12px;
}


/* ------------------------------------------------------------
   PROPIEDADES
------------------------------------------------------------ */

.property-card {
    background: white;
    border: 1px solid #E0E6ED;
    border-radius: 16px;
    padding: 17px 19px;
    margin-bottom: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.035);
}

.property-card.alert {
    border: 1.5px solid #FF9B9B;
}

.property-name {
    color: #172B4D;
    font-size: 18px;
    font-weight: 700;
}

.property-location {
    color: #6B778C;
    font-size: 12px;
    margin-top: 2px;
}

.property-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 15px;
}

.metric-box {
    background: #F7F9FB;
    border-radius: 10px;
    padding: 9px 10px;
}

.metric-label {
    color: #6B778C;
    font-size: 11px;
}

.metric-income {
    color: #00875A;
    font-size: 15px;
    font-weight: 600;
    margin-top: 2px;
}

.metric-expense {
    color: #DE350B;
    font-size: 15px;
    font-weight: 600;
    margin-top: 2px;
}

.metric-flow {
    color: #0065BD;
    font-size: 15px;
    font-weight: 700;
    margin-top: 2px;
}

.margin-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 14px;
}

.margin-label {
    color: #6B778C;
    font-size: 12px;
}

.margin-value {
    font-size: 16px;
    font-weight: 700;
}

.progress-bg {
    width: 100%;
    height: 7px;
    background: #E8EDF2;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 6px;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
}

.status {
    font-size: 11px;
    margin-top: 9px;
    font-weight: 600;
}

.status-ok {
    color: #00875A;
}

.status-alert {
    color: #DE350B;
}


/* ------------------------------------------------------------
   BIGQUERY
------------------------------------------------------------ */

.connection {
    color: #00875A;
    font-size: 11px;
    margin-left: auto;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# BIGQUERY
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
# CONSULTA BIGQUERY
# SOLO AIRBNB
# ============================================================

@st.cache_data(ttl=300)
def cargar_datos():

    query = """
    SELECT
        Fecha,
        Nombre_Propiedad,
        Ciudad,
        Nombre_Socio,
        Nombre_Tipo,
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

    st.error(
        "No se encontraron registros de Airbnb "
        "en Movimientos_Operativos_Reparto."
    )

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

df["Nombre_Propiedad"] = (
    df["Nombre_Propiedad"]
    .fillna("Sin propiedad")
    .astype(str)
)

df["Ciudad"] = (
    df["Ciudad"]
    .fillna("Sin ciudad")
    .astype(str)
)

df["Nombre_Socio"] = (
    df["Nombre_Socio"]
    .fillna("Sin socio")
    .astype(str)
)

df = df.dropna(
    subset=["Fecha"]
)


# ============================================================
# FORMATO MONEDA
# ============================================================

def dinero(valor):

    return f"${valor:,.0f}".replace(
        ",",
        "."
    )


# ============================================================
# HEADER
# ============================================================

render_html("""
<div class="app-header">

    <div class="app-icon">
        🏢
    </div>

    <div>

        <div class="app-name">
            Airbnb <span>Financial Hub</span>
        </div>

        <div class="app-subtitle">
            Rentabilidad financiera · BigQuery · Solo Airbnb
        </div>

    </div>

    <div class="connection">
        ● BigQuery conectado
    </div>

</div>
""")


# ============================================================
# FILTROS
# ============================================================

col1, col2, col3, col4 = st.columns(
    [1, 1, 1, 1]
)


with col1:

    ciudades = (
        ["Todas"]
        +
        sorted(
            df["Ciudad"]
            .unique()
            .tolist()
        )
    )

    ciudad = st.selectbox(
        "Ciudad",
        ciudades
    )


with col2:

    propiedades = (
        ["Todas"]
        +
        sorted(
            df["Nombre_Propiedad"]
            .unique()
            .tolist()
        )
    )

    propiedad = st.selectbox(
        "Propiedad",
        propiedades
    )


with col3:

    socios = (
        ["Todos"]
        +
        sorted(
            df["Nombre_Socio"]
            .unique()
            .tolist()
        )
    )

    socio = st.selectbox(
        "Socio",
        socios
    )


with col4:

    fecha_min = df["Fecha"].min().date()

    fecha_max = df["Fecha"].max().date()

    fechas = st.date_input(
        "Periodo",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_f = df.copy()


if ciudad != "Todas":

    df_f = df_f[
        df_f["Ciudad"] == ciudad
    ]


if propiedad != "Todas":

    df_f = df_f[
        df_f["Nombre_Propiedad"] == propiedad
    ]


if socio != "Todos":

    df_f = df_f[
        df_f["Nombre_Socio"] == socio
    ]


if isinstance(fechas, tuple) and len(fechas) == 2:

    fecha_inicio = pd.Timestamp(
        fechas[0]
    )

    fecha_fin = (
        pd.Timestamp(fechas[1])
        +
        pd.Timedelta(days=1)
    )

    df_f = df_f[
        (df_f["Fecha"] >= fecha_inicio)
        &
        (df_f["Fecha"] < fecha_fin)
    ]


# ============================================================
# VALIDACIÓN
# ============================================================

if df_f.empty:

    st.warning(
        "No existen datos para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# KPIs
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = ingresos - gastos

rentabilidad = (
    flujo / ingresos * 100
    if ingresos != 0
    else 0
)


# ============================================================
# CUATRO KPI EN UNA SOLA FILA
# ============================================================

k1, k2, k3, k4 = st.columns(4)


with k1:

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
💰 INGRESOS BRUTOS
</div>

<div class="kpi-value">
{dinero(ingresos)}
</div>

<div class="kpi-sub">
Ingresos registrados
</div>

</div>
""")


with k2:

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
🧾 GASTOS OPERATIVOS
</div>

<div class="kpi-value">
{dinero(gastos)}
</div>

<div class="kpi-sub">
Egresos registrados
</div>

</div>
""")


with k3:

    flujo_color = (
        "#00875A"
        if flujo >= 0
        else "#DE350B"
    )

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
💵 FLUJO
</div>

<div
class="kpi-value"
style="color:{flujo_color};"
>
{dinero(flujo)}
</div>

<div class="kpi-sub">
Ingresos − gastos
</div>

</div>
""")


with k4:

    margen_color = (
        "#00875A"
        if rentabilidad >= 35
        else "#DE350B"
    )

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
🎯 RENTABILIDAD
</div>

<div
class="kpi-value"
style="color:{margen_color};"
>
{rentabilidad:.1f}%
</div>

<div class="kpi-sub">
Objetivo: 35%
</div>

</div>
""")


# ============================================================
# SECCIÓN PROPIEDADES
# ============================================================

render_html("""
<div class="section-title">
🏢 Rentabilidad por propiedad
</div>

<div class="section-subtitle">
Desempeño financiero de cada propiedad en el periodo seleccionado
</div>
""")


# ============================================================
# AGRUPACIÓN
# ============================================================

resumen = (
    df_f
    .groupby(
        [
            "Nombre_Propiedad",
            "Ciudad"
        ],
        as_index=False
    )
    .agg(
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
)


resumen["Flujo"] = (
    resumen["Ingreso"]
    -
    resumen["Gasto"]
)


resumen["Rentabilidad"] = (
    resumen["Flujo"]
    /
    resumen["Ingreso"]
    *
    100
).fillna(0)


resumen = resumen.sort_values(
    "Rentabilidad",
    ascending=False
)


# ============================================================
# TARJETAS DE PROPIEDADES
# ============================================================

for inicio in range(
    0,
    len(resumen),
    2
):

    columnas = st.columns(2)


    for posicion in range(2):

        indice = inicio + posicion


        if indice >= len(resumen):

            continue


        fila = resumen.iloc[indice]


        nombre = html.escape(
            str(
                fila["Nombre_Propiedad"]
            )
        )


        ciudad_nombre = html.escape(
            str(
                fila["Ciudad"]
            )
        )


        ingreso_prop = float(
            fila["Ingreso"]
        )


        gasto_prop = float(
            fila["Gasto"]
        )


        flujo_prop = float(
            fila["Flujo"]
        )


        margen_prop = float(
            fila["Rentabilidad"]
        )


        progreso = max(
            0,
            min(
                margen_prop,
                100
            )
        )


        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        if margen_prop >= 35:

            color = "#00A878"

            estado = "✓ Sobre objetivo"

            clase_tarjeta = ""

            clase_estado = "status-ok"

        else:

            color = "#EF4444"

            estado = "⚠ Bajo objetivo"

            clase_tarjeta = "alert"

            clase_estado = "status-alert"


        # ----------------------------------------------------
        # TARJETA
        # ----------------------------------------------------

        contenido = f"""
<div class="property-card {clase_tarjeta}">

<div style="
display:flex;
justify-content:space-between;
align-items:flex-start;
">

<div>

<div class="property-name">
{nombre}
</div>

<div class="property-location">
📍 {ciudad_nombre}
</div>

</div>

<div
class="margin-value"
style="color:{color};"
>
{margen_prop:.1f}%
</div>

</div>


<div class="property-metrics">

<div class="metric-box">

<div class="metric-label">
Ingresos
</div>

<div class="metric-income">
{dinero(ingreso_prop)}
</div>

</div>


<div class="metric-box">

<div class="metric-label">
Gastos
</div>

<div class="metric-expense">
{dinero(gasto_prop)}
</div>

</div>


<div class="metric-box">

<div class="metric-label">
Flujo
</div>

<div class="metric-flow">
{dinero(flujo_prop)}
</div>

</div>

</div>


<div class="margin-row">

<div class="margin-label">
Rentabilidad
</div>

<div
class="margin-value"
style="color:{color};"
>
{margen_prop:.1f}%
</div>

</div>


<div class="progress-bg">

<div
class="progress-fill"
style="
width:{progreso}%;
background:{color};
">
</div>

</div>


<div class="status {clase_estado}">
{estado}
</div>


</div>
"""


        with columnas[posicion]:

            render_html(
                contenido
            )


# ============================================================
# PIE
# ============================================================

st.markdown("---")

st.caption(
    f"Airbnb Financial Hub · "
    f"BigQuery · "
    f"{len(df_f):,} registros · "
    f"{len(resumen)} propiedades"
)
