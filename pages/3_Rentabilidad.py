import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date


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
   GENERAL
   ============================================================ */

.stApp {
    background: #F4F7FA;
}

.block-container {
    padding-top: 2.8rem !important;
    padding-bottom: 1.2rem !important;
    max-width: 1550px !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   HEADER
   ============================================================ */

.top-header {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 17px;
    padding: 13px 15px;
    box-shadow: 0 4px 14px rgba(25, 47, 85, 0.045);
    margin-bottom: 12px;
}

.logo {
    width: 54px;
    height: 54px;
    border-radius: 14px;
    background: #FF1F4B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}

.brand {
    font-size: 24px;
    font-weight: 850;
    color: #142F59;
    line-height: 1.05;
}

.brand-pink {
    color: #FF3155;
}

.brand-subtitle {
    font-size: 10px;
    color: #7B8BA3;
    margin-top: 4px;
}


/* ============================================================
   KPI
   ============================================================ */

.header-kpi {
    height: 66px;
    background: #F7F9FC;
    border: 1px solid #E2E8EF;
    border-radius: 11px;
    padding: 8px 11px;
    box-sizing: border-box;
}

.header-kpi-label {
    font-size: 8px;
    font-weight: 700;
    color: #8291A8;
}

.header-kpi-value {
    font-size: 16px;
    font-weight: 850;
    color: #18355F;
    margin-top: 4px;
}

.header-kpi-value.green {
    color: #009B70;
}

.header-kpi-value.red {
    color: #E83B2D;
}

.header-kpi-change {
    font-size: 8px;
    color: #009B70;
    margin-top: 2px;
}


/* ============================================================
   FILTROS
   ============================================================ */

.filter-panel {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 14px;
    padding: 9px 12px 4px 12px;
    margin-bottom: 12px;
}

.filter-label {
    font-size: 9px;
    font-weight: 700;
    color: #71829A;
    margin-bottom: 3px;
}

div[data-baseweb="select"] > div {
    background: #F3F6F9;
    border: none;
    border-radius: 8px;
}

div[data-testid="stDateInput"] > div {
    background: #F3F6F9;
    border-radius: 8px;
}


/* ============================================================
   NAVEGACIÓN
   ============================================================ */

.nav-panel {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 14px;
    padding: 11px;
    min-height: 570px;
    box-shadow: 0 3px 12px rgba(25,47,85,0.03);
}

.nav-title {
    font-size: 12px;
    font-weight: 850;
    color: #17335D;
    margin-bottom: 9px;
}

.nav-item {
    height: 34px;
    border-radius: 8px;
    padding: 8px 10px;
    box-sizing: border-box;
    font-size: 10px;
    color: #61728C;
    margin-bottom: 3px;
}

.nav-item.active {
    background: #FFF0F3;
    color: #FF3155;
    font-weight: 750;
}

.nav-separator {
    height: 1px;
    background: #EDF1F5;
    margin: 11px 0;
}

.nav-small {
    font-size: 8px;
    color: #8A98AB;
    line-height: 1.5;
}


/* ============================================================
   RESUMEN LATERAL
   ============================================================ */

.summary-title {
    font-size: 13px;
    font-weight: 850;
    color: #17335D;
    margin-bottom: 8px;
}

.summary-card {
    border-radius: 11px;
    padding: 10px;
    margin-bottom: 7px;
    background: #F7FAFC;
    border-left: 3px solid #00A879;
}

.summary-card.expense {
    border-left-color: #FF4B43;
}

.summary-card.flow {
    border-left-color: #1478D4;
}

.summary-card.profit {
    border-left-color: #7655E8;
}

.summary-label {
    font-size: 8px;
    color: #75859C;
    font-weight: 700;
}

.summary-value {
    font-size: 20px;
    color: #17355F;
    font-weight: 850;
    margin-top: 2px;
}

.summary-sub {
    font-size: 8px;
    color: #8A98AA;
    margin-top: 2px;
}


/* ============================================================
   SECCIÓN
   ============================================================ */

.section-title {
    font-size: 20px;
    font-weight: 850;
    color: #142F59;
    line-height: 1.1;
}

.section-subtitle {
    font-size: 9px;
    color: #7A8BA3;
    margin-top: 4px;
}


/* ============================================================
   CONTROLES
   ============================================================ */

.sort-box {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 9px;
    padding: 8px 10px;
    font-size: 9px;
    color: #53657F;
}


/* ============================================================
   TARJETAS PROPIEDADES
   ============================================================ */

.property-card {
    background: #FFFFFF;
    border: 1px solid #DDE5ED;
    border-radius: 14px;
    padding: 10px;
    height: 248px;
    box-sizing: border-box;
    box-shadow: 0 3px 10px rgba(25,47,85,0.035);
    overflow: hidden;
}

.property-card.loss {
    border-color: #FFAAA6;
}

.property-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 5px;
}

.property-icon {
    width: 42px;
    height: 42px;
    border-radius: 9px;
    background: linear-gradient(135deg,#DDEEFF,#F4F8FC);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    float: left;
    margin-right: 8px;
}

.property-name {
    font-size: 13px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.15;
    margin-top: 1px;
}

.property-city {
    font-size: 8px;
    color: #71829A;
    margin-top: 4px;
}

.property-profit {
    font-size: 14px;
    font-weight: 850;
    color: #00A879;
    white-space: nowrap;
}

.property-profit.loss {
    color: #EF3E32;
}

.property-year {
    font-size: 7px;
    color: #8796A9;
    text-align: right;
    margin-top: 2px;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.property-metrics {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 4px;
    margin-top: 10px;
}

.property-metric {
    background: #F5F8FA;
    border-radius: 7px;
    padding: 6px;
    height: 47px;
    box-sizing: border-box;
}

.property-metric-label {
    font-size: 7px;
    color: #7788A0;
}

.property-metric-value {
    font-size: 11px;
    font-weight: 850;
    margin-top: 3px;
}

.income {
    color: #009B70;
}

.expense {
    color: #EF3E32;
}

.flow {
    color: #0878D2;
}

.property-average {
    font-size: 6.5px;
    color: #8A98AA;
    margin-top: 2px;
}


/* ============================================================
   BARRA RENTABILIDAD
   ============================================================ */

.profit-line {
    display: flex;
    justify-content: space-between;
    margin-top: 8px;
}

.profit-line-label {
    font-size: 8px;
    color: #71829A;
}

.profit-line-value {
    font-size: 9px;
    font-weight: 800;
}

.progress-background {
    height: 5px;
    background: #E8EDF2;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 3px;
}

.progress-positive {
    height: 100%;
    background: #00B486;
    border-radius: 8px;
}

.progress-negative {
    height: 100%;
    background: #F0443A;
    border-radius: 8px;
}


/* ============================================================
   OCUPACIÓN
   ============================================================ */

.occupancy {
    margin-top: 8px;
    height: 43px;
    background: #F5F7FB;
    border-radius: 8px;
    padding: 6px 8px;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.occupancy-label {
    font-size: 7px;
    color: #71829A;
}

.occupancy-value {
    font-size: 13px;
    font-weight: 850;
    color: #6B4FE8;
    margin-top: 2px;
}

.occupancy-detail {
    text-align: right;
    font-size: 7px;
    color: #7D8DA2;
    line-height: 1.4;
}


/* ============================================================
   PLACEHOLDER
   ============================================================ */

.add-card {
    height: 248px;
    border: 1px dashed #B8C7D8;
    border-radius: 14px;
    background: #FAFCFE;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #7890AE;
    text-align: center;
}

.add-plus {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #EAF0F6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
    color: #7890AE;
}

.add-title {
    font-size: 11px;
    font-weight: 750;
    margin-top: 8px;
}

.add-sub {
    font-size: 8px;
    margin-top: 4px;
}


/* ============================================================
   CHART CARDS
   ============================================================ */

.chart-card {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 13px;
    padding: 11px;
    box-sizing: border-box;
    margin-bottom: 9px;
}

.chart-title {
    font-size: 11px;
    font-weight: 800;
    color: #17345E;
}

.chart-subtitle {
    font-size: 7px;
    color: #8492A6;
    margin-top: 2px;
}

.bar-chart {
    height: 120px;
    display: flex;
    align-items: flex-end;
    gap: 5px;
    margin-top: 10px;
    padding: 0 3px;
}

.bar-wrapper {
    flex: 1;
    height: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: center;
}

.bar {
    width: 100%;
    max-width: 18px;
    background: #22B68D;
    border-radius: 3px 3px 0 0;
}

.bar-label {
    font-size: 6px;
    color: #8997A9;
    margin-top: 3px;
    text-align: center;
}


/* ============================================================
   RANKING
   ============================================================ */

.rank-row {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 7px;
}

.rank-name {
    width: 65px;
    font-size: 7px;
    color: #5F718A;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rank-background {
    flex: 1;
    height: 7px;
    background: #EEF1F5;
    border-radius: 6px;
    overflow: hidden;
}

.rank-bar {
    height: 100%;
    background: #8067E8;
    border-radius: 6px;
}

.rank-value {
    width: 33px;
    text-align: right;
    font-size: 7px;
    color: #6D7D94;
}


/* ============================================================
   DONUT
   ============================================================ */

.donut-area {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 9px;
}

.donut {
    width: 94px;
    height: 94px;
    border-radius: 50%;
    position: relative;
    flex-shrink: 0;
}

.donut-center {
    position: absolute;
    inset: 20px;
    border-radius: 50%;
    background: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
}

.donut-total {
    font-size: 13px;
    font-weight: 850;
    color: #17345E;
}

.donut-label {
    font-size: 6px;
    color: #8290A3;
}

.legend {
    flex: 1;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 5px;
}

.legend-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}

.legend-name {
    flex: 1;
    font-size: 6.5px;
    color: #65758D;
}

.legend-value {
    font-size: 6.5px;
    color: #65758D;
}


/* ============================================================
   INSIGHTS
   ============================================================ */

.insight {
    display: flex;
    gap: 7px;
    align-items: flex-start;
    margin-top: 8px;
}

.insight-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-top: 3px;
    flex-shrink: 0;
}

.insight-text {
    font-size: 8px;
    line-height: 1.4;
    color: #5F718A;
}


/* ============================================================
   TABLA
   ============================================================ */

.table-card {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 13px;
    padding: 11px;
    margin-top: 10px;
}

.table-title {
    font-size: 12px;
    font-weight: 850;
    color: #17345E;
    margin-bottom: 8px;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th {
    font-size: 7px;
    color: #8391A5;
    font-weight: 700;
    text-align: left;
    padding: 6px;
    border-bottom: 1px solid #E8EDF2;
}

.data-table td {
    font-size: 8px;
    color: #52647E;
    padding: 6px;
    border-bottom: 1px solid #F0F3F6;
}

.data-table td.name {
    font-weight: 800;
    color: #17345E;
}

.data-table td.green {
    color: #009B70;
    font-weight: 750;
}

.data-table td.red {
    color: #EF3E32;
    font-weight: 750;
}

.data-table td.blue {
    color: #0878D2;
    font-weight: 750;
}


/* ============================================================
   OBJETIVO
   ============================================================ */

.target-card {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 12px;
    padding: 10px;
    margin-top: 9px;
}

.target-title {
    font-size: 8px;
    color: #71829A;
}

.target-value {
    font-size: 20px;
    font-weight: 850;
    color: #17345E;
    margin-top: 2px;
}

.target-background {
    height: 6px;
    background: #E8EDF2;
    border-radius: 8px;
    margin-top: 5px;
    overflow: hidden;
}

.target-progress {
    height: 100%;
    width: 67%;
    background: #00B486;
    border-radius: 8px;
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
# FORMATO
# ============================================================

def dinero_corto(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    signo = "-" if valor < 0 else ""

    valor = abs(valor)

    if valor >= 1_000_000:
        return f"{signo}${valor/1_000_000:.1f}M"

    if valor >= 1_000:
        return f"{signo}${valor/1_000:.0f}k"

    return f"{signo}${valor:,.0f}".replace(",", ".")


def dinero(valor):

    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


# ============================================================
# FINANCIERO
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

    return df


# ============================================================
# RESERVAS
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
                DATE_ADD(@fecha_fin, INTERVAL 1 DAY)
            ) AS Fin_Overlap

        FROM reservas

        WHERE
            Fecha_Inicio <
                DATE_ADD(@fecha_fin, INTERVAL 1 DAY)

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
            DATE_ADD(@fecha_fin, INTERVAL 1 DAY),
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
# CARGAR
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
# FILTROS
# ============================================================

col1, col2, col3, col4 = st.columns(
    [1.1, 1.1, 1.1, 1.3]
)

with col1:

    st.markdown(
        '<div class="filter-label">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudades = sorted(
        df["Ciudad"].unique()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        label_visibility="collapsed"
    )


with col2:

    st.markdown(
        '<div class="filter-label">🏢 Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedades = sorted(
        df["Nombre_Propiedad"].unique()
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades,
        label_visibility="collapsed"
    )


with col3:

    st.markdown(
        '<div class="filter-label">👥 Socio</div>',
        unsafe_allow_html=True
    )

    socios = sorted(
        df["Nombre_Socio"].unique()
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios,
        label_visibility="collapsed"
    )


with col4:

    st.markdown(
        '<div class="filter-label">📅 Período de análisis</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Periodo",
        value=(inicio_mes, hoy),
        label_visibility="collapsed"
    )


# ============================================================
# HEADER
# ============================================================

df_ytd = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < fin_hoy)
]

ingresos_ytd = df_ytd["Ingreso"].sum()
gastos_ytd = df_ytd["Gasto"].sum()
flujo_ytd = ingresos_ytd - gastos_ytd

rentabilidad_ytd = (
    flujo_ytd / ingresos_ytd * 100
    if ingresos_ytd
    else 0
)

rent_color = (
    "green"
    if rentabilidad_ytd >= 35
    else "red"
)

header_html = f"""
<div class="top-header">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div class="logo">
🏢
</div>

<div style="
width:260px;
flex-shrink:0;
">

<div class="brand">
Airbnb <span class="brand-pink">Financial Hub</span>
</div>

<div class="brand-subtitle">
Rentabilidad financiera · Solo Airbnb
</div>

</div>


<div class="header-kpi" style="flex:1;">

<div class="header-kpi-label">
INGRESOS 2026
</div>

<div class="header-kpi-value">
{dinero_corto(ingresos_ytd)}
</div>

</div>


<div class="header-kpi" style="flex:1;">

<div class="header-kpi-label">
FLUJO 2026
</div>

<div class="header-kpi-value green">
{dinero_corto(flujo_ytd)}
</div>

</div>


<div class="header-kpi" style="flex:1;">

<div class="header-kpi-label">
RENTABILIDAD 2026
</div>

<div class="header-kpi-value {rent_color}">
{rentabilidad_ytd:.1f}%
</div>

</div>


<div class="header-kpi" style="flex:1;">

<div class="header-kpi-label">
INGRESO MENSUAL
</div>

<div style="
display:flex;
align-items:flex-end;
gap:3px;
height:28px;
margin-top:2px;
">
"""

# ============================================================
# MINI BARRAS
# ============================================================

df_chart = df_ytd.copy()

df_chart["Mes"] = df_chart["Fecha"].dt.month

monthly = (
    df_chart
    .groupby("Mes")["Ingreso"]
    .sum()
)

max_month = (
    monthly.max()
    if not monthly.empty
    else 1
)

for month in range(1, hoy.month + 1):

    value = monthly.get(
        month,
        0
    )

    height = (
        max(
            3,
            int(
                value /
                max_month *
                27
            )
        )
        if max_month > 0
        else 3
    )

    header_html += f"""
<div style="
width:7px;
height:{height}px;
background:#27B68C;
border-radius:2px 2px 0 0;
"></div>
"""

header_html += """
</div>

</div>


<div class="header-kpi" style="flex:1;">

<div class="header-kpi-label">
PROMEDIO POR PROPIEDAD
</div>

<div style="
display:flex;
align-items:flex-end;
gap:3px;
height:28px;
margin-top:2px;
">
"""

# ============================================================
# PROMEDIO POR PROPIEDAD
# ============================================================

promedio_header = (
    df_ytd
    .groupby("Nombre_Propiedad")["Ingreso"]
    .sum()
    .sort_values(ascending=False)
    .head(6)
)

max_prom = (
    promedio_header.max()
    if not promedio_header.empty
    else 1
)

for value in promedio_header.values:

    height = max(
        4,
        int(
            value /
            max_prom *
            27
        )
    )

    header_html += f"""
<div style="
width:7px;
height:{height}px;
background:#7965D9;
border-radius:2px 2px 0 0;
"></div>
"""

header_html += """
</div>

</div>

</div>

</div>
"""

st.markdown(
    header_html,
    unsafe_allow_html=True
)


# ============================================================
# PERIODO
# ============================================================

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
# FILTRAR FINANCIERO
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
# KPIs PERIODO
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = ingresos - gastos

rentabilidad = (
    flujo / ingresos * 100
    if ingresos
    else 0
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
    lambda r:
        r["Flujo"] /
        r["Ingresos"] *
        100
        if r["Ingresos"] != 0
        else 0,
    axis=1
)


# ============================================================
# PROMEDIOS
# ============================================================

meses_cerrados = max(
    hoy.month - 1,
    1
)

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
)

df_cerrado = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < inicio_mes_actual)
]

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
    promedios["Ingreso_Promedio"] -
    promedios["Gasto_Promedio"]
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
# OCUPACIÓN
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

    df_ocupacion["Ocupacion"] = (
        df_ocupacion["Noches_Reservadas"]
        /
        df_ocupacion["Noches_Disponibles"]
        * 100
    )

else:

    df_ocupacion["Ocupacion"] = pd.Series(
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
).reset_index(drop=True)


# ============================================================
# LAYOUT PRINCIPAL
# ============================================================

nav_col, main_col, right_col = st.columns(
    [0.12, 0.67, 0.21],
    gap="small"
)


# ============================================================
# NAVEGACIÓN
# ============================================================

with nav_col:

    nav_html = """
<div class="nav-panel">

<div class="nav-title">
Airbnb Financial
</div>

<div class="nav-item active">
▣ &nbsp; Resumen
</div>

<div class="nav-item">
▦ &nbsp; Propiedades
</div>

<div class="nav-item">
↗ &nbsp; Ingresos
</div>

<div class="nav-item">
▣ &nbsp; Gastos
</div>

<div class="nav-item">
◉ &nbsp; Ocupación
</div>

<div class="nav-item">
⌁ &nbsp; Tendencias
</div>

<div class="nav-item">
⇩ &nbsp; Descargas
</div>

<div class="nav-separator"></div>

<div class="nav-small">
Última actualización
</div>

<div class="nav-small">
22 sep 2026
</div>

<div class="nav-small">
Información actualizada
</div>

<div class="target-card">

<div class="target-title">
Objetivo de rentabilidad
</div>

<div class="target-value">
35%
</div>

<div class="target-background">
<div class="target-progress"></div>
</div>

</div>

</div>
"""

    st.markdown(
        nav_html,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN
# ============================================================

with main_col:

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    title_col, control_col = st.columns(
        [0.65, 0.35]
    )

    with title_col:

        st.markdown(
            """
<div class="section-title">
🏢 Desempeño por propiedad
</div>

<div class="section-subtitle">
Rentabilidad, flujo y ocupación de cada propiedad
</div>
""",
            unsafe_allow_html=True
        )

    with control_col:

        st.markdown(
            f"""
<div class="sort-box">
7 propiedades · Ordenadas por rentabilidad
</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # TARJETAS
    # --------------------------------------------------------

    for inicio in range(
        0,
        len(resumen),
        4
    ):

        fila = resumen.iloc[
            inicio:inicio + 4
        ]

        cards = st.columns(
            4,
            gap="small"
        )

        for col, (_, row) in zip(
            cards,
            fila.iterrows()
        ):

            rent = float(
                row["Rentabilidad"]
            )

            es_positiva = rent >= 35

            card_class = (
                ""
                if es_positiva
                else "loss"
            )

            profit_class = (
                ""
                if es_positiva
                else "loss"
            )

            progress = min(
                max(rent, 0),
                100
            )

            ocupacion = row.get(
                "Ocupacion",
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
                else str(int(reservas))
            )

            noches_txt = (
                "—"
                if pd.isna(noches)
                else str(int(noches))
            )

            income_avg = row.get(
                "Ingreso_Promedio",
                0
            )

            expense_avg = row.get(
                "Gasto_Promedio",
                0
            )

            flow_avg = row.get(
                "Flujo_Promedio",
                0
            )


            card_html = f"""
<div class="property-card {card_class}">

<div class="property-top">

<div>

<div class="property-icon">
🏢
</div>

<div style="
margin-left:50px;
">

<div class="property-name">
{row["Nombre_Propiedad"]}
</div>

<div class="property-city">
📍 {row["Ciudad"]}
</div>

</div>

</div>


<div>

<div class="property-profit {profit_class}">
{rent:.1f}%
</div>

<div class="property-year">
Acumulada 2026
</div>

</div>

</div>


<div class="property-metrics">


<div class="property-metric">

<div class="property-metric-label">
Ingresos
</div>

<div class="property-metric-value income">
{dinero_corto(row["Ingresos"])}
</div>

<div class="property-average">
{dinero_corto(income_avg)}/mes
</div>

</div>


<div class="property-metric">

<div class="property-metric-label">
Gastos
</div>

<div class="property-metric-value expense">
{dinero_corto(row["Gastos"])}
</div>

<div class="property-average">
{dinero_corto(expense_avg)}/mes
</div>

</div>


<div class="property-metric">

<div class="property-metric-label">
Flujo
</div>

<div class="property-metric-value flow">
{dinero_corto(row["Flujo"])}
</div>

<div class="property-average">
{dinero_corto(flow_avg)}/mes
</div>

</div>


</div>


<div class="profit-line">

<div class="profit-line-label">
Rentabilidad
</div>

<div
class="profit-line-value"
style="color:{'#00A879' if es_positiva else '#EF3E32'};"
>
{rent:.1f}%
</div>

</div>


<div class="progress-background">

<div
class="{'progress-positive' if es_positiva else 'progress-negative'}"
style="width:{progress:.1f}%;">
</div>

</div>


<div
style="
font-size:7px;
font-weight:700;
color:{'#009B70' if es_positiva else '#EF3E32'};
margin-top:4px;
"
>
{'✓ Sobre objetivo' if es_positiva else '⚠ Bajo objetivo'}
</div>


<div class="occupancy">

<div>

<div class="occupancy-label">
Ocupación Airbnb
</div>

<div class="occupancy-value">
{ocupacion_txt}
</div>

</div>


<div class="occupancy-detail">
{reservas_txt} reservas<br>
{noches_txt} noches
</div>

</div>

</div>
"""

            with col:

                st.html(
                    card_html
                )


        st.markdown(
            "<div style='height:7px'></div>",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # TABLA
    # --------------------------------------------------------

    table_html = """
<div class="table-card">

<div class="table-title">
🏢 Tabla de propiedades
</div>

<table class="data-table">

<thead>

<tr>

<th>Propiedad</th>
<th>Ciudad</th>
<th>Ingresos</th>
<th>Gastos</th>
<th>Flujo</th>
<th>Rentabilidad</th>
<th>Ocupación</th>
<th>Reservas</th>
<th>Noches</th>

</tr>

</thead>

<tbody>
"""

    for _, row in resumen.iterrows():

        rent = float(
            row["Rentabilidad"]
        )

        rent_class = (
            "green"
            if rent >= 0
            else "red"
        )

        flujo_class = (
            "blue"
            if row["Flujo"] >= 0
            else "red"
        )

        ocup = row.get(
            "Ocupacion",
            None
        )

        ocup_txt = (
            "—"
            if pd.isna(ocup)
            else f"{float(ocup):.1f}%"
        )

        reservas = row.get(
            "Reservas",
            None
        )

        noches = row.get(
            "Noches_Reservadas",
            None
        )

        reservas_txt = (
            "—"
            if pd.isna(reservas)
            else str(int(reservas))
        )

        noches_txt = (
            "—"
            if pd.isna(noches)
            else str(int(noches))
        )

        table_html += f"""

<tr>

<td class="name">
{row["Nombre_Propiedad"]}
</td>

<td>
{row["Ciudad"]}
</td>

<td class="green">
{dinero_corto(row["Ingresos"])}
</td>

<td class="red">
{dinero_corto(row["Gastos"])}
</td>

<td class="{flujo_class}">
{dinero_corto(row["Flujo"])}
</td>

<td class="{rent_class}">
{rent:.1f}%
</td>

<td>
{ocup_txt}
</td>

<td>
{reservas_txt}
</td>

<td>
{noches_txt}
</td>

</tr>
"""

    table_html += f"""

<tr>

<td class="name">
TOTAL
</td>

<td>
—
</td>

<td class="green">
{dinero_corto(ingresos)}
</td>

<td class="red">
{dinero_corto(gastos)}
</td>

<td class="blue">
{dinero_corto(flujo)}
</td>

<td class="{'green' if rentabilidad >= 0 else 'red'}">
{rentabilidad:.1f}%
</td>

<td>
—
</td>

<td>
—
</td>

<td>
—
</td>

</tr>

</tbody>

</table>

</div>
"""

    st.html(
        table_html
    )


# ============================================================
# COLUMNA DERECHA
# ============================================================

with right_col:

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    st.markdown(
        """
<div class="summary-title">
Resumen del período
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="summary-card">

<div class="summary-label">
INGRESOS
</div>

<div class="summary-value">
{dinero_corto(ingresos)}
</div>

<div class="summary-sub">
Ingresos registrados
</div>

</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="summary-card expense">

<div class="summary-label">
GASTOS
</div>

<div class="summary-value">
{dinero_corto(gastos)}
</div>

<div class="summary-sub">
Egresos registrados
</div>

</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="summary-card flow">

<div class="summary-label">
FLUJO
</div>

<div class="summary-value">
{dinero_corto(flujo)}
</div>

<div class="summary-sub">
Ingresos − gastos
</div>

</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
<div class="summary-card profit">

<div class="summary-label">
RENTABILIDAD
</div>

<div class="summary-value">
{rentabilidad:.1f}%
</div>

<div class="summary-sub">
Objetivo: 35%
</div>

</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # GRÁFICO INGRESOS
    # --------------------------------------------------------

    st.markdown(
        """
<div class="chart-card">

<div class="chart-title">
Ingresos mensuales 2026
</div>

<div class="chart-subtitle">
Evolución de ingresos Airbnb
</div>
""",
        unsafe_allow_html=True
    )


    chart_data = (
        df_ytd
        .assign(
            MesNumero=df_ytd["Fecha"].dt.month,
            Mes=df_ytd["Fecha"].dt.strftime("%b")
        )
        .groupby(
            ["MesNumero", "Mes"],
            as_index=False
        )["Ingreso"]
        .sum()
        .sort_values("MesNumero")
    )

    max_chart = (
        chart_data["Ingreso"].max()
        if not chart_data.empty
        else 1
    )

    chart_html = """
<div class="bar-chart">
"""

    for _, r in chart_data.iterrows():

        height = (
            max(
                4,
                int(
                    r["Ingreso"] /
                    max_chart *
                    105
                )
            )
            if max_chart > 0
            else 4
        )

        chart_html += f"""
<div class="bar-wrapper">

<div
class="bar"
style="height:{height}px;"
title="{dinero(r["Ingreso"])}">
</div>

</div>
"""

    chart_html += """
</div>
"""

    st.markdown(
        chart_html,
        unsafe_allow_html=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    ranking = (
        df_ytd
        .groupby("Nombre_Propiedad")["Ingreso"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(6)
    )

    max_rank = (
        ranking.max()
        if not ranking.empty
        else 1
    )


    ranking_html = """
<div class="chart-card">

<div class="chart-title">
Top 6 por ingreso
</div>

<div class="chart-subtitle">
Ingresos acumulados 2026
</div>
"""

    for name, value in ranking.items():

        width = (
            value /
            max_rank *
            100
            if max_rank > 0
            else 0
        )

        ranking_html += f"""
<div class="rank-row">

<div class="rank-name">
{name}
</div>

<div class="rank-background">

<div
class="rank-bar"
style="width:{width:.1f}%;">
</div>

</div>

<div class="rank-value">
{dinero_corto(value)}
</div>

</div>
"""

    ranking_html += """
</div>
"""

    st.markdown(
        ranking_html,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    mejor_rentabilidad = (
        resumen.loc[
            resumen["Rentabilidad"].idxmax()
        ]
        if not resumen.empty
        else None
    )

    peor_rentabilidad = (
        resumen.loc[
            resumen["Rentabilidad"].idxmin()
        ]
        if not resumen.empty
        else None
    )

    mayor_ingreso = (
        resumen.loc[
            resumen["Ingresos"].idxmax()
        ]
        if not resumen.empty
        else None
    )


    insights_html = """
<div class="chart-card">

<div class="chart-title">
💡 Insights clave
</div>
"""


    if mejor_rentabilidad is not None:

        insights_html += f"""
<div class="insight">

<div
class="insight-dot"
style="background:#00B486;">
</div>

<div class="insight-text">
<b>{mejor_rentabilidad["Nombre_Propiedad"]}</b>
lidera la rentabilidad con
<b>{mejor_rentabilidad["Rentabilidad"]:.1f}%</b>.
</div>

</div>
"""


    if mayor_ingreso is not None:

        insights_html += f"""
<div class="insight">

<div
class="insight-dot"
style="background:#8067E8;">
</div>

<div class="insight-text">
<b>{mayor_ingreso["Nombre_Propiedad"]}</b>
registra el mayor ingreso del período:
<b>{dinero_corto(mayor_ingreso["Ingresos"])}</b>.
</div>

</div>
"""


    if peor_rentabilidad is not None:

        insights_html += f"""
<div class="insight">

<div
class="insight-dot"
style="background:#F0443A;">
</div>

<div class="insight-text">
<b>{peor_rentabilidad["Nombre_Propiedad"]}</b>
presenta la rentabilidad más baja:
<b>{peor_rentabilidad["Rentabilidad"]:.1f}%</b>.
</div>

</div>
"""


    if rentabilidad >= 35:

        insights_html += """
<div class="insight">

<div
class="insight-dot"
style="background:#00B486;">
</div>

<div class="insight-text">
La rentabilidad del período está
<b>sobre el objetivo del 35%</b>.
</div>

</div>
"""

    else:

        insights_html += """
<div class="insight">

<div
class="insight-dot"
style="background:#F0443A;">
</div>

<div class="insight-text">
La rentabilidad del período está
<b>por debajo del objetivo del 35%</b>.
</div>

</div>
"""


    insights_html += """
</div>
"""

    st.markdown(
        insights_html,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # ESPACIO FUTURA PROPIEDAD
    # --------------------------------------------------------

    st.markdown(
        """
<div class="add-card">

<div class="add-plus">
+
</div>

<div class="add-title">
Agregar propiedad
</div>

<div class="add-sub">
Nuevas oportunidades de inversión
</div>

</div>
""",
        unsafe_allow_html=True
    )
