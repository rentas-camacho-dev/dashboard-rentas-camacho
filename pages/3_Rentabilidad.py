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
# ESTILOS
# ============================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif !important;
}

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
    margin: 0;
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
   TARJETAS DE PROPIEDAD
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
    margin-bottom: 4px;
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

.metric-value {
    color: #172B4D;
    font-size: 18px;
    font-weight: 600;
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

    st.error(
        "No se encontraron registros de Airbnb en BigQuery."
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

st.markdown("""
<div class="hero">

    <div class="hero-title">
        🏠 Rentas Cortas
    </div>

    <div class="hero-subtitle">
        Rentabilidad financiera por propiedad ·
        Datos conectados directamente a BigQuery
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="filter-box">',
    unsafe_allow_html=True
)

st.markdown("### 🔎 Filtros")

col1, col2, col3, col4 = st.columns(4)


with col1:

    ciudades = ["Todas"] + sorted(
        df["Ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ciudades
    )


with col2:

    propiedades = ["Todas"] + sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .unique()
        .tolist()
    )

    propiedad = st.selectbox(
        "Propiedad",
        propiedades
    )


with col3:

    socios = ["Todos"] + sorted(
        df["Nombre_Socio"]
        .dropna()
        .unique()
        .tolist()
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


st.markdown(
    '</div>',
    unsafe_allow_html=True
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
        + pd.Timedelta(days=1)
    )

    df_f = df_f[
        (df_f["Fecha"] >= fecha_inicio)
        &
        (df_f["Fecha"] < fecha_fin)
    ]


# ============================================================
# FUNCIÓN DINERO
# ============================================================

def dinero(valor):

    return f"${valor:,.0f}".replace(
        ",",
        "."
    )


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


k1, k2, k3, k4 = st.columns(4)


with k1:

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True
    )


with k3:

    flujo_color = (
        "#0065BD"
        if flujo >= 0
        else "#DE350B"
    )

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True
    )


with k4:

    margen_color = (
        "#00875A"
        if rentabilidad >= 35
        else "#DE350B"
    )

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RESUMEN POR PROPIEDAD
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🏢 Rentabilidad por propiedad'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Desempeño financiero de cada propiedad '
    'en el periodo seleccionado'
    '</div>',
    unsafe_allow_html=True
)


if df_f.empty:

    st.warning(
        "No existen datos para los filtros seleccionados."
    )

    st.stop()


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

    cols = st.columns(2)

    for posicion, columna in enumerate(cols):

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


        if margen_prop >= 35:

            color = "#00A878"
            estado = "✓ Rentabilidad saludable"
            clase = ""

        else:

            color = "#EF4444"
            estado = "⚠️ Por debajo del objetivo"
            clase = "alert"


        estado_clase = (
            "alert-box"
            if margen_prop < 35
            else "ok-box"
        )


        tarjeta = textwrap.dedent(
            f"""
            <div class="property-card {clase}">

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
                    margin-bottom:10px;
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

                <div>

                    <div class="metric-label">
                        Flujo / beneficio
                    </div>

                    <div class="metric-flow">
                        {dinero(flujo_prop)}
                    </div>

                </div>

                <div style="margin-top:20px;">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
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
                            "
                        >
                        </div>

                    </div>

                </div>


                <div class="{estado_clase}">
                    {estado}
                </div>

            </div>
            """
        )


        with columna:

            st.markdown(
                tarjeta,
                unsafe_allow_html=True
            )


# ============================================================
# PIE
# ============================================================

st.markdown("---")

st.caption(
    f"BigQuery · {len(df_f):,} registros utilizados · "
    f"{len(resumen)} propiedades"
)
