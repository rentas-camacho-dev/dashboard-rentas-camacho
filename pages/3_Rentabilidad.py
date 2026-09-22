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
    padding-top: 2.4rem !important;
    padding-bottom: 2rem !important;
    max-width: 1550px !important;
}

#MainMenu,
footer {
    visibility: hidden;
}


/* ============================================================
   HEADER
   ============================================================ */

.header {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 18px;
    padding: 14px 16px;
    box-shadow: 0 4px 15px rgba(20,47,89,.04);
    margin-bottom: 12px;
}

.logo {
    width: 55px;
    height: 55px;
    border-radius: 14px;
    background: #FF1F4B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 29px;
}

.brand {
    font-size: 23px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.05;
}

.brand-pink {
    color: #FF3155;
}

.subtitle {
    font-size: 9px;
    color: #8290A4;
    margin-top: 4px;
}

.header-kpi {
    height: 65px;
    background: #F7F9FC;
    border: 1px solid #E1E7EE;
    border-radius: 11px;
    padding: 8px 11px;
    box-sizing: border-box;
}

.header-label {
    font-size: 7px;
    font-weight: 750;
    color: #8492A7;
}

.header-value {
    font-size: 16px;
    font-weight: 850;
    color: #17345E;
    margin-top: 5px;
}

.header-value.green {
    color: #009B70;
}

.header-value.red {
    color: #E83D32;
}


/* ============================================================
   NAVEGACIÓN
   ============================================================ */

.navbar {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 12px;
    padding: 5px;
    margin-bottom: 12px;
}

.nav-info {
    font-size: 9px;
    color: #8190A5;
    padding: 7px 9px;
}

div.stButton > button {
    border: none;
    border-radius: 8px;
    background: transparent;
    color: #687991;
    font-size: 9px;
    font-weight: 650;
    padding: 7px 10px;
}

div.stButton > button:hover {
    background: #FFF0F3;
    color: #FF3155;
}


/* ============================================================
   FILTROS
   ============================================================ */

.filter-card {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 13px;
    padding: 8px 11px 3px;
    margin-bottom: 13px;
}

.filter-label {
    font-size: 8px;
    color: #74849B;
    font-weight: 750;
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
   TÍTULOS
   ============================================================ */

.page-title {
    font-size: 21px;
    font-weight: 850;
    color: #15345E;
    line-height: 1.1;
}

.page-subtitle {
    font-size: 9px;
    color: #8190A5;
    margin-top: 4px;
    margin-bottom: 10px;
}


/* ============================================================
   KPI RESUMEN
   ============================================================ */

.kpi-row {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 8px;
    margin-bottom: 11px;
}

.kpi {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 11px;
    padding: 9px 11px;
    height: 70px;
    box-sizing: border-box;
}

.kpi-label {
    font-size: 7px;
    color: #8290A4;
    font-weight: 750;
}

.kpi-value {
    font-size: 19px;
    font-weight: 850;
    color: #17345E;
    margin-top: 4px;
}

.kpi-value.green {
    color: #009B70;
}

.kpi-value.red {
    color: #E83D32;
}

.kpi-sub {
    font-size: 6.5px;
    color: #8D99A9;
    margin-top: 2px;
}


/* ============================================================
   PORTAFOLIO
   ============================================================ */

.portfolio-card {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 14px;
    overflow: hidden;
}

.portfolio-header {
    display: grid;
    grid-template-columns: 2.1fr 1fr 1fr 1fr .85fr .85fr;
    gap: 8px;
    padding: 9px 13px;
    background: #F7F9FB;
    border-bottom: 1px solid #E7ECF1;
}

.portfolio-header div {
    font-size: 7px;
    color: #8492A6;
    font-weight: 750;
}

.property-row {
    display: grid;
    grid-template-columns: 2.1fr 1fr 1fr 1fr .85fr .85fr;
    gap: 8px;
    min-height: 62px;
    align-items: center;
    padding: 7px 13px;
    border-bottom: 1px solid #EEF2F5;
}

.property-row:last-child {
    border-bottom: none;
}

.property-row:hover {
    background: #FAFBFD;
}

.property-name {
    font-size: 10px;
    color: #17345E;
    font-weight: 800;
}

.property-city {
    font-size: 7px;
    color: #8996A8;
    margin-top: 3px;
}

.metric-label {
    font-size: 6.5px;
    color: #8A98AA;
    margin-bottom: 3px;
}

.metric-value {
    font-size: 10px;
    font-weight: 800;
}

.metric-income {
    color: #009B70;
}

.metric-expense {
    color: #EF4035;
}

.metric-flow {
    color: #0878D2;
}

.metric-profit {
    font-size: 11px;
    font-weight: 850;
}

.metric-profit.good {
    color: #009B70;
}

.metric-profit.bad {
    color: #EF4035;
}

.metric-occupancy {
    font-size: 10px;
    font-weight: 800;
    color: #6D52E8;
}

.avg {
    font-size: 6px;
    color: #95A0AF;
    margin-top: 2px;
}

.row-progress {
    width: 100%;
    height: 4px;
    background: #E9EDF1;
    border-radius: 5px;
    margin-top: 5px;
    overflow: hidden;
}

.row-progress-fill {
    height: 100%;
    border-radius: 5px;
    background: #00AD7D;
}

.row-progress-fill.bad {
    background: #F04A40;
}


/* ============================================================
   PANEL DERECHA
   ============================================================ */

.side-panel {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 14px;
    padding: 11px;
    margin-bottom: 9px;
}

.side-title {
    font-size: 10px;
    font-weight: 850;
    color: #17345E;
}

.side-subtitle {
    font-size: 7px;
    color: #8A98AA;
    margin-top: 2px;
}

.side-number {
    font-size: 21px;
    font-weight: 850;
    color: #17345E;
    margin-top: 6px;
}

.side-number.green {
    color: #009B70;
}

.side-number.red {
    color: #E83D32;
}


/* ============================================================
   BARRAS
   ============================================================ */

.mini-chart {
    height: 125px;
    display: flex;
    align-items: flex-end;
    gap: 5px;
    margin-top: 10px;
}

.mini-bar-wrapper {
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
}

.mini-bar {
    width: 100%;
    max-width: 18px;
    background: #27B68D;
    border-radius: 3px 3px 0 0;
}

.mini-bar-label {
    font-size: 6px;
    color: #8795A8;
    margin-top: 3px;
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
    width: 66px;
    font-size: 6.5px;
    color: #64758D;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rank-bg {
    flex: 1;
    height: 7px;
    background: #EEF1F5;
    border-radius: 5px;
    overflow: hidden;
}

.rank-fill {
    height: 100%;
    background: #7965D9;
    border-radius: 5px;
}

.rank-value {
    width: 32px;
    text-align: right;
    font-size: 6.5px;
    color: #697A91;
}


/* ============================================================
   INSIGHTS
   ============================================================ */

.insight {
    display: flex;
    gap: 6px;
    margin-top: 7px;
}

.insight-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-top: 3px;
    flex-shrink: 0;
}

.insight-text {
    font-size: 7px;
    color: #63748C;
    line-height: 1.45;
}


/* ============================================================
   TABLA
   ============================================================ */

.table-card {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 13px;
    padding: 11px;
    margin-top: 10px;
}

.table-title {
    font-size: 10px;
    font-weight: 850;
    color: #17345E;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 7px;
}

.data-table th {
    font-size: 6.5px;
    color: #8592A5;
    padding: 6px;
    text-align: left;
    border-bottom: 1px solid #E8EDF2;
}

.data-table td {
    font-size: 7px;
    color: #596B83;
    padding: 6px;
    border-bottom: 1px solid #F0F3F6;
}

.data-table td.name {
    font-weight: 800;
    color: #17345E;
}

.green {
    color: #009B70 !important;
    font-weight: 750;
}

.red {
    color: #EF4035 !important;
    font-weight: 750;
}

.blue {
    color: #0878D2 !important;
    font-weight: 750;
}


/* ============================================================
   VISTAS SECUNDARIAS
   ============================================================ */

.detail-card {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 14px;
    padding: 13px;
    margin-bottom: 10px;
}

.detail-title {
    font-size: 18px;
    font-weight: 850;
    color: #17345E;
}

.detail-city {
    font-size: 8px;
    color: #7F8EA2;
    margin-top: 3px;
}

.detail-kpis {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 7px;
    margin-top: 12px;
}

.detail-kpi {
    background: #F6F8FA;
    border-radius: 8px;
    padding: 8px;
    height: 62px;
}

.detail-label {
    font-size: 6.5px;
    color: #8190A4;
}

.detail-value {
    font-size: 16px;
    font-weight: 850;
    margin-top: 5px;
}


/* ============================================================
   OCUPACIÓN
   ============================================================ */

.occupancy-card {
    background: white;
    border: 1px solid #DEE6EE;
    border-radius: 13px;
    padding: 11px;
    height: 105px;
}

.occupancy-label {
    font-size: 7px;
    color: #8190A4;
}

.occupancy-value {
    font-size: 25px;
    font-weight: 850;
    color: #6D52E8;
    margin-top: 4px;
}

.occupancy-progress {
    height: 7px;
    background: #E9EAF1;
    border-radius: 7px;
    margin-top: 7px;
    overflow: hidden;
}

.occupancy-fill {
    height: 100%;
    background: #7560E5;
    border-radius: 7px;
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
# FUNCIONES DE FORMATO
# ============================================================

def dinero_corto(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    if valor < 0:
        signo = "-"
        valor = abs(valor)
    else:
        signo = ""

    if valor >= 1_000_000:
        return f"{signo}${valor / 1_000_000:.1f}M"

    if valor >= 1_000:
        return f"{signo}${valor / 1_000:.0f}k"

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
    FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    WHERE LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
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

    for columna in [
        "Nombre_Propiedad",
        "Ciudad",
        "Nombre_Socio"
    ]:

        df[columna] = (
            df[columna]
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

        FROM `rentascamacho.rentas_cortas.Participaciones`

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

        FROM `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

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

    config = bigquery.QueryJobConfig(
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
        job_config=config
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
    flujo_ytd /
    ingresos_ytd *
    100
    if ingresos_ytd
    else 0
)


# ============================================================
# HEADER
# ============================================================

header = f"""
<div class="header">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div class="logo">
🏢
</div>

<div style="
width:250px;
flex-shrink:0;
">

<div class="brand">
Airbnb <span class="brand-pink">Financial Hub</span>
</div>

<div class="subtitle">
Rentabilidad financiera · Solo Airbnb
</div>

</div>

<div class="header-kpi" style="flex:1;">

<div class="header-label">
INGRESOS 2026
</div>

<div class="header-value">
{dinero_corto(ingresos_ytd)}
</div>

</div>

<div class="header-kpi" style="flex:1;">

<div class="header-label">
FLUJO 2026
</div>

<div class="header-value green">
{dinero_corto(flujo_ytd)}
</div>

</div>

<div class="header-kpi" style="flex:1;">

<div class="header-label">
RENTABILIDAD 2026
</div>

<div class="header-value {'green' if rentabilidad_ytd >= 35 else 'red'}">
{rentabilidad_ytd:.1f}%
</div>

</div>

<div class="header-kpi" style="flex:1;">

<div class="header-label">
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

monthly_header = (
    df_ytd
    .assign(
        Mes=df_ytd["Fecha"].dt.month
    )
    .groupby("Mes")["Ingreso"]
    .sum()
)

max_month = (
    monthly_header.max()
    if not monthly_header.empty
    else 1
)

for mes in range(
    1,
    hoy.month + 1
):

    valor = monthly_header.get(
        mes,
        0
    )

    altura = max(
        3,
        int(
            valor /
            max_month *
            25
        )
    )

    header += f"""
<div style="
width:7px;
height:{altura}px;
background:#27B68D;
border-radius:2px 2px 0 0;
"></div>
"""

header += """
</div>
</div>

<div class="header-kpi" style="flex:1;">

<div class="header-label">
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

prop_header = (
    df_ytd
    .groupby(
        "Nombre_Propiedad"
    )["Ingreso"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(6)
)

max_prop = (
    prop_header.max()
    if not prop_header.empty
    else 1
)

for valor in prop_header.values:

    altura = max(
        3,
        int(
            valor /
            max_prop *
            25
        )
    )

    header += f"""
<div style="
width:7px;
height:{altura}px;
background:#7965D9;
border-radius:2px 2px 0 0;
"></div>
"""

header += """
</div>
</div>

</div>
</div>
"""

st.markdown(
    header,
    unsafe_allow_html=True
)


# ============================================================
# NAVEGACIÓN HORIZONTAL
# ============================================================

if "vista_airbnb" not in st.session_state:
    st.session_state.vista_airbnb = "Resumen"


st.markdown(
    '<div class="navbar">',
    unsafe_allow_html=True
)

nav1, nav2, nav3, nav4, nav5 = st.columns(
    [2.5, 1.3, 1.3, 1.3, 1.3]
)

with nav1:

    st.markdown(
        """
<div class="nav-info">
<b>Airbnb Financial Hub</b> · análisis del portafolio
</div>
""",
        unsafe_allow_html=True
    )

with nav2:

    if st.button(
        "🏠 Resumen",
        key="nav_resumen",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Resumen"
        st.rerun()

with nav3:

    if st.button(
        "🏢 Propiedades",
        key="nav_propiedades",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Propiedades"
        st.rerun()

with nav4:

    if st.button(
        "💰 Financiero",
        key="nav_financiero",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Financiero"
        st.rerun()

with nav5:

    if st.button(
        "📊 Ocupación",
        key="nav_ocupacion",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Ocupación"
        st.rerun()

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="filter-card">',
    unsafe_allow_html=True
)

f1, f2, f3, f4 = st.columns(
    [1, 1, 1, 1.25]
)

with f1:

    st.markdown(
        '<div class="filter-label">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] +
        sorted(
            df["Ciudad"].unique()
        ),
        label_visibility="collapsed"
    )

with f2:

    st.markdown(
        '<div class="filter-label">🏢 Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] +
        sorted(
            df["Nombre_Propiedad"].unique()
        ),
        label_visibility="collapsed"
    )

with f3:

    st.markdown(
        '<div class="filter-label">👥 Socio</div>',
        unsafe_allow_html=True
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] +
        sorted(
            df["Nombre_Socio"].unique()
        ),
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

    df_ocupacion = pd.DataFrame()


if not df_ocupacion.empty:

    df_ocupacion["Ocupacion"] = (
        df_ocupacion["Noches_Reservadas"] /
        df_ocupacion["Noches_Disponibles"] *
        100
    )

else:

    df_ocupacion = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas",
            "Noches_Disponibles",
            "Ocupacion"
        ]
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
# CONTENIDO PRINCIPAL
# ============================================================

vista = st.session_state.vista_airbnb


# ============================================================
# RESUMEN
# ============================================================

if vista == "Resumen":

    st.markdown(
        """
<div class="page-title">
🏢 Tu portafolio
</div>

<div class="page-subtitle">
Visión consolidada de las propiedades Airbnb.
</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    st.markdown(
        f"""
<div class="kpi-row">

<div class="kpi">

<div class="kpi-label">
INGRESOS
</div>

<div class="kpi-value">
{dinero_corto(ingresos)}
</div>

<div class="kpi-sub">
Período seleccionado
</div>

</div>


<div class="kpi">

<div class="kpi-label">
GASTOS
</div>

<div class="kpi-value">
{dinero_corto(gastos)}
</div>

<div class="kpi-sub">
Egresos registrados
</div>

</div>


<div class="kpi">

<div class="kpi-label">
FLUJO
</div>

<div class="kpi-value green">
{dinero_corto(flujo)}
</div>

<div class="kpi-sub">
Ingresos − gastos
</div>

</div>


<div class="kpi">

<div class="kpi-label">
RENTABILIDAD
</div>

<div class="kpi-value {'green' if rentabilidad >= 35 else 'red'}">
{rentabilidad:.1f}%
</div>

<div class="kpi-sub">
Objetivo: 35%
</div>

</div>

</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DOS COLUMNAS
    # --------------------------------------------------------

    left, right = st.columns(
        [3.15, 1],
        gap="small"
    )


    # ========================================================
    # MATRIZ DE PROPIEDADES
    # ========================================================

    with left:

        st.markdown(
            """
<div class="portfolio-card">

<div class="portfolio-header">

<div>PROPIEDAD</div>
<div>INGRESOS</div>
<div>GASTOS</div>
<div>FLUJO</div>
<div>RENTABILIDAD</div>
<div>OCUPACIÓN</div>

</div>
""",
            unsafe_allow_html=True
        )


        for _, row in resumen.iterrows():

            rent = float(
                row["Rentabilidad"]
            )

            positiva = rent >= 35

            ocup = row.get(
                "Ocupacion",
                None
            )

            ocup_txt = (
                "—"
                if pd.isna(ocup)
                else f"{float(ocup):.1f}%"
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


            row_html = f"""
<div class="property-row">

<div>

<div class="property-name">
🏢 {row["Nombre_Propiedad"]}
</div>

<div class="property-city">
📍 {row["Ciudad"]}
</div>

</div>


<div>

<div class="metric-label">
INGRESOS
</div>

<div class="metric-value metric-income">
{dinero_corto(row["Ingresos"])}
</div>

<div class="avg">
{dinero_corto(income_avg)}/mes
</div>

</div>


<div>

<div class="metric-label">
GASTOS
</div>

<div class="metric-value metric-expense">
{dinero_corto(row["Gastos"])}
</div>

<div class="avg">
{dinero_corto(expense_avg)}/mes
</div>

</div>


<div>

<div class="metric-label">
FLUJO
</div>

<div class="metric-value metric-flow">
{dinero_corto(row["Flujo"])}
</div>

<div class="avg">
{dinero_corto(flow_avg)}/mes
</div>

</div>


<div>

<div class="metric-profit {'good' if positiva else 'bad'}">
{rent:.1f}%
</div>

<div class="row-progress">

<div
class="row-progress-fill {'bad' if not positiva else ''}"
style="width:{progress:.1f}%;">
</div>

</div>

</div>


<div>

<div class="metric-occupancy">
{ocup_txt}
</div>

<div class="avg">
"""

            reservas = row.get(
                "Reservas",
                None
            )

            noches = row.get(
                "Noches_Reservadas",
                None
            )

            if pd.isna(reservas):

                row_html += "Sin datos"

            else:

                row_html += (
                    f"{int(reservas)} reservas · "
                    f"{int(noches)} noches"
                )

            row_html += """
</div>

</div>

</div>
"""

            st.markdown(
                row_html,
                unsafe_allow_html=True
            )


        # TOTAL

        st.markdown(
            f"""
<div class="property-row"
style="
background:#F8FAFC;
font-weight:800;
">

<div>

<div class="property-name">
TOTAL PORTAFOLIO
</div>

<div class="property-city">
Airbnb
</div>

</div>

<div class="metric-value metric-income">
{dinero_corto(ingresos)}
</div>

<div class="metric-value metric-expense">
{dinero_corto(gastos)}
</div>

<div class="metric-value metric-flow">
{dinero_corto(flujo)}
</div>

<div class="metric-profit {'good' if rentabilidad >= 35 else 'bad'}">
{rentabilidad:.1f}%
</div>

<div class="metric-occupancy">
—
</div>

</div>

</div>
""",
            unsafe_allow_html=True
        )


    # ========================================================
    # PANEL DERECHO
    # ========================================================

    with right:

        # ----------------------------------------------------
        # INGRESOS
        # ----------------------------------------------------

        st.markdown(
            f"""
<div class="side-panel">

<div class="side-title">
Ingresos del período
</div>

<div class="side-subtitle">
Total Airbnb
</div>

<div class="side-number">
{dinero_corto(ingresos)}
</div>

</div>
""",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # FLUJO
        # ----------------------------------------------------

        st.markdown(
            f"""
<div class="side-panel">

<div class="side-title">
Flujo
</div>

<div class="side-subtitle">
Ingresos − gastos
</div>

<div class="side-number green">
{dinero_corto(flujo)}
</div>

</div>
""",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # RENTABILIDAD
        # ----------------------------------------------------

        st.markdown(
            f"""
<div class="side-panel">

<div class="side-title">
Rentabilidad
</div>

<div class="side-subtitle">
Objetivo 35%
</div>

<div class="side-number {'green' if rentabilidad >= 35 else 'red'}">
{rentabilidad:.1f}%
</div>

</div>
""",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # GRÁFICO MENSUAL
        # ----------------------------------------------------

        monthly = (
            df_ytd
            .assign(
                MesNum=df_ytd["Fecha"].dt.month,
                Mes=df_ytd["Fecha"].dt.strftime("%b")
            )
            .groupby(
                ["MesNum", "Mes"],
                as_index=False
            )["Ingreso"]
            .sum()
            .sort_values("MesNum")
        )

        max_month = (
            monthly["Ingreso"].max()
            if not monthly.empty
            else 1
        )


        chart_html = """
<div class="side-panel">

<div class="side-title">
Ingresos mensuales 2026
</div>

<div class="side-subtitle">
Evolución acumulada
</div>

<div class="mini-chart">
"""


        for _, r in monthly.iterrows():

            altura = max(
                4,
                int(
                    r["Ingreso"] /
                    max_month *
                    100
                )
            )

            chart_html += f"""
<div class="mini-bar-wrapper">

<div
class="mini-bar"
style="height:{altura}px;">
</div>

<div class="mini-bar-label">
{r["Mes"]}
</div>

</div>
"""


        chart_html += """
</div>
</div>
"""

        st.markdown(
            chart_html,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # TOP PROPIEDADES
        # ----------------------------------------------------

        ranking = (
            resumen
            .sort_values(
                "Ingresos",
                ascending=False
            )
            .head(5)
        )

        max_rank = (
            ranking["Ingresos"].max()
            if not ranking.empty
            else 1
        )


        rank_html = """
<div class="side-panel">

<div class="side-title">
Top propiedades
</div>

<div class="side-subtitle">
Por ingresos del período
</div>
"""


        for _, r in ranking.iterrows():

            width = (
                r["Ingresos"] /
                max_rank *
                100
                if max_rank
                else 0
            )

            rank_html += f"""
<div class="rank-row">

<div class="rank-name">
{r["Nombre_Propiedad"]}
</div>

<div class="rank-bg">

<div
class="rank-fill"
style="width:{width:.1f}%;">
</div>

</div>

<div class="rank-value">
{dinero_corto(r["Ingresos"])}
</div>

</div>
"""


        rank_html += """
</div>
"""

        st.markdown(
            rank_html,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # INSIGHTS
        # ----------------------------------------------------

        if not resumen.empty:

            mejor = resumen.loc[
                resumen["Rentabilidad"].idxmax()
            ]

            peor = resumen.loc[
                resumen["Rentabilidad"].idxmin()
            ]

            mayor = resumen.loc[
                resumen["Ingresos"].idxmax()
            ]


            insights = f"""
<div class="side-panel">

<div class="side-title">
💡 Insights
</div>

<div class="insight">

<div
class="insight-dot"
style="background:#00B486;">
</div>

<div class="insight-text">
<b>{mejor["Nombre_Propiedad"]}</b>
lidera rentabilidad con
<b>{mejor["Rentabilidad"]:.1f}%</b>.
</div>

</div>


<div class="insight">

<div
class="insight-dot"
style="background:#7965D9;">
</div>

<div class="insight-text">
<b>{mayor["Nombre_Propiedad"]}</b>
tiene el mayor ingreso:
<b>{dinero_corto(mayor["Ingresos"])}</b>.
</div>

</div>


<div class="insight">

<div
class="insight-dot"
style="background:#EF4035;">
</div>

<div class="insight-text">
<b>{peor["Nombre_Propiedad"]}</b>
presenta la menor rentabilidad:
<b>{peor["Rentabilidad"]:.1f}%</b>.
</div>

</div>

</div>
"""

            st.markdown(
                insights,
                unsafe_allow_html=True
            )


    # ========================================================
    # TABLA DETALLADA
    # ========================================================

    table_html = """
<div class="table-card">

<div class="table-title">
📋 Detalle del portafolio
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

<td>—</td>
<td>—</td>
<td>—</td>

</tr>

</tbody>
</table>
</div>
"""

    st.markdown(
        table_html,
        unsafe_allow_html=True
    )


# ============================================================
# PROPIEDADES
# ============================================================

elif vista == "Propiedades":

    st.markdown(
        """
<div class="page-title">
🏢 Propiedades
</div>

<div class="page-subtitle">
Análisis individual de cada propiedad del portafolio.
</div>
""",
        unsafe_allow_html=True
    )


    nombres = sorted(
        resumen["Nombre_Propiedad"]
        .unique()
    )


    if nombres:

        seleccion = st.selectbox(
            "Propiedad",
            nombres,
            label_visibility="collapsed"
        )


        row = resumen[
            resumen["Nombre_Propiedad"]
            == seleccion
        ].iloc[0]


        rent = float(
            row["Rentabilidad"]
        )


        st.markdown(
            f"""
<div class="detail-card">

<div class="detail-title">
🏢 {row["Nombre_Propiedad"]}
</div>

<div class="detail-city">
📍 {row["Ciudad"]}
</div>


<div class="detail-kpis">

<div class="detail-kpi">

<div class="detail-label">
INGRESOS
</div>

<div class="detail-value income">
{dinero_corto(row["Ingresos"])}
</div>

</div>


<div class="detail-kpi">

<div class="detail-label">
GASTOS
</div>

<div class="detail-value expense">
{dinero_corto(row["Gastos"])}
</div>

</div>


<div class="detail-kpi">

<div class="detail-label">
FLUJO
</div>

<div class="detail-value flow">
{dinero_corto(row["Flujo"])}
</div>

</div>


<div class="detail-kpi">

<div class="detail-label">
RENTABILIDAD
</div>

<div class="detail-value {'income' if rent >= 35 else 'expense'}">
{rent:.1f}%
</div>

</div>

</div>

</div>
""",
            unsafe_allow_html=True
        )


        p1, p2 = st.columns(2)


        with p1:

            ocup = row.get(
                "Ocupacion",
                None
            )

            ocup_txt = (
                "—"
                if pd.isna(ocup)
                else f"{float(ocup):.1f}%"
            )

            width = (
                0
                if pd.isna(ocup)
                else min(
                    max(float(ocup), 0),
                    100
                )
            )


            st.markdown(
                f"""
<div class="occupancy-card">

<div class="occupancy-label">
OCUPACIÓN AIRBNB
</div>

<div class="occupancy-value">
{ocup_txt}
</div>

<div class="occupancy-progress">

<div
class="occupancy-fill"
style="width:{width}%;"
>
</div>

</div>

</div>
""",
                unsafe_allow_html=True
            )


        with p2:

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


            st.markdown(
                f"""
<div class="occupancy-card">

<div class="occupancy-label">
ACTIVIDAD DEL PERÍODO
</div>

<div class="occupancy-value"
style="color:#17345E;">
{reservas_txt}
</div>

<div style="
font-size:7px;
color:#8190A4;
margin-top:4px;
">
reservas · {noches_txt} noches
</div>

</div>
""",
                unsafe_allow_html=True
            )


# ============================================================
# FINANCIERO
# ============================================================

elif vista == "Financiero":

    st.markdown(
        """
<div class="page-title">
💰 Financiero
</div>

<div class="page-subtitle">
Evolución mensual de ingresos, gastos y flujo.
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
        financiero["Fecha"].dt.strftime("%b")
    )


    mensual = (
        financiero
        .groupby(
            ["Mes_Num", "Mes"],
            as_index=False
        )
        .agg(
            Ingresos=("Ingreso", "sum"),
            Gastos=("Gasto", "sum")
        )
        .sort_values("Mes_Num")
    )


    mensual["Flujo"] = (
        mensual["Ingresos"] -
        mensual["Gastos"]
    )


    max_val = max(
        mensual["Ingresos"].max(),
        mensual["Gastos"].max(),
        1
    )


    st.markdown(
        """
<div class="side-panel">

<div class="side-title">
Ingresos vs gastos
</div>

<div class="side-subtitle">
Evolución mensual 2026
</div>

<div class="mini-chart">
""",
        unsafe_allow_html=True
    )


    chart_html = ""

    for _, row in mensual.iterrows():

        hi = max(
            4,
            int(
                row["Ingresos"] /
                max_val *
                100
            )
        )

        hg = max(
            4,
            int(
                row["Gastos"] /
                max_val *
                100
            )
        )


        chart_html += f"""
<div class="mini-bar-wrapper">

<div style="
display:flex;
align-items:flex-end;
gap:2px;
height:105px;
">

<div
style="
width:11px;
height:{hi}px;
background:#27B68D;
border-radius:3px 3px 0 0;
">
</div>

<div
style="
width:11px;
height:{hg}px;
background:#FF766C;
border-radius:3px 3px 0 0;
">
</div>

</div>

<div class="mini-bar-label">
{row["Mes"]}
</div>

</div>
"""


    st.markdown(
        chart_html +
        """
</div>
</div>
""",
        unsafe_allow_html=True
    )


    # TABLA

    tabla = """
<div class="table-card">

<div class="table-title">
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


    for _, row in mensual.iterrows():

        rent_m = (
            row["Flujo"] /
            row["Ingresos"] *
            100
            if row["Ingresos"]
            else 0
        )


        tabla += f"""
<tr>

<td class="name">
{row["Mes"]}
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

<td class="{'green' if rent_m >= 0 else 'red'}">
{rent_m:.1f}%
</td>

</tr>
"""


    tabla += """
</tbody>
</table>
</div>
"""


    st.markdown(
        tabla,
        unsafe_allow_html=True
    )


# ============================================================
# OCUPACIÓN
# ============================================================

elif vista == "Ocupación":

    st.markdown(
        """
<div class="page-title">
📊 Ocupación
</div>

<div class="page-subtitle">
Reservas y utilización de las noches disponibles.
</div>
""",
        unsafe_allow_html=True
    )


    try:

        ocupacion = cargar_reservas(
            fecha_inicio,
            fecha_fin
        )

    except Exception:

        ocupacion = pd.DataFrame()


    if ocupacion.empty:

        st.info(
            "No hay información de reservas para el período seleccionado."
        )

    else:

        ocupacion["Ocupacion"] = (
            ocupacion["Noches_Reservadas"] /
            ocupacion["Noches_Disponibles"] *
            100
        )


        noches_reservadas = (
            ocupacion["Noches_Reservadas"].sum()
        )

        noches_disponibles = (
            ocupacion["Noches_Disponibles"].sum()
        )

        reservas_total = (
            ocupacion["Reservas"].sum()
        )

        ocupacion_total = (
            noches_reservadas /
            noches_disponibles *
            100
            if noches_disponibles
            else 0
        )


        o1, o2, o3 = st.columns(3)


        with o1:

            st.markdown(
                f"""
<div class="occupancy-card">

<div class="occupancy-label">
OCUPACIÓN PORTAFOLIO
</div>

<div class="occupancy-value">
{ocupacion_total:.1f}%
</div>

<div class="occupancy-progress">

<div
class="occupancy-fill"
style="width:{min(ocupacion_total,100):.1f}%;">
</div>

</div>

</div>
""",
                unsafe_allow_html=True
            )


        with o2:

            st.markdown(
                f"""
<div class="occupancy-card">

<div class="occupancy-label">
RESERVAS
</div>

<div class="occupancy-value"
style="color:#17345E;">
{int(reservas_total)}
</div>

<div style="
font-size:7px;
color:#8190A4;
margin-top:3px;
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
<div class="occupancy-card">

<div class="occupancy-label">
NOCHES RESERVADAS
</div>

<div class="occupancy-value"
style="color:#17345E;">
{int(noches_reservadas)}
</div>

<div style="
font-size:7px;
color:#8190A4;
margin-top:3px;
">
De {int(noches_disponibles)} disponibles
</div>

</div>
""",
                unsafe_allow_html=True
            )


        # RANKING

        ocupacion = ocupacion.sort_values(
            "Ocupacion",
            ascending=False
        )


        ranking_html = """
<div class="side-panel"
style="margin-top:10px;">

<div class="side-title">
Ocupación por propiedad
</div>

<div class="side-subtitle">
Noches reservadas / noches disponibles
</div>
"""


        for _, row in ocupacion.iterrows():

            width = min(
                max(
                    float(row["Ocupacion"]),
                    0
                ),
                100
            )


            ranking_html += f"""
<div class="rank-row">

<div class="rank-name">
{row["Nombre_Propiedad"]}
</div>

<div class="rank-bg">

<div
class="rank-fill"
style="width:{width:.1f}%;">
</div>

</div>

<div class="rank-value">
{float(row["Ocupacion"]):.1f}%
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


        # TABLA

        tabla = """
<div class="table-card">

<div class="table-title">
Detalle de ocupación
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


        for _, row in ocupacion.iterrows():

            tabla += f"""
<tr>

<td class="name">
{row["Nombre_Propiedad"]}
</td>

<td>
{row["Ciudad"]}
</td>

<td style="
color:#6D52E8;
font-weight:750;
">
{float(row["Ocupacion"]):.1f}%
</td>

<td>
{int(row["Reservas"])}
</td>

<td>
{int(row["Noches_Reservadas"])}
</td>

<td>
{int(row["Noches_Disponibles"])}
</td>

</tr>
"""


        tabla += """
</tbody>
</table>
</div>
"""


        st.markdown(
            tabla,
            unsafe_allow_html=True
        )
