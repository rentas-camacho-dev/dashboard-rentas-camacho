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
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GENERAL
   ============================================================ */

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 0.8rem !important;
    padding-left: 3.0rem !important;
    padding-right: 3.0rem !important;
    max-width: 1800px !important;
}

.stApp {
    background: #F5F7F9;
}


/* Quitar espacios excesivos entre elementos de Streamlit */

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

div[data-testid="column"] {
    padding-left: 0.35rem;
    padding-right: 0.35rem;
}


/* ============================================================
   HEADER
   ============================================================ */

.dashboard-header {
    background: #FFFFFF;
    border: 1px solid #DDE4EC;
    border-radius: 22px;
    padding: 18px 22px;
    min-height: 112px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 5px 18px rgba(24, 48, 80, 0.05);
    margin-bottom: 10px;
}

.brand-area {
    display: flex;
    align-items: center;
    gap: 16px;
    min-width: 350px;
}

.brand-icon {
    width: 76px;
    height: 76px;
    background: #FF2450;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 43px;
    flex-shrink: 0;
}

.brand-title {
    font-size: 30px;
    line-height: 1.05;
    font-weight: 800;
    color: #172F56;
    white-space: nowrap;
}

.brand-title span {
    color: #FF3155;
}

.brand-subtitle {
    font-size: 14px;
    color: #71809A;
    margin-top: 7px;
}


/* ============================================================
   HEADER KPI
   ============================================================ */

.header-kpis {
    display: flex;
    gap: 12px;
    flex: 1;
}

.header-kpi {
    background: #F6F8FA;
    border: 1px solid #E0E6ED;
    border-radius: 15px;
    padding: 12px 15px;
    min-width: 145px;
    flex: 1;
}

.header-kpi-label {
    font-size: 11px;
    font-weight: 700;
    color: #8A97AA;
    text-transform: uppercase;
    margin-bottom: 7px;
}

.header-kpi-value {
    font-size: 21px;
    font-weight: 800;
    color: #19345C;
}

.header-kpi-value.green {
    color: #008F63;
}


/* ============================================================
   MINI GRÁFICOS
   ============================================================ */

.mini-chart-card {
    background: #F6F8FA;
    border: 1px solid #E0E6ED;
    border-radius: 15px;
    padding: 10px 13px;
    width: 180px;
    height: 80px;
    flex-shrink: 0;
}

.mini-chart-title {
    font-size: 10px;
    font-weight: 700;
    color: #7B899D;
    margin-bottom: 6px;
}

.mini-bars {
    height: 42px;
    display: flex;
    align-items: end;
    gap: 5px;
}

.mini-bar {
    flex: 1;
    min-width: 7px;
    border-radius: 3px 3px 0 0;
    background: #35B693;
}

.mini-bar-purple {
    background: #7661D9;
}

.mini-chart-footer {
    display: flex;
    justify-content: space-between;
    font-size: 8px;
    color: #9AA6B7;
    margin-top: 2px;
}


/* ============================================================
   FILTROS
   ============================================================ */

.filter-label {
    font-size: 13px;
    color: #71809A;
    margin-bottom: 3px;
    font-weight: 500;
}

div[data-baseweb="select"] > div {
    background-color: #F0F3F7;
    border: 1px solid transparent;
    border-radius: 10px;
    min-height: 42px;
}

div[data-baseweb="select"] > div:hover {
    border-color: #D5DDE7;
}


/* ============================================================
   KPI PRINCIPALES
   ============================================================ */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DDE4EC;
    border-radius: 18px;
    padding: 13px 20px;
    height: 112px;
    box-shadow: 0 5px 16px rgba(24, 48, 80, 0.045);
}

.kpi-title {
    font-size: 13px;
    font-weight: 700;
    color: #71809A;
    margin-bottom: 7px;
}

.kpi-value {
    font-size: 29px;
    line-height: 1;
    font-weight: 800;
    color: #19345C;
}

.kpi-value.green {
    color: #008F63;
}

.kpi-value.red {
    color: #E63B24;
}

.kpi-sub {
    font-size: 12px;
    color: #8B99AD;
    margin-top: 8px;
}


/* ============================================================
   TÍTULO DE SECCIÓN
   ============================================================ */

.section-title {
    font-size: 26px;
    font-weight: 800;
    color: #192F55;
    margin-top: 7px;
    margin-bottom: 0;
}

.section-subtitle {
    font-size: 13px;
    color: #71809A;
    margin-top: 2px;
    margin-bottom: 8px;
}


/* ============================================================
   TARJETAS DE PROPIEDAD
   ============================================================ */

.property-card {
    background: #FFFFFF;
    border: 1px solid #DDE4EC;
    border-radius: 21px;
    padding: 17px;
    box-shadow: 0 5px 16px rgba(24, 48, 80, 0.045);
    min-height: 425px;
    margin-bottom: 12px;
}

.property-card.bad {
    border: 1.5px solid #FF5A5F;
}

.property-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.property-name {
    font-size: 22px;
    font-weight: 800;
    color: #19345C;
}

.property-city {
    font-size: 13px;
    color: #71809A;
    margin-top: 5px;
}

.property-profit {
    text-align: right;
}

.property-profit-value {
    font-size: 20px;
    font-weight: 800;
}

.property-profit-value.good {
    color: #00A878;
}

.property-profit-value.bad {
    color: #FF4045;
}

.property-profit-year {
    font-size: 11px;
    color: #8795A9;
    margin-top: 4px;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 9px;
    margin-top: 4px;
}

.metric-box {
    background: #F5F7F9;
    border-radius: 15px;
    padding: 12px 11px;
}

.metric-label {
    font-size: 12px;
    color: #71809A;
    margin-bottom: 7px;
}

.metric-value {
    font-size: 17px;
    font-weight: 800;
    color: #009B6D;
}

.metric-value.expense {
    color: #FF3E28;
}

.metric-value.flow {
    color: #0074C8;
}

.metric-average {
    font-size: 11px;
    color: #8291A7;
    margin-top: 7px;
}


/* ============================================================
   RENTABILIDAD
   ============================================================ */

.profit-row {
    margin-top: 17px;
}

.profit-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    color: #71809A;
}

.profit-number {
    font-size: 21px;
    font-weight: 800;
}

.profit-number.good {
    color: #00A878;
}

.profit-number.bad {
    color: #FF4045;
}

.progress-bg {
    height: 10px;
    background: #E6EBF0;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 9px;
}

.progress-fill {
    height: 100%;
    border-radius: 20px;
    background: #00AE7C;
}

.progress-fill.bad {
    background: #FF4A4F;
}

.target-status {
    font-size: 12px;
    font-weight: 700;
    margin-top: 9px;
}

.target-status.good {
    color: #00A878;
}

.target-status.bad {
    color: #FF4045;
}


/* ============================================================
   OCUPACIÓN
   ============================================================ */

.occupancy-box {
    background: #F5F7F9;
    border-radius: 15px;
    padding: 12px 13px;
    margin-top: 15px;
}

.occupancy-title {
    font-size: 12px;
    color: #71809A;
}

.occupancy-value {
    font-size: 20px;
    font-weight: 800;
    color: #7659E8;
    margin-top: 5px;
}

.occupancy-detail {
    font-size: 11px;
    color: #8795A9;
    margin-top: 4px;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 1200px) {

    .brand-area {
        min-width: 280px;
    }

    .brand-title {
        font-size: 25px;
    }

    .mini-chart-card {
        width: 150px;
    }

}

</style>
""",
    unsafe_allow_html=True
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
# FUNCIONES
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

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Ingreso"] = pd.to_numeric(df["Ingreso"], errors="coerce").fillna(0)
    df["Gasto"] = pd.to_numeric(df["Gasto"], errors="coerce").fillna(0)

    return df


@st.cache_data(ttl=300)
def cargar_ocupacion():

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

    reservas AS (

        SELECT
            TRIM(C__digo_de_confirmaci__n) AS Codigo_Reserva,
            LOWER(TRIM(Anuncio)) AS anuncio_key,
            DATE(Fecha_de_inicio) AS Fecha_Inicio,
            DATE(Fecha_de_finalizaci__n) AS Fecha_Fin
        FROM
            `rentascamacho.rentas_cortas.Airbnb_Prorrateado`
        WHERE
            LOWER(TRIM(Tipo)) = 'reservación'
            AND C__digo_de_confirmaci__n IS NOT NULL
            AND Fecha_de_inicio IS NOT NULL
            AND Fecha_de_finalizaci__n IS NOT NULL

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY C__digo_de_confirmaci__n
            ORDER BY Fecha_de_inicio
        ) = 1
    )

    SELECT
        r.Codigo_Reserva,
        m.Nombre_Propiedad,
        m.Ciudad,
        r.Fecha_Inicio,
        r.Fecha_Fin
    FROM reservas r
    INNER JOIN mapa m
        ON r.anuncio_key = m.anuncio_key
    """

    df = client.query(query).to_dataframe()

    df["Fecha_Inicio"] = pd.to_datetime(
        df["Fecha_Inicio"],
        errors="coerce"
    )

    df["Fecha_Fin"] = pd.to_datetime(
        df["Fecha_Fin"],
        errors="coerce"
    )

    return df


def dinero(valor):

    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


def dinero_corto(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"${valor / 1_000:.0f}k"

    return f"${valor:,.0f}".replace(",", ".")


def porcentaje(valor):

    if pd.isna(valor):
        valor = 0

    return f"{valor:.1f}%"


# ============================================================
# CARGA DE DATOS
# ============================================================

df = cargar_datos_financieros()
df_ocupacion = cargar_ocupacion()


# ============================================================
# FECHAS
# ============================================================

hoy = date.today()

inicio_anio = pd.Timestamp(hoy.year, 1, 1)
fin_hoy = pd.Timestamp(hoy) + pd.Timedelta(days=1)

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
)

meses_cerrados = max(hoy.month - 1, 0)


# ============================================================
# HEADER - DATOS ANUALES
# ============================================================

df_ytd = df[
    (df["Fecha"] >= inicio_anio)
    &
    (df["Fecha"] < fin_hoy)
].copy()

ingreso_ytd = df_ytd["Ingreso"].sum()
gasto_ytd = df_ytd["Gasto"].sum()
flujo_ytd = ingreso_ytd - gasto_ytd

rentabilidad_ytd = (
    flujo_ytd / ingreso_ytd * 100
    if ingreso_ytd != 0
    else 0
)


# ============================================================
# MINI GRÁFICO INGRESOS MENSUALES
# ============================================================

df_mensual = df_ytd.copy()

if not df_mensual.empty:

    df_mensual["Mes"] = df_mensual["Fecha"].dt.month

    mensual = (
        df_mensual
        .groupby("Mes")["Ingreso"]
        .sum()
        .reindex(range(1, hoy.month + 1), fill_value=0)
    )

else:

    mensual = pd.Series(
        [0] * hoy.month,
        index=range(1, hoy.month + 1)
    )


max_mensual = max(mensual.max(), 1)

bars_ingreso = ""

for valor in mensual.values:

    altura = max(8, int((valor / max_mensual) * 38))

    bars_ingreso += f"""
        <div class="mini-bar"
             style="height:{altura}px;">
        </div>
    """


# ============================================================
# MINI GRÁFICO PROMEDIO POR PROPIEDAD
# ============================================================

if meses_cerrados > 0:

    df_cerrado = df[
        (df["Fecha"] >= inicio_anio)
        &
        (df["Fecha"] < inicio_mes_actual)
    ].copy()

    promedio_prop = (
        df_cerrado
        .groupby("Nombre_Propiedad")["Ingreso"]
        .sum()
        .div(meses_cerrados)
        .sort_values(ascending=False)
        .head(6)
    )

else:

    promedio_prop = pd.Series(dtype=float)


if not promedio_prop.empty:

    max_promedio = max(promedio_prop.max(), 1)

else:

    max_promedio = 1


bars_promedio = ""

for valor in promedio_prop.values:

    altura = max(8, int((valor / max_promedio) * 38))

    bars_promedio += f"""
        <div class="mini-bar mini-bar-purple"
             style="height:{altura}px;">
        </div>
    """


# ============================================================
# HEADER
# ============================================================

header_html = f"""
<div class="dashboard-header">

    <div class="brand-area">

        <div class="brand-icon">
            🏢
        </div>

        <div>

            <div class="brand-title">
                Airbnb <span>Financial Hub</span>
            </div>

            <div class="brand-subtitle">
                Rentabilidad financiera · Solo Airbnb
            </div>

        </div>

    </div>


    <div class="header-kpis">

        <div class="header-kpi">

            <div class="header-kpi-label">
                Ingresos 2026
            </div>

            <div class="header-kpi-value">
                {dinero(ingreso_ytd)}
            </div>

        </div>


        <div class="header-kpi">

            <div class="header-kpi-label">
                Flujo 2026
            </div>

            <div class="header-kpi-value green">
                {dinero(flujo_ytd)}
            </div>

        </div>


        <div class="header-kpi">

            <div class="header-kpi-label">
                Rentabilidad 2026
            </div>

            <div class="header-kpi-value green">
                {rentabilidad_ytd:.1f}%
            </div>

        </div>


        <div class="mini-chart-card">

            <div class="mini-chart-title">
                Ingreso mensual
            </div>

            <div class="mini-bars">
                {bars_ingreso}
            </div>

            <div class="mini-chart-footer">
                <span>2026</span>
                <span>Mes</span>
            </div>

        </div>


        <div class="mini-chart-card">

            <div class="mini-chart-title">
                Promedio mensual
            </div>

            <div class="mini-bars">
                {bars_promedio}
            </div>

            <div class="mini-chart-footer">
                <span>Propiedades</span>
                <span>2026</span>
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
    "<div style='height:2px'></div>",
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(
    [1, 1, 1, 0.95],
    gap="small"
)


with col1:

    st.markdown(
        '<div class="filter-label">Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudades = ["Todas"] + sorted(
        df["Ciudad"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ciudades,
        label_visibility="collapsed"
    )


with col2:

    st.markdown(
        '<div class="filter-label">Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedades = ["Todas"] + sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    propiedad = st.selectbox(
        "Propiedad",
        propiedades,
        label_visibility="collapsed"
    )


with col3:

    st.markdown(
        '<div class="filter-label">Socio</div>',
        unsafe_allow_html=True
    )

    socios = ["Todos"] + sorted(
        df["Nombre_Socio"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    socio = st.selectbox(
        "Socio",
        socios,
        label_visibility="collapsed"
    )


with col4:

    st.markdown(
        '<div class="filter-label">Período de análisis</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Período",
        value=(date(hoy.year, hoy.month, 1), hoy),
        label_visibility="collapsed"
    )


# ============================================================
# FECHAS DEL FILTRO
# ============================================================

if isinstance(periodo, tuple) and len(periodo) == 2:

    fecha_inicio = pd.Timestamp(periodo[0])
    fecha_fin = pd.Timestamp(periodo[1])

else:

    fecha_inicio = pd.Timestamp(periodo)
    fecha_fin = pd.Timestamp(periodo)


fecha_fin_exclusiva = fecha_fin + pd.Timedelta(days=1)


# ============================================================
# FILTRO FINANCIERO
# ============================================================

df_f = df[
    (df["Fecha"] >= fecha_inicio)
    &
    (df["Fecha"] < fecha_fin_exclusiva)
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
# KPI DEL PERÍODO
# ============================================================

ingreso_periodo = df_f["Ingreso"].sum()
gasto_periodo = df_f["Gasto"].sum()
flujo_periodo = ingreso_periodo - gasto_periodo

rentabilidad_periodo = (
    flujo_periodo / ingreso_periodo * 100
    if ingreso_periodo != 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.markdown(
    "<div style='height:4px'></div>",
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4, gap="small")


with k1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                💰 INGRESOS BRUTOS
            </div>

            <div class="kpi-value">
                {dinero(ingreso_periodo)}
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
                {dinero(gasto_periodo)}
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
                {dinero(flujo_periodo)}
            </div>

            <div class="kpi-sub">
                Ingresos − gastos
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with k4:

    rent_class = (
        "green"
        if rentabilidad_periodo >= 35
        else "red"
    )

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🎯 RENTABILIDAD
            </div>

            <div class="kpi-value {rent_class}">
                {rentabilidad_periodo:.1f}%
            </div>

            <div class="kpi-sub">
                Objetivo: 35%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TÍTULO PROPIEDADES
# ============================================================

st.markdown(
    """
    <div class="section-title">
        🏢 Rentabilidad por propiedad
    </div>

    <div class="section-subtitle">
        Desempeño financiero de cada propiedad en el período seleccionado
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PROMEDIOS MENSUALES
# ============================================================

if meses_cerrados > 0:

    df_cerrado = df[
        (df["Fecha"] >= inicio_anio)
        &
        (df["Fecha"] < inicio_mes_actual)
    ].copy()

    promedios = (
        df_cerrado
        .groupby(
            ["Nombre_Propiedad", "Ciudad"],
            as_index=False
        )
        .agg(
            Ingreso_Promedio=("Ingreso", "sum"),
            Gasto_Promedio=("Gasto", "sum")
        )
    )

    promedios["Ingreso_Promedio"] = (
        promedios["Ingreso_Promedio"]
        / meses_cerrados
    )

    promedios["Gasto_Promedio"] = (
        promedios["Gasto_Promedio"]
        / meses_cerrados
    )

    promedios["Flujo_Promedio"] = (
        promedios["Ingreso_Promedio"]
        - promedios["Gasto_Promedio"]
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


# ============================================================
# RESUMEN POR PROPIEDAD
# ============================================================

resumen = (
    df_f
    .groupby(
        ["Nombre_Propiedad", "Ciudad"],
        as_index=False
    )
    .agg(
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
)

resumen["Flujo"] = (
    resumen["Ingreso"]
    - resumen["Gasto"]
)

resumen["Rentabilidad"] = resumen.apply(
    lambda row:
        row["Flujo"] / row["Ingreso"] * 100
        if row["Ingreso"] != 0
        else 0,
    axis=1
)


# ============================================================
# RENTABILIDAD ACUMULADA 2026 POR PROPIEDAD
# ============================================================

ytd_prop = (
    df_ytd
    .groupby(
        ["Nombre_Propiedad", "Ciudad"],
        as_index=False
    )
    .agg(
        YTD_Ingreso=("Ingreso", "sum"),
        YTD_Gasto=("Gasto", "sum")
    )
)

ytd_prop["YTD_Flujo"] = (
    ytd_prop["YTD_Ingreso"]
    - ytd_prop["YTD_Gasto"]
)

ytd_prop["YTD_Rentabilidad"] = ytd_prop.apply(
    lambda row:
        row["YTD_Flujo"] / row["YTD_Ingreso"] * 100
        if row["YTD_Ingreso"] != 0
        else 0,
    axis=1
)


# ============================================================
# OCUPACIÓN
# ============================================================

if not df_ocupacion.empty:

    reservas = df_ocupacion.copy()

    reservas["Inicio_Overlap"] = reservas[
        "Fecha_Inicio"
    ].where(
        reservas["Fecha_Inicio"] > fecha_inicio,
        fecha_inicio
    )

    reservas["Fin_Overlap"] = reservas[
        "Fecha_Fin"
    ].where(
        reservas["Fecha_Fin"] < fecha_fin_exclusiva,
        fecha_fin_exclusiva
    )

    reservas["Noches_Overlap"] = (
        reservas["Fin_Overlap"]
        - reservas["Inicio_Overlap"]
    ).dt.days.clip(lower=0)

    reservas_validas = reservas[
        reservas["Noches_Overlap"] > 0
    ].copy()

    ocupacion = (
        reservas_validas
        .groupby(
            ["Nombre_Propiedad", "Ciudad"],
            as_index=False
        )
        .agg(
            Reservas=("Codigo_Reserva", "nunique"),
            Noches_Reservadas=("Noches_Overlap", "sum")
        )
    )

else:

    ocupacion = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas"
        ]
    )


dias_periodo = (
    fecha_fin_exclusiva
    - fecha_inicio
).days

ocupacion["Noches_Disponibles"] = dias_periodo

ocupacion["Ocupacion"] = (
    ocupacion["Noches_Reservadas"]
    / ocupacion["Noches_Disponibles"]
    * 100
)


# ============================================================
# MERGE FINAL
# ============================================================

resumen = resumen.merge(
    promedios,
    on=["Nombre_Propiedad", "Ciudad"],
    how="left"
)

resumen = resumen.merge(
    ytd_prop[
        [
            "Nombre_Propiedad",
            "Ciudad",
            "YTD_Rentabilidad"
        ]
    ],
    on=["Nombre_Propiedad", "Ciudad"],
    how="left"
)

resumen = resumen.merge(
    ocupacion[
        [
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas",
            "Noches_Disponibles",
            "Ocupacion"
        ]
    ],
    on=["Nombre_Propiedad", "Ciudad"],
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

if resumen.empty:

    st.info(
        "No hay información para los filtros seleccionados."
    )

else:

    for inicio in range(0, len(resumen), 3):

        fila = resumen.iloc[inicio:inicio + 3]

        cols = st.columns(
            len(fila),
            gap="small"
        )

        for col, (_, row) in zip(cols, fila.iterrows()):

            with col:

                nombre = row["Nombre_Propiedad"]
                ciudad_prop = row["Ciudad"]

                rent = row["Rentabilidad"]

                ytd_rent = row.get(
                    "YTD_Rentabilidad",
                    0
                )

                if pd.isna(ytd_rent):
                    ytd_rent = 0

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

                if pd.isna(ingreso_prom):
                    ingreso_prom = 0

                if pd.isna(gasto_prom):
                    gasto_prom = 0

                if pd.isna(flujo_prom):
                    flujo_prom = 0

                reservas_prop = row.get(
                    "Reservas",
                    None
                )

                noches_prop = row.get(
                    "Noches_Reservadas",
                    None
                )

                ocupacion_prop = row.get(
                    "Ocupacion",
                    None
                )

                if (
                    reservas_prop is None
                    or pd.isna(reservas_prop)
                ):

                    reservas_texto = "Sin datos"

                else:

                    reservas_texto = (
                        f"{int(reservas_prop)} reservas"
                    )

                if (
                    noches_prop is None
                    or pd.isna(noches_prop)
                ):

                    noches_texto = ""

                else:

                    noches_texto = (
                        f" · {int(noches_prop)} noches"
                    )

                if (
                    ocupacion_prop is None
                    or pd.isna(ocupacion_prop)
                ):

                    ocupacion_html = """
                    <div class="occupancy-value">
                        —
                    </div>

                    <div class="occupancy-detail">
                        Sin información de ocupación
                    </div>
                    """

                else:

                    ocupacion_html = f"""
                    <div class="occupancy-value">
                        {ocupacion_prop:.1f}%
                    </div>

                    <div class="occupancy-detail">
                        {reservas_texto}{noches_texto}
                    </div>
                    """

                es_buena = rent >= 35

                card_class = (
                    "property-card"
                    if es_buena
                    else "property-card bad"
                )

                profit_class = (
                    "good"
                    if es_buena
                    else "bad"
                )

                progress = max(
                    0,
                    min(float(rent), 100)
                )

                progress_class = (
                    ""
                    if es_buena
                    else "bad"
                )

                status_class = (
                    "good"
                    if es_buena
                    else "bad"
                )

                status_text = (
                    "✓ Sobre objetivo"
                    if es_buena
                    else "⚠ Bajo objetivo"
                )

                html = f"""
                <div class="{card_class}">

                    <div class="property-header">

                        <div>

                            <div class="property-name">
                                {nombre}
                            </div>

                            <div class="property-city">
                                📍 {ciudad_prop}
                            </div>

                        </div>

                        <div class="property-profit">

                            <div class="property-profit-value {profit_class}">
                                {rent:.1f}%
                            </div>

                            <div class="property-profit-year">
                                Acumulada 2026
                            </div>

                        </div>

                    </div>


                    <div class="metrics-row">

                        <div class="metric-box">

                            <div class="metric-label">
                                Ingresos
                            </div>

                            <div class="metric-value">
                                {dinero( row["Ingreso"] )}
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
                                {dinero( row["Gasto"] )}
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
                                {dinero( row["Flujo"] )}
                            </div>

                            <div class="metric-average">
                                Prom. mes {dinero_corto(flujo_prom)}
                            </div>

                        </div>

                    </div>


                    <div class="profit-row">

                        <div class="profit-label">

                            <span>
                                Rentabilidad
                            </span>

                            <span class="profit-number {profit_class}">
                                {rent:.1f}%
                            </span>

                        </div>


                        <div class="progress-bg">

                            <div
                                class="progress-fill {progress_class}"
                                style="width:{progress}%;">
                            </div>

                        </div>


                        <div class="target-status {status_class}">
                            {status_text}
                        </div>

                    </div>


                    <div class="occupancy-box">

                        <div class="occupancy-title">
                            Ocupación Airbnb
                        </div>

                        {ocupacion_html}

                    </div>

                </div>
                """

                st.markdown(
                    html,
                    unsafe_allow_html=True
                )
