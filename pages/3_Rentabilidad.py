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
    padding-top: 2.6rem !important;
    padding-bottom: 1.5rem !important;
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
    box-shadow: 0 4px 14px rgba(25,47,85,0.045);
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
   HEADER KPI
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


/* ============================================================
   FILTROS
   ============================================================ */

.filter-panel {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 14px;
    padding: 8px 12px 3px 12px;
    margin-bottom: 13px;
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
   MENÚ
   ============================================================ */

.menu-card {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 14px;
    padding: 9px;
    box-shadow: 0 3px 12px rgba(25,47,85,0.03);
}

.menu-title {
    font-size: 11px;
    font-weight: 850;
    color: #17335D;
    padding: 5px 7px 8px 7px;
}

.menu-description {
    font-size: 7px;
    color: #8A98AA;
    padding: 0 7px 8px 7px;
    line-height: 1.4;
}

.menu-footer {
    font-size: 7px;
    color: #9AA6B6;
    padding: 9px 7px 3px 7px;
    border-top: 1px solid #EDF1F5;
    margin-top: 6px;
}


/* ============================================================
   TÍTULOS
   ============================================================ */

.page-title {
    font-size: 21px;
    font-weight: 850;
    color: #142F59;
    line-height: 1.1;
}

.page-subtitle {
    font-size: 9px;
    color: #7A8BA3;
    margin-top: 4px;
}


/* ============================================================
   RESUMEN SUPERIOR
   ============================================================ */

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 7px;
    margin-top: 10px;
    margin-bottom: 11px;
}

.summary-box {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 11px;
    padding: 9px 11px;
    height: 72px;
    box-sizing: border-box;
}

.summary-label {
    font-size: 8px;
    font-weight: 700;
    color: #7B8BA1;
}

.summary-value {
    font-size: 19px;
    font-weight: 850;
    color: #17355F;
    margin-top: 4px;
}

.summary-value.green {
    color: #009B70;
}

.summary-value.red {
    color: #E83B32;
}

.summary-sub {
    font-size: 7px;
    color: #8A98AA;
    margin-top: 2px;
}


/* ============================================================
   PROPERTY CARDS
   ============================================================ */

.property-card {
    background: #FFFFFF;
    border: 1px solid #DDE5ED;
    border-radius: 14px;
    padding: 11px;
    height: 244px;
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

.property-name {
    font-size: 13px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.15;
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

.property-metrics {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 5px;
    margin-top: 11px;
}

.property-metric {
    background: #F5F8FA;
    border-radius: 7px;
    padding: 7px;
    height: 51px;
    box-sizing: border-box;
}

.property-metric-label {
    font-size: 7px;
    color: #7788A0;
}

.property-metric-value {
    font-size: 11px;
    font-weight: 850;
    margin-top: 4px;
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

.profit-line {
    display: flex;
    justify-content: space-between;
    margin-top: 9px;
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
    margin-top: 4px;
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

.occupancy {
    margin-top: 9px;
    height: 45px;
    background: #F5F7FB;
    border-radius: 8px;
    padding: 7px 8px;
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
   PANEL
   ============================================================ */

.panel {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 13px;
    padding: 11px;
    margin-bottom: 10px;
    box-sizing: border-box;
}

.panel-title {
    font-size: 11px;
    font-weight: 850;
    color: #17345E;
}

.panel-subtitle {
    font-size: 7px;
    color: #8492A6;
    margin-top: 2px;
}


/* ============================================================
   TABLA
   ============================================================ */

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
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
   GRÁFICOS
   ============================================================ */

.bar-chart {
    height: 145px;
    display: flex;
    align-items: flex-end;
    gap: 7px;
    margin-top: 12px;
    padding: 0 4px;
}

.bar-wrapper {
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
}

.bar {
    width: 100%;
    max-width: 25px;
    background: #24B58B;
    border-radius: 4px 4px 0 0;
}

.bar-label {
    font-size: 7px;
    color: #8997A9;
    margin-top: 4px;
}

.bar-value {
    font-size: 6px;
    color: #7D8CA0;
    margin-bottom: 2px;
}


/* ============================================================
   RANKING
   ============================================================ */

.rank-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 9px;
}

.rank-name {
    width: 75px;
    font-size: 7px;
    color: #5F718A;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rank-background {
    flex: 1;
    height: 8px;
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
    width: 36px;
    text-align: right;
    font-size: 7px;
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
   DETALLE PROPIEDAD
   ============================================================ */

.detail-header {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 14px;
    padding: 13px;
    margin-bottom: 10px;
}

.detail-name {
    font-size: 19px;
    font-weight: 850;
    color: #17345E;
}

.detail-city {
    font-size: 9px;
    color: #71829A;
    margin-top: 3px;
}

.detail-kpi {
    background: #F6F8FA;
    border-radius: 9px;
    padding: 9px;
    height: 70px;
    box-sizing: border-box;
}

.detail-kpi-label {
    font-size: 7px;
    color: #7A8AA1;
}

.detail-kpi-value {
    font-size: 18px;
    font-weight: 850;
    margin-top: 4px;
}


/* ============================================================
   OCUPACIÓN
   ============================================================ */

.occupancy-big {
    background: #FFFFFF;
    border: 1px solid #DFE6EE;
    border-radius: 13px;
    padding: 12px;
    height: 120px;
    box-sizing: border-box;
}

.occupancy-big-label {
    font-size: 8px;
    color: #71829A;
}

.occupancy-big-value {
    font-size: 28px;
    font-weight: 850;
    color: #6D52E8;
    margin-top: 4px;
}

.occupancy-bar-bg {
    height: 8px;
    background: #E8EAF1;
    border-radius: 8px;
    margin-top: 8px;
    overflow: hidden;
}

.occupancy-bar-fill {
    height: 100%;
    background: #7660E5;
    border-radius: 8px;
}


/* ============================================================
   BOTONES STREAMLIT
   ============================================================ */

div.stButton > button {
    width: 100%;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #64758D;
    font-size: 9px;
    text-align: left;
    padding: 8px 9px;
}

div.stButton > button:hover {
    background: #FFF1F4;
    color: #FF3155;
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

    for col in [
        "Nombre_Propiedad",
        "Ciudad",
        "Nombre_Socio"
    ]:

        df[col] = (
            df[col]
            .fillna("Sin información")
            .astype(str)
        )

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
# CARGA
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
# HEADER YTD
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
    flujo_ytd /
    ingresos_ytd *
    100
    if ingresos_ytd
    else 0
)


# ============================================================
# HEADER
# ============================================================

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
width:255px;
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

<div class="header-kpi-value {'green' if rentabilidad_ytd >= 35 else 'red'}">
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
height:27px;
margin-top:3px;
">
"""

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

for month in range(
    1,
    hoy.month + 1
):

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
                25
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
PROMEDIO PROPIEDAD
</div>

<div style="
display:flex;
align-items:flex-end;
gap:3px;
height:27px;
margin-top:3px;
">
"""

promedios_header = (
    df_ytd
    .groupby("Nombre_Propiedad")["Ingreso"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(6)
)

max_prom = (
    promedios_header.max()
    if not promedios_header.empty
    else 1
)

for value in promedios_header.values:

    height = max(
        3,
        int(
            value /
            max_prom *
            25
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
# FILTROS
# ============================================================

st.markdown(
    '<div class="filter-panel">',
    unsafe_allow_html=True
)

f1, f2, f3, f4 = st.columns(
    [1, 1, 1, 1.2]
)

with f1:

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

with f2:

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

with f3:

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

with f4:

    st.markdown(
        '<div class="filter-label">📅 Período de análisis</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Periodo",
        value=(
            inicio_mes,
            hoy
        ),
        label_visibility="collapsed"
    )

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FECHAS
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

flujo = ingresos - gastos

rentabilidad = (
    flujo /
    ingresos *
    100
    if ingresos
    else 0
)


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
# PROMEDIOS MENSUALES
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
].copy()

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
        df_ocupacion["Noches_Reservadas"] /
        df_ocupacion["Noches_Disponibles"] *
        100
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

resumen = resumen.sort_values(
    "Rentabilidad",
    ascending=False
).reset_index(drop=True)


# ============================================================
# ESTADO DE LA VISTA
# ============================================================

if "vista_airbnb" not in st.session_state:

    st.session_state.vista_airbnb = "Resumen"


# ============================================================
# LAYOUT
# ============================================================

menu_col, contenido_col = st.columns(
    [0.14, 0.86],
    gap="small"
)


# ============================================================
# MENÚ
# ============================================================

with menu_col:

    st.markdown(
        """
<div class="menu-card">

<div class="menu-title">
Airbnb Financial
</div>

<div class="menu-description">
Navega por el desempeño de tu portafolio.
</div>

</div>
""",
        unsafe_allow_html=True
    )


    opciones = [
        ("🏠", "Resumen"),
        ("🏢", "Propiedades"),
        ("💰", "Financiero"),
        ("📊", "Ocupación")
    ]


    for icono, nombre in opciones:

        if st.button(
            f"{icono}  {nombre}",
            key=f"menu_{nombre}",
            use_container_width=True
        ):

            st.session_state.vista_airbnb = nombre

            st.rerun()


    st.markdown(
        f"""
<div class="menu-footer">

<b>Airbnb solamente</b><br><br>

7 propiedades<br>
Información financiera<br>
Reservas Airbnb<br>
Ocupación

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# CONTENIDO
# ============================================================

with contenido_col:

    vista = st.session_state.vista_airbnb


    # ========================================================
    # VISTA RESUMEN
    # ========================================================

    if vista == "Resumen":

        st.markdown(
            """
<div class="page-title">
🏠 Tu portafolio
</div>

<div class="page-subtitle">
Vista general de rentabilidad, flujo y ocupación de las propiedades.
</div>
""",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # RESUMEN KPI
        # ----------------------------------------------------

        st.markdown(
            f"""
<div class="summary-grid">

<div class="summary-box">

<div class="summary-label">
INGRESOS
</div>

<div class="summary-value">
{dinero_corto(ingresos)}
</div>

<div class="summary-sub">
Período seleccionado
</div>

</div>


<div class="summary-box">

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


<div class="summary-box">

<div class="summary-label">
FLUJO
</div>

<div class="summary-value green">
{dinero_corto(flujo)}
</div>

<div class="summary-sub">
Ingresos − gastos
</div>

</div>


<div class="summary-box">

<div class="summary-label">
RENTABILIDAD
</div>

<div class="summary-value {'green' if rentabilidad >= 35 else 'red'}">
{rentabilidad:.1f}%
</div>

<div class="summary-sub">
Objetivo: 35%
</div>

</div>

</div>
""",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # PROPIEDADES
        # ----------------------------------------------------

        st.markdown(
            """
<div class="panel">

<div class="panel-title">
🏢 Desempeño por propiedad
</div>

<div class="panel-subtitle">
Cada tarjeta resume la situación financiera y ocupación.
</div>

</div>
""",
            unsafe_allow_html=True
        )


        for inicio in range(
            0,
            len(resumen),
            4
        ):

            fila = resumen.iloc[
                inicio:inicio + 4
            ]

            cols = st.columns(
                4,
                gap="small"
            )

            for col, (_, row) in zip(
                cols,
                fila.iterrows()
            ):

                rent = float(
                    row["Rentabilidad"]
                )

                positiva = rent >= 35

                ocup = row.get(
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

                ocup_txt = (
                    "—"
                    if pd.isna(ocup)
                    else f"{float(ocup):.1f}%"
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

                progress = min(
                    max(rent, 0),
                    100
                )


                card = f"""
<div class="property-card {'loss' if not positiva else ''}">

<div class="property-top">

<div>

<div class="property-name">
{row["Nombre_Propiedad"]}
</div>

<div class="property-city">
📍 {row["Ciudad"]}
</div>

</div>

<div>

<div class="property-profit {'loss' if not positiva else ''}">
{rent:.1f}%
</div>

<div class="property-year">
Rentabilidad
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
Objetivo 35%
</div>

<div
class="profit-line-value"
style="
color:{'#00A879' if positiva else '#EF3E32'};
">
{rent:.1f}%
</div>

</div>


<div class="progress-background">

<div
class="{'progress-positive' if positiva else 'progress-negative'}"
style="width:{progress:.1f}%;">
</div>

</div>


<div
style="
font-size:7px;
font-weight:700;
color:{'#009B70' if positiva else '#EF3E32'};
margin-top:4px;
">
{'✓ Sobre objetivo' if positiva else '⚠ Bajo objetivo'}
</div>


<div class="occupancy">

<div>

<div class="occupancy-label">
Ocupación Airbnb
</div>

<div class="occupancy-value">
{ocup_txt}
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

                    st.html(card)


            st.markdown(
                "<div style='height:7px'></div>",
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # TABLA
        # ----------------------------------------------------

        table = """
<div class="panel">

<div class="panel-title">
📋 Comparativo del portafolio
</div>

<table class="data-table">

<thead>

<tr>

<th>Propiedad</th>
<th>Ciudad</th>
<th>Ingresos</th>
<th>Gastos</th>
<th>Flujo</th>
<th>Rent.</th>
<th>Ocup.</th>
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

            ocup = row.get(
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

            ocup_txt = (
                "—"
                if pd.isna(ocup)
                else f"{float(ocup):.1f}%"
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

            table += f"""

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

<td class="blue">
{dinero_corto(row["Flujo"])}
</td>

<td class="{'green' if rent >= 0 else 'red'}">
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

        table += f"""

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

        st.html(table)


    # ========================================================
    # VISTA PROPIEDADES
    # ========================================================

    elif vista == "Propiedades":

        st.markdown(
            """
<div class="page-title">
🏢 Propiedades
</div>

<div class="page-subtitle">
Análisis detallado de cada activo del portafolio.
</div>
""",
            unsafe_allow_html=True
        )


        propiedad_detalle = st.selectbox(
            "Selecciona una propiedad",
            sorted(
                resumen["Nombre_Propiedad"]
                .unique()
            ),
            key="propiedad_detalle"
        )


        row = resumen[
            resumen["Nombre_Propiedad"]
            == propiedad_detalle
        ].iloc[0]


        rent = float(
            row["Rentabilidad"]
        )

        ocup = row.get(
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


        st.markdown(
            f"""
<div class="detail-header">

<div class="detail-name">
{row["Nombre_Propiedad"]}
</div>

<div class="detail-city">
📍 {row["Ciudad"]}
</div>

</div>
""",
            unsafe_allow_html=True
        )


        d1, d2, d3, d4 = st.columns(4)

        with d1:

            st.markdown(
                f"""
<div class="detail-kpi">

<div class="detail-kpi-label">
INGRESOS
</div>

<div class="detail-kpi-value income">
{dinero_corto(row["Ingresos"])}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        with d2:

            st.markdown(
                f"""
<div class="detail-kpi">

<div class="detail-kpi-label">
GASTOS
</div>

<div class="detail-kpi-value expense">
{dinero_corto(row["Gastos"])}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        with d3:

            st.markdown(
                f"""
<div class="detail-kpi">

<div class="detail-kpi-label">
FLUJO
</div>

<div class="detail-kpi-value flow">
{dinero_corto(row["Flujo"])}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        with d4:

            st.markdown(
                f"""
<div class="detail-kpi">

<div class="detail-kpi-label">
RENTABILIDAD
</div>

<div class="detail-kpi-value {'income' if rent >= 35 else 'expense'}">
{rent:.1f}%
</div>

</div>
""",
                unsafe_allow_html=True
            )


        st.markdown("<br>", unsafe_allow_html=True)


        left, right = st.columns(2)

        with left:

            ocup_txt = (
                "—"
                if pd.isna(ocup)
                else f"{float(ocup):.1f}%"
            )

            ocup_width = (
                0
                if pd.isna(ocup)
                else min(
                    max(float(ocup), 0),
                    100
                )
            )

            st.markdown(
                f"""
<div class="occupancy-big">

<div class="occupancy-big-label">
OCUPACIÓN AIRBNB
</div>

<div class="occupancy-big-value">
{ocup_txt}
</div>

<div class="occupancy-bar-bg">

<div
class="occupancy-bar-fill"
style="width:{ocup_width}%;"
>
</div>

</div>

</div>
""",
                unsafe_allow_html=True
            )


        with right:

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

            st.markdown(
                f"""
<div class="panel">

<div class="panel-title">
Reservas del período
</div>

<br>

<b>{reservas_txt}</b> reservas

<br><br>

<b>{noches_txt}</b> noches reservadas

</div>
""",
                unsafe_allow_html=True
            )


    # ========================================================
    # VISTA FINANCIERO
    # ========================================================

    elif vista == "Financiero":

        st.markdown(
            """
<div class="page-title">
💰 Financiero
</div>

<div class="page-subtitle">
Evolución mensual de ingresos, gastos y flujo del portafolio.
</div>
""",
            unsafe_allow_html=True
        )


        financiero = df[
            (df["Fecha"] >= inicio_anio) &
            (df["Fecha"] < fin_hoy)
        ].copy()

        financiero["Mes_Num"] = (
            financiero["Fecha"].dt.month
        )

        financiero["Mes"] = (
            financiero["Fecha"]
            .dt.strftime("%b")
        )


        mensual_fin = (
            financiero
            .groupby(
                [
                    "Mes_Num",
                    "Mes"
                ],
                as_index=False
            )
            .agg(
                Ingresos=("Ingreso", "sum"),
                Gastos=("Gasto", "sum")
            )
        )

        mensual_fin["Flujo"] = (
            mensual_fin["Ingresos"] -
            mensual_fin["Gastos"]
        )

        mensual_fin = mensual_fin.sort_values(
            "Mes_Num"
        )


        max_val = max(
            mensual_fin[
                "Ingresos"
            ].max(),
            mensual_fin[
                "Gastos"
            ].max(),
            1
        )


        st.markdown(
            """
<div class="panel">

<div class="panel-title">
Ingresos vs gastos por mes
</div>

<div class="panel-subtitle">
Valores acumulados mensuales de Airbnb.
</div>
""",
            unsafe_allow_html=True
        )


        chart = """
<div class="bar-chart">
"""


        for _, r in mensual_fin.iterrows():

            ingreso_h = max(
                4,
                int(
                    r["Ingresos"] /
                    max_val *
                    105
                )
            )

            gasto_h = max(
                4,
                int(
                    r["Gastos"] /
                    max_val *
                    105
                )
            )


            chart += f"""
<div class="bar-wrapper">

<div style="
display:flex;
align-items:flex-end;
gap:2px;
height:110px;
">

<div
class="bar"
style="
height:{ingreso_h}px;
background:#22B68D;
">
</div>

<div
class="bar"
style="
height:{gasto_h}px;
background:#FF7166;
">
</div>

</div>

<div class="bar-label">
{r["Mes"]}
</div>

</div>
"""


        chart += """
</div>

<div style="
display:flex;
gap:12px;
font-size:7px;
color:#7A8AA0;
margin-top:5px;
">

<span>
<span style="
display:inline-block;
width:7px;
height:7px;
background:#22B68D;
border-radius:2px;
"></span>
Ingresos
</span>

<span>
<span style="
display:inline-block;
width:7px;
height:7px;
background:#FF7166;
border-radius:2px;
"></span>
Gastos
</span>

</div>

</div>
"""

        st.html(chart)


        # ----------------------------------------------------
        # TABLA MENSUAL
        # ----------------------------------------------------

        monthly_table = """
<div class="panel">

<div class="panel-title">
Detalle mensual
</div>

<table class="data-table">

<thead>

<tr>
<th>Mes</th>
<th>Ingresos</th>
<th>Gastos</th>
<th>Flujo</th>
<th>Rentabilidad</th>
</tr>

</thead>

<tbody>
"""

        for _, r in mensual_fin.iterrows():

            rent_m = (
                r["Flujo"] /
                r["Ingresos"] *
                100
                if r["Ingresos"]
                else 0
            )

            monthly_table += f"""
<tr>

<td class="name">
{r["Mes"]}
</td>

<td class="green">
{dinero_corto(r["Ingresos"])}
</td>

<td class="red">
{dinero_corto(r["Gastos"])}
</td>

<td class="blue">
{dinero_corto(r["Flujo"])}
</td>

<td class="{'green' if rent_m >= 0 else 'red'}">
{rent_m:.1f}%
</td>

</tr>
"""

        monthly_table += """
</tbody>
</table>
</div>
"""

        st.html(monthly_table)


    # ========================================================
    # VISTA OCUPACIÓN
    # ========================================================

    elif vista == "Ocupación":

        st.markdown(
            """
<div class="page-title">
📊 Ocupación
</div>

<div class="page-subtitle">
Uso de las noches disponibles y actividad de reservas Airbnb.
</div>
""",
            unsafe_allow_html=True
        )


        try:

            ocupacion_view = cargar_reservas(
                fecha_inicio,
                fecha_fin
            )

        except Exception:

            ocupacion_view = pd.DataFrame()


        if ocupacion_view.empty:

            st.info(
                "No hay información de reservas para el período seleccionado."
            )

        else:

            ocupacion_view["Ocupacion"] = (
                ocupacion_view["Noches_Reservadas"]
                /
                ocupacion_view["Noches_Disponibles"]
                *
                100
            )


            # ------------------------------------------------
            # PROMEDIO PORTAFOLIO
            # ------------------------------------------------

            noches_reservadas = (
                ocupacion_view[
                    "Noches_Reservadas"
                ].sum()
            )

            noches_disponibles = (
                ocupacion_view[
                    "Noches_Disponibles"
                ].sum()
            )

            ocupacion_portafolio = (
                noches_reservadas /
                noches_disponibles *
                100
                if noches_disponibles
                else 0
            )

            reservas_total = (
                ocupacion_view[
                    "Reservas"
                ].sum()
            )


            o1, o2, o3 = st.columns(3)


            with o1:

                st.markdown(
                    f"""
<div class="occupancy-big">

<div class="occupancy-big-label">
OCUPACIÓN PORTAFOLIO
</div>

<div class="occupancy-big-value">
{ocupacion_portafolio:.1f}%
</div>

<div class="occupancy-bar-bg">

<div
class="occupancy-bar-fill"
style="
width:{min(ocupacion_portafolio,100):.1f}%;
">
</div>

</div>

</div>
""",
                    unsafe_allow_html=True
                )


            with o2:

                st.markdown(
                    f"""
<div class="occupancy-big">

<div class="occupancy-big-label">
RESERVAS
</div>

<div class="occupancy-big-value">
{int(reservas_total)}
</div>

<div style="
font-size:8px;
color:#7A8AA0;
margin-top:5px;
">
Período seleccionado
</div>

</div>
""",
                    unsafe_allow_html=True
                )


            with o3:

                st.markdown(
                    f"""
<div class="occupancy-big">

<div class="occupancy-big-label">
NOCHES RESERVADAS
</div>

<div class="occupancy-big-value">
{int(noches_reservadas)}
</div>

<div style="
font-size:8px;
color:#7A8AA0;
margin-top:5px;
">
De {int(noches_disponibles)} disponibles
</div>

</div>
""",
                    unsafe_allow_html=True
                )


            # ------------------------------------------------
            # RANKING OCUPACIÓN
            # ------------------------------------------------

            st.markdown(
                "<br>",
                unsafe_allow_html=True
            )


            ocupacion_view = ocupacion_view.sort_values(
                "Ocupacion",
                ascending=False
            )


            ranking_ocup = """
<div class="panel">

<div class="panel-title">
Ocupación por propiedad
</div>

<div class="panel-subtitle">
Comparación de noches reservadas frente a noches disponibles.
</div>
"""


            max_ocup = max(
                ocupacion_view[
                    "Ocupacion"
                ].max(),
                1
            )


            for _, r in ocupacion_view.iterrows():

                width = min(
                    max(
                        float(r["Ocupacion"]),
                        0
                    ),
                    100
                )

                ranking_ocup += f"""
<div class="rank-row">

<div class="rank-name">
{r["Nombre_Propiedad"]}
</div>

<div class="rank-background">

<div
class="rank-bar"
style="
width:{width:.1f}%;
background:#7560E5;
">
</div>

</div>

<div class="rank-value">
{float(r["Ocupacion"]):.1f}%
</div>

</div>
"""


            ranking_ocup += """
</div>
"""

            st.markdown(
                ranking_ocup,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # TABLA OCUPACIÓN
            # ------------------------------------------------

            tabla_ocup = """
<div class="panel">

<div class="panel-title">
Detalle de reservas
</div>

<table class="data-table">

<thead>

<tr>

<th>Propiedad</th>
<th>Ciudad</th>
<th>Ocupación</th>
<th>Reservas</th>
<th>Noches reservadas</th>
<th>Noches disponibles</th>

</tr>

</thead>

<tbody>
"""


            for _, r in ocupacion_view.iterrows():

                tabla_ocup += f"""
<tr>

<td class="name">
{r["Nombre_Propiedad"]}
</td>

<td>
{r["Ciudad"]}
</td>

<td style="
color:#6D52E8;
font-weight:750;
">
{float(r["Ocupacion"]):.1f}%
</td>

<td>
{int(r["Reservas"])}
</td>

<td>
{int(r["Noches_Reservadas"])}
</td>

<td>
{int(r["Noches_Disponibles"])}
</td>

</tr>
"""


            tabla_ocup += """
</tbody>
</table>
</div>
"""

            st.html(
                tabla_ocup
            )
