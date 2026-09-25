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

.portfolio-progress {
    width: 100%;
    height: 4px;
    background: rgba(255,255,255,.28);
    border-radius: 8px;
    overflow: hidden;
    margin-top: 4px;
}

.portfolio-progress-fill {
    height: 100%;
    background: #FFFFFF;
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
   TABLA DE ANÁLISIS DE INVERSIÓN
============================================================ */

.investment-panel {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 13px;
    padding: 15px 17px 12px;
    margin-top: 14px;
}

.investment-title {
    font-size: 15px;
    font-weight: 850;
    color: #17345E;
    margin-bottom: 2px;
}

.investment-subtitle {
    font-size: 9px;
    color: #8A98AA;
    margin-bottom: 12px;
}

.investment-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 10px;
    color: #4D6078;
}

.investment-table th {
    background: #F4F7FA;
    color: #71839A;
    font-size: 8px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 9px 10px;
    border-bottom: 1px solid #DCE5EE;
    text-align: right;
    white-space: nowrap;
}

.investment-table th:first-child,
.investment-table th:nth-child(2) {
    text-align: left;
}

.investment-table td {
    padding: 9px 10px;
    border-bottom: 1px solid #EDF1F5;
    text-align: right;
    white-space: nowrap;
}

.investment-table tr:last-child td {
    border-bottom: none;
}

.investment-table td:first-child {
    text-align: left;
    font-weight: 750;
    color: #17345E;
}

.investment-table td:nth-child(2) {
    text-align: left;
}

.investment-status {
    display: inline-block;
    padding: 3px 7px;
    border-radius: 20px;
    font-size: 8px;
    font-weight: 750;
    background: #E8F8F2;
    color: #008866;
}

.investment-status.development {
    background: #FFF3D9;
    color: #B57900;
}

.investment-money {
    color: #17345E;
    font-weight: 700;
}

.investment-flow-positive {
    color: #009B70;
}

.investment-flow-negative {
    color: #E84235;
}

.investment-muted {
    color: #A0ACBA;
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
        grid-template-columns: repeat(4, minmax(0, 1fr));
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

/* ============================================================
   ENCABEZADO SUPERIOR COMPACTO Y CENTRADO
   ============================================================ */

div[data-testid="stHorizontalBlock"]:has(.st-key-nav_portafolio) {
    min-height: 78px !important;
    height: 78px !important;
    padding: 5px 10px !important;
    margin-top: 12px !important;
    margin-bottom: -10px !important;
    box-sizing: border-box !important;
    align-items: center !important;
    top: 6px !important;
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
    padding: 5px 10px !important;
    box-sizing: border-box !important;
    align-items: center !important;
}}

/* ============================================================
   ICONOS PERSONALIZADOS — SIN RECUADRO BLANCO
   ============================================================ */

.st-key-nav_portafolio button,
.st-key-nav_propiedades button,
.st-key-nav_ocupacion button,
.st-key-nav_financiero button,
.st-key-nav_analisis button,
.st-key-nav_reportes button {{
    height: 62px !important;
    min-height: 62px !important;
    padding: 0 !important;
    margin: 0 !important;

    background-color: transparent !important;
    background-repeat: no-repeat !important;
    background-position: center center !important;
    background-size: 46px 46px !important;

    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;

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
# INVERSIONES POR PROPIEDAD
# ============================================================

@st.cache_data(ttl=300)
def cargar_inversiones():

    query = """
    SELECT
        Activo_Proyecto,
        ANY_VALUE(Ciudad) AS Ciudad,
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

    # ========================================================
    # INVERSIÓN TOTAL DEL ACTIVO
    # ========================================================
    # La inversión utilizada para el análisis corresponde al
    # valor total del activo: apartamento + amoblamiento +
    # equipamiento + demás inversión registrada.
    #
    # Excepciones definidas para el portafolio:
    # - Torre Acqua: inversión registrada + crédito
    # - Torre Evoca: inversión registrada (contado)
    # - Torre Ventto: valor total informado externamente
    # - Lotus: valor total del activo informado
    # - Santa Marina: inversión registrada + créditos
    # - Base Loft: inversión registrada ya incluye el crédito
    # - Tempus 49: inversión registrada + crédito
    # - Iwani: se mantiene la inversión registrada

    inversiones_totales = {
        "Torre Acqua": 174662034,
        "Torre Evoca": 172456719,
        "Torre Ventto": 190000000,
        "Lotus": 349775542,
        "Santa Marina": 181281438,
        "Base Loft": 166613251,
        "Tempus 49": 183969093,
    }

    for propiedad, valor in inversiones_totales.items():
        inversiones.loc[
            inversiones["Activo_Proyecto"] == propiedad,
            "Inversion"
        ] = valor

    return inversiones


# ============================================================
# CAPITAL REAL REGISTRADO + CDT HIPOTÉTICO
# ============================================================

# Para la comparación contra CDT se utiliza EXCLUSIVAMENTE
# el valor registrado en Vista_Inversiones_Prorrateadas.
# No se resta ni se suma deuda/crédito.
TASA_CDT_BENCHMARK_EA = 0.1231


@st.cache_data(ttl=300)
def cargar_capital_cdt(fecha_hoy):
    query = """
    SELECT
        Activo_Proyecto,
        DATE(Fecha) AS Fecha,
        SUM(Valor_Prorrateado_Calculado) AS Capital
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
      AND Fecha IS NOT NULL
      AND Valor_Prorrateado_Calculado IS NOT NULL
    GROUP BY Activo_Proyecto, DATE(Fecha)
    ORDER BY Activo_Proyecto, Fecha
    """

    capital = client.query(query).to_dataframe()

    if capital.empty:
        return pd.DataFrame(
            columns=[
                "Nombre_Propiedad",
                "Capital_Registrado",
                "Valor_CDT_Hoy",
                "Ganancia_CDT"
            ]
        )

    capital["Fecha"] = pd.to_datetime(
        capital["Fecha"], errors="coerce"
    )
    capital["Capital"] = pd.to_numeric(
        capital["Capital"], errors="coerce"
    ).fillna(0)

    fecha_hoy_ts = pd.Timestamp(fecha_hoy)

    capital["Dias"] = (
        fecha_hoy_ts - capital["Fecha"]
    ).dt.days.clip(lower=0)

    capital["Valor_CDT"] = (
        capital["Capital"]
        * (1 + TASA_CDT_BENCHMARK_EA)
        ** (capital["Dias"] / 365.25)
    )

    resultado = (
        capital
        .groupby("Activo_Proyecto", as_index=False)
        .agg(
            Capital_Registrado=("Capital", "sum"),
            Valor_CDT_Hoy=("Valor_CDT", "sum")
        )
        .rename(
            columns={"Activo_Proyecto": "Nombre_Propiedad"}
        )
    )

    resultado["Ganancia_CDT"] = (
        resultado["Valor_CDT_Hoy"]
        - resultado["Capital_Registrado"]
    )

    return resultado


# ============================================================
# CRÉDITOS, AMORTIZACIÓN Y VALOR ACTUAL DE LOS ACTIVOS
# ============================================================

# La hoja de Créditos representa la última cuota efectivamente
# registrada/pagada al cierre de agosto de 2026.
#
# Regla futura:
# - septiembre 2026 permanece pendiente hasta el día 30;
# - el día 30 de cada mes se agrega una cuota;
# - febrero utiliza el último día del mes.
#
# No se modifica la hoja de Google Sheets: la cuota futura se calcula
# dinámicamente en la aplicación.

FECHA_BASE_CUOTAS = date(2026, 8, 31)


def fecha_corte_cuota(fecha):
    """
    Día de aplicación de la cuota:
    día 30 de cada mes; si el mes no tiene 30, último día.
    """
    fecha = pd.Timestamp(fecha)
    ultimo_dia = (
        fecha + pd.offsets.MonthEnd(0)
    ).day

    dia = min(30, ultimo_dia)

    return date(
        fecha.year,
        fecha.month,
        dia
    )


def incremento_cuotas_desde_base(fecha):
    """
    Calcula cuántas cuotas nuevas se consideran aplicadas
    desde la base 31-ago-2026.

    Ejemplo:
    - 25-sep-2026 -> 0
    - 30-sep-2026 -> 1
    - 01-oct-2026 -> 1
    - 30-oct-2026 -> 2
    """
    fecha = pd.Timestamp(fecha)
    base = pd.Timestamp(FECHA_BASE_CUOTAS)

    diferencia_meses = (
        (fecha.year - base.year) * 12
        + (fecha.month - base.month)
    )

    if diferencia_meses <= 0:
        return 0

    corte = fecha_corte_cuota(fecha)

    if fecha.date() >= corte:
        return diferencia_meses

    return max(
        0,
        diferencia_meses - 1
    )


def calcular_amortizacion(
    valor_inicial,
    tasa_interes_ea,
    cuota_mensual,
    cuota_hasta
):
    """
    Amortización teórica por cuota.

    La tasa efectiva anual se convierte a tasa efectiva mensual.
    La cuota contractual se toma de la tabla de Créditos.
    El seguro NO se mezcla con capital/interés.
    """
    try:
        valor_inicial = float(valor_inicial)
        tasa_interes_ea = float(tasa_interes_ea)
        cuota_mensual = float(cuota_mensual)
        cuota_hasta = int(cuota_hasta)
    except (TypeError, ValueError):
        return pd.DataFrame()

    if (
        valor_inicial <= 0
        or cuota_mensual <= 0
        or cuota_hasta <= 0
    ):
        return pd.DataFrame()

    tasa_mensual = (
        (1 + tasa_interes_ea) ** (1 / 12)
        - 1
    )

    saldo = valor_inicial
    registros = []

    for numero_cuota in range(
        1,
        cuota_hasta + 1
    ):
        saldo_inicial = saldo

        interes = (
            saldo_inicial
            * tasa_mensual
        )

        capital = min(
            max(
                cuota_mensual
                - interes,
                0
            ),
            saldo_inicial
        )

        saldo = max(
            0,
            saldo_inicial - capital
        )

        registros.append(
            {
                "Cuota": numero_cuota,
                "Saldo_Inicial": saldo_inicial,
                "Interes_Teorico": interes,
                "Capital_Teorico": capital,
                "Cuota_Principal_Interes":
                    interes + capital,
                "Saldo_Final": saldo
            }
        )

        if saldo <= 0:
            break

    return pd.DataFrame(registros)


@st.cache_data(ttl=300)
def cargar_creditos(fecha_calculo):
    query = """
    SELECT
        ID_Credito,
        ID_Propiedad,
        Propiedad,
        Banco,
        Valor_Inicial,
        Saldo_Actual,
        Cuota_Mensual,
        Cuota,
        Tasa_Interes,
        Plazo_Meses,
        Cuota_Seguros,
        Valor_Actual,
        Equipamiento,
        Valor_Total_Actual,
        Patrimonio_Actual,
        Costo_Mensual_Total
    FROM `rentascamacho.rentas_cortas.Creditos_Vista`
    WHERE Propiedad IS NOT NULL
    """

    detalle = client.query(
        query
    ).to_dataframe()

    columnas_numericas = [
        "Valor_Inicial",
        "Saldo_Actual",
        "Cuota_Mensual",
        "Cuota",
        "Tasa_Interes",
        "Plazo_Meses",
        "Cuota_Seguros",
        "Valor_Actual",
        "Equipamiento",
        "Valor_Total_Actual",
        "Patrimonio_Actual",
        "Costo_Mensual_Total"
    ]

    for col in columnas_numericas:
        detalle[col] = pd.to_numeric(
            detalle[col],
            errors="coerce"
        )

    incremento = incremento_cuotas_desde_base(
        fecha_calculo
    )

    detalle["Cuota_Base"] = (
        detalle["Cuota"]
        .fillna(0)
        .astype(int)
    )

    detalle["Cuota_Actual"] = (
        detalle["Cuota_Base"]
        + incremento
    )

    detalle["Saldo_Teorico_Actual"] = 0.0
    detalle["Interes_Cuota_Actual"] = 0.0
    detalle["Capital_Cuota_Actual"] = 0.0

    for idx, row in detalle.iterrows():
        amortizacion = calcular_amortizacion(
            row["Valor_Inicial"],
            row["Tasa_Interes"],
            row["Cuota_Mensual"],
            row["Cuota_Actual"]
        )

        if amortizacion.empty:
            continue

        ultima = amortizacion.iloc[-1]

        detalle.loc[
            idx,
            "Saldo_Teorico_Actual"
        ] = ultima["Saldo_Final"]

        detalle.loc[
            idx,
            "Interes_Cuota_Actual"
        ] = ultima["Interes_Teorico"]

        detalle.loc[
            idx,
            "Capital_Cuota_Actual"
        ] = ultima["Capital_Teorico"]

    # Si el saldo real está diligenciado, se utiliza.
    # Si está vacío, se utiliza el saldo teórico de amortización.
    detalle["Saldo_Usado"] = (
        detalle["Saldo_Actual"]
        .where(
            detalle["Saldo_Actual"].notna(),
            detalle["Saldo_Teorico_Actual"]
        )
        .fillna(0)
    )

    # Consolidación por propiedad para valoración/patrimonio.
    # La amortización sigue siendo individual por crédito.
    creditos_propiedad = (
        detalle
        .groupby(
            "Propiedad",
            as_index=False
        )
        .agg(
            Saldo_Actual=(
                "Saldo_Actual",
                "sum"
            ),
            Saldo_Teorico_Actual=(
                "Saldo_Teorico_Actual",
                "sum"
            ),
            Saldo_Usado=(
                "Saldo_Usado",
                "sum"
            ),
            Cuota_Mensual=(
                "Cuota_Mensual",
                "sum"
            ),
            Cuota_Seguros=(
                "Cuota_Seguros",
                "sum"
            ),
            Valor_Actual=(
                "Valor_Actual",
                "max"
            ),
            Equipamiento=(
                "Equipamiento",
                "max"
            ),
            Valor_Total_Actual=(
                "Valor_Total_Actual",
                "max"
            ),
            Costo_Mensual_Total=(
                "Costo_Mensual_Total",
                "sum"
            ),
            Cuota_Actual=(
                "Cuota_Actual",
                "max"
            )
        )
    )

    creditos_propiedad["Patrimonio_Actual"] = (
        creditos_propiedad[
            "Valor_Total_Actual"
        ].fillna(0)
        -
        creditos_propiedad[
            "Saldo_Usado"
        ].fillna(0)
    )

    return detalle, creditos_propiedad


@st.cache_data(ttl=300)
def cargar_pagos_hipotecarios():
    """
    Pagos reales registrados en Movimientos_Operativos_Reparto.

    SUB-0032 = Crédito Hipotecario.
    Se agrupan por propiedad y mes para obtener el pago real
    efectivamente registrado, independientemente de la cuenta
    desde la cual se realizó el pago.
    """
    query = """
    SELECT
        DATE(Fecha) AS Fecha,
        Nombre_Propiedad AS Propiedad,
        SUM(Gasto) AS Pago_Real
    FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    WHERE TRIM(Subcategoria) = 'SUB-0032'
      AND LOWER(TRIM(Nombre_Subcategoria))
            = 'crédito hipotecario'
      AND LOWER(TRIM(Detalle))
            = 'crédito'
      AND Gasto IS NOT NULL
      AND Gasto > 0
    GROUP BY
        Fecha,
        Propiedad
    ORDER BY
        Propiedad,
        Fecha
    """

    pagos = client.query(
        query
    ).to_dataframe()

    if pagos.empty:
        return pagos

    pagos["Fecha"] = pd.to_datetime(
        pagos["Fecha"],
        errors="coerce"
    )

    pagos["Pago_Real"] = pd.to_numeric(
        pagos["Pago_Real"],
        errors="coerce"
    ).fillna(0)

    pagos["Mes"] = (
        pagos["Fecha"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    pagos_mensuales = (
        pagos
        .groupby(
            [
                "Propiedad",
                "Mes"
            ],
            as_index=False
        )["Pago_Real"]
        .sum()
        .sort_values(
            [
                "Propiedad",
                "Mes"
            ]
        )
        .reset_index(drop=True)
    )

    return pagos_mensuales


def calcular_amortizacion_historica(
    creditos_detalle,
    pagos_hipotecarios
):
    """
    Cruza pagos reales históricos con amortización teórica.

    Regla:
    - el último pago histórico se alinea con Cuota_Actual;
    - los pagos anteriores ocupan las cuotas anteriores;
    - el pago real se utiliza como monto efectivamente pagado;
    - el interés se calcula teóricamente;
    - el capital estimado es:
          pago real - interés teórico - seguro
      sin permitir capital negativo.

    Para propiedades con más de un crédito, el pago real mensual
    se distribuye proporcionalmente al costo contractual de cada
    crédito (cuota + seguro).
    """
    columnas_salida = [
        "Propiedad",
        "Pagos_Hipotecarios_Reales",
        "Interes_Historico_Estimado",
        "Seguro_Historico_Estimado",
        "Capital_Historico_Estimado",
        "Cuotas_Conciliadas"
    ]

    if (
        creditos_detalle.empty
        or pagos_hipotecarios.empty
    ):
        return pd.DataFrame(
            columns=columnas_salida
        )

    resultados = []

    for propiedad, grupo_creditos in (
        creditos_detalle
        .groupby("Propiedad")
    ):
        pagos_propiedad = (
            pagos_hipotecarios[
                pagos_hipotecarios[
                    "Propiedad"
                ] == propiedad
            ]
            .sort_values("Mes")
            .reset_index(drop=True)
        )

        if pagos_propiedad.empty:
            continue

        grupo_creditos = (
            grupo_creditos
            .copy()
            .reset_index(drop=True)
        )

        # Base contractual para repartir pagos entre
        # créditos de una misma propiedad.
        grupo_creditos["Base_Reparto"] = (
            grupo_creditos[
                "Cuota_Mensual"
            ].fillna(0)
            +
            grupo_creditos[
                "Cuota_Seguros"
            ].fillna(0)
        )

        base_total = (
            grupo_creditos[
                "Base_Reparto"
            ].sum()
        )

        for _, credito in grupo_creditos.iterrows():
            cuota_actual = int(
                credito["Cuota_Actual"]
            )

            n_pagos = len(
                pagos_propiedad
            )

            if n_pagos <= 0:
                continue

            # Los pagos reales conocidos se alinean hacia
            # atrás desde la cuota vigente.
            cuota_inicial = max(
                1,
                cuota_actual
                - n_pagos
                + 1
            )

            amortizacion = calcular_amortizacion(
                credito["Valor_Inicial"],
                credito["Tasa_Interes"],
                credito["Cuota_Mensual"],
                cuota_actual
            )

            if amortizacion.empty:
                continue

            amortizacion = (
                amortizacion
                .set_index("Cuota")
            )

            if base_total > 0:
                proporcion = (
                    credito["Base_Reparto"]
                    / base_total
                )
            else:
                proporcion = (
                    1
                    / len(grupo_creditos)
                )

            for posicion, pago in (
                pagos_propiedad
                .iterrows()
            ):
                numero_cuota = (
                    cuota_inicial
                    + posicion
                )

                if numero_cuota not in amortizacion.index:
                    continue

                fila_amort = (
                    amortizacion
                    .loc[numero_cuota]
                )

                pago_credito = (
                    pago["Pago_Real"]
                    * proporcion
                )

                interes = max(
                    0,
                    float(
                        fila_amort[
                            "Interes_Teorico"
                        ]
                    )
                )

                seguro = max(
                    0,
                    float(
                        credito[
                            "Cuota_Seguros"
                        ]
                    )
                )

                capital = max(
                    0,
                    pago_credito
                    - interes
                    - seguro
                )

                resultados.append(
                    {
                        "Propiedad": propiedad,
                        "Pago_Real": pago_credito,
                        "Interes": min(
                            interes,
                            pago_credito
                        ),
                        "Seguro": min(
                            seguro,
                            max(
                                0,
                                pago_credito
                                - min(
                                    interes,
                                    pago_credito
                                )
                            )
                        ),
                        "Capital": capital,
                        "Cuota": numero_cuota
                    }
                )

    if not resultados:
        return pd.DataFrame(
            columns=columnas_salida
        )

    detalle_amort = pd.DataFrame(
        resultados
    )

    resumen = (
        detalle_amort
        .groupby(
            "Propiedad",
            as_index=False
        )
        .agg(
            Pagos_Hipotecarios_Reales=(
                "Pago_Real",
                "sum"
            ),
            Interes_Historico_Estimado=(
                "Interes",
                "sum"
            ),
            Seguro_Historico_Estimado=(
                "Seguro",
                "sum"
            ),
            Capital_Historico_Estimado=(
                "Capital",
                "sum"
            ),
            Cuotas_Conciliadas=(
                "Cuota",
                "nunique"
            )
        )
    )

    return resumen


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

capital_cdt = cargar_capital_cdt(hoy)

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
# DATOS DE CRÉDITOS / VALOR ACTUAL
# ============================================================

creditos_detalle, creditos = cargar_creditos(hoy)

pagos_hipotecarios = cargar_pagos_hipotecarios()

amortizacion_historica = (
    calcular_amortizacion_historica(
        creditos_detalle,
        pagos_hipotecarios
    )
)


# ============================================================
# TARJETA PROPIEDAD
# ============================================================

def tarjeta_propiedad(row):

    rent = float(row["Rentabilidad"])
    good = rent >= 35

    progress = min(max(abs(rent) if rent < 0 else rent, 0), 100)

    ocup = row.get("Ocupacion", None)
    reservas = row.get("Reservas", None)
    noches = row.get("Noches_Reservadas", None)

    if pd.isna(ocup):
        ocup_text = "—"
        detalle = "—"
    else:
        ocup_text = f"{float(ocup):.1f}%"
        if pd.isna(reservas) or pd.isna(noches):
            detalle = "—"
        else:
            detalle = f"{int(reservas)} R · {int(noches)} N"

    ciudad = str(row["Ciudad"]).strip().lower()

    if ciudad == "bogotá":
        equipo = "team-bogota"
    elif ciudad in ["santa marta", "cartagena"]:
        equipo = "team-costa"
    elif ciudad == "medellín":
        equipo = "team-medellin"
    elif ciudad == "ibagué":
        equipo = "team-ibague"
    else:
        equipo = "team-bogota"

    return f"""
<div class="property-card {equipo}">

    <div class="property-header">
        <div>
            <div class="property-name">
                {row["Nombre_Propiedad"]}
            </div>
            <div class="property-city">
                {row["Ciudad"]}
            </div>
        </div>
    </div>

    <div class="property-income-main">
        {dinero_corto(row["Ingresos"])}
    </div>

    <div class="metrics-grid">

        <div class="metric-box">
            <div class="metric-content">
                <div class="metric-label">Gastos</div>
                <div class="metric-value metric-expense">
                    {dinero_corto(row["Gastos"])}
                </div>
            </div>
        </div>

        <div class="metric-box">
            <div class="metric-content">
                <div class="metric-label">Flujo</div>
                <div class="metric-value metric-flow">
                    {dinero_corto(row["Flujo"])}
                </div>
            </div>
        </div>

    </div>

    <div class="property-bottom">

        <div class="property-bottom-block">
            <div class="profit-label">Rentabilidad</div>
            <div class="profit-number {'good' if good else 'bad'}">
                {rent:.1f}%
            </div>
            <div class="progress">
                <div
                    class="progress-fill {'bad' if not good else ''}"
                    style="width:{progress:.1f}%;">
                </div>
            </div>
        </div>

        <div class="property-bottom-block occupancy">
            <div class="occupancy-label">Ocup. %</div>
            <div class="occupancy-value">
                {ocup_text}
            </div>
            <div class="occupancy-detail">
                {detalle}
            </div>
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

    <div class="portfolio-title">Portafolio</div>

    <div class="portfolio-main">
        {dinero_corto(ingresos)}
    </div>

    <div class="portfolio-metrics">

        <div class="portfolio-metric">
            <div class="portfolio-mini-label">Gastos</div>
            <div class="portfolio-mini-value">
                {dinero_corto(gastos)}
            </div>
        </div>

        <div class="portfolio-metric">
            <div class="portfolio-mini-label">Flujo</div>
            <div class="portfolio-mini-value">
                {dinero_corto(flujo)}
            </div>
        </div>

    </div>

    <div class="portfolio-profit-row">

        <div class="portfolio-profit-block">
            <div class="portfolio-profit-label">Rentabilidad</div>
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
            <div class="portfolio-profit-label">Objetivo</div>
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
    # TABLA DE ANÁLISIS DE INVERSIÓN
    # ========================================================

    tabla = inversiones.rename(
        columns={
            "Activo_Proyecto": "Nombre_Propiedad"
        }
    ).copy()

    # Estado del activo
    tabla["Estado"] = tabla["Nombre_Propiedad"].apply(
        lambda x: "En desarrollo"
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

    # ========================================================
    # HISTÓRICO FINANCIERO DESDE EL INICIO DE OPERACIÓN
    # ========================================================
    # La primera fecha registrada en los movimientos Airbnb
    # se toma como inicio de operación de cada propiedad.
    historico = (
        df
        .groupby("Nombre_Propiedad", as_index=False)
        .agg(
            Fecha_Inicio=("Fecha", "min"),
            Ingresos_Historicos=("Ingreso", "sum"),
            Gastos_Historicos=("Gasto", "sum")
        )
    )

    # ========================================================
    # CORRECCIÓN DE INGRESOS: TORRE ACQUA + TEMPUS 49
    # ========================================================
    # Los movimientos contables tienen el ingreso combinado de
    # ambas propiedades distribuido de forma incorrecta.
    # Airbnb_Prorrateado establece la proporción real:
    #   Torre Acqua = 70.322145948%
    #   Tempus 49   = 29.677854052%
    #
    # Se conserva exactamente el ingreso histórico combinado
    # y solamente se redistribuye entre las dos propiedades.

    propiedades_corregidas = [
        "Torre Acqua",
        "Tempus 49"
    ]

    ingreso_combinado = historico.loc[
        historico["Nombre_Propiedad"].isin(
            propiedades_corregidas
        ),
        "Ingresos_Historicos"
    ].sum()

    proporcion_acqua = 0.703221459479914
    proporcion_tempus = 0.296778540520086

    historico.loc[
        historico["Nombre_Propiedad"] == "Torre Acqua",
        "Ingresos_Historicos"
    ] = (
        ingreso_combinado
        * proporcion_acqua
    )

    historico.loc[
        historico["Nombre_Propiedad"] == "Tempus 49",
        "Ingresos_Historicos"
    ] = (
        ingreso_combinado
        * proporcion_tempus
    )

    # ========================================================
    # AMORTIZACIÓN HISTÓRICA
    # ========================================================
    # Los pagos hipotecarios reales permanecen intactos.
    # Solamente se separa el capital estimado para que no
    # permanezca como gasto económico.
    historico = historico.merge(
        amortizacion_historica[
            [
                "Propiedad",
                "Pagos_Hipotecarios_Reales",
                "Interes_Historico_Estimado",
                "Seguro_Historico_Estimado",
                "Capital_Historico_Estimado",
                "Cuotas_Conciliadas"
            ]
        ],
        left_on="Nombre_Propiedad",
        right_on="Propiedad",
        how="left"
    ).drop(
        columns=["Propiedad"],
        errors="ignore"
    )

    for col in [
        "Pagos_Hipotecarios_Reales",
        "Interes_Historico_Estimado",
        "Seguro_Historico_Estimado",
        "Capital_Historico_Estimado",
        "Cuotas_Conciliadas"
    ]:
        historico[col] = (
            historico[col]
            .fillna(0)
        )

    # Capital hipotecario no es gasto económico:
    # reduce deuda y aumenta patrimonio.
    historico["Gastos_Historicos_Ajustados"] = (
        historico["Gastos_Historicos"]
        - historico["Capital_Historico_Estimado"]
    ).clip(lower=0)

    historico["Flujo_Historico"] = (
        historico["Ingresos_Historicos"]
        - historico["Gastos_Historicos_Ajustados"]
    )

    hoy_ts = pd.Timestamp(hoy)
    historico["Meses_Operados"] = (
        (hoy_ts - historico["Fecha_Inicio"]).dt.days
        / 30.4375
    ).clip(lower=1)

    historico["Ingreso_Mensual_Promedio"] = (
        historico["Ingresos_Historicos"]
        / historico["Meses_Operados"]
    )

    historico["Flujo_Mensual_Promedio"] = (
        historico["Flujo_Historico"]
        / historico["Meses_Operados"]
    )

    historico["Flujo_Anualizado"] = (
        historico["Flujo_Mensual_Promedio"] * 12
    )

    historico = historico.merge(
        inversiones[["Activo_Proyecto", "Inversion"]],
        left_on="Nombre_Propiedad",
        right_on="Activo_Proyecto",
        how="left"
    ).drop(columns=["Activo_Proyecto"])

    historico["ROI_Acumulado"] = (
        historico["Flujo_Historico"]
        / historico["Inversion"]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        pd.NA
    )

    historico["Yield_Anualizado"] = (
        historico["Flujo_Anualizado"]
        / historico["Inversion"]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        pd.NA
    )

    tabla = tabla.drop(
        columns=[
            "Ingresos", "Gastos", "Flujo", "Rentabilidad",
            "Ocupacion", "Reservas", "Noches_Reservadas"
        ],
        errors="ignore"
    )

    tabla = tabla.merge(
        historico[
            [
                "Nombre_Propiedad",
                "Fecha_Inicio",
                "Ingresos_Historicos",
                "Gastos_Historicos",
                "Gastos_Historicos_Ajustados",
                "Capital_Historico_Estimado",
                "Interes_Historico_Estimado",
                "Seguro_Historico_Estimado",
                "Flujo_Historico",
                "Meses_Operados",
                "Ingreso_Mensual_Promedio",
                "Flujo_Mensual_Promedio",
                "Flujo_Anualizado",
                "ROI_Acumulado",
                "Yield_Anualizado"
            ]
        ],
        on="Nombre_Propiedad",
        how="left"
    )

    # ========================================================
    # VALOR ACTUAL / EQUIPAMIENTO / PATRIMONIO
    # ========================================================
    tabla = tabla.merge(
        creditos[
            [
                "Propiedad",
                "Saldo_Actual",
                "Valor_Actual",
                "Equipamiento",
                "Valor_Total_Actual",
                "Patrimonio_Actual",
                "Costo_Mensual_Total"
            ]
        ],
        left_on="Nombre_Propiedad",
        right_on="Propiedad",
        how="left"
    ).drop(columns=["Propiedad"], errors="ignore")

    # ========================================================
    # RETORNO ECONÓMICO TOTAL
    # ========================================================
    # Combina el flujo histórico generado por Airbnb con el
    # valor económico actual del activo.

    tabla["Valorizacion_Actual"] = (
        tabla["Valor_Total_Actual"]
        - tabla["Inversion"]
    )

    tabla["Ganancia_Economica"] = (
        tabla["Flujo_Historico"]
        + tabla["Valorizacion_Actual"]
    )

    tabla["ROI_Total"] = (
        tabla["Ganancia_Economica"]
        / tabla["Inversion"]
        * 100
    ).replace([float("inf"), -float("inf")], pd.NA)

    tabla["Retorno_Anualizado_Total"] = (
        (
            1 + tabla["ROI_Total"] / 100
        ) ** (1 / (tabla["Meses_Operados"] / 12))
        - 1
    ) * 100

    tabla.loc[
        tabla["Estado"] == "En desarrollo",
        [
            "Valorizacion_Actual",
            "Ganancia_Economica",
            "ROI_Total",
            "Retorno_Anualizado_Total"
        ]
    ] = pd.NA

    # ========================================================
    # ORDEN VISUAL IGUAL AL PORTAFOLIO
    # ========================================================
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

    def porcentaje_tabla(valor):
        if pd.isna(valor):
            return "—"
        return f'{float(valor):.1f}%'

    html_tabla = """
<div class="investment-panel">

<div class="investment-title">
📊 Análisis de inversión
</div>

<div class="investment-subtitle">
Desempeño histórico · capital hipotecario separado por amortización · valor neto de salida
</div>

<table class="investment-table">

<thead>
<tr>
<th>Propiedad</th>
<th>Estado</th>
<th>Inversión</th>
<th>Valor actual</th>
<th>Equipamiento</th>
<th>Valor neto salida</th>
<th>Ingresos hist.</th>
<th>Gastos hist. ajust.</th>
<th>Flujo hist.</th>
<th>ROI total</th>
<th>Ingreso prom./mes</th>
<th>Flujo prom./mes</th>
<th>Yield total anual</th>

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

        flujo = row["Flujo_Historico"]

        if pd.isna(flujo):
            flujo_html = '<span class="investment-muted">—</span>'
        elif float(flujo) < 0:
            flujo_html = (
                f'<span class="investment-flow-negative">'
                f'{dinero_corto(flujo)}'
                f'</span>'
            )
        else:
            flujo_html = (
                f'<span class="investment-flow-positive">'
                f'{dinero_corto(flujo)}'
                f'</span>'
            )

        roi_html = porcentaje_tabla(row["ROI_Total"])
        yield_html = porcentaje_tabla(row["Retorno_Anualizado_Total"])

        html_tabla += f"""
<tr>

<td>{nombre}</td>

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

<td>{valor_tabla(row["Valor_Actual"])}</td>

<td>{valor_tabla(row["Equipamiento"])}</td>

<td>
<span class="investment-money">
{valor_tabla(row["Patrimonio_Actual"])}
</span>
</td>

<td>{valor_tabla(row["Ingresos_Historicos"])}</td>

<td>{valor_tabla(row["Gastos_Historicos_Ajustados"])}</td>

<td>{flujo_html}</td>

<td>{roi_html}</td>

<td>{valor_tabla(row["Ingreso_Mensual_Promedio"])}</td>

<td>{valor_tabla(row["Flujo_Mensual_Promedio"])}</td>

<td>{yield_html}</td>

</tr>
"""

    html_tabla += """
</tbody>
</table>

<div style="
    margin-top:8px;
    font-size:8px;
    color:#8A98AA;
">
    * Gastos históricos ajustados: se excluye el capital hipotecario,
    tratado como amortización de deuda. Intereses y seguros permanecen
    como gasto. Los pagos reales provienen de Movimientos_Operativos_Reparto.
</div>

</div>
"""

    st.markdown(
        html_tabla,
        unsafe_allow_html=True
    )

    # ========================================================
    # RETORNO ECONÓMICO TOTAL
    # ========================================================

    st.markdown(
        """
        <div class="investment-panel" style="margin-top:12px;">
            <div class="investment-title">
                📈 Retorno económico total
            </div>
            <div class="investment-subtitle">
                Flujo histórico + valorización actual del activo · desde el inicio de operación
            </div>
        """,
        unsafe_allow_html=True
    )

    html_retorno = """
    <table class="investment-table">
    <thead>
    <tr>
        <th>Propiedad</th>
        <th>Inversión</th>
        <th>Flujo hist.</th>
        <th>Valor total actual</th>
        <th>Valorización</th>
        <th>Ganancia económica</th>
        <th>ROI total</th>
        <th>Retorno anualizado</th>
    </tr>
    </thead>
    <tbody>
    """

    for _, row in tabla.iterrows():

        valorizacion = row["Valorizacion_Actual"]
        ganancia = row["Ganancia_Economica"]
        roi_total = row["ROI_Total"]
        retorno_anual = row["Retorno_Anualizado_Total"]

        def retorno_dinero(valor):
            if pd.isna(valor):
                return '<span class="investment-muted">—</span>'
            clase = (
                "investment-flow-negative"
                if float(valor) < 0
                else "investment-flow-positive"
            )
            return (
                f'<span class="{clase}">'
                f'{dinero_corto(valor)}'
                f'</span>'
            )

        def retorno_porcentaje(valor):
            if pd.isna(valor):
                return '<span class="investment-muted">—</span>'
            clase = (
                "investment-flow-negative"
                if float(valor) < 0
                else "investment-flow-positive"
            )
            return (
                f'<span class="{clase}">'
                f'{float(valor):.1f}%'
                f'</span>'
            )

        html_retorno += f"""
        <tr>
            <td>{row["Nombre_Propiedad"]}</td>
            <td>{dinero_corto(row["Inversion"])}</td>
            <td>{retorno_dinero(row["Flujo_Historico"])}</td>
            <td>{valor_tabla(row["Valor_Total_Actual"])}</td>
            <td>{retorno_dinero(valorizacion)}</td>
            <td>{retorno_dinero(ganancia)}</td>
            <td>{retorno_porcentaje(roi_total)}</td>
            <td>{retorno_porcentaje(retorno_anual)}</td>
        </tr>
        """

    html_retorno += """
    </tbody>
    </table>
    </div>
    """

    st.markdown(
        html_retorno,
        unsafe_allow_html=True
    )

    # ========================================================
    # COMPARACIÓN: INMOBILIARIO VS CDT
    # ========================================================

    tabla_cdt = tabla.merge(
        capital_cdt,
        on="Nombre_Propiedad",
        how="left"
    )

    tabla_cdt["Resultado_Inmobiliario"] = (
        tabla_cdt["Flujo_Historico"].fillna(0)
        + tabla_cdt["Patrimonio_Actual"].fillna(0)
    )

    tabla_cdt["Diferencia_vs_CDT"] = (
        tabla_cdt["Resultado_Inmobiliario"]
        - tabla_cdt["Valor_CDT_Hoy"]
    )

    st.markdown(
        f"""
        <div class="investment-panel" style="margin-top:12px;">
            <div class="investment-title">
                🏦 Inmobiliario vs CDT
            </div>
            <div class="investment-subtitle">
                Mismo capital registrado en Vista_Inversiones_Prorrateadas,
                capitalizado desde cada fecha real de inversión ·
                benchmark CDT {TASA_CDT_BENCHMARK_EA * 100:.2f}% E.A.
            </div>
        """,
        unsafe_allow_html=True
    )

    html_cdt = """
    <table class="investment-table">
    <thead>
    <tr>
        <th>Propiedad</th>
        <th>Capital invertido</th>
        <th>Valor CDT hoy</th>
        <th>Ganancia CDT</th>
        <th>Flujo + valor neto salida</th>
        <th>Diferencia vs CDT</th>
    </tr>
    </thead>
    <tbody>
    """

    for _, row in tabla_cdt.iterrows():

        capital = row["Capital_Registrado"]
        valor_cdt = row["Valor_CDT_Hoy"]
        ganancia_cdt = row["Ganancia_CDT"]
        resultado_inmobiliario = row["Resultado_Inmobiliario"]
        diferencia = row["Diferencia_vs_CDT"]

        if pd.isna(capital):
            continue

        def cdt_money(valor):
            if pd.isna(valor):
                return '<span class="investment-muted">—</span>'

            clase = (
                "investment-flow-negative"
                if float(valor) < 0
                else "investment-flow-positive"
            )

            return (
                f'<span class="{clase}">'
                f'{dinero_corto(valor)}'
                f'</span>'
            )

        html_cdt += f"""
        <tr>
            <td>{row["Nombre_Propiedad"]}</td>
            <td>{dinero_corto(capital)}</td>
            <td>{dinero_corto(valor_cdt)}</td>
            <td>{cdt_money(ganancia_cdt)}</td>
            <td>{dinero_corto(resultado_inmobiliario)}</td>
            <td>{cdt_money(diferencia)}</td>
        </tr>
        """

    html_cdt += """
    </tbody>
    </table>

    <div style="
        margin-top:8px;
        font-size:8px;
        color:#8A98AA;
    ">
        El escenario CDT es hipotético: toma únicamente el capital
        registrado en la base de inversiones y respeta la fecha de cada
        inversión. No se incorpora deuda al capital CDT. El resultado
        inmobiliario suma el flujo histórico y el valor neto de salida.
    </div>

    </div>
    """

    st.markdown(
        html_cdt,
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
