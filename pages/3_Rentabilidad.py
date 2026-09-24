import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

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
# ESTILOS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   BASE
============================================================ */

.stApp {
    background: #F4F7FA;
}

.block-container {
    max-width: 1500px !important;

    /* Espacio compacto alrededor de la barra superior */
    padding-top: 0.35rem !important;
    padding-bottom: 0.50rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

#MainMenu,
footer {
    visibility: hidden;
}


/* ============================================================
   BARRA SUPERIOR STREAMLIT
============================================================ */

header[data-testid="stHeader"] {
    height: 46px !important;
    min-height: 46px !important;
    background: #FFFFFF !important;
    border-bottom: 1px solid #EEF2F5 !important;
}

header[data-testid="stHeader"] > div {
    height: 46px !important;
}

div[data-testid="stToolbar"] {
    height: 46px !important;
}

div[data-testid="stDecoration"] {
    display: none !important;
}


/* ============================================================
   MARCA
============================================================ */

.brand-mini {
    height: 64px;
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    display: flex;
    align-items: center;
    box-sizing: border-box;
}

.logo-mini {
    width: 48px;
    height: 48px;
    border-radius: 13px;
    background: #FF214B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
    margin-right: 10px;
}

.brand-mini-title {
    font-size: 17px;
    line-height: 1.05;
    font-weight: 850;
    color: #17345E;
    white-space: nowrap;
}

.brand-mini-title span {
    color: #FF3155;
}

.brand-mini-sub {
    font-size: 9px;
    color: #8290A4;
    margin-top: 5px;
    white-space: nowrap;
}


/* ============================================================
   FILTROS
============================================================ */

.filter-label {
    font-size: 10px;
    font-weight: 800;
    color: #71839A;
    margin-bottom: 3px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label {
    display: none !important;
}

div[data-baseweb="select"] > div {
    background: #F4F7FA !important;
    border: 1px solid #DFE6ED !important;
    border-radius: 9px !important;
    min-height: 36px !important;
    height: 36px !important;
}

div[data-baseweb="select"] span {
    font-size: 12px !important;
    color: #3E4B5D !important;
}

div[data-testid="stDateInput"] > div {
    background: #F4F7FA !important;
    border: 1px solid #DFE6ED !important;
    border-radius: 9px !important;
    min-height: 36px !important;
    height: 36px !important;
}

div[data-testid="stDateInput"] input {
    font-size: 12px !important;
    color: #3E4B5D !important;
}


/* ============================================================
   MINI GRÁFICOS
============================================================ */

div[data-testid="stPopover"] {
    width: 100% !important;
}

div[data-testid="stPopover"] button {
    height: 72px !important;
    min-height: 72px !important;
    width: 100% !important;
    border-radius: 13px !important;
    border: 1px solid #DCE5EE !important;
    background: #FFFFFF !important;
    color: #50637B !important;
    font-size: 11px !important;
    font-weight: 750 !important;
    padding: 8px !important;
}

div[data-testid="stPopover"] button:hover {
    border-color: #17345E !important;
    color: #17345E !important;
    background: #F8FAFC !important;
}

div[data-testid="stPopoverBody"] {
    width: 780px !important;
    max-width: 780px !important;
}


/* ============================================================
   INDICADORES SUPERIORES
============================================================ */

.top-card {
    height: 72px;
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 13px;
    padding: 10px 14px;
    box-sizing: border-box;
}

.top-label {
    font-size: 8px;
    font-weight: 800;
    color: #8290A4;
}

.top-value {
    font-size: 22px;
    font-weight: 850;
    color: #17345E;
    margin-top: 7px;
    line-height: 1;
}

.top-value.green {
    color: #009B70;
}

.top-value.red {
    color: #E84235;
}

/* ============================================================
   MENÚ PRINCIPAL
============================================================ */

.nav-button {
    text-align: center;
}

div.stButton > button {
    height: 52px !important;
    min-height: 52px !important;

    background: #FFFFFF !important;

    border: 1px solid #DCE5EE !important;
    border-radius: 12px !important;

    color: #50637B !important;

    font-size: 11px !important;
    font-weight: 750 !important;

    padding: 4px 5px !important;

    white-space: nowrap !important;
}

div.stButton > button:hover {
    border-color: #FF8FA3 !important;
    color: #17345E !important;
    background: #FFF7F8 !important;
}

/* ============================================================
   SECCIONES
============================================================ */

.section-title {
    font-size: 27px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.1;
    margin-top: 12px;
}

.section-subtitle {
    font-size: 11px;
    color: #8290A4;
    margin-top: 4px;
    margin-bottom: 10px;
}


/* ============================================================
   KPI
============================================================ */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 14px;
    height: 104px;
    padding: 14px 17px;
    box-sizing: border-box;
}

.kpi-label {
    font-size: 9px;
    font-weight: 800;
    color: #7E8EA4;
}

.kpi-value {
    font-size: 26px;
    font-weight: 850;
    color: #17345E;
    margin-top: 9px;
    line-height: 1;
}

.kpi-value.green {
    color: #009B70;
}

.kpi-value.red {
    color: #E84235;
}

.kpi-sub {
    font-size: 9px;
    color: #8B98A9;
    margin-top: 8px;
}


/* ============================================================
   TARJETAS DEL PORTAFOLIO / PROPIEDADES
   Diseño compacto — contenido ajustado a 165px
============================================================ */

.properties-grid {
    display: grid;
    grid-template-columns: repeat(8, minmax(0, 1fr));
    gap: 7px;
    margin-top: 0;
}

/* Tarjetas de propiedades */
.property-card {
    position: relative;
    overflow: hidden;
    border: none;
    border-radius: 10px;
    padding: 10px 10px 8px;
    height: 165px;
    box-sizing: border-box;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(24,52,94,.08);
}

/* Colores por equipo */
.property-card.team-bogota {
    background: linear-gradient(135deg, #2298DE 0%, #149FE8 100%);
}

.property-card.team-costa {
    background: linear-gradient(135deg, #08AE98 0%, #08B89F 100%);
}

.property-card.team-medellin,
.property-card.team-ibague {
    background: linear-gradient(135deg, #7657C5 0%, #8064C9 100%);
}

.property-header {
    height: 30px;
    display: flex;
    align-items: flex-start;
}

.property-name {
    font-size: 13px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.05;
    white-space: nowrap;
}

.property-city {
    font-size: 7.5px;
    font-weight: 400;
    color: rgba(255,255,255,.86);
    margin-top: 3px;
}

.property-income-main {
    font-size: 22px;
    font-weight: 400;
    color: #FFFFFF;
    line-height: 1;
    margin-top: 2px;
}

.property-income-label {
    display: none;
}

.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    margin-top: 7px;
    padding-top: 6px;
    border-top: 1px solid rgba(255,255,255,.20);
}

.metric-box {
    background: transparent;
    border-radius: 0;
    padding: 0;
    height: 28px;
    box-sizing: border-box;
    display: block;
}

.metric-box + .metric-box {
    border-left: 1px solid rgba(255,255,255,.20);
    padding-left: 9px;
}

.metric-icon {
    display: none;
}

.metric-content {
    min-width: 0;
}

.metric-label {
    font-size: 7.5px;
    font-weight: 700;
    color: rgba(255,255,255,.76);
    line-height: 1;
}

.metric-value {
    font-size: 12px;
    font-weight: 400;
    margin-top: 3px;
    white-space: nowrap;
    line-height: 1;
}

.metric-expense,
.metric-flow {
    color: #FFFFFF;
}

.property-divider {
    display: none;
}

.property-bottom {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    margin-top: 2px;
    padding-top: 5px;
    border-top: 1px solid rgba(255,255,255,.20);
}

.property-bottom-block {
    min-width: 0;
}

.property-bottom-block.occupancy {
    border-left: 1px solid rgba(255,255,255,.20);
    padding-left: 9px;
}

.profit-label,
.occupancy-label {
    font-size: 7.5px;
    font-weight: 700;
    color: rgba(255,255,255,.76);
}

.profit-number {
    font-size: 14px;
    font-weight: 400;
    margin-top: 2px;
    line-height: 1;
}

.profit-number.good,
.profit-number.bad {
    color: #FFFFFF;
}

.progress {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,.28);
    border-radius: 7px;
    margin-top: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #37E49B;
    border-radius: 7px;
}

.progress-fill.bad {
    background: #FF4D57;
}

.occupancy-value {
    font-size: 14px;
    font-weight: 400;
    color: #FFFFFF;
    margin-top: 2px;
    line-height: 1;
}

.occupancy-detail {
    font-size: 7.5px;
    font-weight: 400;
    color: rgba(255,255,255,.78);
    margin-top: 4px;
    white-space: nowrap;
}

/* ============================================================
   PORTAFOLIO
============================================================ */

.portfolio-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #FF3158 0%, #FF3F61 100%);
    border: none;
    border-radius: 10px;
    padding: 10px 10px 8px;
    height: 165px;
    box-sizing: border-box;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(255,49,88,.12);
}

.portfolio-title,
.portfolio-main,
.portfolio-main-label,
.portfolio-metrics,
.portfolio-divider,
.portfolio-profit-row {
    position: relative;
    z-index: 1;
}

.portfolio-title {
    font-size: 15px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
}

.portfolio-main {
    font-size: 26px;
    font-weight: 400;
    color: #FFFFFF;
    margin-top: 11px;
    line-height: 1;
}

.portfolio-main-label {
    display: none;
}

.portfolio-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    margin-top: 7px;
    padding-top: 6px;
    border-top: 1px solid rgba(255,255,255,.20);
}

.portfolio-metric {
    display: block;
}

.portfolio-metric + .portfolio-metric {
    border-left: 1px solid rgba(255,255,255,.20);
    padding-left: 9px;
}

.portfolio-metric-icon {
    display: none;
}

.portfolio-mini-label {
    font-size: 7.5px;
    font-weight: 700;
    color: rgba(255,255,255,.76);
}

.portfolio-mini-value {
    font-size: 12px;
    font-weight: 400;
    color: #FFFFFF;
    margin-top: 4px;
    line-height: 1;
}

.portfolio-divider {
    display: none;
}

.portfolio-profit-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    margin-top: 2px;
    padding-top: 5px;
    border-top: 1px solid rgba(255,255,255,.20);
}

.portfolio-profit-block {
    position: relative;
}

.portfolio-profit-block.target {
    border-left: 1px solid rgba(255,255,255,.20);
    padding-left: 9px;
}

.portfolio-profit-label {
    font-size: 7.5px;
    font-weight: 700;
    color: rgba(255,255,255,.76);
}

.portfolio-profit-value {
    font-size: 15px;
    font-weight: 400;
    margin-top: 2px;
    line-height: 1;
}

.portfolio-profit,
.portfolio-target {
    color: #FFFFFF;
}

    font-size: 0 !important;
    color: transparent !important;
}}

/* SVG de cada sección */

.st-key-nav_portafolio button {{
    background-image: url("data:image/svg+xml;base64,{icon_portafolio}") !important;
}}

.st-key-nav_propiedades button {{
    background-image: url("data:image/svg+xml;base64,{icon_propiedades}") !important;
}}

.st-key-nav_ocupacion button {{
    background-image: url("data:image/svg+xml;base64,{icon_ocupacion}") !important;
}}

.st-key-nav_financiero button {{
    background-image: url("data:image/svg+xml;base64,{icon_financiero}") !important;
}}

.st-key-nav_analisis button {{
    background-image: url("data:image/svg+xml;base64,{icon_analisis}") !important;
}}

.st-key-nav_reportes button {{
    background-image: url("data:image/svg+xml;base64,{icon_reportes}") !important;
}}

/* Hover limpio */

.st-key-nav_portafolio button:hover,
.st-key-nav_propiedades button:hover,
.st-key-nav_ocupacion button:hover,
.st-key-nav_financiero button:hover,
.st-key-nav_analisis button:hover,
.st-key-nav_reportes button:hover {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transform: none !important;
}}

/* ============================================================
   FILTROS CENTRADOS VERTICALMENTE
   ============================================================ */

div[data-testid="stHorizontalBlock"]:has(.st-key-nav_portafolio)
div[data-testid="column"] {{
    align-self: center !important;
}}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# FORMATO DINERO
# ============================================================

def dinero_corto(valor):

    if pd.isna(valor):
        return "$0"

    valor = float(valor)

    if abs(valor) >= 1_000_000_000:
        return f"${valor / 1_000_000_000:.1f}B"

    if abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"${valor / 1_000:.0f}K"

    return f"${valor:,.0f}"


# ============================================================
# CARGA FINANCIERA
# ============================================================

@st.cache_data(ttl=300)
def cargar_financiero():

    query = """
    SELECT
        Fecha,
        Nombre_Propiedad,
        Ciudad,
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

    df["Nombre_Propiedad"] = (
        df["Nombre_Propiedad"]
        .astype(str)
        .str.strip()
    )

    df["Ciudad"] = (
        df["Ciudad"]
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# INVERSIONES POR PROPIEDAD
# ============================================================

@st.cache_data(ttl=300)
def cargar_inversiones():

    query = """
    SELECT
        Activo_Proyecto,
        SUM(Valor_Prorrateado_Calculado) AS Inversion
    FROM `rentascamacho.rentas_cortas.Vista_Inversiones_Prorrateadas`
    WHERE Activo_Proyecto IN (
        'Torre Acqua',
        'Torre Evoca',
        'Torre Ventto',
        'Lotus',
        'Santa Marina',
        'Base Loft',
        'Tempus 49',
        'Iwani'
    )
    GROUP BY Activo_Proyecto
    """

    inversiones = client.query(query).to_dataframe()

    inversiones["Inversion"] = pd.to_numeric(
        inversiones["Inversion"],
        errors="coerce"
    ).fillna(0)

    return inversiones


# ============================================================
# RESERVAS / OCUPACIÓN
# ============================================================

@st.cache_data(ttl=300)
def cargar_reservas(
    fecha_inicio,
    fecha_fin
):

    query = f"""
    WITH reservas_base AS (

        SELECT DISTINCT
            Codigo_Confirmacion,
            Nombre_Propiedad,
            Ciudad,
            CAST(Fecha_Check_In AS DATE) AS Fecha_Check_In,
            CAST(Fecha_Check_Out AS DATE) AS Fecha_Check_Out
        FROM `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

        WHERE
            CAST(Fecha_Check_Out AS DATE) > DATE('{fecha_inicio}')
            AND CAST(Fecha_Check_In AS DATE) < DATE_ADD(
                DATE('{fecha_fin}'),
                INTERVAL 1 DAY
            )

            AND LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
    ),

    reservas_overlap AS (

        SELECT
            *,
            GREATEST(
                Fecha_Check_In,
                DATE('{fecha_inicio}')
            ) AS Inicio_Real,

            LEAST(
                Fecha_Check_Out,
                DATE_ADD(
                    DATE('{fecha_fin}'),
                    INTERVAL 1 DAY
                )
            ) AS Fin_Real

        FROM reservas_base
    )

    SELECT
        Nombre_Propiedad,
        Ciudad,

        COUNT(
            DISTINCT Codigo_Confirmacion
        ) AS Reservas,

        SUM(
            DATE_DIFF(
                Fin_Real,
                Inicio_Real,
                DAY
            )
        ) AS Noches_Reservadas,

        DATE_DIFF(
            DATE_ADD(
                DATE('{fecha_fin}'),
                INTERVAL 1 DAY
            ),
            DATE('{fecha_inicio}'),
            DAY
        ) AS Noches_Disponibles

    FROM reservas_overlap

    GROUP BY
        Nombre_Propiedad,
        Ciudad
    """

    df = client.query(query).to_dataframe()

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Nombre_Propiedad",
                "Ciudad",
                "Reservas",
                "Noches_Reservadas",
                "Noches_Disponibles"
            ]
        )

    df["Reservas"] = pd.to_numeric(
        df["Reservas"],
        errors="coerce"
    ).fillna(0)

    df["Noches_Reservadas"] = pd.to_numeric(
        df["Noches_Reservadas"],
        errors="coerce"
    ).fillna(0)

    df["Noches_Disponibles"] = pd.to_numeric(
        df["Noches_Disponibles"],
        errors="coerce"
    ).fillna(0)

    return df


# ============================================================
# DATOS BASE
# ============================================================

df = cargar_financiero()

hoy = date.today()

inicio_mes = hoy.replace(
    day=1
)

inicio_anio = hoy.replace(
    month=1,
    day=1
)

fin_hoy = (
    pd.Timestamp(hoy)
    + pd.Timedelta(days=1)
)


# ============================================================
# ESTADO DE NAVEGACIÓN
# ============================================================

if "vista_airbnb" not in st.session_state:

    st.session_state.vista_airbnb = "Portafolio"


# ============================================================
# ENCABEZADO
# ============================================================

top1, top2, top3, top4, top5, top6, top7, top8, top9, top10 = st.columns(
    [
        2.35,
        0.75,
        0.75,
        0.75,
        0.75,
        0.75,
        0.75,
        0.85,
        1.10,
        1.65
    ],
    gap="small"
)


# ============================================================
# MARCA
# ============================================================

with top1:

    st.markdown(
        f"""
<div class="brand-mini">

    <img
        src="{logo_data}"
        style="
            width:48px;
            height:48px;
            border-radius:13px;
            object-fit:cover;
            margin-right:10px;
        "
    >

    <div>

        <div class="brand-mini-title">
            Airbnb <span>Financial Hub</span>
        </div>

        <div class="brand-mini-sub">
            Rentas Camacho · Gestión financiera
        </div>

    </div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# NAVEGACIÓN
# ============================================================

with top2:

    if st.button(
        "",
        key="nav_portafolio",
        help="Portafolio"
    ):
        st.session_state.vista_airbnb = "Portafolio"
        st.rerun()


with top3:

    if st.button(
        "",
        key="nav_propiedades",
        help="Propiedades"
    ):
        st.session_state.vista_airbnb = "Propiedades"
        st.rerun()


with top4:

    if st.button(
        "",
        key="nav_ocupacion",
        help="Ocupación"
    ):
        st.session_state.vista_airbnb = "Ocupación"
        st.rerun()


with top5:

    if st.button(
        "",
        key="nav_financiero",
        help="Financiero"
    ):
        st.session_state.vista_airbnb = "Financiero"
        st.rerun()


with top6:

    if st.button(
        "",
        key="nav_analisis",
        help="Análisis"
    ):
        st.session_state.vista_airbnb = "Análisis"
        st.rerun()


with top7:

    if st.button(
        "",
        key="nav_reportes",
        help="Reportes"
    ):
        st.session_state.vista_airbnb = "Reportes"
        st.rerun()


# ============================================================
# FILTRO CIUDAD
# ============================================================

ciudades = sorted(
    df["Ciudad"]
    .dropna()
    .unique()
    .tolist()
)

with top8:

    st.markdown(
        '<div class="filter-label">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        index=0,
        label_visibility="collapsed"
    )


# ============================================================
# FILTRO PROPIEDAD
# ============================================================

with top9:

    st.markdown(
        '<div class="filter-label">🏠 Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"]
        +
        sorted(
            df["Nombre_Propiedad"]
            .dropna()
            .unique()
            .tolist()
        ),
        label_visibility="collapsed"
    )


# ============================================================
# FILTRO PERÍODO
# ============================================================

with top10:

    st.markdown(
        '<div class="filter-label">📅 Período</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Período",
        value=(
            inicio_mes,
            hoy
        ),
        label_visibility="collapsed"
    )


# ============================================================
# FECHAS SELECCIONADAS
# ============================================================

if (
    isinstance(
        periodo,
        (tuple, list)
    )
    and
    len(periodo) == 2
):

    fecha_inicio = periodo[0]
    fecha_fin = periodo[1]

else:

    fecha_inicio = inicio_mes
    fecha_fin = hoy


# ============================================================
# FILTRAR DATOS
# ============================================================

df_f = df[
    (df["Fecha"].dt.date >= fecha_inicio)
    &
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


# ============================================================
# TOTALES
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = (
    ingresos -
    gastos
)

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
        Ingresos=(
            "Ingreso",
            "sum"
        ),
        Gastos=(
            "Gasto",
            "sum"
        )
    )
)

resumen["Flujo"] = (
    resumen["Ingresos"]
    -
    resumen["Gastos"]
)

resumen["Rentabilidad"] = (
    resumen["Flujo"]
    /
    resumen["Ingresos"]
    *
    100
).fillna(0)


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
        df_ocupacion["Noches_Reservadas"]
        /
        df_ocupacion["Noches_Disponibles"]
        *
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

# Orden visual por equipos:
# 1. Bogotá → 2. Costa → 3. Medellín → 4. Ibagué
orden_ciudad = {
    "Bogotá": 1,
    "Santa Marta": 2,
    "Cartagena": 2,
    "Medellín": 3,
    "Ibagué": 4
}

resumen["OrdenEquipo"] = (
    resumen["Ciudad"]
    .map(orden_ciudad)
    .fillna(99)
)

resumen = (
    resumen
    .sort_values(
        ["OrdenEquipo", "Nombre_Propiedad"],
        ascending=[True, True]
    )
    .drop(columns=["OrdenEquipo"])
    .reset_index(drop=True)
)


# ============================================================
# DATOS DE INVERSIÓN
# ============================================================

inversiones = cargar_inversiones()

# ============================================================
# VISTA PROPIEDADES
# ============================================================

if st.session_state.vista_airbnb == "Propiedades":

    # ========================================================
    # TARJETAS
    # ========================================================

    cards_html = '<div class="properties-grid">'

    cards_html += tarjeta_portafolio()

    for _, row in resumen.iterrows():

        cards_html += tarjeta_propiedad(row)

    cards_html += "</div>"

    cards_html = "\n".join(
        linea.strip()
        for linea in cards_html.splitlines()
    )

    st.markdown(
        cards_html,
        unsafe_allow_html=True
    )

    # ========================================================
    # TABLA DE ANÁLISIS DE INVERSIÓN
    # ========================================================

    tabla = inversiones.rename(
        columns={
            "Activo_Proyecto": "Nombre_Propiedad"
        }
    ).copy()

    tabla = tabla.merge(
        resumen[
            [
                "Nombre_Propiedad",
                "Ciudad",
                "Ingresos",
                "Gastos",
                "Flujo",
                "Rentabilidad",
                "Ocupacion",
                "Reservas",
                "Noches_Reservadas"
            ]
        ],
        on="Nombre_Propiedad",
        how="left"
    )

    # Estado del activo
    tabla["Estado"] = tabla["Nombre_Propiedad"].apply(
        lambda x:
            "En desarrollo"
            if str(x).strip().lower() == "iwani"
            else "Operando"
    )

    # Filtros actuales
    if propiedad != "Todas":

        tabla = tabla[
            tabla["Nombre_Propiedad"] == propiedad
        ]

    if ciudad != "Todas":

        tabla = tabla[
            tabla["Ciudad"] == ciudad
        ]

    # Orden visual
    orden_tabla = {
        "Torre Acqua": 1,
        "Torre Evoca": 2,
        "Torre Ventto": 3,
        "Lotus": 4,
        "Santa Marina": 5,
        "Base Loft": 6,
        "Tempus 49": 7,
        "Iwani": 8
    }

    tabla["Orden"] = (
        tabla["Nombre_Propiedad"]
        .map(orden_tabla)
        .fillna(99)
    )

    tabla = (
        tabla
        .sort_values("Orden")
        .drop(columns=["Orden"])
        .reset_index(drop=True)
    )

    def valor_tabla(valor):

        if pd.isna(valor):
            return "—"

        return dinero_corto(valor)


    html_tabla = """
<div class="investment-panel">

<div class="investment-title">
📊 Análisis de inversión
</div>

<div class="investment-subtitle">
Inversión acumulada por activo y desempeño del período seleccionado
</div>

<table class="investment-table">

<thead>

<tr>

<th>Propiedad</th>
<th>Estado</th>
<th>Inversión</th>
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


    for _, row in tabla.iterrows():

        nombre = row["Nombre_Propiedad"]

        estado = row["Estado"]

        estado_class = (
            "development"
            if estado == "En desarrollo"
            else ""
        )

        flujo = row["Flujo"]

        if pd.isna(flujo):

            flujo_html = (
                '<span class="investment-muted">—</span>'
            )

        elif float(flujo) < 0:

            flujo_html = (
                '<span class="investment-flow-negative">'
                f'{dinero_corto(flujo)}'
                '</span>'
            )

        else:

            flujo_html = (
                '<span class="investment-flow-positive">'
                f'{dinero_corto(flujo)}'
                '</span>'
            )


        if pd.isna(row["Rentabilidad"]):

            rent_html = (
                '<span class="investment-muted">—</span>'
            )

        else:

            rent_html = (
                f'{float(row["Rentabilidad"]):.1f}%'
            )


        if pd.isna(row["Ocupacion"]):

            ocup_html = (
                '<span class="investment-muted">—</span>'
            )

        else:

            ocup_html = (
                f'{float(row["Ocupacion"]):.1f}%'
            )


        reservas_html = (

            "—"

            if pd.isna(row["Reservas"])

            else f'{int(row["Reservas"])}'

        )


        noches_html = (

            "—"

            if pd.isna(row["Noches_Reservadas"])

            else f'{int(row["Noches_Reservadas"])}'

        )


        html_tabla += f"""
<tr>

<td>
{nombre}
</td>

<td>

<span class="investment-status {estado_class}">
{estado}
</span>

</td>

<td>

<span class="investment-money">
{dinero_corto(row["Inversion"])}
</span>

</td>

<td>
{valor_tabla(row["Ingresos"])}
</td>

<td>
{valor_tabla(row["Gastos"])}
</td>

<td>
{flujo_html}
</td>

<td>
{rent_html}
</td>

<td>
{ocup_html}
</td>

<td>
{reservas_html}
</td>

<td>
{noches_html}
</td>

</tr>
"""


    html_tabla += """
</tbody>

</table>

</div>
"""


    st.markdown(
        html_tabla,
        unsafe_allow_html=True
    )


# ============================================================
# VISTA FINANCIERO
# ============================================================

elif st.session_state.vista_airbnb == "Financiero":

    st.markdown(
        """
<div class="section-title">
💰 Financiero
</div>

<div class="section-subtitle">
Evolución mensual de ingresos, gastos y flujo durante 2026.
</div>
""",
        unsafe_allow_html=True
    )


    financiero = df[
        (df["Fecha"] >= inicio_anio)
        &
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
            Ingresos=(
                "Ingreso",
                "sum"
            ),
            Gastos=(
                "Gasto",
                "sum"
            )
        )
        .sort_values("Mes_Num")
    )


    mensual_fin["Flujo"] = (
        mensual_fin["Ingresos"]
        -
        mensual_fin["Gastos"]
    )


    fig_fin = go.Figure()


    fig_fin.add_trace(
        go.Bar(
            x=mensual_fin["Mes"],
            y=mensual_fin["Ingresos"],
            name="Ingresos",
            marker_color="#27B68D"
        )
    )


    fig_fin.add_trace(
        go.Bar(
            x=mensual_fin["Mes"],
            y=mensual_fin["Gastos"],
            name="Gastos",
            marker_color="#EF4338"
        )
    )


    fig_fin.add_trace(
        go.Scatter(
            x=mensual_fin["Mes"],
            y=mensual_fin["Flujo"],
            name="Flujo",
            mode="lines+markers",
            line=dict(
                color="#17345E",
                width=3
            )
        )
    )


    fig_fin.update_layout(
        height=470,
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
            l=50,
            r=30,
            t=40,
            b=40
        ),
        yaxis=dict(
            tickprefix="$",
            tickformat=",.0f",
            gridcolor="#E9EEF3"
        ),
        xaxis=dict(
            showgrid=False
        )
    )


    st.plotly_chart(
        fig_fin,
        use_container_width=True
    )


# ============================================================
# VISTA OCUPACIÓN
# ============================================================

elif st.session_state.vista_airbnb == "Ocupación":

    st.markdown(
        """
<div class="section-title">
📊 Ocupación Airbnb
</div>

<div class="section-subtitle">
Reservas y noches ocupadas durante el período seleccionado.
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
            "No hay reservas para el período seleccionado."
        )

    else:

        ocupacion["Ocupacion"] = (
            ocupacion["Noches_Reservadas"]
            /
            ocupacion["Noches_Disponibles"]
            *
            100
        )


        total_reservas = (
            ocupacion["Reservas"].sum()
        )

        total_noches = (
            ocupacion["Noches_Reservadas"].sum()
        )

        total_disponibles = (
            ocupacion["Noches_Disponibles"].sum()
        )

        ocupacion_total = (
            total_noches
            /
            total_disponibles
            *
            100
            if total_disponibles
            else 0
        )


        a, b, c = st.columns(
            3,
            gap="small"
        )


        with a:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
OCUPACIÓN PORTAFOLIO
</div>

<div
class="kpi-value"
style="color:#6954E6;">
{ocupacion_total:.1f}%
</div>

<div class="kpi-sub">
Noches ocupadas / disponibles
</div>

</div>
""",
                unsafe_allow_html=True
            )


        with b:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
RESERVAS
</div>

<div class="kpi-value">
{int(total_reservas)}
</div>

<div class="kpi-sub">
Período seleccionado
</div>

</div>
""",
                unsafe_allow_html=True
            )


        with c:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
NOCHES RESERVADAS
</div>

<div class="kpi-value">
{int(total_noches)}
</div>

<div class="kpi-sub">
De {int(total_disponibles)} disponibles
</div>

</div>
""",
                unsafe_allow_html=True
            )


        # ====================================================
        # TARJETAS DE OCUPACIÓN
        # ====================================================

        cards_html = '<div class="properties-grid">'

        for _, row in ocupacion.iterrows():

            porcentaje = float(
                row["Ocupacion"]
            )

            progress = min(
                max(porcentaje, 0),
                100
            )

            cards_html += f"""
<div class="property-card">

<div class="property-header">

<div>

<div class="property-name">
{row["Nombre_Propiedad"]}
</div>

<div class="property-city">
📍 {row["Ciudad"]}
</div>

</div>

<div class="property-profit">

<div
class="property-profit-value"
style="color:#6954E6;">
{porcentaje:.1f}%
</div>

<div class="property-profit-label">
Ocupación
</div>

</div>

</div>

<div style="
margin-top:12px;
">

<div class="metric-label">
NOCHES RESERVADAS
</div>

<div style="
font-size:26px;
font-weight:850;
color:#17345E;
margin-top:5px;
">
{int(row["Noches_Reservadas"])}
</div>

</div>

<div class="profit-section">

<div class="profit-line">

<div class="profit-label">
Ocupación
</div>

<div
class="profit-number"
style="color:#6954E6;">
{porcentaje:.1f}%
</div>

</div>

<div class="progress">

<div
class="progress-fill"
style="
width:{progress:.1f}%;
background:#6954E6;
">
</div>

</div>

</div>

<div class="occupancy-box">

<div class="occupancy-top">

<div class="occupancy-label">
Reservas
</div>

<div class="occupancy-value">
{int(row["Reservas"])}
</div>

</div>

<div class="occupancy-detail">
{int(row["Noches_Disponibles"])} noches disponibles
</div>

</div>

</div>
"""

        cards_html += "</div>"

        st.markdown(
            cards_html,
            unsafe_allow_html=True
        )
# ============================================================
# VISTA PROPIEDADES
# ============================================================

if st.session_state.vista_airbnb == "Propiedades":

    # ========================================================
    # TARJETAS
    # ========================================================

    cards_html = '<div class="properties-grid">'

    cards_html += tarjeta_portafolio()

    for _, row in resumen.iterrows():

        cards_html += tarjeta_propiedad(row)

    cards_html += "</div>"

    cards_html = "\n".join(
        linea.strip()
        for linea in cards_html.splitlines()
    )

    st.markdown(
        cards_html,
        unsafe_allow_html=True
    )

    # ========================================================
    # TABLA DE ANÁLISIS DE INVERSIÓN
    # ========================================================

    tabla = inversiones.rename(
        columns={
            "Activo_Proyecto": "Nombre_Propiedad"
        }
    ).copy()

    tabla = tabla.merge(
        resumen[
            [
                "Nombre_Propiedad",
                "Ciudad",
                "Ingresos",
                "Gastos",
                "Flujo",
                "Rentabilidad",
                "Ocupacion",
                "Reservas",
                "Noches_Reservadas"
            ]
        ],
        on="Nombre_Propiedad",
        how="left"
    )

    tabla["Estado"] = tabla["Nombre_Propiedad"].apply(
        lambda x: "En desarrollo"
        if str(x).strip().lower() == "iwani"
        else "Operando"
    )

    if propiedad != "Todas":

        tabla = tabla[
            tabla["Nombre_Propiedad"] == propiedad
        ]

    if ciudad != "Todas":

        tabla = tabla[
            tabla["Ciudad"] == ciudad
        ]

    orden_tabla = {
        "Torre Acqua": 1,
        "Torre Evoca": 2,
        "Torre Ventto": 3,
        "Lotus": 4,
        "Santa Marina": 5,
        "Base Loft": 6,
        "Tempus 49": 7,
        "Iwani": 8
    }

    tabla["Orden"] = (
        tabla["Nombre_Propiedad"]
        .map(orden_tabla)
        .fillna(99)
    )

    tabla = (
        tabla
        .sort_values("Orden")
        .drop(columns=["Orden"])
        .reset_index(drop=True)
    )

    def valor_tabla(valor):

        if pd.isna(valor):
            return "—"

        return dinero_corto(valor)


    html_tabla = """
<div class="investment-panel">

<div class="investment-title">
📊 Análisis de inversión
</div>

<div class="investment-subtitle">
Inversión acumulada por activo y desempeño del período seleccionado
</div>

<table class="investment-table">

<thead>

<tr>

<th>Propiedad</th>
<th>Estado</th>
<th>Inversión</th>
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


    for _, row in tabla.iterrows():

        nombre = row["Nombre_Propiedad"]

        estado = row["Estado"]

        estado_class = (
            "development"
            if estado == "En desarrollo"
            else ""
        )

        flujo = row["Flujo"]

        if pd.isna(flujo):

            flujo_html = (
                '<span class="investment-muted">—</span>'
            )

        elif float(flujo) < 0:

            flujo_html = (
                '<span class="investment-flow-negative">'
                f'{dinero_corto(flujo)}'
                '</span>'
            )

        else:

            flujo_html = (
                '<span class="investment-flow-positive">'
                f'{dinero_corto(flujo)}'
                '</span>'
            )


        if pd.isna(row["Rentabilidad"]):

            rent_html = (
                '<span class="investment-muted">—</span>'
            )

        else:

            rent_html = (
                f'{float(row["Rentabilidad"]):.1f}%'
            )


        if pd.isna(row["Ocupacion"]):

            ocup_html = (
                '<span class="investment-muted">—</span>'
            )

        else:

            ocup_html = (
                f'{float(row["Ocupacion"]):.1f}%'
            )


        reservas_html = (

            "—"

            if pd.isna(row["Reservas"])

            else f'{int(row["Reservas"])}'

        )


        noches_html = (

            "—"

            if pd.isna(row["Noches_Reservadas"])

            else f'{int(row["Noches_Reservadas"])}'

        )


        html_tabla += f"""
<tr>

<td>
{nombre}
</td>

<td>

<span class="investment-status {estado_class}">
{estado}
</span>

</td>

<td>

<span class="investment-money">
{dinero_corto(row["Inversion"])}
</span>

</td>

<td>
{valor_tabla(row["Ingresos"])}
</td>

<td>
{valor_tabla(row["Gastos"])}
</td>

<td>
{flujo_html}
</td>

<td>
{rent_html}
</td>

<td>
{ocup_html}
</td>

<td>
{reservas_html}
</td>

<td>
{noches_html}
</td>

</tr>
"""


    html_tabla += """
</tbody>

</table>

</div>
"""


    st.markdown(
        html_tabla,
        unsafe_allow_html=True
    )


# ============================================================
# VISTA FINANCIERO
# ============================================================

elif st.session_state.vista_airbnb == "Financiero":

    st.markdown(
        """
<div class="section-title">
💰 Financiero
</div>

<div class="section-subtitle">
Evolución mensual de ingresos, gastos y flujo durante 2026.
</div>
""",
        unsafe_allow_html=True
    )


    financiero = df[
        (df["Fecha"] >= inicio_anio)
        &
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
            Ingresos=(
                "Ingreso",
                "sum"
            ),
            Gastos=(
                "Gasto",
                "sum"
            )
        )
        .sort_values("Mes_Num")
    )


    mensual_fin["Flujo"] = (
        mensual_fin["Ingresos"]
        -
        mensual_fin["Gastos"]
    )


    fig_fin = go.Figure()


    fig_fin.add_trace(
        go.Bar(
            x=mensual_fin["Mes"],
            y=mensual_fin["Ingresos"],
            name="Ingresos",
            marker_color="#27B68D"
        )
    )


    fig_fin.add_trace(
        go.Bar(
            x=mensual_fin["Mes"],
            y=mensual_fin["Gastos"],
            name="Gastos",
            marker_color="#EF4338"
        )
    )


    fig_fin.add_trace(
        go.Scatter(
            x=mensual_fin["Mes"],
            y=mensual_fin["Flujo"],
            name="Flujo",
            mode="lines+markers",
            line=dict(
                color="#17345E",
                width=3
            )
        )
    )


    fig_fin.update_layout(
        height=470,
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
            l=50,
            r=30,
            t=40,
            b=40
        ),
        yaxis=dict(
            tickprefix="$",
            tickformat=",.0f",
            gridcolor="#E9EEF3"
        ),
        xaxis=dict(
            showgrid=False
        )
    )


    st.plotly_chart(
        fig_fin,
        use_container_width=True
    )


# ============================================================
# VISTA OCUPACIÓN
# ============================================================

elif st.session_state.vista_airbnb == "Ocupación":

    st.markdown(
        """
<div class="section-title">
📊 Ocupación Airbnb
</div>

<div class="section-subtitle">
Reservas y noches ocupadas durante el período seleccionado.
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
            "No hay reservas para el período seleccionado."
        )

    else:

        ocupacion["Ocupacion"] = (
            ocupacion["Noches_Reservadas"]
            /
            ocupacion["Noches_Disponibles"]
            *
            100
        )


        total_reservas = (
            ocupacion["Reservas"].sum()
        )

        total_noches = (
            ocupacion["Noches_Reservadas"].sum()
        )

        total_disponibles = (
            ocupacion["Noches_Disponibles"].sum()
        )

        ocupacion_total = (
            total_noches
            /
            total_disponibles
            *
            100
            if total_disponibles
            else 0
        )


        a, b, c = st.columns(
            3,
            gap="small"
        )


        with a:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
OCUPACIÓN PORTAFOLIO
</div>

<div
class="kpi-value"
style="color:#6954E6;">
{ocupacion_total:.1f}%
</div>

<div class="kpi-sub">
Noches ocupadas / disponibles
</div>

</div>
""",
                unsafe_allow_html=True
            )


        with b:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
RESERVAS
</div>

<div class="kpi-value">
{int(total_reservas)}
</div>

<div class="kpi-sub">
Período seleccionado
</div>

</div>
""",
                unsafe_allow_html=True
            )


        with c:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
NOCHES RESERVADAS
</div>

<div class="kpi-value">
{int(total_noches)}
</div>

<div class="kpi-sub">
De {int(total_disponibles)} disponibles
</div>

</div>
""",
                unsafe_allow_html=True
            )


        cards_html = '<div class="properties-grid">'

        for _, row in ocupacion.iterrows():

            porcentaje = float(
                row["Ocupacion"]
            )

            progress = min(
                max(porcentaje, 0),
                100
            )

            cards_html += f"""
<div class="property-card">

<div class="property-header">

<div>

<div class="property-name">
{row["Nombre_Propiedad"]}
</div>

<div class="property-city">
📍 {row["Ciudad"]}
</div>

</div>

<div class="property-profit">

<div
class="property-profit-value"
style="color:#6954E6;">
{porcentaje:.1f}%
</div>

<div class="property-profit-label">
Ocupación
</div>

</div>

</div>

<div style="
margin-top:12px;
">

<div class="metric-label">
NOCHES RESERVADAS
</div>

<div style="
font-size:26px;
font-weight:850;
color:#17345E;
margin-top:5px;
">
{int(row["Noches_Reservadas"])}
</div>

</div>

<div class="profit-section">

<div class="profit-line">

<div class="profit-label">
Ocupación
</div>

<div
class="profit-number"
style="color:#6954E6;">
{porcentaje:.1f}%
</div>

</div>

<div class="progress">

<div
class="progress-fill"
style="
width:{progress:.1f}%;
background:#6954E6;
">
</div>

</div>

</div>

<div class="occupancy-box">

<div class="occupancy-top">

<div class="occupancy-label">
Reservas
</div>

<div class="occupancy-value">
{int(row["Reservas"])}
</div>

</div>

<div class="occupancy-detail">
{int(row["Noches_Disponibles"])} noches disponibles
</div>

</div>

</div>
"""

        cards_html += "</div>"

        st.markdown(
            cards_html,
            unsafe_allow_html=True
        )
