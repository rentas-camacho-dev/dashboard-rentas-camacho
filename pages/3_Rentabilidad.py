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
    page_title="Rentabilidad por Propiedad",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FUNCIÓN PARA RENDERIZAR HTML
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

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1500px !important;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    background: white;
    border-radius: 18px;
    padding: 26px 30px;
    margin-bottom: 22px;
    border: 1px solid #E3E8EF;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
}

.hero-title {
    color: #172B4D;
    font-size: 32px;
    font-weight: 700;
}

.hero-subtitle {
    color: #6B778C;
    font-size: 15px;
    margin-top: 7px;
}


/* ============================================================
   FILTROS
   ============================================================ */

.filter-box {
    background: white;
    border-radius: 18px;
    padding: 20px 24px 8px 24px;
    margin-bottom: 22px;
    border: 1px solid #E3E8EF;
}


/* ============================================================
   KPI
   ============================================================ */

.kpi-card {
    background: white;
    border: 1px solid #E3E8EF;
    border-radius: 18px;
    padding: 22px 24px;
    min-height: 135px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
}

.kpi-label {
    color: #6B778C;
    font-size: 15px;
    font-weight: 500;
    margin-bottom: 12px;
}

.kpi-value {
    color: #172B4D;
    font-size: 29px;
    font-weight: 700;
}

.kpi-sub {
    color: #6B778C;
    font-size: 13px;
    margin-top: 8px;
}


/* ============================================================
   SECCIONES
   ============================================================ */

.section-title {
    color: #172B4D;
    font-size: 25px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 4px;
}

.section-subtitle {
    color: #6B778C;
    font-size: 14px;
    margin-bottom: 18px;
}


/* ============================================================
   PROPIEDADES
   ============================================================ */

.property-card {
    background: white;
    border: 1px solid #E0E6ED;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.045);
}

.property-card.alert {
    border: 2px solid #FF8A8A;
    background: #FFF9F9;
}

.property-name {
    color: #172B4D;
    font-size: 21px;
    font-weight: 700;
}

.property-location {
    color: #6B778C;
    font-size: 14px;
    margin-bottom: 20px;
}

.metric-label {
    color: #6B778C;
    font-size: 13px;
}

.metric-income {
    color: #00875A;
    font-size: 18px;
    font-weight: 600;
}

.metric-expense {
    color: #DE350B;
    font-size: 18px;
    font-weight: 600;
}

.metric-flow {
    color: #0065BD;
    font-size: 21px;
    font-weight: 700;
}

.divider {
    height: 1px;
    background: #E5EAF0;
    margin: 18px 0;
}

.margin-label {
    color: #6B778C;
    font-size: 14px;
}

.margin-value {
    font-size: 20px;
    font-weight: 700;
}


/* ============================================================
   ALERTAS
   ============================================================ */

.alert-box {
    background: #FFF0F0;
    border: 1px solid #FFB3B3;
    border-radius: 10px;
    padding: 8px 12px;
    color: #C62828;
    font-size: 13px;
    margin-top: 12px;
}

.ok-box {
    background: #EAF8F1;
    border: 1px solid #B7E4CC;
    border-radius: 10px;
    padding: 8px 12px;
    color: #087443;
    font-size: 13px;
    margin-top: 12px;
}


/* ============================================================
   BARRA
   ============================================================ */

.progress-bg {
    width: 100%;
    height: 9px;
    background: #E8EDF2;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 8px;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


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
# CARGAR DATOS DESDE BIGQUERY
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

    st.warning(
        "No se encontraron movimientos de tipo Airbnb "
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
# ENCABEZADO
# ============================================================

render_html("""
<div class="hero">

<div class="hero-title">
🏠 Rentas Cortas
</div>

<div class="hero-subtitle">
Rentabilidad financiera por propiedad ·
Datos conectados directamente a BigQuery
</div>

</div>
""")


# ============================================================
# FILTROS
# ============================================================

render_html("""
<div class="filter-box">

<h3>🔎 Filtros</h3>

</div>
""")


col1, col2, col3, col4 = st.columns(4)


# ============================================================
# FILTRO CIUDAD
# ============================================================

with col1:

    ciudades = (
        ["Todas"]
        +
        sorted(
            df["Ciudad"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    ciudad = st.selectbox(
        "Ciudad",
        ciudades
    )


# ============================================================
# FILTRO PROPIEDAD
# ============================================================

with col2:

    propiedades = (
        ["Todas"]
        +
        sorted(
            df["Nombre_Propiedad"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    propiedad = st.selectbox(
        "Propiedad",
        propiedades
    )


# ============================================================
# FILTRO SOCIO
# ============================================================

with col3:

    socios = (
        ["Todos"]
        +
        sorted(
            df["Nombre_Socio"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    socio = st.selectbox(
        "Socio",
        socios
    )


# ============================================================
# FILTRO FECHA
# ============================================================

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
# FUNCIÓN MONEDA
# ============================================================

def dinero(valor):

    return f"${valor:,.0f}".replace(
        ",",
        "."
    )


# ============================================================
# KPIs GENERALES
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
# KPI 1
# ============================================================

k1, k2, k3, k4 = st.columns(4)


with k1:

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
💰 Ingresos brutos
</div>

<div class="kpi-value">
{dinero(ingresos)}
</div>

<div class="kpi-sub">
Ingresos registrados
</div>

</div>
""")


# ============================================================
# KPI 2
# ============================================================

with k2:

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
🧾 Gastos operativos
</div>

<div class="kpi-value">
{dinero(gastos)}
</div>

<div class="kpi-sub">
Egresos registrados
</div>

</div>
""")


# ============================================================
# KPI 3
# ============================================================

with k3:

    flujo_color = (
        "#0065BD"
        if flujo >= 0
        else "#DE350B"
    )

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
💵 Flujo / beneficio
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


# ============================================================
# KPI 4
# ============================================================

with k4:

    margen_color = (
        "#00875A"
        if rentabilidad >= 35
        else "#DE350B"
    )

    render_html(f"""
<div class="kpi-card">

<div class="kpi-label">
🎯 Rentabilidad
</div>

<div
class="kpi-value"
style="color:{margen_color};"
>
{rentabilidad:.1f}%
</div>

<div class="kpi-sub">
Objetivo de referencia: 35%
</div>

</div>
""")


# ============================================================
# TÍTULO PROPIEDADES
# ============================================================

render_html("""
<div class="section-title">
🏢 Rentabilidad por propiedad
</div>

<div class="section-subtitle">
Desempeño financiero de cada propiedad
en el periodo seleccionado
</div>
""")


# ============================================================
# VALIDAR FILTROS
# ============================================================

if df_f.empty:

    st.warning(
        "No existen datos para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# RESUMEN POR PROPIEDAD
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
            str(fila["Nombre_Propiedad"])
        )


        ciudad_nombre = html.escape(
            str(fila["Ciudad"])
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

            estado = (
                "✓ Rentabilidad saludable"
            )

            clase_estado = "ok-box"

            clase_tarjeta = ""

        else:

            color = "#EF4444"

            estado = (
                "⚠️ Por debajo del objetivo"
            )

            clase_estado = "alert-box"

            clase_tarjeta = "alert"


        # ----------------------------------------------------
        # TARJETA
        # ----------------------------------------------------

        contenido = f"""
<div class="property-card {clase_tarjeta}">

<div class="property-name">
{nombre}
</div>

<div class="property-location">
📍 {ciudad_nombre}
</div>

<div class="divider"></div>


<div style="
display:flex;
justify-content:space-between;
">


<div>

<div class="metric-label">
Ingresos
</div>

<div class="metric-income">
{dinero(ingreso_prop)}
</div>

</div>


<div>

<div class="metric-label">
Gastos
</div>

<div class="metric-expense">
{dinero(gasto_prop)}
</div>

</div>


</div>


<div class="divider"></div>


<div class="metric-label">
Flujo / beneficio
</div>

<div class="metric-flow">
{dinero(flujo_prop)}
</div>


<div style="margin-top:20px;">


<div style="
display:flex;
justify-content:space-between;
">


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


</div>


<div class="{clase_estado}">
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
    f"BigQuery · "
    f"Filtro: Airbnb · "
    f"{len(df_f):,} registros · "
    f"{len(resumen)} propiedades"
)
