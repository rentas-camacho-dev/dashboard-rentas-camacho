import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date, timedelta


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

st.markdown(
    """
    <style>

    /* ========================================================
       GENERAL
       ======================================================== */

    .stApp {
        background: #F4F6F8;
    }

    .block-container {
        max-width: 1680px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #19345C;
    }


    /* ========================================================
       HEADER
       ======================================================== */

    .main-header {
        background: #FFFFFF;
        border: 1px solid #DDE4EC;
        border-radius: 22px;
        padding: 18px 22px;
        margin-bottom: 22px;
        box-shadow: 0 5px 18px rgba(25, 52, 92, 0.05);

        display: flex;
        align-items: center;
        gap: 18px;
    }

    .brand-area {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1.15;
        min-width: 320px;
    }

    .brand-icon {
        width: 78px;
        height: 78px;
        border-radius: 20px;
        background: #FF1F4B;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 42px;
        flex-shrink: 0;
    }

    .brand-title {
        font-size: 30px;
        line-height: 1.05;
        font-weight: 800;
        color: #19345C;
        margin: 0;
        letter-spacing: -0.7px;
    }

    .brand-title span {
        color: #FF365B;
    }

    .brand-subtitle {
        color: #71809A;
        font-size: 14px;
        margin-top: 7px;
    }


    /* ========================================================
       HEADER KPIs
       ======================================================== */

    .header-kpis {
        display: flex;
        gap: 12px;
        flex: 1;
    }

    .header-kpi {
        background: #F7F9FB;
        border: 1px solid #E0E6ED;
        border-radius: 15px;
        padding: 12px 15px;
        min-width: 170px;
        flex: 1;
    }

    .header-kpi-label {
        font-size: 10px;
        color: #8795AA;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.2px;
    }

    .header-kpi-value {
        font-size: 21px;
        font-weight: 800;
        color: #19345C;
        margin-top: 5px;
    }

    .header-kpi-value.green {
        color: #00966B;
    }


    /* ========================================================
       MINI CHARTS
       ======================================================== */

    .mini-chart-card {
        width: 190px;
        min-width: 190px;
        height: 82px;

        background: #F7F9FB;
        border: 1px solid #E0E6ED;
        border-radius: 15px;

        padding: 9px 11px;
        box-sizing: border-box;
    }

    .mini-chart-title {
        font-size: 10px;
        color: #8795AA;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .mini-bars {
        height: 40px;
        display: flex;
        align-items: flex-end;
        gap: 4px;
    }

    .mini-bar-green {
        flex: 1;
        min-width: 5px;
        background: #38B894;
        border-radius: 3px 3px 0 0;
    }

    .mini-bar-purple {
        flex: 1;
        min-width: 5px;
        background: #7561D8;
        border-radius: 3px 3px 0 0;
    }

    .mini-chart-footer {
        display: flex;
        justify-content: space-between;
        font-size: 8px;
        color: #8795AA;
        margin-top: 2px;
    }


    /* ========================================================
       FILTROS
       ======================================================== */

    .filter-title {
        font-size: 13px;
        font-weight: 600;
        color: #71809A;
        margin-bottom: 4px;
    }

    div[data-baseweb="select"] > div {
        background-color: #F0F3F7 !important;
        border: 0 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] {
        margin-bottom: 0 !important;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #DDE4EC;
        border-radius: 17px;
        padding: 19px 20px;
        min-height: 132px;
        box-shadow: 0 4px 12px rgba(25, 52, 92, 0.04);
    }

    .kpi-title {
        color: #71809A;
        font-size: 14px;
        font-weight: 700;
    }

    .kpi-value {
        color: #19345C;
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
        letter-spacing: -0.5px;
    }

    .kpi-value.green {
        color: #00966B;
    }

    .kpi-value.red {
        color: #E43C20;
    }

    .kpi-sub {
        color: #8795AA;
        font-size: 13px;
        margin-top: 8px;
    }


    /* ========================================================
       SECCIÓN PROPIEDADES
       ======================================================== */

    .section-title {
        font-size: 29px;
        font-weight: 800;
        color: #19345C;
        margin-top: 5px;
        margin-bottom: 2px;
    }

    .section-subtitle {
        font-size: 14px;
        color: #71809A;
        margin-bottom: 17px;
    }


    /* ========================================================
       TARJETAS DE PROPIEDAD — COMPACTAS
       ======================================================== */

    .property-card {
        background: #FFFFFF;
        border: 1px solid #DDE4EC;
        border-radius: 20px;
        padding: 15px;
        min-height: 365px;
        box-shadow: 0 4px 12px rgba(20,40,70,0.04);
        margin-bottom: 15px;
    }

    .property-card.bad {
        border: 2px solid #FF6262;
    }

    .property-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .property-name {
        font-size: 20px;
        font-weight: 800;
        color: #19345C;
        line-height: 1.15;
    }

    .property-city {
        font-size: 13px;
        color: #71809A;
        margin-top: 5px;
    }

    .property-profit-block {
        text-align: right;
    }

    .property-profit {
        font-size: 18px;
        font-weight: 800;
    }

    .property-profit.good {
        color: #00A879;
    }

    .property-profit.bad {
        color: #FF4141;
    }

    .accumulated {
        font-size: 11px;
        color: #8795AA;
        margin-top: 3px;
    }


    /* ========================================================
       MÉTRICAS
       ======================================================== */

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 14px;
    }

    .metric-box {
        background: #F6F8FA;
        border-radius: 12px;
        padding: 10px 9px;
        min-height: 76px;
        box-sizing: border-box;
    }

    .metric-label {
        font-size: 11px;
        color: #71809A;
    }

    .metric-value {
        font-size: 15px;
        font-weight: 800;
        margin-top: 4px;
        white-space: nowrap;
    }

    .metric-value.income {
        color: #00966B;
    }

    .metric-value.expense {
        color: #FF452C;
    }

    .metric-value.flow {
        color: #0073C8;
    }

    .metric-average {
        font-size: 9px;
        color: #8795AA;
        margin-top: 3px;
        white-space: nowrap;
    }


    /* ========================================================
       RENTABILIDAD
       ======================================================== */

    .profit-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 14px;
    }

    .profit-label {
        font-size: 12px;
        color: #71809A;
    }

    .profit-percent {
        font-size: 19px;
        font-weight: 800;
    }

    .progress-bg {
        height: 7px;
        border-radius: 10px;
        background: #E7ECF1;
        margin-top: 7px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
        background: #00A879;
    }

    .progress-fill.bad {
        background: #FF4C4C;
    }

    .target-good {
        color: #00966B;
        font-size: 11px;
        font-weight: 600;
        margin-top: 7px;
    }

    .target-bad {
        color: #E43C20;
        font-size: 11px;
        font-weight: 600;
        margin-top: 7px;
    }


    /* ========================================================
       OCUPACIÓN
       ======================================================== */

    .occupancy-box {
        background: #F6F8FA;
        border-radius: 13px;
        padding: 10px 11px;
        margin-top: 11px;
    }

    .occupancy-title {
        font-size: 11px;
        color: #71809A;
    }

    .occupancy-value {
        font-size: 16px;
        font-weight: 800;
        color: #7256E8;
        margin-top: 4px;
    }

    .occupancy-detail {
        font-size: 10px;
        color: #8795AA;
        margin-top: 3px;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 1100px) {

        .main-header {
            flex-wrap: wrap;
        }

        .brand-area {
            min-width: 100%;
        }

        .header-kpis {
            width: 100%;
        }

        .mini-chart-card {
            flex: 1;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


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
# FUNCIONES DE CARGA
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

    df["Ingreso"] = pd.to_numeric(
        df["Ingreso"],
        errors="coerce"
    ).fillna(0)

    df["Gasto"] = pd.to_numeric(
        df["Gasto"],
        errors="coerce"
    ).fillna(0)

    return df


@st.cache_data(ttl=300)
def cargar_reservas_airbnb():

    query = """
    WITH reservas_base AS (

        SELECT
            TRIM(C__digo_de_confirmaci__n) AS Codigo_Reserva,
            TRIM(Anuncio) AS Anuncio,
            DATE(Fecha_de_inicio) AS Fecha_Inicio,
            DATE(Fecha_de_finalizaci__n) AS Fecha_Fin

        FROM
            `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

        WHERE
            LOWER(TRIM(Tipo)) = 'reservación'

            AND C__digo_de_confirmaci__n IS NOT NULL
            AND TRIM(C__digo_de_confirmaci__n) <> ''

            AND Anuncio IS NOT NULL
            AND TRIM(Anuncio) <> ''

            AND Fecha_de_inicio IS NOT NULL
            AND Fecha_de_finalizaci__n IS NOT NULL

        QUALIFY
            ROW_NUMBER() OVER (
                PARTITION BY
                    TRIM(C__digo_de_confirmaci__n)
                ORDER BY
                    Fecha_de_inicio
            ) = 1
    ),

    mapa AS (

        SELECT
            LOWER(TRIM(Anuncio)) AS anuncio_key,
            Nombre AS Nombre_Propiedad,
            Ciudad

        FROM
            `rentascamacho.rentas_cortas.Participaciones`

        WHERE
            Anuncio IS NOT NULL
            AND TRIM(Anuncio) <> ''

        QUALIFY
            ROW_NUMBER() OVER (
                PARTITION BY LOWER(TRIM(Anuncio))
                ORDER BY ID_Activo
            ) = 1
    )

    SELECT
        r.Codigo_Reserva,
        r.Anuncio,
        r.Fecha_Inicio,
        r.Fecha_Fin,
        m.Nombre_Propiedad,
        m.Ciudad

    FROM reservas_base r

    INNER JOIN mapa m
        ON LOWER(TRIM(r.Anuncio)) = m.anuncio_key

    WHERE
        r.Fecha_Fin > r.Fecha_Inicio
    """

    return client.query(query).to_dataframe()


# ============================================================
# FORMATO
# ============================================================

def dinero(valor):

    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


def dinero_corto(valor):

    if pd.isna(valor):
        valor = 0

    valor_abs = abs(valor)

    signo = "-" if valor < 0 else ""

    if valor_abs >= 1_000_000:
        return f"{signo}${valor_abs / 1_000_000:.1f}M"

    if valor_abs >= 1_000:
        return f"{signo}${valor_abs / 1_000:.0f}k"

    return f"{signo}${valor_abs:,.0f}".replace(",", ".")


def porcentaje(valor):

    if pd.isna(valor):
        valor = 0

    return f"{valor:.1f}%"


# ============================================================
# CARGAR INFORMACIÓN
# ============================================================

df = cargar_datos_financieros()
df_reservas = cargar_reservas_airbnb()


# ============================================================
# FECHAS
# ============================================================

hoy = date.today()

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
)

inicio_anio = pd.Timestamp(
    hoy.year,
    1,
    1
)

fin_hoy = pd.Timestamp(hoy) + pd.Timedelta(days=1)


# ============================================================
# LIMPIEZA
# ============================================================

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    errors="coerce"
)

df = df.dropna(
    subset=["Fecha"]
)

df["Nombre_Propiedad"] = (
    df["Nombre_Propiedad"]
    .fillna("Sin propiedad")
)

df["Ciudad"] = (
    df["Ciudad"]
    .fillna("Sin ciudad")
)

df["Nombre_Socio"] = (
    df["Nombre_Socio"]
    .fillna("Sin socio")
)


# ============================================================
# DATOS YTD
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
# HEADER
# ============================================================

# Mini gráfico de ingresos mensuales
df_meses = (
    df_ytd
    .groupby(df_ytd["Fecha"].dt.month)["Ingreso"]
    .sum()
)

meses_2026 = list(range(1, hoy.month + 1))

valores_mensuales = [
    float(df_meses.get(m, 0))
    for m in meses_2026
]

max_mes = max(valores_mensuales) if valores_mensuales else 1

barras_ingreso = ""

for valor in valores_mensuales:

    altura = (
        int((valor / max_mes) * 38)
        if max_mes > 0
        else 2
    )

    altura = max(4, altura)

    barras_ingreso += (
        f'<div class="mini-bar-green" '
        f'style="height:{altura}px;"></div>'
    )


# Promedio mensual por propiedad
df_prom_header = (
    df_ytd
    .groupby("Nombre_Propiedad")["Ingreso"]
    .sum()
    .sort_values(ascending=False)
)

valores_prom = (
    df_prom_header.head(7).tolist()
)

if valores_prom:

    max_prom = max(valores_prom)

else:

    max_prom = 1

barras_promedio = ""

for valor in valores_prom:

    altura = (
        int((valor / max_prom) * 38)
        if max_prom > 0
        else 2
    )

    altura = max(4, altura)

    barras_promedio += (
        f'<div class="mini-bar-purple" '
        f'style="height:{altura}px;"></div>'
    )


# ============================================================
# HEADER HTML
# ============================================================

st.markdown(
    f"""
    <div class="main-header">

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
                    Ingresos {hoy.year}
                </div>

                <div class="header-kpi-value">
                    {dinero(ingreso_ytd)}
                </div>

            </div>


            <div class="header-kpi">

                <div class="header-kpi-label">
                    Flujo {hoy.year}
                </div>

                <div class="header-kpi-value green">
                    {dinero(flujo_ytd)}
                </div>

            </div>


            <div class="header-kpi">

                <div class="header-kpi-label">
                    Rentabilidad {hoy.year}
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
                    {barras_ingreso}
                </div>

                <div class="mini-chart-footer">
                    <span>{hoy.year}</span>
                    <span>Mes</span>
                </div>

            </div>


            <div class="mini-chart-card">

                <div class="mini-chart-title">
                    Promedio mensual
                </div>

                <div class="mini-bars">
                    {barras_promedio}
                </div>

                <div class="mini-chart-footer">
                    <span>Propiedades</span>
                    <span>{hoy.year}</span>
                </div>

            </div>

        </div>

    </div>
    """,
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
    [1, 1, 1, 1]
)


with col1:

    st.markdown(
        '<div class="filter-title">Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad_seleccionada = st.selectbox(
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
        .unique()
        .tolist()
    )

    propiedad_seleccionada = st.selectbox(
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
        .unique()
        .tolist()
    )

    socio_seleccionado = st.selectbox(
        "Socio",
        ["Todos"] + socios,
        label_visibility="collapsed"
    )


with col4:

    st.markdown(
        '<div class="filter-title">Período de análisis</div>',
        unsafe_allow_html=True
    )

    rango = st.date_input(
        "Período",
        value=(
            hoy.replace(day=1),
            hoy
        ),
        label_visibility="collapsed",
        format="DD/MM/YYYY"
    )


# ============================================================
# FECHAS DEL FILTRO
# ============================================================

if isinstance(rango, tuple) and len(rango) == 2:

    fecha_inicio = pd.Timestamp(rango[0])
    fecha_fin = pd.Timestamp(rango[1])

else:

    fecha_inicio = pd.Timestamp(
        hoy.replace(day=1)
    )

    fecha_fin = pd.Timestamp(hoy)


fecha_fin_exclusiva = (
    fecha_fin + pd.Timedelta(days=1)
)


# ============================================================
# FILTRO FINANCIERO
# ============================================================

df_f = df[
    (df["Fecha"] >= fecha_inicio)
    &
    (df["Fecha"] < fecha_fin_exclusiva)
].copy()


if ciudad_seleccionada != "Todas":

    df_f = df_f[
        df_f["Ciudad"] == ciudad_seleccionada
    ]


if propiedad_seleccionada != "Todas":

    df_f = df_f[
        df_f["Nombre_Propiedad"]
        == propiedad_seleccionada
    ]


if socio_seleccionado != "Todos":

    df_f = df_f[
        df_f["Nombre_Socio"]
        == socio_seleccionado
    ]


# ============================================================
# KPI DEL PERÍODO
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
# KPI CARDS
# ============================================================

st.markdown(
    "<div style='height:16px'></div>",
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)


with k1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                💰 INGRESOS BRUTOS
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
                📄 GASTOS OPERATIVOS
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

    rent_class = (
        "green"
        if rentabilidad >= 35
        else "red"
    )

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🎯 RENTABILIDAD
            </div>

            <div class="kpi-value {rent_class}">
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
# PROMEDIOS MENSUALES
# ============================================================

meses_cerrados = max(
    hoy.month - 1,
    0
)

if meses_cerrados > 0:

    df_cerrado = df[
        (df["Fecha"] >= inicio_anio)
        &
        (df["Fecha"] < inicio_mes_actual)
    ].copy()

    promedios = (
        df_cerrado
        .groupby(
            [
                "Nombre_Propiedad",
                "Ciudad"
            ]
        )
        .agg(
            Ingreso_Promedio=("Ingreso", "sum"),
            Gasto_Promedio=("Gasto", "sum")
        )
        .reset_index()
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


# ============================================================
# OCUPACIÓN DEL PERÍODO
# ============================================================

df_reservas["Fecha_Inicio"] = pd.to_datetime(
    df_reservas["Fecha_Inicio"],
    errors="coerce"
)

df_reservas["Fecha_Fin"] = pd.to_datetime(
    df_reservas["Fecha_Fin"],
    errors="coerce"
)

df_reservas = df_reservas.dropna(
    subset=[
        "Fecha_Inicio",
        "Fecha_Fin"
    ]
)


# Reservas que tienen cualquier cruce con el período
reservas_periodo = df_reservas[
    (df_reservas["Fecha_Inicio"] < fecha_fin_exclusiva)
    &
    (df_reservas["Fecha_Fin"] > fecha_inicio)
].copy()


# Calcular noches realmente dentro del período
if not reservas_periodo.empty:

    reservas_periodo["Inicio_Overlap"] = (
        reservas_periodo["Fecha_Inicio"]
        .where(
            reservas_periodo["Fecha_Inicio"] >= fecha_inicio,
            fecha_inicio
        )
    )

    reservas_periodo["Fin_Overlap"] = (
        reservas_periodo["Fecha_Fin"]
        .where(
            reservas_periodo["Fecha_Fin"] <= fecha_fin_exclusiva,
            fecha_fin_exclusiva
        )
    )

    reservas_periodo["Noches_Reservadas"] = (
        reservas_periodo["Fin_Overlap"]
        -
        reservas_periodo["Inicio_Overlap"]
    ).dt.days

    reservas_periodo["Noches_Reservadas"] = (
        reservas_periodo["Noches_Reservadas"]
        .clip(lower=0)
    )

else:

    reservas_periodo["Noches_Reservadas"] = []


dias_periodo = (
    fecha_fin_exclusiva - fecha_inicio
).days


ocupacion = pd.DataFrame(
    columns=[
        "Nombre_Propiedad",
        "Ciudad",
        "Reservas",
        "Noches_Reservadas",
        "Noches_Disponibles",
        "Ocupacion_Porcentaje"
    ]
)


if not reservas_periodo.empty:

    ocupacion = (
        reservas_periodo
        .groupby(
            [
                "Nombre_Propiedad",
                "Ciudad"
            ]
        )
        .agg(
            Reservas=(
                "Codigo_Reserva",
                "nunique"
            ),
            Noches_Reservadas=(
                "Noches_Reservadas",
                "sum"
            )
        )
        .reset_index()
    )

    ocupacion["Noches_Disponibles"] = dias_periodo

    ocupacion["Ocupacion_Porcentaje"] = (
        ocupacion["Noches_Reservadas"]
        /
        ocupacion["Noches_Disponibles"]
        * 100
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
        ]
    )
    .agg(
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
    .reset_index()
)


resumen["Flujo"] = (
    resumen["Ingreso"]
    -
    resumen["Gasto"]
)


resumen["Rentabilidad"] = resumen.apply(
    lambda row:
        (
            row["Flujo"]
            /
            row["Ingreso"]
            * 100
        )
        if row["Ingreso"] != 0
        else 0,
    axis=1
)


# ============================================================
# MERGE PROMEDIOS
# ============================================================

resumen = resumen.merge(
    promedios,
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)


# ============================================================
# MERGE OCUPACIÓN
# ============================================================

resumen = resumen.merge(
    ocupacion,
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)


# ============================================================
# ORDENAR POR RENTABILIDAD
# ============================================================

resumen = resumen.sort_values(
    "Rentabilidad",
    ascending=False
).reset_index(drop=True)


# ============================================================
# SECCIÓN PROPIEDADES
# ============================================================

st.markdown(
    "<div style='height:16px'></div>",
    unsafe_allow_html=True
)

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
# TARJETAS
# ============================================================

for inicio in range(
    0,
    len(resumen),
    3
):

    fila = resumen.iloc[
        inicio:inicio + 3
    ]

    columnas = st.columns(3)

    for columna, (_, row) in zip(
        columnas,
        fila.iterrows()
    ):

        nombre = row["Nombre_Propiedad"]

        ciudad = row["Ciudad"]

        ingreso_prop = row["Ingreso"]

        gasto_prop = row["Gasto"]

        flujo_prop = row["Flujo"]

        rent_prop = row["Rentabilidad"]


        # Promedios
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


        # Ocupación
        reservas_prop = row.get(
            "Reservas",
            0
        )

        noches_prop = row.get(
            "Noches_Reservadas",
            0
        )

        ocupacion_prop = row.get(
            "Ocupacion_Porcentaje",
            None
        )


        if pd.isna(ocupacion_prop):
            ocupacion_prop = None

        if pd.isna(reservas_prop):
            reservas_prop = 0

        if pd.isna(noches_prop):
            noches_prop = 0


        es_buena = rent_prop >= 35

        card_class = (
            ""
            if es_buena
            else "bad"
        )

        profit_class = (
            "good"
            if es_buena
            else "bad"
        )


        # Barra de progreso
        progreso = max(
            0,
            min(
                rent_prop,
                100
            )
        )

        progress_class = (
            ""
            if es_buena
            else "bad"
        )


        # Ocupación HTML
        if ocupacion_prop is not None:

            ocupacion_html = f"""
            <div class="occupancy-box">

                <div class="occupancy-title">
                    Ocupación Airbnb
                </div>

                <div class="occupancy-value">
                    {ocupacion_prop:.1f}%
                </div>

                <div class="occupancy-detail">
                    {int(reservas_prop)} reservas ·
                    {int(noches_prop)} noches
                </div>

            </div>
            """

        else:

            ocupacion_html = """
            <div class="occupancy-box">

                <div class="occupancy-title">
                    Ocupación Airbnb
                </div>

                <div class="occupancy-value">
                    —
                </div>

                <div class="occupancy-detail">
                    Sin reservas en el período
                </div>

            </div>
            """


        html = f"""
        <div class="property-card {card_class}">

            <div class="property-top">

                <div>

                    <div class="property-name">
                        {nombre}
                    </div>

                    <div class="property-city">
                        📍 {ciudad}
                    </div>

                </div>


                <div class="property-profit-block">

                    <div class="property-profit {profit_class}">
                        {rent_prop:.1f}%
                    </div>

                    <div class="accumulated">
                        Acumulada {hoy.year}
                    </div>

                </div>

            </div>


            <div class="metric-grid">

                <div class="metric-box">

                    <div class="metric-label">
                        Ingresos
                    </div>

                    <div class="metric-value income">
                        {dinero_corto(ingreso_prop)}
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
                        {dinero_corto(gasto_prop)}
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
                        {dinero_corto(flujo_prop)}
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

                <div class="profit-percent {profit_class}">
                    {rent_prop:.1f}%
                </div>

            </div>


            <div class="progress-bg">

                <div
                    class="progress-fill {progress_class}"
                    style="width:{progreso:.1f}%;">
                </div>

            </div>


            {
                '<div class="target-good">✓ Sobre objetivo</div>'
                if es_buena
                else
                '<div class="target-bad">⚠ Bajo objetivo</div>'
            }


            {ocupacion_html}

        </div>
        """

        with columna:

            st.markdown(
                html,
                unsafe_allow_html=True
            )


# ============================================================
# ESPACIO FINAL
# ============================================================

st.markdown(
    "<div style='height:15px'></div>",
    unsafe_allow_html=True
)
