import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date
import textwrap


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Airbnb Financial Hub",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   APP
   ============================================================ */

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 1.7rem !important;
    padding-bottom: 1.2rem !important;
    max-width: 1500px !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}


/* ============================================================
   HEADER PRINCIPAL
   ============================================================ */

.hero {
    background: white;
    border: 1px solid #E0E6ED;
    border-radius: 22px;
    padding: 13px 20px;
    box-shadow: 0 4px 14px rgba(20,40,70,0.05);
    margin-bottom: 18px;
}


/* ============================================================
   LOGO
   ============================================================ */

.logo-box {
    width: 66px;
    height: 66px;
    border-radius: 17px;
    background: #FF1F4B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    flex-shrink: 0;
}


/* ============================================================
   TITULO
   ============================================================ */

.main-title {
    font-size: 29px;
    font-weight: 800;
    color: #192F55;
    line-height: 1.05;
    margin: 0;
    white-space: nowrap;
}

.main-title .pink {
    color: #FF3657;
}

.subtitle {
    font-size: 13px;
    color: #71809A;
    margin-top: 6px;
    white-space: nowrap;
}


/* ============================================================
   MINI KPIs DEL HEADER
   ============================================================ */

.mini-card {
    background: #F7F9FB;
    border: 1px solid #E1E7EE;
    border-radius: 14px;
    padding: 9px 12px;
    height: 68px;
    box-sizing: border-box;
    overflow: hidden;
}

.mini-label {
    font-size: 9px;
    font-weight: 700;
    color: #8190A7;
    margin-bottom: 4px;
}

.mini-value {
    font-size: 17px;
    font-weight: 800;
    color: #19345C;
}

.mini-value.green {
    color: #008F63;
}


/* ============================================================
   MINI GRAFICOS
   ============================================================ */

.mini-chart-card {
    background: #F7F9FB;
    border: 1px solid #E1E7EE;
    border-radius: 14px;
    padding: 8px 11px;
    height: 68px;
    box-sizing: border-box;
    overflow: hidden;
}

.mini-chart-title {
    font-size: 9px;
    font-weight: 700;
    color: #8190A7;
    margin-bottom: 2px;
}

.mini-bars {
    height: 34px;
    width: 100%;
    display: flex;
    align-items: flex-end;
    gap: 3px;
    overflow: hidden;
}

.mini-bar {
    flex: 1;
    background: #35B58C;
    border-radius: 2px 2px 0 0;
    min-width: 3px;
    max-width: 9px;
}

.mini-bar.purple {
    background: #7563D9;
}

.mini-chart-footer {
    display: flex;
    justify-content: space-between;
    font-size: 7px;
    color: #8996AA;
    margin-top: 1px;
}


/* ============================================================
   FILTROS
   ============================================================ */

.filter-title {
    font-size: 13px;
    color: #71809A;
    margin-bottom: 5px;
}

div[data-baseweb="select"] > div {
    background-color: #F0F3F7;
    border: none;
    border-radius: 10px;
}


/* ============================================================
   KPI PRINCIPALES
   ============================================================ */

.kpi-card {
    background: white;
    border: 1px solid #E0E6ED;
    border-radius: 18px;
    padding: 17px 20px;
    min-height: 120px;
    box-shadow: 0 4px 14px rgba(20,40,70,0.04);
}

.kpi-title {
    font-size: 14px;
    font-weight: 700;
    color: #71809A;
}

.kpi-value {
    font-size: 31px;
    font-weight: 800;
    color: #19345C;
    margin-top: 7px;
}

.kpi-value.green {
    color: #008F63;
}

.kpi-value.red {
    color: #E53B24;
}

.kpi-sub {
    font-size: 13px;
    color: #8B99AD;
    margin-top: 4px;
}


/* ============================================================
   SECCIÓN
   ============================================================ */

.section-title {
    font-size: 28px;
    font-weight: 800;
    color: #192F55;
    margin-top: 18px;
    margin-bottom: 2px;
}

.section-subtitle {
    font-size: 14px;
    color: #71809A;
    margin-bottom: 15px;
}


/* ============================================================
   TARJETAS PROPIEDADES
   ============================================================ */

.property-card {
    background: white;
    border: 1px solid #DDE4EC;
    border-radius: 22px;
    padding: 20px;
    min-height: 445px;
    box-shadow: 0 5px 15px rgba(20,40,70,0.04);
}

.property-card.bad {
    border: 2px solid #FF6262;
}

.property-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.property-name {
    font-size: 22px;
    font-weight: 800;
    color: #19345C;
}

.property-city {
    font-size: 14px;
    color: #71809A;
    margin-top: 7px;
}

.property-profit {
    font-size: 19px;
    font-weight: 800;
}

.property-profit.good {
    color: #00A878;
}

.property-profit.bad {
    color: #FF4040;
}

.accumulated {
    font-size: 12px;
    color: #8795AA;
    margin-top: 4px;
    text-align: right;
}


/* ============================================================
   METRICAS
   ============================================================ */

.metric-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 10px;
    margin-top: 22px;
}

.metric-box {
    background: #F6F8FA;
    border-radius: 14px;
    padding: 12px 10px;
}

.metric-label {
    font-size: 12px;
    color: #71809A;
}

.metric-value {
    font-size: 16px;
    font-weight: 800;
    margin-top: 5px;
}

.metric-value.income {
    color: #009D72;
}

.metric-value.expense {
    color: #FF3B20;
}

.metric-value.flow {
    color: #006FCB;
}

.metric-average {
    font-size: 10px;
    color: #8795AA;
    margin-top: 3px;
}


/* ============================================================
   RENTABILIDAD
   ============================================================ */

.profit-row {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

.profit-label {
    font-size: 13px;
    color: #71809A;
}

.progress-bg {
    height: 8px;
    border-radius: 10px;
    background: #E7ECF1;
    margin-top: 9px;
    overflow: hidden;
}

.progress-good {
    height: 100%;
    background: #00A878;
    border-radius: 10px;
}

.progress-bad {
    height: 100%;
    background: #FF4A4A;
    border-radius: 10px;
}

.target-good {
    color: #009A6C;
    font-size: 12px;
    font-weight: 600;
    margin-top: 9px;
}

.target-bad {
    color: #E53B24;
    font-size: 12px;
    font-weight: 600;
    margin-top: 9px;
}


/* ============================================================
   OCUPACION
   ============================================================ */

.occupancy-box {
    background: #F6F8FA;
    border-radius: 15px;
    padding: 13px 12px;
    margin-top: 15px;
}

.occupancy-title {
    font-size: 12px;
    color: #71809A;
}

.occupancy-value {
    font-size: 17px;
    font-weight: 800;
    color: #7256E8;
    margin-top: 6px;
}

.occupancy-detail {
    font-size: 11px;
    color: #8795AA;
    margin-top: 4px;
}


/* ============================================================
   STREAMLIT
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
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
# FUNCIONES
# ============================================================

def dinero(valor):

    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


def dinero_corto(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"${valor/1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"${valor/1_000:.0f}k"

    return f"${valor:,.0f}".replace(",", ".")


# ============================================================
# DATOS FINANCIEROS
# ============================================================

@st.cache_data(ttl=300)
def cargar_datos_financieros():

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

    df = client.query(query).to_dataframe()

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

    return df


# ============================================================
# RESERVAS AIRBNB
# ============================================================

@st.cache_data(ttl=300)
def cargar_reservas(fecha_inicio, fecha_fin):

    query = """
    WITH mapa AS (

        SELECT
            LOWER(TRIM(Anuncio)) AS anuncio_key,
            Nombre AS Nombre_Propiedad,
            Ciudad

        FROM
            `rentascamacho.rentas_cortas.Participaciones`

        WHERE
            Anuncio IS NOT NULL
            AND TRIM(Anuncio) <> ''

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY LOWER(TRIM(Anuncio))
            ORDER BY ID_Activo
        ) = 1
    ),

    reservas_base AS (

        SELECT
            C__digo_de_confirmaci__n AS Codigo_Reserva,
            LOWER(TRIM(Anuncio)) AS anuncio_key,
            DATE(Fecha_de_inicio) AS Fecha_Inicio,
            DATE(Fecha_de_finalizaci__n) AS Fecha_Fin

        FROM
            `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

        WHERE
            LOWER(TRIM(Tipo)) = 'reservación'
            AND C__digo_de_confirmaci__n IS NOT NULL
            AND Anuncio IS NOT NULL
            AND Fecha_de_inicio IS NOT NULL
            AND Fecha_de_finalizaci__n IS NOT NULL

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY C__digo_de_confirmaci__n
            ORDER BY Fecha_de_inicio
        ) = 1
    ),

    reservas AS (

        SELECT
            r.Codigo_Reserva,
            m.Nombre_Propiedad,
            m.Ciudad,
            r.Fecha_Inicio,
            r.Fecha_Fin

        FROM reservas_base r

        INNER JOIN mapa m
            ON r.anuncio_key = m.anuncio_key
    ),

    calculo AS (

        SELECT
            Codigo_Reserva,
            Nombre_Propiedad,
            Ciudad,

            GREATEST(
                Fecha_Inicio,
                @fecha_inicio
            ) AS Inicio_Overlap,

            LEAST(
                Fecha_Fin,
                DATE_ADD(
                    @fecha_fin,
                    INTERVAL 1 DAY
                )
            ) AS Fin_Overlap

        FROM reservas

        WHERE
            Fecha_Inicio <
                DATE_ADD(
                    @fecha_fin,
                    INTERVAL 1 DAY
                )

            AND Fecha_Fin >
                @fecha_inicio
    )

    SELECT

        Nombre_Propiedad,
        Ciudad,

        COUNT(DISTINCT Codigo_Reserva)
            AS Reservas,

        SUM(
            GREATEST(
                DATE_DIFF(
                    Fin_Overlap,
                    Inicio_Overlap,
                    DAY
                ),
                0
            )
        ) AS Noches_Reservadas,

        DATE_DIFF(
            DATE_ADD(
                @fecha_fin,
                INTERVAL 1 DAY
            ),
            @fecha_inicio,
            DAY
        ) AS Noches_Disponibles

    FROM calculo

    GROUP BY
        Nombre_Propiedad,
        Ciudad
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "fecha_inicio",
                "DATE",
                fecha_inicio
            ),
            bigquery.ScalarQueryParameter(
                "fecha_fin",
                "DATE",
                fecha_fin
            )
        ]
    )

    return client.query(
        query,
        job_config=job_config
    ).to_dataframe()


# ============================================================
# CARGAR DATOS
# ============================================================

df = cargar_datos_financieros()

hoy = date.today()

inicio_anio = pd.Timestamp(
    hoy.year,
    1,
    1
)

fin_hoy = (
    pd.Timestamp(hoy)
    + pd.Timedelta(days=1)
)

inicio_mes = date(
    hoy.year,
    hoy.month,
    1
)


# ============================================================
# YTD
# ============================================================

df_ytd = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < fin_hoy)
].copy()

ingresos_ytd = df_ytd["Ingreso"].sum()

gastos_ytd = df_ytd["Gasto"].sum()

flujo_ytd = (
    ingresos_ytd -
    gastos_ytd
)

rentabilidad_ytd = (
    flujo_ytd / ingresos_ytd * 100
    if ingresos_ytd != 0
    else 0
)


# ============================================================
# MINI GRAFICO INGRESO MENSUAL
# ============================================================

df_anio = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < fin_hoy)
].copy()

df_anio["Mes"] = (
    df_anio["Fecha"]
    .dt.month
)

mensual = (
    df_anio
    .groupby(
        "Mes",
        as_index=False
    )["Ingreso"]
    .sum()
)

meses = list(
    range(
        1,
        hoy.month + 1
    )
)

mensual = (
    pd.DataFrame(
        {"Mes": meses}
    )
    .merge(
        mensual,
        on="Mes",
        how="left"
    )
    .fillna(0)
)

max_ingreso = (
    mensual["Ingreso"].max()
)

if max_ingreso > 0:

    mensual["altura"] = (
        mensual["Ingreso"]
        / max_ingreso
        * 30
    )

else:

    mensual["altura"] = 4


# ============================================================
# MINI GRAFICO PROMEDIO
# ============================================================

promedio_propiedad = (
    df_anio
    .groupby(
        [
            "Nombre_Propiedad",
            "Ciudad"
        ],
        as_index=False
    )
    .agg(
        Ingreso_Promedio=(
            "Ingreso",
            "mean"
        )
    )
    .sort_values(
        "Ingreso_Promedio",
        ascending=False
    )
)

promedio_propiedad = (
    promedio_propiedad.head(6)
)

max_promedio = (
    promedio_propiedad[
        "Ingreso_Promedio"
    ].max()
    if not promedio_propiedad.empty
    else 0
)

if max_promedio > 0:

    promedio_propiedad["altura"] = (
        promedio_propiedad[
            "Ingreso_Promedio"
        ]
        / max_promedio
        * 30
    )

else:

    promedio_propiedad["altura"] = 4


# ============================================================
# BARRAS
# ============================================================

barras_ingreso = ""

for _, row in mensual.iterrows():

    altura = max(
        3,
        min(
            30,
            float(row["altura"])
        )
    )

    barras_ingreso += (
        '<div class="mini-bar" '
        f'style="height:{altura:.0f}px;"></div>'
    )


barras_promedio = ""

for _, row in promedio_propiedad.iterrows():

    altura = max(
        3,
        min(
            30,
            float(row["altura"])
        )
    )

    barras_promedio += (
        '<div class="mini-bar purple" '
        f'style="height:{altura:.0f}px;"></div>'
    )


# ============================================================
# HEADER
# ============================================================

header_html = f"""
<div class="hero">

<div style="
display:flex;
align-items:center;
gap:16px;
width:100%;
">

<div class="logo-box">
🏢
</div>

<div style="
min-width:330px;
flex:1.65;
">

<div class="main-title">
Airbnb <span class="pink">Financial Hub</span>
</div>

<div class="subtitle">
Rentabilidad financiera · Solo Airbnb
</div>

</div>


<div class="mini-card" style="flex:0.95;">

<div class="mini-label">
INGRESOS 2026
</div>

<div class="mini-value">
{dinero(ingresos_ytd)}
</div>

</div>


<div class="mini-card" style="flex:0.95;">

<div class="mini-label">
FLUJO 2026
</div>

<div class="mini-value green">
{dinero(flujo_ytd)}
</div>

</div>


<div class="mini-card" style="flex:0.95;">

<div class="mini-label">
RENTABILIDAD 2026
</div>

<div class="mini-value green">
{rentabilidad_ytd:.1f}%
</div>

</div>


<div class="mini-chart-card" style="flex:0.95;">

<div class="mini-chart-title">
Ingreso mensual
</div>

<div class="mini-bars">
{barras_ingreso}
</div>

<div class="mini-chart-footer">
<span>2026</span>
<span>Mes</span>
</div>

</div>


<div class="mini-chart-card" style="flex:0.95;">

<div class="mini-chart-title">
Promedio mensual
</div>

<div class="mini-bars">
{barras_promedio}
</div>

<div class="mini-chart-footer">
<span>Propiedades</span>
<span>2026</span>
</div>

</div>

</div>

</div>
"""

header_html = textwrap.dedent(
    header_html
).strip()

st.markdown(
    header_html,
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        '<div class="filter-title">Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .astype(str)
        .unique()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        label_visibility="collapsed"
    )


with col2:

    st.markdown(
        '<div class="filter-title">Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades,
        label_visibility="collapsed"
    )


with col3:

    st.markdown(
        '<div class="filter-title">Socio</div>',
        unsafe_allow_html=True
    )

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .astype(str)
        .unique()
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios,
        label_visibility="collapsed"
    )


with col4:

    st.markdown(
        '<div class="filter-title">Período de análisis</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Período",
        value=(inicio_mes, hoy),
        label_visibility="collapsed"
    )


if (
    isinstance(periodo, tuple)
    and len(periodo) == 2
):

    fecha_inicio = periodo[0]
    fecha_fin = periodo[1]

else:

    fecha_inicio = inicio_mes
    fecha_fin = hoy


# ============================================================
# FILTRO FINANCIERO
# ============================================================

df_f = df[
    (df["Fecha"].dt.date >= fecha_inicio) &
    (df["Fecha"].dt.date <= fecha_fin)
].copy()


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


# ============================================================
# KPIs
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = (
    ingresos -
    gastos
)

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

<div class="kpi-title">
🤑 INGRESOS BRUTOS
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

<div class="kpi-title">
🧾 GASTOS OPERATIVOS
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

    st.markdown(
        f"""
<div class="kpi-card">

<div class="kpi-title">
💵 FLUJO
</div>

<div class="kpi-value green">
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

    color = (
        "#008F63"
        if rentabilidad >= 35
        else "#E53B24"
    )

    st.markdown(
        f"""
<div class="kpi-card">

<div class="kpi-title">
🎯 RENTABILIDAD
</div>

<div
class="kpi-value"
style="color:{color};"
>
{rentabilidad:.1f}%
</div>

<div class="kpi-sub">
Objetivo: 35%
</div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# TITULO PROPIEDADES
# ============================================================

st.markdown(
    """
<div class="section-title">
🏢 Rentabilidad por propiedad
</div>

<div class="section-subtitle">
Desempeño financiero de cada propiedad
en el período seleccionado
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# RESUMEN PROPIEDADES
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
        Ingresos=("Ingreso", "sum"),
        Gastos=("Gasto", "sum")
    )
)

resumen["Flujo"] = (
    resumen["Ingresos"] -
    resumen["Gastos"]
)

resumen["Rentabilidad"] = resumen.apply(
    lambda x:
        x["Flujo"]
        / x["Ingresos"]
        * 100
        if x["Ingresos"] != 0
        else 0,
    axis=1
)


# ============================================================
# PROMEDIOS MENSUALES
# ============================================================

meses_cerrados = max(
    hoy.month - 1,
    0
)

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
)

df_cerrado = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < inicio_mes_actual)
].copy()


if meses_cerrados > 0:

    promedios = (
        df_cerrado
        .groupby(
            [
                "Nombre_Propiedad",
                "Ciudad"
            ],
            as_index=False
        )
        .agg(
            Ingreso_Promedio=(
                "Ingreso",
                "sum"
            ),
            Gasto_Promedio=(
                "Gasto",
                "sum"
            )
        )
    )

    promedios["Ingreso_Promedio"] /= meses_cerrados

    promedios["Gasto_Promedio"] /= meses_cerrados

    promedios["Flujo_Promedio"] = (
        promedios["Ingreso_Promedio"]
        -
        promedios["Gasto_Promedio"]
    )

else:

    promedios = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Ingreso_Promedio",
            "Gasto_Promedio",
            "Flujo_Promedio"
        ]
    )


resumen = resumen.merge(
    promedios,
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)


# ============================================================
# OCUPACION
# ============================================================

try:

    df_ocupacion = cargar_reservas(
        fecha_inicio,
        fecha_fin
    )

except Exception:

    df_ocupacion = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas",
            "Noches_Disponibles"
        ]
    )


if not df_ocupacion.empty:

    df_ocupacion[
        "Ocupacion_Porcentaje"
    ] = (
        df_ocupacion[
            "Noches_Reservadas"
        ]
        /
        df_ocupacion[
            "Noches_Disponibles"
        ]
        * 100
    )

else:

    df_ocupacion[
        "Ocupacion_Porcentaje"
    ] = pd.Series(
        dtype=float
    )


resumen = resumen.merge(
    df_ocupacion,
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)


# ============================================================
# ORDEN
# ============================================================

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
    3
):

    fila = resumen.iloc[
        inicio:inicio + 3
    ]

    cols = st.columns(3)

    for col, (_, row) in zip(
        cols,
        fila.iterrows()
    ):

        rent = float(
            row["Rentabilidad"]
        )

        es_buena = rent >= 35

        card_class = (
            "good"
            if es_buena
            else "bad"
        )

        profit_class = (
            "good"
            if es_buena
            else "bad"
        )

        progress = min(
            max(rent, 0),
            100
        )


        if es_buena:

            objetivo = """
<div class="target-good">
✓ Sobre objetivo
</div>
"""

        else:

            objetivo = """
<div class="target-bad">
⚠ Bajo objetivo
</div>
"""


        ingreso_prom = row.get(
            "Ingreso_Promedio",
            0
        )

        gasto_prom = row.get(
            "Gasto_Promedio",
            0
        )

        flujo_prom = row.get(
            "Flujo_Promedio",
            0
        )

        ocupacion = row.get(
            "Ocupacion_Porcentaje",
            None
        )

        reservas = row.get(
            "Reservas",
            None
        )

        noches = row.get(
            "Noches_Reservadas",
            None
        )


        ocupacion_txt = (
            "—"
            if pd.isna(ocupacion)
            else f"{float(ocupacion):.1f}%"
        )

        reservas_txt = (
            "—"
            if pd.isna(reservas)
            else f"{int(reservas)} reservas"
        )

        noches_txt = (
            "—"
            if pd.isna(noches)
            else f"{int(noches)} noches"
        )


        html_card = f"""
<div class="property-card {card_class}">

<div class="property-header">

<div>

<div class="property-name">
{row["Nombre_Propiedad"]}
</div>

<div class="property-city">
📍 {row["Ciudad"]}
</div>

</div>

<div>

<div class="property-profit {profit_class}">
{rent:.1f}%
</div>

<div class="accumulated">
Acumulada 2026
</div>

</div>

</div>


<div class="metric-grid">

<div class="metric-box">

<div class="metric-label">
Ingresos
</div>

<div class="metric-value income">
{dinero(row["Ingresos"])}
</div>

<div class="metric-average">
Prom. mes {dinero_corto(ingreso_prom)}
</div>

</div>


<div class="metric-box">

<div class="metric-label">
Gastos
</div>

<div class="metric-value expense">
{dinero(row["Gastos"])}
</div>

<div class="metric-average">
Prom. mes {dinero_corto(gasto_prom)}
</div>

</div>


<div class="metric-box">

<div class="metric-label">
Flujo
</div>

<div class="metric-value flow">
{dinero(row["Flujo"])}
</div>

<div class="metric-average">
Prom. mes {dinero_corto(flujo_prom)}
</div>

</div>

</div>


<div class="profit-row">

<div class="profit-label">
Rentabilidad
</div>

<div class="property-profit {profit_class}">
{rent:.1f}%
</div>

</div>


<div class="progress-bg">

<div
class="progress-{'good' if es_buena else 'bad'}"
style="width:{progress:.1f}%">
</div>

</div>

{objetivo}


<div class="occupancy-box">

<div class="occupancy-title">
Ocupación Airbnb
</div>

<div class="occupancy-value">
{ocupacion_txt}
</div>

<div class="occupancy-detail">
{reservas_txt} · {noches_txt}
</div>

</div>

</div>
"""

        html_card = textwrap.dedent(
            html_card
        ).strip()

        with col:

            st.markdown(
                html_card,
                unsafe_allow_html=True
            )


    st.markdown(
        "<div style='height:15px'></div>",
        unsafe_allow_html=True
    )
