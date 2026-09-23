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

    /* Espacio suficiente para la barra superior */
    padding-top: 2.15rem !important;
    padding-bottom: 1rem !important;
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
    height: 72px;
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
   PROPIEDADES
============================================================ */

.properties-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 13px;
    margin-top: 13px;
}

.property-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 15px;
    padding: 15px;
    height: 270px;
    box-sizing: border-box;
    box-shadow: 0 3px 12px rgba(24,52,94,.035);
}

.property-card.negative {
    border-color: #FF7770;
}

.property-header {
    height: 46px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.property-name {
    font-size: 18px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.1;
}

.property-city {
    font-size: 10px;
    color: #8290A4;
    margin-top: 5px;
}

.property-profit {
    text-align: right;
}

.property-profit-value {
    font-size: 19px;
    font-weight: 850;
    line-height: 1;
}

.property-profit-value.good {
    color: #009B70;
}

.property-profit-value.bad {
    color: #E84235;
}

.property-profit-label {
    font-size: 8px;
    color: #9AA5B4;
    margin-top: 5px;
}


/* ============================================================
   MÉTRICAS
============================================================ */

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 7px;
    margin-top: 10px;
}

.metric-box {
    background: #F5F7F9;
    border-radius: 9px;
    padding: 9px;
    height: 61px;
    box-sizing: border-box;
}

.metric-label {
    font-size: 8px;
    color: #8290A4;
}

.metric-value {
    font-size: 15px;
    font-weight: 850;
    margin-top: 6px;
    white-space: nowrap;
}

.metric-income {
    color: #009B70;
}

.metric-expense {
    color: #EF4338;
}

.metric-flow {
    color: #0878D2;
}


/* ============================================================
   RENTABILIDAD
============================================================ */

.profit-section {
    margin-top: 10px;
}

.profit-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.profit-label {
    font-size: 9px;
    color: #8290A4;
}

.profit-number {
    font-size: 13px;
    font-weight: 850;
}

.profit-number.good {
    color: #009B70;
}

.profit-number.bad {
    color: #E84235;
}

.progress {
    width: 100%;
    height: 6px;
    background: #E7EDF1;
    border-radius: 6px;
    margin-top: 5px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #00AC7C;
    border-radius: 6px;
}

.progress-fill.bad {
    background: #EF4A42;
}


/* ============================================================
   OCUPACIÓN
============================================================ */

.occupancy-box {
    background: #F5F7FA;
    border-radius: 9px;
    margin-top: 9px;
    padding: 8px 10px;
    height: 48px;
    box-sizing: border-box;
}

.occupancy-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.occupancy-label {
    font-size: 8px;
    color: #8290A4;
}

.occupancy-value {
    font-size: 14px;
    font-weight: 850;
    color: #6954E6;
}

.occupancy-detail {
    font-size: 8px;
    color: #96A1AF;
    margin-top: 3px;
}

/* ============================================================
   PORTAFOLIO
============================================================ */

.portfolio-card {
    position: relative;
    overflow: hidden;
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 18px;
    padding: 17px;
    height: 270px;
    box-sizing: border-box;
    color: #17345E;
    box-shadow: 0 3px 12px rgba(24,52,94,.035);
}

.portfolio-watermark-circle {
    position: absolute;
    right: -35px;
    top: -45px;
    width: 205px;
    height: 205px;
    border-radius: 50%;
    background: #FFF0F3;
    z-index: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.portfolio-watermark-circle img {
    width: 135px;
    height: 135px;
    object-fit: contain;
    opacity: 0.10;
}

.portfolio-title,
.portfolio-subtitle,
.portfolio-main,
.portfolio-main-label,
.portfolio-metrics,
.portfolio-divider,
.portfolio-profit-row {
    position: relative;
    z-index: 1;
}


/* ------------------------------------------------------------
   ENCABEZADO
------------------------------------------------------------ */

.portfolio-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 22px;
    font-weight: 850;
    color: #17345E;
    line-height: 1;
}

.portfolio-icon {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: #FF214B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -1px;
    flex-shrink: 0;
}

.portfolio-subtitle {
    font-size: 11px;
    color: #71839A;
    margin-top: 7px;
    margin-left: 56px;
    white-space: nowrap;
}


/* ------------------------------------------------------------
   INGRESO PRINCIPAL
------------------------------------------------------------ */

.portfolio-main {
    font-size: 39px;
    font-weight: 900;
    color: #17345E;
    margin-top: 10px;
    line-height: 1;
}

.portfolio-main-label {
    font-size: 10px;
    color: #71839A;
    margin-top: 7px;
}


/* ------------------------------------------------------------
   MÉTRICAS GASTOS / FLUJO
------------------------------------------------------------ */

.portfolio-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-top: 7px;
}

.portfolio-metric {
    display: flex;
    align-items: center;
    gap: 10px;
}

.portfolio-metric-icon {
    width: 38px;
    height: 38px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    flex-shrink: 0;
}

.portfolio-metric-icon.expense {
    background: #FFF0F1;
    color: #FF4B5C;
}

.portfolio-metric-icon.flow {
    background: #EAF8F3;
    color: #00A779;
}

.portfolio-mini-label {
    font-size: 10px;
    color: #71839A;
}

.portfolio-mini-value {
    font-size: 19px;
    font-weight: 850;
    color: #17345E;
    margin-top: 3px;
    line-height: 1;
}


/* ------------------------------------------------------------
   LÍNEA GRIS
------------------------------------------------------------ */

.portfolio-divider {
    height: 1px;
    background: #E3E8ED;
    margin-top: 6px;
}


/* ------------------------------------------------------------
   RENTABILIDAD / OBJETIVO
------------------------------------------------------------ */

.portfolio-profit-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 4px;
}

.portfolio-profit-block {
    position: relative;
}

.portfolio-profit-block.target {
    border-left: 1px solid #E3E8ED;
    padding-left: 20px;
}

.portfolio-profit-label {
    font-size: 10px;
    color: #71839A;
}

.portfolio-profit-value {
    font-size: 25px;
    font-weight: 900;
    margin-top: 5px;
    line-height: 1;
}

.portfolio-profit {
    color: #FF4B5C;
}

.portfolio-target {
    color: #17345E;
}


/* ------------------------------------------------------------
   BARRA DE RENTABILIDAD
------------------------------------------------------------ */

.portfolio-progress {
    width: 100%;
    height: 7px;
    background: #E7EDF1;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 8px;
}

.portfolio-progress-fill {
    height: 100%;
    width: 67.1%;
    background: #FF5A67;
    border-radius: 8px;
}

/* ============================================================
   PANELES
============================================================ */

.side-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 13px;
    padding: 13px 15px;
    margin-top: 12px;
}

.side-title {
    font-size: 14px;
    font-weight: 850;
    color: #17345E;
}

.side-subtitle {
    font-size: 9px;
    color: #8A98AA;
    margin-top: 4px;
}


/* ============================================================
   RANKING
============================================================ */

.rank {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 9px;
}

.rank-name {
    width: 95px;
    font-size: 9px;
    color: #61738C;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rank-background {
    flex: 1;
    height: 8px;
    background: #EDF0F4;
    border-radius: 8px;
    overflow: hidden;
}

.rank-fill {
    height: 100%;
    background: #7964DD;
    border-radius: 8px;
}

.rank-number {
    width: 42px;
    text-align: right;
    font-size: 9px;
    color: #697A91;
}


/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 1200px) {

    .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    .properties-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 900px) {

    .properties-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 650px) {

    .properties-grid {
        grid-template-columns: 1fr;
    }

    .brand-mini-title {
        font-size: 14px;
    }
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

with open(
    "assets/logo_rentas_camacho.png",
    "rb"
) as f:
    logo_b64 = base64.b64encode(
        f.read()
    ).decode()

logo_data = f"data:image/png;base64,{logo_b64}"
# ============================================================
# ICONOS DEL MENÚ SUPERIOR
# ============================================================

def cargar_svg_base64(nombre):
    with open(f"assets/{nombre}", "rb") as f:
        return base64.b64encode(f.read()).decode()

icon_portafolio = cargar_svg_base64("icon_portafolio.svg")
icon_propiedades = cargar_svg_base64("icon_propiedades.svg")
icon_ocupacion = cargar_svg_base64("icon_ocupacion.svg")
icon_financiero = cargar_svg_base64("icon_financiero.svg")
icon_analisis = cargar_svg_base64("icon_analisis.svg")
icon_reportes = cargar_svg_base64("icon_reportes.svg")

# ============================================================
# ICONOS PERSONALIZADOS DEL MENÚ
# ============================================================

st.markdown(
    f"""
<style>

/* ============================================================
   RECUADRO GENERAL DEL MENÚ SUPERIOR
   ============================================================ */

div[data-testid="stHorizontalBlock"]:has(.st-key-nav_portafolio) {{
    background: #FFFFFF !important;
    border: 1px solid #DCE5EE !important;
    border-radius: 16px !important;
    padding: 8px 10px 6px 10px !important;
    box-sizing: border-box !important;
}}

/* ----------------------------- */
/* PORTAFOLIO */
/* ----------------------------- */

.st-key-nav_portafolio button {{
    background-image: url("data:image/svg+xml;base64,{icon_portafolio}") !important;
    background-repeat: no-repeat !important;
    background-position: center 6px !important;
    background-size: 46px 46px !important;

    height: 82px !important;
    min-height: 82px !important;

    padding-top: 50px !important;

    border-radius: 14px !important;
    background-color: #FFFFFF !important;

    background-color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}}


/* ----------------------------- */
/* PROPIEDADES */
/* ----------------------------- */

.st-key-nav_propiedades button {{
    background-image: url("data:image/svg+xml;base64,{icon_propiedades}") !important;
    background-repeat: no-repeat !important;
    background-position: center 6px !important;
    background-size: 46px 46px !important;

    height: 82px !important;
    min-height: 82px !important;

    padding-top: 50px !important;

    border-radius: 14px !important;
    background-color: #FFFFFF !important;

    background-color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}}


/* ----------------------------- */
/* OCUPACIÓN */
/* ----------------------------- */

.st-key-nav_ocupacion button {{
    background-image: url("data:image/svg+xml;base64,{icon_ocupacion}") !important;
    background-repeat: no-repeat !important;
    background-position: center 6px !important;
    background-size: 46px 46px !important;

    height: 82px !important;
    min-height: 82px !important;

    padding-top: 50px !important;

    border-radius: 14px !important;
    background-color: #FFFFFF !important;

    background-color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}}


/* ----------------------------- */
/* FINANCIERO */
/* ----------------------------- */

.st-key-nav_financiero button {{
    background-image: url("data:image/svg+xml;base64,{icon_financiero}") !important;
    background-repeat: no-repeat !important;
    background-position: center 6px !important;
    background-size: 46px 46px !important;

    height: 82px !important;
    min-height: 82px !important;

    padding-top: 50px !important;

    border-radius: 14px !important;
    background-color: #FFFFFF !important;

    background-color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}}


/* ----------------------------- */
/* ANÁLISIS */
/* ----------------------------- */

.st-key-nav_analisis button {{
    background-image: url("data:image/svg+xml;base64,{icon_analisis}") !important;
    background-repeat: no-repeat !important;
    background-position: center 6px !important;
    background-size: 46px 46px !important;

    height: 82px !important;
    min-height: 82px !important;

    padding-top: 50px !important;

    border-radius: 14px !important;
    background-color: #FFFFFF !important;

    background-color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}}


/* ----------------------------- */
/* REPORTES */
/* ----------------------------- */

.st-key-nav_reportes button {{
    background-image: url("data:image/svg+xml;base64,{icon_reportes}") !important;
    background-repeat: no-repeat !important;
    background-position: center 6px !important;
    background-size: 46px 46px !important;

    height: 82px !important;
    min-height: 82px !important;

    padding-top: 50px !important;

    border-radius: 14px !important;
    background-color: #FFFFFF !important;

    background-color: #FFFFFF !important;
    font-size: 11px !important;
    font-weight: 800 !important;
}}

/* ============================================================
   NOMBRES DEL MENÚ
   ============================================================ */

.st-key-nav_portafolio button {{
    color: #FF3155 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
}}

.st-key-nav_propiedades button {{
    color: #1688F5 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
}}

.st-key-nav_ocupacion button {{
    color: #18B58A !important;
    font-size: 9px !important;
    font-weight: 700 !important;
}}

.st-key-nav_financiero button {{
    color: #F5A623 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
}}

.st-key-nav_analisis button {{
    color: #F23861 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
}}

.st-key-nav_reportes button {{
    color: #7654E8 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
}}

/* ----------------------------- */
/* QUITAR RECUADRO BLANCO */
/* ----------------------------- */

.st-key-nav_portafolio button,
.st-key-nav_propiedades button,
.st-key-nav_ocupacion button,
.st-key-nav_financiero button,
.st-key-nav_analisis button,
.st-key-nav_reportes button {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

/* ----------------------------- */
/* HOVER */
/* ----------------------------- */

.st-key-nav_portafolio button:hover,
.st-key-nav_propiedades button:hover,
.st-key-nav_ocupacion button:hover,
.st-key-nav_financiero button:hover,
.st-key-nav_analisis button:hover,
.st-key-nav_reportes button:hover {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
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
        valor = 0

    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"${valor / 1_000:.0f}k"

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
# RESERVAS AIRBNB / OCUPACIÓN
# ============================================================

@st.cache_data(ttl=300)
def cargar_reservas(
    fecha_inicio,
    fecha_fin
):

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

inicio_mes = date(
    hoy.year,
    hoy.month,
    1
)

inicio_anio = pd.Timestamp(
    hoy.year,
    1,
    1
)

fin_hoy = (
    pd.Timestamp(hoy)
    +
    pd.Timedelta(days=1)
)


# ============================================================
# YTD
# ============================================================

df_ytd = df[
    (df["Fecha"] >= inicio_anio)
    &
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
# MENÚ SUPERIOR
# MARCA + NAVEGACIÓN + FILTROS
# ============================================================

if "vista_airbnb" not in st.session_state:

    st.session_state.vista_airbnb = "Portafolio"

top1, top2, top3, top4, top5, top6, top7, top8, top9, top10 = st.columns(
    [
        1.90,
        0.68,
        0.68,
        0.68,
        0.68,
        0.68,
        0.68,
        0.90,
        0.90,
        1.10
    ],
    gap="small"
)

# ============================================================
# MARCA
# ============================================================

with top1:

    st.html(
        f"""
        <div class="brand-mini">

            <div class="logo-mini">

                <img
                    src="{logo_data}"
                    alt="Rentas Camacho"
                    style="
                        width:42px;
                        height:42px;
                        object-fit:contain;
                    "
                >

            </div>

            <div>

                <div class="brand-mini-title">
                    Airbnb <span>Financial Hub</span>
                </div>

                <div class="brand-mini-sub">
                    Rentabilidad financiera · Solo Airbnb
                </div>

            </div>

        </div>
        """
    )

# ============================================================
# PORTAFOLIO
# ============================================================

with top2:

    if st.button(
        "",
        key="nav_portafolio",
        use_container_width=True,
        help="Portafolio"
    ):

        st.session_state.vista_airbnb = "Portafolio"
        st.rerun()


# ============================================================
# PROPIEDADES
# ============================================================

with top3:

    if st.button(
        "",
        key="nav_propiedades",
        use_container_width=True,
        help="Propiedades"
    ):

        st.session_state.vista_airbnb = "Propiedades"
        st.rerun()


# ============================================================
# OCUPACIÓN
# ============================================================

with top4:

    if st.button(
        "",
        key="nav_ocupacion",
        use_container_width=True,
        help="Ocupación"
    ):

        st.session_state.vista_airbnb = "Ocupación"
        st.rerun()


# ============================================================
# FINANCIERO
# ============================================================

with top5:

    if st.button(
        "",
        key="nav_financiero",
        use_container_width=True,
        help="Financiero"
    ):

        st.session_state.vista_airbnb = "Financiero"
        st.rerun()


# ============================================================
# ANÁLISIS
# ============================================================

with top6:

    if st.button(
        "",
        key="nav_analisis",
        use_container_width=True,
        help="Análisis"
    ):

        st.session_state.vista_airbnb = "Análisis"
        st.rerun()


# ============================================================
# REPORTES
# ============================================================

with top7:

    if st.button(
        "",
        key="nav_reportes",
        use_container_width=True,
        help="Reportes"
    ):

        st.session_state.vista_airbnb = "Reportes"
        st.rerun()


# ============================================================
# FILTRO CIUDAD
# ============================================================

with top8:

    st.markdown(
        '<div class="filter-label">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"]
        +
        sorted(
            df["Ciudad"]
            .dropna()
            .unique()
            .tolist()
        ),
        label_visibility="collapsed"
    )


# ============================================================
# FILTRO PROPIEDAD
# ============================================================

with top9:

    st.markdown(
        '<div class="filter-label">🏢 Propiedad</div>',
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

resumen = (
    resumen
    .sort_values(
        "Rentabilidad",
        ascending=False
    )
    .reset_index(drop=True)
)



# ============================================================
# TARJETA PROPIEDAD
# ============================================================

def tarjeta_propiedad(row):

    rent = float(
        row["Rentabilidad"]
    )

    good = rent >= 35

    progress = min(
        max(rent, 0),
        100
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

    if pd.isna(ocup):

        ocup_text = "—"

        detalle = "Sin datos de Airbnb"

    else:

        ocup_text = (
            f"{float(ocup):.1f}%"
        )

        if pd.isna(reservas):

            detalle = "Sin reservas"

        else:

            detalle = (
                f"{int(reservas)} reservas · "
                f"{int(noches)} noches"
            )

    return f"""
<div class="property-card {'negative' if not good else ''}">

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

<div class="property-profit-value {'good' if good else 'bad'}">
{rent:.1f}%
</div>

<div class="property-profit-label">
Rentabilidad
</div>

</div>

</div>

<div class="metrics-grid">

<div class="metric-box">

<div class="metric-label">
Ingresos
</div>

<div class="metric-value metric-income">
{dinero_corto(row["Ingresos"])}
</div>

</div>

<div class="metric-box">

<div class="metric-label">
Gastos
</div>

<div class="metric-value metric-expense">
{dinero_corto(row["Gastos"])}
</div>

</div>

<div class="metric-box">

<div class="metric-label">
Flujo
</div>

<div class="metric-value metric-flow">
{dinero_corto(row["Flujo"])}
</div>

</div>

</div>

<div class="profit-section">

<div class="profit-line">

<div class="profit-label">
Rentabilidad
</div>

<div class="profit-number {'good' if good else 'bad'}">
{rent:.1f}%
</div>

</div>

<div class="progress">

<div
class="progress-fill {'bad' if not good else ''}"
style="width:{progress:.1f}%;">
</div>

</div>

</div>

<div class="occupancy-box">

<div class="occupancy-top">

<div class="occupancy-label">
Ocupación Airbnb
</div>

<div class="occupancy-value">
{ocup_text}
</div>

</div>

<div class="occupancy-detail">
{detalle}
</div>

</div>

</div>
"""

# ============================================================
# TARJETA PORTAFOLIO
# ============================================================

def tarjeta_portafolio():

    progreso_rentabilidad = min(
        max((rentabilidad / 35) * 100, 0),
        100
    )

    return f"""
<div class="portfolio-card">
    <div class="portfolio-watermark-circle">
        <img
            src="{logo_data}"
            alt=""
        >
    </div>

    <div class="portfolio-title">

    <div class="portfolio-icon">
        <img
            src="{logo_data}"
            alt="Rentas Camacho"
        >
    </div>

        <div>
            Portafolio
        </div>

    </div>

    <div class="portfolio-main">
        {dinero_corto(ingresos)}
    </div>

    <div class="portfolio-main-label">
        Ingresos del período
    </div>

    <div class="portfolio-metrics">

        <div class="portfolio-metric">

            <div class="portfolio-metric-icon expense">
                📈
            </div>

            <div>
                <div class="portfolio-mini-label">
                    Gastos
                </div>

                <div class="portfolio-mini-value">
                    {dinero_corto(gastos)}
                </div>
            </div>

        </div>


        <div class="portfolio-metric">

            <div class="portfolio-metric-icon flow">
                🪙
            </div>

            <div>
                <div class="portfolio-mini-label">
                    Flujo
                </div>

                <div class="portfolio-mini-value">
                    {dinero_corto(flujo)}
                </div>
            </div>

        </div>

    </div>


    <div class="portfolio-divider"></div>


    <div class="portfolio-profit-row">

        <div class="portfolio-profit-block">

            <div class="portfolio-profit-label">
                Rentabilidad
            </div>

            <div class="portfolio-profit-value portfolio-profit">
                {rentabilidad:.1f}%
            </div>

            <div class="portfolio-progress">

                <div
                    class="portfolio-progress-fill"
                    style="width:{progreso_rentabilidad:.1f}%;">
                </div>

            </div>

        </div>


        <div class="portfolio-profit-block target">

            <div class="portfolio-profit-label">
                Objetivo
            </div>

            <div class="portfolio-profit-value portfolio-target">
                35%
            </div>

        </div>

    </div>

</div>
"""

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
    # RANKING + ACUMULADO
    # ========================================================

    ranking_col, acumulado_col = st.columns(
        [1.6, 1],
        gap="small"
    )


    with ranking_col:

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

        html = """
<div class="side-card">

<div class="side-title">
🏆 Top por ingresos
</div>

<div class="side-subtitle">
Período seleccionado
</div>
"""

        for _, row in ranking.iterrows():

            width = (
                row["Ingresos"]
                /
                max_rank
                *
                100
                if max_rank
                else 0
            )

            html += f"""
<div class="rank">

<div class="rank-name">
{row["Nombre_Propiedad"]}
</div>

<div class="rank-background">

<div
class="rank-fill"
style="width:{width:.1f}%;">
</div>

</div>

<div class="rank-number">
{dinero_corto(row["Ingresos"])}
</div>

</div>
"""

        html += "</div>"

        st.markdown(
            html,
            unsafe_allow_html=True
        )


    with acumulado_col:

        st.markdown(
            f"""
<div class="side-card">

<div class="side-title">
📅 Acumulado 2026
</div>

<div class="side-subtitle">
Desde enero hasta hoy
</div>

<div style="
font-size:28px;
font-weight:850;
color:#17345E;
margin-top:10px;
">
{dinero_corto(ingresos_ytd)}
</div>

<div class="side-subtitle">
Ingresos
</div>

<div style="
font-size:24px;
font-weight:850;
color:#009B70;
margin-top:9px;
">
{dinero_corto(flujo_ytd)}
</div>

<div class="side-subtitle">
Flujo
</div>

</div>
""",
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
