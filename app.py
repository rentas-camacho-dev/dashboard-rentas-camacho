import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import textwrap
import requests
import re

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
    font-size: 16px;
    line-height: 1.05;
    font-weight: 850;
    color: #17345E;
    white-space: nowrap;
}

.brand-mini-title span {
    color: #FF3155;
}

.brand-mini-sub {
    font-size: 8px;
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
   Diseño compacto - contenido ajustado a 165px
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
   VISTA APORTES / CAPITAL FAMILIAR
============================================================ */
.aportes-panel { background:#FFFFFF; border:1px solid #DCE5EE; border-radius:14px; padding:16px 18px 14px; margin-top:12px; overflow:hidden; }
.aportes-title { font-size:18px; font-weight:850; color:#17345E; }
.aportes-subtitle { font-size:9px; color:#8A98AA; margin-top:4px; margin-bottom:12px; }
.aportes-kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:9px; margin-top:12px; }
.aportes-kpi { background:#F8FAFC; border:1px solid #E4EAF0; border-radius:12px; padding:11px 12px; min-height:78px; box-sizing:border-box; }
.aportes-kpi-label { font-size:8px; font-weight:800; color:#8290A4; text-transform:uppercase; }
.aportes-kpi-value { font-size:22px; font-weight:850; color:#17345E; margin-top:7px; line-height:1; }
.aportes-kpi-sub { font-size:8px; color:#8A98AA; margin-top:6px; }
.aportes-body-grid { display:grid; grid-template-columns:1.35fr .85fr; gap:12px; margin-top:12px; }
.aportes-card { background:#FFFFFF; border:1px solid #E1E8EF; border-radius:12px; padding:12px 14px; box-sizing:border-box; }
.aportes-card-title { font-size:11px; font-weight:850; color:#17345E; }
.aportes-card-subtitle { font-size:8px; color:#8A98AA; margin-top:3px; margin-bottom:9px; }
.aportes-row { display:grid; grid-template-columns:105px 1fr 78px; gap:8px; align-items:center; margin-top:10px; }
.aportes-row-name { font-size:9px; font-weight:750; color:#50637B; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.aportes-bar-bg { height:8px; background:#EEF2F6; border-radius:8px; overflow:hidden; }
.aportes-bar-fill { height:100%; background:linear-gradient(90deg,#7964DD 0%,#B37DE8 100%); border-radius:8px; }
.aportes-row-value { text-align:right; font-size:9px; font-weight:800; color:#17345E; }
.aportes-table { width:100%; border-collapse:separate; border-spacing:0; font-size:9px; color:#50637B; }
.aportes-table th { background:#F4F7FA; color:#71839A; font-size:7.5px; font-weight:800; text-transform:uppercase; padding:6px 9px; border-bottom:1px solid #DCE5EE; text-align:right; white-space:nowrap; }
.aportes-table th:first-child { text-align:left; }
.aportes-table td { padding:9px; border-bottom:1px solid #EDF1F5; text-align:right; white-space:nowrap; }
.aportes-table tr:last-child td { border-bottom:none; }
.aportes-table td:first-child { text-align:left; font-weight:800; color:#17345E; }
.aportes-total-row td { background:#F8FAFC; font-weight:850; border-top:1px solid #DCE5EE; }
.aportes-positive { color:#009B70; font-weight:800; }
.aportes-note { margin-top:10px; padding:9px 11px; background:#F8FAFC; border:1px solid #E5EBF1; border-radius:10px; font-size:8px; color:#71839A; line-height:1.45; }
.aportes-note b { color:#17345E; }
@media (max-width: 900px) { .aportes-kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .aportes-body-grid { grid-template-columns:1fr; } }

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
   ICONOS PERSONALIZADOS - SIN RECUADRO BLANCO
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
# ESTILOS - RADAR INMOBILIARIO
# ============================================================

st.markdown("""
<style>
.radar-panel {
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:16px 18px 12px;
    margin-top:12px;
    overflow-x:auto;
}
.radar-title {
    font-size:18px;
    font-weight:850;
    color:#17345E;
}
.radar-subtitle {
    font-size:9px;
    color:#8A98AA;
    margin-top:4px;
    margin-bottom:12px;
}
.radar-table {
    width:100%;
    border-collapse:separate;
    border-spacing:0;
    font-size:10px;
    color:#50637B;
    min-width:1080px;
}
.radar-table th {
    background:#F4F7FA;
    color:#71839A;
    font-size:8px;
    font-weight:800;
    text-transform:uppercase;
    padding:9px 8px;
    border-bottom:1px solid #DCE5EE;
    white-space:nowrap;
    text-align:center;
}
.radar-table th:first-child, .radar-table th:nth-child(2) { text-align:left; }
.radar-table td {
    padding:10px 8px;
    border-bottom:1px solid #EDF1F5;
    white-space:nowrap;
    text-align:center;
    vertical-align:middle;
}
.radar-table tr:last-child td { border-bottom:none; }
.radar-table td:first-child {
    text-align:left;
    font-weight:800;
    color:#17345E;
}
.radar-table td:nth-child(2) { text-align:left; color:#8290A4; font-size:9px; }
.radar-badge {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-width:62px;
    padding:4px 7px;
    border-radius:20px;
    font-size:8px;
    font-weight:800;
}
.radar-green { background:#E8F8F2; color:#008866; }
.radar-yellow { background:#FFF3D9; color:#B57900; }
.radar-red { background:#FDEBE9; color:#D33A2C; }
.radar-neutral { background:#EEF2F6; color:#71839A; }
.radar-number { font-weight:800; color:#17345E; }
.radar-positive { color:#009B70; font-weight:800; }
.radar-negative { color:#E84235; font-weight:800; }
.radar-note {
    font-size:8px;
    color:#8A98AA;
    margin-top:9px;
    line-height:1.45;
}
.radar-signal {
    margin-top:10px;
    padding:9px 11px;
    background:#F8FAFC;
    border:1px solid #E5EBF1;
    border-radius:10px;
    font-size:9px;
    color:#61738C;
}
.radar-signal b { color:#17345E; }
/* ============================================================
   RADAR EJECUTIVO - DECISIÓN DEL PORTAFOLIO
============================================================ */
.radar-decision-panel { background:#FFFFFF; border:1px solid #DCE5EE; border-radius:14px; padding:16px 18px 12px; margin-top:12px; overflow-x:auto; }
.radar-decision-title { font-size:18px; font-weight:850; color:#17345E; }
.radar-decision-subtitle { font-size:9px; color:#8A98AA; margin-top:4px; margin-bottom:12px; }
.radar-decision-table { width:100%; border-collapse:separate; border-spacing:0; font-size:10px; color:#50637B; min-width:1180px; }
.radar-decision-table th { background:#F4F7FA; color:#71839A; font-size:8px; font-weight:800; text-transform:uppercase; padding:9px 8px; border-bottom:1px solid #DCE5EE; white-space:nowrap; text-align:center; }
.radar-decision-table th:first-child, .radar-decision-table th:last-child { text-align:left; }
.radar-decision-table td { padding:10px 8px; border-bottom:1px solid #EDF1F5; text-align:center; vertical-align:middle; }
.radar-decision-table tr:last-child td { border-bottom:none; }
.radar-decision-table td:first-child { text-align:left; font-weight:800; color:#17345E; white-space:nowrap; }
.radar-decision-table td:last-child { text-align:left; color:#61738C; font-size:9px; line-height:1.35; min-width:300px; white-space:normal; }
.radar-decision-value { font-weight:800; color:#17345E; white-space:nowrap; }
.radar-decision-projection { font-weight:850; color:#17345E; white-space:nowrap; }
.radar-decision-badge { display:inline-flex; align-items:center; justify-content:center; padding:4px 8px; border-radius:20px; font-size:8px; font-weight:800; white-space:nowrap; }
.radar-decision-good { background:#E8F8F2; color:#008866; }
.radar-decision-medium { background:#FFF3D9; color:#B57900; }
.radar-decision-low { background:#FDEBE9; color:#D33A2C; }
.radar-decision-neutral { background:#EEF2F6; color:#71839A; }
.radar-status-green { background:#E8F8F2; color:#008866; }
.radar-status-yellow { background:#FFF3D9; color:#B57900; }
.radar-status-blue { background:#EAF2FF; color:#2867B2; }
.radar-status-neutral { background:#EEF2F6; color:#71839A; }
.radar-decision-maintain { background:#E8F8F2; color:#008866; }
.radar-decision-optimize { background:#EAF2FF; color:#2867B2; }
.radar-decision-sell { background:#FFF0E8; color:#C65A16; }
.radar-decision-review { background:#FFF3D9; color:#B57900; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FORMATO DINERO
# ============================================================

def fecha_corta_es(valor):
    if pd.isna(valor):
        return "-"

    ts = pd.Timestamp(valor)

    meses = {
        1: "Ene",
        2: "Feb",
        3: "Mar",
        4: "Abr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dic",
    }

    return f"{ts.day:02d} {meses.get(ts.month, '')} {ts.year}"


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
        Nombre_Subcategoria,
        Detalle,
        Nombre_Cuenta,
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
        "Nombre_Socio",
        "Nombre_Subcategoria",
        "Detalle",
        "Nombre_Cuenta"
    ]:

        df[col] = (
            df[col]
            .fillna("Sin información")
            .astype(str)
        )

    return df


# ============================================================
# APORTES DE SOCIOS - CAPITAL REAL APORTADO
# ============================================================

@st.cache_data(ttl=300)
def cargar_aportes_socios():
    query = (
        "SELECT ID_Aporte, DATE(Fecha) AS Fecha, Socio, Nombre_Socio, "
        "Categoria, Nombre_Categoria, Subcategoria, Nombre_Subcategoria, "
        "Detalle, Valor, Cuenta, Nombre_Cuenta, Observaciones "
        "FROM `rentascamacho.rentas_cortas.Aportes_Socios` "
        "WHERE Valor IS NOT NULL ORDER BY Fecha, Nombre_Socio"
    )

    aportes = client.query(query).to_dataframe()

    if aportes.empty:
        return pd.DataFrame(columns=[
            "ID_Aporte", "Fecha", "Socio", "Nombre_Socio",
            "Categoria", "Nombre_Categoria", "Subcategoria",
            "Nombre_Subcategoria", "Detalle", "Valor",
            "Cuenta", "Nombre_Cuenta", "Observaciones"
        ])

    aportes["Fecha"] = pd.to_datetime(aportes["Fecha"], errors="coerce")
    aportes["Valor"] = pd.to_numeric(aportes["Valor"], errors="coerce").fillna(0)

    for col in [
        "Nombre_Socio", "Nombre_Categoria", "Nombre_Subcategoria",
        "Detalle", "Nombre_Cuenta", "Observaciones"
    ]:
        aportes[col] = aportes[col].fillna("Sin información").astype(str).str.strip()

    return aportes


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
# ============================================================
# ============================================================
# ESTUDIO DE MERCADO INMOBILIARIO - BIGQUERY
# ============================================================

@st.cache_data(ttl=900)
def cargar_estudio_mercado_inmobiliario():
    query = """
    SELECT
        ID_Activo, Nombre_Entidad, Ciudad, Conjunto_Proyecto, Direccion,
        Venta_Min_M, Venta_Max_M,
        Renta_Amoblada_Min_M, Renta_Amoblada_Max_M,
        Renta_Sin_Amoblar_Min_M, Renta_Sin_Amoblar_Max_M,
        Facilidad_Venta, Facilidad_Arriendo,
        Proyeccion_Zona_5A, Rol_Portafolio
    FROM `rentascamacho.rentas_cortas.Estudio_Mercado_Inmobiliario`
    ORDER BY ID_Activo
    """
    estudio = client.query(query).to_dataframe()

    # ============================================================
    # ELIMINAR FILAS VACÍAS DEL ESTUDIO DE MERCADO
    # ============================================================
    estudio["ID_Activo"] = (
        estudio["ID_Activo"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    estudio = estudio[
        estudio["ID_Activo"] != ""
    ].copy()

    numeric_cols = [
        "Venta_Min_M", "Venta_Max_M",
        "Renta_Amoblada_Min_M", "Renta_Amoblada_Max_M",
        "Renta_Sin_Amoblar_Min_M", "Renta_Sin_Amoblar_Max_M",
        "Proyeccion_Zona_5A"
    ]

    # La hoja de Google Sheets usa coma decimal en la proyección
    # (ej. 7,8 y 7,5). BigQuery la puede entregar como STRING.
    # Convertimos coma decimal a punto antes de pasar a número.
    estudio["Proyeccion_Zona_5A"] = (
        estudio["Proyeccion_Zona_5A"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
    )

    for col in numeric_cols:
        estudio[col] = pd.to_numeric(estudio[col], errors="coerce")
    text_cols = [
        "ID_Activo", "Nombre_Entidad", "Ciudad", "Conjunto_Proyecto",
        "Direccion", "Facilidad_Venta", "Facilidad_Arriendo",
        "Rol_Portafolio"
    ]
    for col in text_cols:
        estudio[col] = estudio[col].fillna("").astype(str)

    # ------------------------------------------------------------
    # RADAR = SOLO FINCA RAÍZ
    # La categoría maestra del activo es la fuente de verdad.
    # Normalizamos tildes/espacios para aceptar "Finca Raíz" o
    # "Finca Raiz" sin dejar entrar Comercio ni Vehículos.
    # ------------------------------------------------------------
    categoria_radar = (
        estudio["Conjunto_Proyecto"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("ascii")
    )

    estudio = estudio[
        categoria_radar.eq("finca raiz")
    ].copy()

    return estudio


def rango_millones(minimo, maximo):
    if pd.isna(minimo) and pd.isna(maximo):
        return "-"
    if pd.isna(maximo):
        return f"${float(minimo)/1_000_000:.1f}M"
    if pd.isna(minimo):
        return f"${float(maximo)/1_000_000:.1f}M"
    return f"${float(minimo)/1_000_000:.1f}–{float(maximo)/1_000_000:.1f}M"


def generar_decision_estrategica_radar(
    row,
    comparable
):
    """Genera un estatus breve + lectura estratégica del Radar.

    El estatus se deriva de los números visibles del Radar:
    renta amoblada, Airbnb comparable, proyección de zona y liquidez.
    Tempus 49 conserva una excepción explícita por uso familiar.
    No utiliza Rol_Portafolio para redactar la explicación.
    """

    id_activo = str(row.get("ID_Activo", ""))

    valor = rango_millones(
        row.get("Venta_Min_M"),
        row.get("Venta_Max_M")
    )

    renta = rango_millones(
        row.get("Renta_Amoblada_Min_M"),
        row.get("Renta_Amoblada_Max_M")
    )

    renta_min = pd.to_numeric(
        row.get("Renta_Amoblada_Min_M"),
        errors="coerce"
    )
    renta_max = pd.to_numeric(
        row.get("Renta_Amoblada_Max_M"),
        errors="coerce"
    )
    renta_media = (
        (float(renta_min) + float(renta_max)) / 2
        if pd.notna(renta_min) and pd.notna(renta_max)
        else pd.NA
    )

    venta = str(row.get("Facilidad_Venta", "-") or "-").strip()

    proyeccion_val = pd.to_numeric(
        row.get("Proyeccion_Zona_5A"),
        errors="coerce"
    )
    proyeccion = (
        f"{float(proyeccion_val):.1f}/10"
        if pd.notna(proyeccion_val)
        else "sin dato"
    )

    comparable_val = pd.to_numeric(comparable, errors="coerce")
    comparable_txt = (
        dinero_corto(comparable_val)
        if pd.notna(comparable_val)
        else "sin dato"
    )

    # --------------------------------------------------------
    # TEMPUS 49 - uso familiar cambia la lectura financiera
    # --------------------------------------------------------
    if id_activo == "ENT-0004":
        return (
            "Uso familiar",
            "El ingreso Airbnb no es representativo por el uso familiar; el activo conserva valor y la decisión depende de la necesidad de vivienda."
        )

    # --------------------------------------------------------
    # AIRBNB COMPETITIVO
    # Cuando el Airbnb comparable supera o se acerca a la renta
    # amoblada media, el modelo actual sigue siendo competitivo.
    # --------------------------------------------------------
    if pd.notna(comparable_val) and pd.notna(renta_media):
        diferencia = float(comparable_val) - float(renta_media)

        if diferencia >= -100_000:
            return (
                "Airbnb competitivo",
                f"Airbnb comparable {comparable_txt} frente a renta amoblada {renta}; el modelo actual sigue siendo competitivo."
            )

    # --------------------------------------------------------
    # POTENCIAL DE VALORIZACIÓN
    # Una proyección alta puede dominar la decisión aunque exista
    # una alternativa de renta mejor; la tesis principal pasa a ser
    # la valorización futura del activo.
    # --------------------------------------------------------
    if pd.notna(proyeccion_val) and float(proyeccion_val) >= 8.5:
        return (
            "Potencial de valorización",
            f"Proyección de zona {proyeccion}, valor {valor} y renta amoblada {renta}; el atractivo principal está en la evolución esperada de la zona."
        )

    # --------------------------------------------------------
    # PROBAR RENTA TRADICIONAL
    # Hay una brecha relevante a favor de la renta amoblada y la
    # proyección no domina la tesis del activo.
    # --------------------------------------------------------
    if pd.notna(comparable_val) and pd.notna(renta_media):
        brecha = float(renta_media) - float(comparable_val)

        if brecha >= 250_000:
            return (
                "Probar renta tradicional",
                f"Renta amoblada {renta} supera el Airbnb comparable de {comparable_txt}; conviene probar el modelo antes de vender."
            )

    # --------------------------------------------------------
    # EQUILIBRIO / AIRBNB COMPETITIVO POR AUSENCIA DE BRECHA
    # --------------------------------------------------------
    return (
        "Airbnb competitivo",
        f"Valor {valor}, renta amoblada {renta}, proyección {proyeccion} y Airbnb comparable {comparable_txt}; no aparece una alternativa claramente superior."
    )


def clase_decision(decision):
    d = str(decision or "").upper()
    if "AIRBNB COMPETITIVO" in d:
        return "radar-status-green"
    if "POTENCIAL DE VALORIZACIÓN" in d:
        return "radar-status-green"
    if "PROBAR RENTA TRADICIONAL" in d:
        return "radar-status-yellow"
    if "USO FAMILIAR" in d:
        return "radar-status-blue"
    return "radar-status-neutral"


def clase_venta(facilidad):
    f = str(facilidad or "").upper()
    if "BUENA" in f:
        return "radar-decision-good"
    if "MEDIA" in f:
        return "radar-decision-medium"
    if "BAJA" in f:
        return "radar-decision-low"
    return "radar-decision-neutral"


def escape_html(valor):
    return (
        str(valor)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def calcular_airbnb_comparable_radar(
    df_base,
    fecha_fin_radar
):
    """
    Calcula el ingreso Airbnb comparable mensual YTD para el Radar.

    Ingreso:
        acumulado del año / meses completos transcurridos.

    Gastos:
        primero suma de registros prorrateados del mismo mes;
        luego promedio únicamente de los meses con información.

    Si una categoría no tiene información:
        se toma como 0.

    No se descuentan:
        administración, inmobiliaria ni comisiones.
    """

    fecha_fin_ts = pd.Timestamp(
        fecha_fin_radar
    )

    anio = int(
        fecha_fin_ts.year
    )

    if anio == int(hoy.year):

        ultimo_mes_cerrado = (
            pd.Timestamp(
                hoy.year,
                hoy.month,
                1
            )
            - pd.offsets.MonthEnd(1)
        )

        fecha_corte = min(
            fecha_fin_ts,
            ultimo_mes_cerrado
        )

        meses = max(
            1,
            int(fecha_corte.month)
        )

    else:

        fecha_corte = pd.Timestamp(
            anio,
            12,
            31
        )

        meses = 12

    anual = df_base[
        (df_base["Fecha"].dt.year == anio)
        &
        (df_base["Fecha"] <= fecha_corte)
    ].copy()

    if anual.empty:

        return pd.DataFrame(
            columns=[
                "Nombre_Propiedad",
                "Ingreso_Mensual_Radar",
                "Airbnb_Comparable_Mensual"
            ]
        )

    for col in [
        "Nombre_Subcategoria",
        "Detalle",
        "Nombre_Cuenta"
    ]:

        if col not in anual.columns:
            anual[col] = ""

        anual[col] = (
            anual[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    anual["_Texto_Gasto_Radar"] = (
        anual["Nombre_Subcategoria"]
        + " "
        + anual["Detalle"]
        + " "
        + anual["Nombre_Cuenta"]
    ).str.lower()

    # ========================================================
    # INGRESO BRUTO
    # ========================================================
    ingresos = (
        anual
        .groupby(
            "Nombre_Propiedad",
            as_index=False
        )["Ingreso"]
        .sum()
        .rename(
            columns={
                "Ingreso":
                    "Ingreso_Anual_Radar"
            }
        )
    )

    # Misma distribución especial de Acqua + Tempus 49.
    mask_acqua_tempus = ingresos[
        "Nombre_Propiedad"
    ].isin(
        [
            "Torre Acqua",
            "Tempus 49"
        ]
    )

    ingreso_combinado = (
        ingresos.loc[
            mask_acqua_tempus,
            "Ingreso_Anual_Radar"
        ]
        .sum()
    )

    if ingreso_combinado > 0:

        ingresos.loc[
            ingresos["Nombre_Propiedad"]
            == "Torre Acqua",
            "Ingreso_Anual_Radar"
        ] = (
            ingreso_combinado
            * 0.703221459479914
        )

        ingresos.loc[
            ingresos["Nombre_Propiedad"]
            == "Tempus 49",
            "Ingreso_Anual_Radar"
        ] = (
            ingreso_combinado
            * 0.296778540520086
        )

    ingresos[
        "Ingreso_Mensual_Radar"
    ] = (
        ingresos["Ingreso_Anual_Radar"]
        / meses
    )

    # ========================================================
    # CLASIFICACIÓN DE GASTOS
    # ========================================================
    no_comparable = (
        anual["_Texto_Gasto_Radar"]
        .str.contains(
            r"\badministraci[oó]n\b|\binmobiliaria\b|\bcomisi[oó]n\b",
            regex=True,
            na=False
        )
    )

    validos = (
        (anual["Gasto"] > 0)
        &
        (~no_comparable)
    )

    categoria = pd.Series(
        "",
        index=anual.index,
        dtype="object"
    )

    mask_aseo = (
        validos
        &
        anual["_Texto_Gasto_Radar"].str.contains(
            r"\baseo\b|\blimpieza\b|\bcleaning\b",
            regex=True,
            na=False
        )
    )

    categoria.loc[
        mask_aseo
    ] = "ASEO"

    mask_internet = (
        validos
        &
        (categoria == "")
        &
        anual["_Texto_Gasto_Radar"].str.contains(
            r"\binternet\b|\bwifi\b|\bwi[\s-]?fi\b",
            regex=True,
            na=False
        )
    )

    categoria.loc[
        mask_internet
    ] = "INTERNET"

    mask_servicios = (
        validos
        &
        (categoria == "")
        &
        anual["_Texto_Gasto_Radar"].str.contains(
            (
                r"\bservicios?\s+p[úu]blicos?\b"
                r"|\benerg[ií]a\b"
                r"|\bagua\b"
                r"|\bacueducto\b"
                r"|\belectricidad\b"
                r"|\bluz\b"
                r"|\bgas\b"
            ),
            regex=True,
            na=False
        )
    )

    categoria.loc[
        mask_servicios
    ] = "SERVICIOS"

    anual["_Categoria_Radar"] = categoria

    gastos = anual[
        anual["_Categoria_Radar"] != ""
    ].copy()

    # Si no hay gastos comparables, comparable = ingreso bruto.
    if gastos.empty:

        resultado = ingresos[
            [
                "Nombre_Propiedad",
                "Ingreso_Mensual_Radar"
            ]
        ].copy()

        resultado[
            "Airbnb_Comparable_Mensual"
        ] = resultado[
            "Ingreso_Mensual_Radar"
        ]

        return resultado

    # ========================================================
    # CONSOLIDAR PRORRATEOS POR MES
    # ========================================================
    gastos["_Mes_Radar"] = (
        gastos["Fecha"]
        .dt.to_period("M")
        .astype(str)
    )

    gastos_mensuales = (
        gastos
        .groupby(
            [
                "Nombre_Propiedad",
                "_Categoria_Radar",
                "_Mes_Radar"
            ],
            as_index=False
        )["Gasto"]
        .sum()
    )

    # Promedio de los meses que sí tienen información.
    gastos_promedio = (
        gastos_mensuales
        .groupby(
            [
                "Nombre_Propiedad",
                "_Categoria_Radar"
            ],
            as_index=False
        )["Gasto"]
        .mean()
        .pivot(
            index="Nombre_Propiedad",
            columns="_Categoria_Radar",
            values="Gasto"
        )
        .reset_index()
    )

    for col in [
        "ASEO",
        "INTERNET",
        "SERVICIOS"
    ]:

        if col not in gastos_promedio.columns:
            gastos_promedio[col] = 0

    gastos_promedio = (
        gastos_promedio
        .rename(
            columns={
                "ASEO":
                    "Aseo_Radar",
                "INTERNET":
                    "Internet_Radar",
                "SERVICIOS":
                    "Servicios_Radar"
            }
        )
    )

    resultado = (
        ingresos[
            [
                "Nombre_Propiedad",
                "Ingreso_Mensual_Radar"
            ]
        ]
        .merge(
            gastos_promedio[
                [
                    "Nombre_Propiedad",
                    "Aseo_Radar",
                    "Internet_Radar",
                    "Servicios_Radar"
                ]
            ],
            on="Nombre_Propiedad",
            how="left"
        )
    )

    for col in [
        "Aseo_Radar",
        "Internet_Radar",
        "Servicios_Radar"
    ]:

        resultado[col] = (
            pd.to_numeric(
                resultado[col],
                errors="coerce"
            )
            .fillna(0)
        )

    resultado[
        "Airbnb_Comparable_Mensual"
    ] = (
        resultado["Ingreso_Mensual_Radar"]
        - resultado["Aseo_Radar"]
        - resultado["Internet_Radar"]
        - resultado["Servicios_Radar"]
    )

    return resultado[
        [
            "Nombre_Propiedad",
            "Ingreso_Mensual_Radar",
            "Airbnb_Comparable_Mensual"
        ]
    ]

# CAPITAL PROPIO / CASH + CDT HIPOTÉTICO
# ============================================================

# REGLA DEL CASH PARA EL CDT
# ------------------------------------------------------------
# El capital de comparación contra CDT sale EXCLUSIVAMENTE
# de la base real de inversiones:
#
#   Vista_Inversiones_Prorrateadas
#   SUM(Valor_Prorrateado_Calculado)
#
# NO se utilizan:
#   - ingresos Airbnb
#   - flujo histórico
#   - valor actual del inmueble
#   - patrimonio
#   - valorización
#   - créditos de otras propiedades
#
# ÚNICA EXCEPCIÓN:
# Base Loft tiene el crédito incluido dentro de la inversión
# registrada en la base, por lo que para obtener el CASH propio
# se descuenta únicamente su crédito inicial.
#
# Para todas las demás propiedades:
#   Capital propio = inversión registrada en la base
#
# Para Base Loft:
#   Capital propio = inversión registrada - crédito inicial
#
# Las fechas originales de cada inversión se conservan para
# capitalizar el CDT desde la fecha real de cada aporte.

# ============================================================
# TASAS CDT HISTÓRICAS POR AÑO
# ============================================================
# Benchmark hipotético para comparar cada aporte de capital
# contra un CDT, respetando la tasa correspondiente a cada año.
#
# 2020-2025: promedio anual utilizado para el ejercicio.
# 2026: promedio provisional del año, al ser un año aún abierto.
#
# La capitalización se hace año por año y conserva la fecha
# real de cada aporte de inversión.
#
TASAS_CDT_ANUALES = {
    2020: 0.0338,
    2021: 0.0207,
    2022: 0.0850,
    2023: 0.1321,
    2024: 0.1017,
    2025: 0.0896,
    2026: 0.1000,
}


def valor_cdt_historico(
    capital_inicial,
    fecha_inicio,
    fecha_fin
):
    """
    Capitaliza un aporte de capital utilizando la tasa anual
    correspondiente a cada año del período.

    Se utiliza capitalización efectiva anual prorrateada por
    fracción de año para los períodos parciales.
    """
    if (
        pd.isna(capital_inicial)
        or pd.isna(fecha_inicio)
        or pd.isna(fecha_fin)
    ):
        return float(capital_inicial or 0)

    valor = float(capital_inicial)

    inicio = pd.Timestamp(fecha_inicio)
    fin = pd.Timestamp(fecha_fin)

    if fin <= inicio:
        return valor

    for anio in range(
        inicio.year,
        fin.year + 1
    ):
        tasa = TASAS_CDT_ANUALES.get(anio)

        if tasa is None:
            continue

        inicio_anio = max(
            inicio,
            pd.Timestamp(anio, 1, 1)
        )

        fin_anio = min(
            fin,
            pd.Timestamp(anio + 1, 1, 1)
        )

        dias = (
            fin_anio - inicio_anio
        ).days

        if dias <= 0:
            continue

        valor *= (
            1 + tasa
        ) ** (
            dias / 365.25
        )

    return valor


@st.cache_data(ttl=300)
def cargar_capital_cdt(fecha_hoy):

    # --------------------------------------------------------
    # 1. INVERSIONES REALES DE LA BASE
    # --------------------------------------------------------
    query_inversiones = """
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
    GROUP BY
        Activo_Proyecto,
        DATE(Fecha)
    ORDER BY
        Activo_Proyecto,
        Fecha
    """

    capital = client.query(
        query_inversiones
    ).to_dataframe()

    if capital.empty:
        return pd.DataFrame(
            columns=[
                "Nombre_Propiedad",
                "Capital_Registrado",
                "Capital_Propio",
                "Valor_CDT_Hoy",
                "Ganancia_CDT",
                "CDT_Promedio"
            ]
        )

    capital["Fecha"] = pd.to_datetime(
        capital["Fecha"],
        errors="coerce"
    )

    capital["Capital"] = pd.to_numeric(
        capital["Capital"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # 2. ÚNICO CRÉDITO QUE SE DESCUENTA DEL CASH:
    #    BASE LOFT
    # --------------------------------------------------------
    query_credito_base_loft = """
    SELECT
        SUM(COALESCE(Valor_Inicial, 0)) AS Credito_Base_Loft
    FROM `rentascamacho.rentas_cortas.Creditos_Vista`
    WHERE Propiedad = 'Base Loft'
    """

    credito_base_loft = client.query(
        query_credito_base_loft
    ).to_dataframe()

    credito_base_loft = float(
        pd.to_numeric(
            credito_base_loft["Credito_Base_Loft"].iloc[0],
            errors="coerce"
        )
        if not credito_base_loft.empty
        else 0
    )

    if pd.isna(credito_base_loft):
        credito_base_loft = 0.0

    # --------------------------------------------------------
    # 3. CAPITAL CASH
    # --------------------------------------------------------
    #
    # Por defecto el CASH es exactamente el valor registrado
    # en la base de inversiones.
    #
    # Solo Base Loft recibe el ajuste por su crédito.
    #
    capital_por_propiedad = (
        capital
        .groupby("Activo_Proyecto")["Capital"]
        .transform("sum")
    )

    capital["Capital_Propio"] = capital["Capital"]

    mask_base_loft = (
        capital["Activo_Proyecto"] == "Base Loft"
    ) & (
        capital_por_propiedad > 0
    )

    # Como no tenemos la fecha histórica del desembolso del
    # crédito, la deducción se distribuye proporcionalmente
    # entre las inversiones de Base Loft. Esto conserva las
    # fechas originales para la capitalización del CDT.
    if credito_base_loft > 0:
        factor_base_loft = (
            (
                capital_por_propiedad[mask_base_loft]
                - credito_base_loft
            )
            / capital_por_propiedad[mask_base_loft]
        ).clip(
            lower=0,
            upper=1
        )

        capital.loc[
            mask_base_loft,
            "Capital_Propio"
        ] = (
            capital.loc[
                mask_base_loft,
                "Capital"
            ]
            * factor_base_loft
        )

    # --------------------------------------------------------
    # 4. CAPITALIZACIÓN DEL CDT
    # --------------------------------------------------------
    fecha_hoy_ts = pd.Timestamp(
        fecha_hoy
    )

    capital["Valor_CDT"] = capital.apply(
        lambda row: valor_cdt_historico(
            row["Capital_Propio"],
            row["Fecha"],
            fecha_hoy_ts
        ),
        axis=1
    )

    # --------------------------------------------------------
    # 5. TASA CDT PROMEDIO POR PROPIEDAD
    # --------------------------------------------------------
    # Promedio ponderado por capital y días de exposición.
    # Se calcula sobre los años para los cuales existe una tasa
    # definida en TASAS_CDT_ANUALES.
    fecha_hoy_ts = pd.Timestamp(fecha_hoy)
    capital["Dias_Exposicion"] = (
        fecha_hoy_ts - capital["Fecha"]
    ).dt.days.clip(lower=0)

    def tasa_promedio_fila(row):
        dias = int(row["Dias_Exposicion"])
        if dias <= 0 or row["Capital_Propio"] <= 0:
            return 0.0, 0.0

        inicio = pd.Timestamp(row["Fecha"])
        fin = fecha_hoy_ts
        suma = 0.0
        peso = 0.0

        for anio in range(inicio.year, fin.year + 1):
            tasa = TASAS_CDT_ANUALES.get(anio)
            if tasa is None:
                continue

            inicio_anio = max(inicio, pd.Timestamp(anio, 1, 1))
            fin_anio = min(fin, pd.Timestamp(anio + 1, 1, 1))
            dias_anio = max(0, (fin_anio - inicio_anio).days)

            if dias_anio > 0:
                peso_tramo = float(row["Capital_Propio"]) * dias_anio
                suma += peso_tramo * tasa
                peso += peso_tramo

        return suma, peso

    tasas_tmp = capital.apply(
        tasa_promedio_fila,
        axis=1,
        result_type="expand"
    )
    tasas_tmp.columns = ["Peso_Tasa_CDT", "Peso_Capital_CDT"]
    capital[["Peso_Tasa_CDT", "Peso_Capital_CDT"]] = tasas_tmp

    # --------------------------------------------------------
    # 6. RESUMEN POR PROPIEDAD
    # --------------------------------------------------------
    resultado = (
        capital
        .groupby(
            "Activo_Proyecto",
            as_index=False
        )
        .agg(
            Capital_Registrado=(
                "Capital",
                "sum"
            ),
            Capital_Propio=(
                "Capital_Propio",
                "sum"
            ),
            Valor_CDT_Hoy=(
                "Valor_CDT",
                "sum"
            ),
            Peso_Tasa_CDT=(
                "Peso_Tasa_CDT",
                "sum"
            ),
            Peso_Capital_CDT=(
                "Peso_Capital_CDT",
                "sum"
            )
        )
        .rename(
            columns={
                "Activo_Proyecto":
                    "Nombre_Propiedad"
            }
        )
    )

    resultado["CDT_Promedio"] = (
        resultado["Peso_Tasa_CDT"]
        / resultado["Peso_Capital_CDT"]
        * 100
    ).replace(
        [float("inf"), -float("inf")],
        pd.NA
    )

    resultado["Ganancia_CDT"] = (
        resultado["Valor_CDT_Hoy"]
        - resultado["Capital_Propio"]
    )

    return resultado
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

    st.session_state.vista_airbnb = "Aportes"

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
                    {(
                        "Aportes y patrimonio"
                        if st.session_state.vista_airbnb == "Aportes"
                        else "Airbnb Financial Hub"
                    )}
                </div>

                <div class="brand-mini-sub">
                    {(
                        "Capital · Predios · Deuda"
                        if st.session_state.vista_airbnb == "Aportes"
                        else "Rentabilidad financiera · Solo Airbnb"
                    )}
                </div>

            </div>

        </div>
        """
    )

# ============================================================
# APORTES
# ============================================================

with top2:

    if st.button(
        "",
        key="nav_portafolio",
        use_container_width=True,
        help="Aportes"
    ):

        st.session_state.vista_airbnb = "Aportes"
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

# Cargar aportes de socios antes de construir la vista Aportes
aportes_socios = cargar_aportes_socios()

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
        ocup_text = "-"
        detalle = "-"
    else:
        ocup_text = f"{float(ocup):.1f}%"
        if pd.isna(reservas) or pd.isna(noches):
            detalle = "-"
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
# ============================================================
# VISTA APORTES - CAPITAL Y PATRIMONIO FAMILIAR
# ============================================================

if st.session_state.vista_airbnb == "Aportes":

    def render_aportes_html(html, unsafe_allow_html=True):
        """Renderiza HTML evitando que la indentación rompa el layout."""
        limpio = "\n".join(
            linea.strip()
            for linea in str(html).splitlines()
            if linea.strip()
        )
        if hasattr(st, "html"):
            st.html(limpio)
        else:
            st.markdown(
                limpio,
                unsafe_allow_html=unsafe_allow_html
            )

    @st.cache_data(ttl=900)
    def cargar_estudio_mercado_prorrateado():
        query = """
        SELECT
            ID_Activo,
            Nombre_Entidad,
            Ciudad,
            Conjunto_Proyecto,
            Direccion,
            Venta_Min_M_Prorrateada,
            Venta_Max_M_Prorrateada,
            Renta_Amoblada_Min_M_Prorrateada,
            Renta_Amoblada_Max_M_Prorrateada,
            Renta_Sin_Amoblar_Min_M_Prorrateada,
            Renta_Sin_Amoblar_Max_M_Prorrateada,
            Facilidad_Venta,
            Facilidad_Arriendo,
            Proyeccion_Zona_5A,
            Rol_Portafolio,
            Socio,
            Nombre_Socio,
            Participaci__n,
            Propietario,
            Anuncio
        FROM `rentascamacho.rentas_cortas.Estudio_Mercado_Inmobiliario_Prorrateado`
        ORDER BY ID_Activo, Nombre_Socio
        """
        vista = client.query(query).to_dataframe()

        if vista.empty:
            return vista

        numeric_cols = [
            "Venta_Min_M_Prorrateada",
            "Venta_Max_M_Prorrateada",
            "Renta_Amoblada_Min_M_Prorrateada",
            "Renta_Amoblada_Max_M_Prorrateada",
            "Renta_Sin_Amoblar_Min_M_Prorrateada",
            "Renta_Sin_Amoblar_Max_M_Prorrateada",
            "Proyeccion_Zona_5A",
            "Participaci__n",
        ]
        for col in numeric_cols:
            vista[col] = pd.to_numeric(vista[col], errors="coerce")

        text_cols = [
            "ID_Activo", "Nombre_Entidad", "Ciudad", "Conjunto_Proyecto",
            "Direccion", "Facilidad_Venta", "Facilidad_Arriendo",
            "Rol_Portafolio", "Socio", "Nombre_Socio", "Propietario",
            "Anuncio"
        ]
        for col in text_cols:
            vista[col] = (
                vista[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        return vista

    @st.cache_data(ttl=900)
    def cargar_gastos_familiares_prorrateados():
        """
        Carga los gastos familiares y personales desde
        Movimientos_Operativos_Reparto.

        La tabla ya está prorrateada por socio, por lo que el
        Gasto se suma directamente por Nombre_Socio.

        Categorías exactas:
            - Gasto Familiar
            - Gasto Personal
        """
        try:
            query = """
            SELECT
                Nombre_Socio,
                SUM(
                    CASE
                        WHEN LOWER(TRIM(COALESCE(Nombre_Categoria, '')))
                            = 'gasto familiar'
                        THEN ABS(COALESCE(Gasto, 0))
                        ELSE 0
                    END
                ) AS Gastos_Familiares,

                SUM(
                    CASE
                        WHEN LOWER(TRIM(COALESCE(Nombre_Categoria, '')))
                            = 'gasto personal'
                        THEN ABS(COALESCE(Gasto, 0))
                        ELSE 0
                    END
                ) AS Gastos_Personales

            FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`

            WHERE LOWER(TRIM(COALESCE(Nombre_Categoria, '')))
                IN ('gasto familiar', 'gasto personal')

            GROUP BY Nombre_Socio
            """

            gastos = client.query(query).to_dataframe()

            if gastos.empty:
                return pd.DataFrame(
                    columns=[
                        "Nombre_Socio",
                        "Gastos_Familiares",
                        "Gastos_Personales",
                        "Gastos_Familiares_Personales",
                    ]
                )

            gastos["Nombre_Socio"] = (
                gastos["Nombre_Socio"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            for col in [
                "Gastos_Familiares",
                "Gastos_Personales",
            ]:
                gastos[col] = (
                    pd.to_numeric(
                        gastos[col],
                        errors="coerce"
                    )
                    .fillna(0)
                    .abs()
                )

            gastos["Gastos_Familiares_Personales"] = (
                gastos["Gastos_Familiares"]
                + gastos["Gastos_Personales"]
            )

            return gastos

        except Exception:
            return pd.DataFrame(
                columns=[
                    "Nombre_Socio",
                    "Gastos_Familiares",
                    "Gastos_Personales",
                    "Gastos_Familiares_Personales",
                ]
            )


    @st.cache_data(ttl=900)
    def cargar_creditos_prorrateados():
        """Carga deuda actual atribuible a cada socio desde la vista prorrateada."""
        try:
            query = """
            SELECT
                ID_Credito,
                ID_Activo,
                Propiedad,
                Banco,
                Socio,
                Nombre_Socio,
                Participacion_Efectiva,
                Valor_Inicial_Prorrateado,
                Saldo_Actual_Prorrateado,
                Cuota_Mensual_Prorrateada,
                Cuota_Seguros_Prorrateada,
                Tasa_Interes,
                Plazo_Meses
            FROM `rentascamacho.rentas_cortas.Creditos_Prorrateados`
            ORDER BY ID_Activo, Nombre_Socio, ID_Credito
            """
            creditos = client.query(query).to_dataframe()

            if creditos.empty:
                return creditos

            numeric_cols = [
                "Participacion_Efectiva",
                "Valor_Inicial_Prorrateado",
                "Saldo_Actual_Prorrateado",
                "Cuota_Mensual_Prorrateada",
                "Cuota_Seguros_Prorrateada",
                "Plazo_Meses",
            ]

            for col in numeric_cols:
                if col in creditos.columns:
                    creditos[col] = pd.to_numeric(
                        creditos[col],
                        errors="coerce"
                    ).fillna(0)

            for col in [
                "ID_Credito",
                "ID_Activo",
                "Propiedad",
                "Banco",
                "Socio",
                "Nombre_Socio",
                "Tasa_Interes",
            ]:
                if col in creditos.columns:
                    creditos[col] = (
                        creditos[col]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

            return creditos

        except Exception:
            return pd.DataFrame()


    @st.cache_data(ttl=900)
    def cargar_negocios_y_otros():
        """Carga participaciones no inmobiliarias. Valores monetarios se incorporan después."""
        try:
            query = """
            SELECT
                ID_Activo,
                Nombre,
                Sector,
                Ciudad,
                Nombre_Socio,
                Participaci__n
            FROM `rentascamacho.rentas_cortas.Participaciones`
            WHERE LOWER(TRIM(COALESCE(Sector, ''))) != 'finca raíz'
            ORDER BY Nombre, Nombre_Socio
            """
            df_no_inmo = client.query(query).to_dataframe()
            if df_no_inmo.empty:
                return df_no_inmo

            df_no_inmo["Participaci__n"] = pd.to_numeric(
                df_no_inmo["Participaci__n"],
                errors="coerce"
            )
            for col in ["ID_Activo", "Nombre", "Sector", "Ciudad", "Nombre_Socio"]:
                df_no_inmo[col] = (
                    df_no_inmo[col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )
            return df_no_inmo
        except Exception:
            return pd.DataFrame()

    aportes_base = aportes_socios.copy()
    vista_patrimonio = cargar_estudio_mercado_prorrateado()
    creditos_prorrateados = cargar_creditos_prorrateados()
    gastos_familiares = cargar_gastos_familiares_prorrateados()

    render_aportes_html("""
<style>
/* ============================================================
   APORTES - LAYOUT FINAL
============================================================ */
.aportes-wrap { margin-top: 2px; }

.aportes-kpi-grid6 {
    display:grid;
    grid-template-columns:repeat(6,minmax(0,1fr));
    gap:8px;
    margin:3px 0 11px;
}
.aportes-kpi6 {
    background:#FFFFFF;
    border:1px solid #E3E9F0;
    border-radius:12px;
    padding:8px 10px;
    min-height:70px;
    box-sizing:border-box;
    display:flex;
    align-items:center;
    gap:9px;
    box-shadow:0 1px 2px rgba(23,52,94,.025);
}
.aportes-kpi6-icon {
    width:30px;height:30px;border-radius:9px;
    display:flex;align-items:center;justify-content:center;
    font-size:15px;flex:0 0 30px;
}
.aportes-kpi6:nth-child(1) .aportes-kpi6-icon { background:#E8F8F1; }
.aportes-kpi6:nth-child(2) .aportes-kpi6-icon { background:#F1EAFE; }
.aportes-kpi6:nth-child(3) .aportes-kpi6-icon { background:#EAF2FF; }
.aportes-kpi6:nth-child(4) .aportes-kpi6-icon { background:#F6ECFF; }
.aportes-kpi6:nth-child(5) .aportes-kpi6-icon { background:#FFF0E5; }
.aportes-kpi6-label { font-size:7px;color:#7E8DA3;font-weight:800;line-height:1.15; }
.aportes-kpi6-value { font-size:18px;line-height:1.05;color:#17345E;font-weight:900;margin-top:5px;white-space:nowrap; }
.aportes-kpi6-sub { font-size:7px;color:#8795A8;margin-top:4px; }
.aportes-kpi-debt { color:#D64242 !important; }
.aportes-kpi-net { color:#17345E !important; }

.aportes-socios-grid {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:12px;
}
.aportes-socio-panel {
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:11px;
    box-sizing:border-box;
    min-height:480px;
    overflow:hidden;
}
.aportes-socio-panel.diego { border-top:3px solid #FF5A73; }
.aportes-socio-panel.william { border-top:3px solid #5DA7F4; }
.aportes-socio-panel.andres { border-top:3px solid #43C995; }
.aportes-socio-head { display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:5px; }
.aportes-avatar { width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:900; }
.aportes-avatar.diego { background:#FFE9EE;color:#FF5A73; }
.aportes-avatar.william { background:#EAF2FF;color:#5DA7F4; }
.aportes-avatar.andres { background:#E8F8F1;color:#43C995; }
.aportes-socio-name { font-size:14px;font-weight:900;color:#17345E; }
.aportes-header-total { margin-left:auto;text-align:right; }
.aportes-header-total-label { font-size:7px;font-weight:800;color:#8795A8;text-transform:uppercase;letter-spacing:.1px; }
.aportes-header-total-value { font-size:17px;font-weight:900;color:#17345E;line-height:1;margin-top:3px; }
.aportes-socio-layout { display:grid;grid-template-columns:0.94fr 1.06fr;gap:10px;align-items:start; }
.aportes-aporte-box { border-radius:10px;padding:10px 11px;background:#F8FAFC;border:1px solid #E5EBF1; }
.aportes-socio-panel.diego .aportes-aporte-box { background:#FFF5F7;border-color:#FFE0E7; }
.aportes-socio-panel.william .aportes-aporte-box { background:#F4F8FF;border-color:#DDEAFF; }
.aportes-socio-panel.andres .aportes-aporte-box { background:#F3FBF7;border-color:#D9F2E6; }
.aportes-box-title { font-size:9px;font-weight:900;color:#17345E;margin-bottom:9px; }
.aportes-socio-line { display:flex;justify-content:space-between;gap:6px;margin-top:7px;font-size:8.5px; }
.aportes-socio-line span:first-child { color:#71839A; }
.aportes-socio-line span:last-child { color:#17345E;font-weight:850; }
.aportes-socio-total-line { margin-top:9px;padding-top:8px;border-top:1px solid #DFE7EF;display:flex;justify-content:space-between;font-size:9px;font-weight:900;color:#17345E; }
.aportes-finca-title { font-size:10px;font-weight:900;color:#17345E;margin-bottom:2px; }
.aportes-finca-sub { font-size:7.5px;color:#8795A8;margin-bottom:2px; }
.aportes-donut-wrap { min-height:275px; }
.aportes-adicionales-title { font-size:9px;font-weight:900;color:#17345E;margin-top:4px;margin-bottom:4px; }
.aportes-mini-asset { display:flex;justify-content:space-between;gap:8px;padding:5px 8px;margin-top:4px;border:1px solid #E7EDF3;border-radius:8px;background:#FAFBFC; }
.aportes-mini-asset-name { font-size:8.5px;color:#5F7189;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }
.aportes-mini-asset-value { font-size:8.5px;font-weight:900;color:#17345E;white-space:nowrap; }
.aportes-additional { color:#7757C8;font-weight:800; }
.aportes-patrimonio-strip { margin-top:9px;border-top:1px solid #E6ECF2;padding-top:9px;display:flex;justify-content:space-between;align-items:flex-end; }
.aportes-patrimonio-label { font-size:9px;font-weight:850;color:#71839A; }
.aportes-patrimonio-value { font-size:21px;font-weight:900;color:#17345E;line-height:1; }
.aportes-patrimonio-ratio { font-size:8px;font-weight:850;color:#009B70;margin-top:4px;text-align:right; }

.aportes-otros-panel { background:#FFFFFF;border:1px solid #DCE5EE;border-radius:14px;padding:14px 16px 10px;margin-top:13px;overflow-x:auto; }
.aportes-card-title2 { font-size:15px;font-weight:900;color:#17345E; }
.aportes-card-sub2 { font-size:8.5px;color:#8A98AA;margin-top:4px;margin-bottom:9px; }
.aportes-table2 { width:100%;border-collapse:separate;border-spacing:0;font-size:9.5px;color:#50637B;min-width:950px; }
.aportes-table2 th { background:#F4F7FA;color:#71839A;font-size:8px;font-weight:800;text-transform:uppercase;padding:10px 10px;border-bottom:1px solid #DCE5EE;text-align:right;white-space:nowrap; }
.aportes-table2 th:first-child,.aportes-table2 th:nth-child(2){text-align:left;}
.aportes-table2 td { padding:10px 10px;border-bottom:1px solid #EDF1F5;text-align:right;white-space:nowrap; }
.aportes-table2 tr:last-child td { border-bottom:none; }
.aportes-table2 td:first-child{text-align:left;font-weight:800;color:#17345E;}
.aportes-table2 td:nth-child(2){text-align:left;color:#8290A4;}
.aportes-badge { display:inline-flex;align-items:center;padding:3px 7px;border-radius:20px;background:#EEF2F6;color:#61738C;font-size:7.5px;font-weight:800; }
.aportes-badge-warn { background:#FFF3D9; color:#A56B00; }
.aportes-money-muted { color:#8B98AA; font-weight:800; }
.aportes-note2 { margin-top:8px;padding:8px 10px;background:#F8FAFC;border:1px solid #E5EBF1;border-radius:9px;font-size:7.5px;color:#71839A;line-height:1.45; }

@media (max-width: 1200px) {
    .aportes-kpi-grid6 { grid-template-columns:repeat(3,minmax(0,1fr)); }
    .aportes-socios-grid { grid-template-columns:1fr; }
}
@media (max-width: 700px) {
    .aportes-kpi-grid6 { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .aportes-socio-layout { grid-template-columns:1fr; }
}
</style>
""", unsafe_allow_html=True)

    if aportes_base.empty:
        render_aportes_html("""
<div class="aportes-otros-panel">
    <div class="aportes-card-title2">💰 Aportes y patrimonio familiar</div>
    <div class="aportes-card-sub2">No se encontraron registros en Aportes_Socios.</div>
</div>
""", unsafe_allow_html=True)
    elif vista_patrimonio.empty:
        render_aportes_html("""
<div class="aportes-otros-panel">
    <div class="aportes-card-title2">💰 Aportes y patrimonio familiar</div>
    <div class="aportes-card-sub2">La vista Estudio_Mercado_Inmobiliario_Prorrateado no devolvió registros.</div>
</div>
""", unsafe_allow_html=True)
    else:
        # --------------------------------------------------------
        # NORMALIZACIÓN
        # --------------------------------------------------------
        aportes_base["Fecha"] = pd.to_datetime(aportes_base["Fecha"], errors="coerce")
        aportes_base["Valor"] = pd.to_numeric(aportes_base["Valor"], errors="coerce").fillna(0)
        aportes_base = aportes_base.dropna(subset=["Fecha"]).copy()

        vista_patrimonio = vista_patrimonio.copy()
        vista_patrimonio["Valor_Mercado_Socio"] = pd.to_numeric(
            vista_patrimonio["Venta_Min_M_Prorrateada"],
            errors="coerce"
        ).fillna(0)

        # --------------------------------------------------------
        # APORTE BRUTO vs. CAPITAL NETO APORTADO
        # --------------------------------------------------------
        # Los aportes brutos vienen exclusivamente de Aportes_Socios.
        # Los gastos familiares y personales vienen de las categorías exactas
        # Nombre_Categoria = 'Gasto Familiar' / 'Gasto Personal' en
        # Movimientos_Operativos_Reparto, que ya está prorrateado
        # por socio.
        # --------------------------------------------------------

        socios = (
            aportes_base
            .groupby("Nombre_Socio", as_index=False)
            .agg(
                Aportes_Brutos=("Valor", "sum"),
                Movimientos=("ID_Aporte", "nunique"),
                Primer_Aporte=("Fecha", "min"),
                Ultimo_Aporte=("Fecha", "max")
            )
            .sort_values("Aportes_Brutos", ascending=False)
            .reset_index(drop=True)
        )

        # Gastos familiares atribuibles a cada socio.
        socios = socios.merge(
            gastos_familiares,
            on="Nombre_Socio",
            how="left"
        )

        for col in [
            "Gastos_Familiares",
            "Gastos_Personales",
            "Gastos_Familiares_Personales",
        ]:
            socios[col] = (
                pd.to_numeric(
                    socios[col],
                    errors="coerce"
                )
                .fillna(0)
                .abs()
            )

        # Capital neto realmente aportado:
        # aportes registrados - gastos familiares - gastos personales.
        socios["Aportes"] = (
            socios["Aportes_Brutos"]
            - socios["Gastos_Familiares_Personales"]
        ).clip(lower=0)

        nombres_socios = socios["Nombre_Socio"].tolist()
        nombres_socios_set = set(nombres_socios)

        total_aportes_brutos = float(
            socios["Aportes_Brutos"].sum()
        )

        total_gastos_familiares = float(
            socios["Gastos_Familiares"].sum()
        )

        total_gastos_personales = float(
            socios["Gastos_Personales"].sum()
        )

        total_gastos_familiares_personales = float(
            socios["Gastos_Familiares_Personales"].sum()
        )

        total_aportes = float(
            socios["Aportes"].sum()
        )

        socios["Participacion"] = (
            socios["Aportes"] / total_aportes * 100
            if total_aportes else 0
        )

        # --------------------------------------------------------
        # CLASIFICACIÓN PATRIMONIAL POR CATEGORÍA
        # Conjunto_Proyecto es la fuente de verdad:
        #   - Finca Raíz
        #   - Comercio
        #   - Vehículos
        #
        # Un activo solo entra al "patrimonio conjunto" cuando:
        #   1) es Finca Raíz, y
        #   2) aparecen los 3 socios.
        #
        # Todo lo demás queda como activo adicional, pero conserva
        # su categoría para poder mostrar Finca Raíz + Comercio +
        # Vehículos sin mezclar RIE ni Carro Padre con la Finca Raíz.
        # --------------------------------------------------------
        vista_patrimonio["_Categoria_Activo"] = (
            vista_patrimonio["Conjunto_Proyecto"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("ascii")
        )

        socios_por_activo = (
            vista_patrimonio
            .groupby("ID_Activo")["Nombre_Socio"]
            .apply(lambda s: set(x for x in s if x))
            .to_dict()
        )

        categoria_por_activo = (
            vista_patrimonio
            .groupby("ID_Activo")["_Categoria_Activo"]
            .first()
            .to_dict()
        )

        activos_finca_ids = {
            id_activo
            for id_activo, propietarios in socios_por_activo.items()
            if (
                categoria_por_activo.get(id_activo, "") == "finca raiz"
                and nombres_socios_set.issubset(propietarios)
            )
        }

        activos_asociados = vista_patrimonio[
            vista_patrimonio["ID_Activo"].isin(activos_finca_ids)
            & vista_patrimonio["Nombre_Socio"].isin(nombres_socios_set)
        ].copy()

        activos_adicionales = vista_patrimonio[
            ~vista_patrimonio["ID_Activo"].isin(activos_finca_ids)
            & vista_patrimonio["Nombre_Socio"].isin(nombres_socios_set)
        ].copy()

        # Subconjuntos por categoría para el resumen patrimonial.
        activos_finca_adicional = activos_adicionales[
            activos_adicionales["_Categoria_Activo"] == "finca raiz"
        ].copy()

        activos_comercio = activos_adicionales[
            activos_adicionales["_Categoria_Activo"] == "comercio"
        ].copy()

        activos_vehiculos = activos_adicionales[
            activos_adicionales["_Categoria_Activo"] == "vehiculos"
        ].copy()

        # --------------------------------------------------------
        # RESUMEN POR SOCIO
        # --------------------------------------------------------
        resumen_socios = socios[
            [
                "Nombre_Socio",
                "Aportes",
                "Aportes_Brutos",
                "Gastos_Familiares",
                "Gastos_Personales",
                "Gastos_Familiares_Personales",
                "Participacion",
                "Movimientos",
                "Primer_Aporte",
                "Ultimo_Aporte",
            ]
        ].copy()

        finca_socio = (
            activos_asociados
            .groupby("Nombre_Socio", as_index=False)["Valor_Mercado_Socio"]
            .sum()
            .rename(columns={"Valor_Mercado_Socio": "Finca_Raiz"})
        )
        # Comercio y vehículos forman parte del patrimonio principal.
        # Solo la Finca Raíz que NO es conjunta queda fuera de este
        # cálculo principal y se presenta como "Activos adicionales".
        comercio_socio = (
            activos_comercio
            .groupby("Nombre_Socio", as_index=False)["Valor_Mercado_Socio"]
            .sum()
            .rename(columns={"Valor_Mercado_Socio": "Comercio"})
        )

        vehiculos_socio = (
            activos_vehiculos
            .groupby("Nombre_Socio", as_index=False)["Valor_Mercado_Socio"]
            .sum()
            .rename(columns={"Valor_Mercado_Socio": "Vehiculos"})
        )

        finca_adicional_socio = (
            activos_finca_adicional
            .groupby("Nombre_Socio", as_index=False)["Valor_Mercado_Socio"]
            .sum()
            .rename(columns={"Valor_Mercado_Socio": "Activos_Adicionales"})
        )

        resumen_socios = resumen_socios.merge(
            finca_socio, on="Nombre_Socio", how="left"
        )
        resumen_socios = resumen_socios.merge(
            comercio_socio, on="Nombre_Socio", how="left"
        )
        resumen_socios = resumen_socios.merge(
            vehiculos_socio, on="Nombre_Socio", how="left"
        )
        resumen_socios = resumen_socios.merge(
            finca_adicional_socio, on="Nombre_Socio", how="left"
        )

        # Activos principales = Finca Raíz conjunta + Comercio + Vehículos.
        resumen_socios[
            ["Finca_Raiz", "Comercio", "Vehiculos", "Activos_Adicionales"]
        ] = resumen_socios[
            ["Finca_Raiz", "Comercio", "Vehiculos", "Activos_Adicionales"]
        ].fillna(0)

        resumen_socios["Activos_Principales"] = (
            resumen_socios["Finca_Raiz"]
            + resumen_socios["Comercio"]
            + resumen_socios["Vehiculos"]
        )

        # --------------------------------------------------------
        # DEUDA SEPARADA:
        # 1) deuda principal = Finca Raíz conjunta + Comercio + Vehículos
        # 2) deuda adicional = Finca Raíz adicional
        # --------------------------------------------------------
        activos_principal_ids = (
            set(activos_finca_ids)
            | set(activos_comercio["ID_Activo"].unique())
            | set(activos_vehiculos["ID_Activo"].unique())
        )

        if not creditos_prorrateados.empty:
            creditos_prorrateados = creditos_prorrateados.copy()

            # Se conserva esta bandera para el detalle de Finca Raíz.
            creditos_prorrateados["Es_Conjunta"] = (
                creditos_prorrateados["ID_Activo"]
                .isin(activos_finca_ids)
            )

            # Esta es la clasificación patrimonial principal.
            creditos_prorrateados["Es_Principal"] = (
                creditos_prorrateados["ID_Activo"]
                .isin(activos_principal_ids)
            )

            deuda_principal_socio = (
                creditos_prorrateados[
                    creditos_prorrateados["Es_Principal"]
                ]
                .groupby("Nombre_Socio", as_index=False)[
                    "Saldo_Actual_Prorrateado"
                ]
                .sum()
                .rename(
                    columns={
                        "Saldo_Actual_Prorrateado": "Deuda_Principal"
                    }
                )
            )

            deuda_adicional_socio = (
                creditos_prorrateados[
                    ~creditos_prorrateados["Es_Principal"]
                ]
                .groupby("Nombre_Socio", as_index=False)[
                    "Saldo_Actual_Prorrateado"
                ]
                .sum()
                .rename(
                    columns={
                        "Saldo_Actual_Prorrateado": "Deuda_Adicional"
                    }
                )
            )

        else:
            deuda_principal_socio = pd.DataFrame(
                columns=["Nombre_Socio", "Deuda_Principal"]
            )
            deuda_adicional_socio = pd.DataFrame(
                columns=["Nombre_Socio", "Deuda_Adicional"]
            )

        resumen_socios = resumen_socios.merge(
            deuda_principal_socio,
            on="Nombre_Socio",
            how="left"
        )
        resumen_socios = resumen_socios.merge(
            deuda_adicional_socio,
            on="Nombre_Socio",
            how="left"
        )

        resumen_socios[
            ["Deuda_Principal", "Deuda_Adicional"]
        ] = resumen_socios[
            ["Deuda_Principal", "Deuda_Adicional"]
        ].fillna(0)

        # --------------------------------------------------------
        # PATRIMONIO PRINCIPAL
        # --------------------------------------------------------
        # Incluye Finca Raíz conjunta + Comercio + Vehículos.
        # Excluye Finca Raíz adicional.
        resumen_socios["Patrimonio_Neto_Principal"] = (
            resumen_socios["Activos_Principales"]
            - resumen_socios["Deuda_Principal"]
        )

        # Compatibilidad con el resto del diseño existente.
        resumen_socios["Patrimonio_Neto_Conjunto"] = (
            resumen_socios["Patrimonio_Neto_Principal"]
        )
        resumen_socios["Deuda_Conjunta"] = resumen_socios["Deuda_Principal"]

        # Patrimonio total histórico/personal, usado solo en tablas
        # secundarias: incluye también los activos adicionales.
        resumen_socios["Patrimonio_Bruto"] = (
            resumen_socios["Activos_Principales"]
            + resumen_socios["Activos_Adicionales"]
        )

        resumen_socios["Deuda_Actual"] = (
            resumen_socios["Deuda_Principal"]
            + resumen_socios["Deuda_Adicional"]
        )

        resumen_socios["Patrimonio_Neto"] = (
            resumen_socios["Patrimonio_Bruto"]
            - resumen_socios["Deuda_Actual"]
        )

        resumen_socios["Neto_Conjunto_vs_Aportes"] = (
            (
                (resumen_socios["Patrimonio_Neto_Principal"]
                 / resumen_socios["Aportes"])
                - 1
            ) * 100
        ).replace(
            [float("inf"), -float("inf")],
            pd.NA
        ).fillna(0)

        valor_finca_total = float(
            activos_asociados["Valor_Mercado_Socio"].sum()
        )

        valor_comercio_total = float(
            activos_comercio["Valor_Mercado_Socio"].sum()
        )

        valor_vehiculos_total = float(
            activos_vehiculos["Valor_Mercado_Socio"].sum()
        )

        valor_adicional_total = float(
            activos_finca_adicional["Valor_Mercado_Socio"].sum()
        )

        valor_activos_principales_total = (
            valor_finca_total
            + valor_comercio_total
            + valor_vehiculos_total
        )

        deuda_principal_total = float(
            creditos_prorrateados.loc[
                creditos_prorrateados["Es_Principal"],
                "Saldo_Actual_Prorrateado"
            ].sum()
        ) if not creditos_prorrateados.empty else 0.0

        deuda_adicional_total = float(
            creditos_prorrateados.loc[
                ~creditos_prorrateados["Es_Principal"],
                "Saldo_Actual_Prorrateado"
            ].sum()
        ) if not creditos_prorrateados.empty else 0.0

        deuda_conjunta_total = float(
            creditos_prorrateados.loc[
                creditos_prorrateados["Es_Conjunta"],
                "Saldo_Actual_Prorrateado"
            ].sum()
        ) if not creditos_prorrateados.empty else 0.0

        deuda_total = (
            deuda_principal_total
            + deuda_adicional_total
        )

        patrimonio_neto_conjunto_total = (
            valor_activos_principales_total
            - deuda_principal_total
        )

        patrimonio_total = (
            valor_activos_principales_total
            + valor_adicional_total
        )

        patrimonio_neto_total = (
            patrimonio_total
            - deuda_total
        )

        patrimonio_vs_aportes = (
            (
                (patrimonio_neto_conjunto_total / total_aportes)
                - 1
            ) * 100
            if total_aportes
            else 0
        )

        # --------------------------------------------------------
        # COLORES POR SOCIO
        # --------------------------------------------------------
        palette = ["#FF5A73", "#5DA7F4", "#43C995"]
        socio_colors = {
            row["Nombre_Socio"]: palette[i % len(palette)]
            for i, (_, row) in enumerate(socios.iterrows())
        }

        # --------------------------------------------------------
        # KPIs
        # --------------------------------------------------------
        kpi_items = [
            ("🏠", "Activos", dinero_corto(valor_activos_principales_total), "Finca Raíz + Comercio + Vehículos"),
            ("💳", "Deuda principal", f"-{dinero_corto(deuda_principal_total)}", "Activos incluidos en el patrimonio neto"),
            ("📈", "Patrimonio neto", dinero_corto(patrimonio_neto_conjunto_total), "Activos - deuda principal"),
            ("🔗", "Activos adicionales", dinero_corto(valor_adicional_total), "Finca Raíz adicional, fuera del patrimonio neto"),
            ("💳", "Deuda adicional", f"-{dinero_corto(deuda_adicional_total)}", "Deuda de activos adicionales"),
            ("💰", "Capital neto aportado", dinero_corto(total_aportes), "Aportes - familiar - personal"),
        ]

        kpi_html = '<div class="aportes-kpi-grid6">'
        for icon, label, value, sub in kpi_items:
            kpi_html += f"""
<div class="aportes-kpi6">
    <div class="aportes-kpi6-icon">{icon}</div>
    <div>
        <div class="aportes-kpi6-label">{escape_html(label)}</div>
        <div class="aportes-kpi6-value {("aportes-kpi-debt" if "Deuda" in label else "aportes-kpi-net" if "Patrimonio neto" in label else "")}">{escape_html(value)}</div>
        <div class="aportes-kpi6-sub">{escape_html(sub)}</div>
    </div>
</div>
"""
        kpi_html += "</div>"
        render_aportes_html(kpi_html)

        
        # --------------------------------------------------------
        # COMPOSICIÓN PATRIMONIAL POR SOCIO
        # Diseño compacto inspirado en la referencia visual:
        # donut + resumen patrimonial + adicionales.
        # --------------------------------------------------------

        render_aportes_html("""
<style>
/* ============================================================
   APPORTES / PATRIMONIO — NUEVO DISEÑO COMPACTO
============================================================ */
.aportes-compact-section {
    margin-top: 0;
}

.aportes-compact-title-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    margin: 4px 0 8px;
}

.aportes-compact-title {
    font-size:18px;
    line-height:1.1;
    font-weight:900;
    color:#17345E;
}

.aportes-compact-toggle {
    display:inline-flex;
    background:#F3F6FA;
    border:1px solid #DCE5EE;
    border-radius:18px;
    padding:2px;
    gap:2px;
}

.aportes-compact-toggle span {
    padding:5px 11px;
    font-size:8px;
    font-weight:800;
    color:#71839A;
    border-radius:14px;
}

.aportes-compact-toggle .active {
    background:#17345E;
    color:#FFFFFF;
}

/* ---------- 3 tarjetas ---------- */
.aportes-compact-grid {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:12px;
}

.aportes-compact-card {
    margin-top:-10px;
    margin-bottom:-2px;
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:15px;
    overflow:hidden;
    box-sizing:border-box;
    box-shadow:0 2px 8px rgba(23,52,94,.035);
}

.aportes-compact-card.diego { border-top:3px solid #FF5A73; }
.aportes-compact-card.william { border-top:3px solid #5DA7F4; }
.aportes-compact-card.andres { border-top:3px solid #43C995; }

.aportes-compact-head {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:8px;
    padding:10px 13px 7px;
}

.aportes-compact-name-wrap {
    display:flex;
    align-items:center;
    gap:8px;
    min-width:0;
}

.aportes-compact-avatar {
    width:30px;
    height:30px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:13px;
    font-weight:900;
    flex:0 0 30px;
}

.aportes-compact-avatar.diego { background:#FFE8EE; color:#FF4C6D; }
.aportes-compact-avatar.william { background:#EAF2FF; color:#5DA7F4; }
.aportes-compact-avatar.andres { background:#E9F8F2; color:#43C995; }

.aportes-compact-name {
    font-size:17px;
    font-weight:900;
    color:#17345E;
    white-space:nowrap;
}

.aportes-compact-total {
    text-align:right;
    min-width:150px;
}

.aportes-header-patrimonio-label {
    font-size:8px;
    color:#6F8198;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.2px;
    margin-top:2px;
}

.aportes-header-patrimonio-value {
    font-size:21px;
    line-height:1;
    font-weight:950;
    color:#17345E;
    margin-top:3px;
    white-space:nowrap;
}

.aportes-header-patrimonio-ratio {
    font-size:9.5px;
    font-weight:950;
    margin-top:5px;
    white-space:nowrap;
}

.aportes-header-patrimonio-ratio.positive {
    color:#009B70;
}

.aportes-header-patrimonio-ratio.negative {
    color:#D64242;
}

.aportes-header-capital-label {
    font-size:7px;
    color:#8795A8;
    font-weight:800;
    margin-top:5px;
}

.aportes-header-capital-value {
    font-size:10px;
    font-weight:900;
    color:#17345E;
    margin-top:1px;
    white-space:nowrap;
}

.aportes-compact-total-label {
    font-size:8px;
    color:#6F8198;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.2px;
}

.aportes-capital-breakdown {
    display:grid;
    grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;
    align-items:center;
    gap:5px;
    margin:7px 9px 5px;
    padding:6px 8px;
    background:#F8FAFC;
    border:1px solid #E6ECF2;
    border-radius:8px;
}

.aportes-capital-item {
    min-width:0;
    display:flex;
    align-items:baseline;
    justify-content:space-between;
    gap:5px;
}

.aportes-capital-label {
    font-size:9px;
    color:#60738B;
    font-weight:850;
    white-space:nowrap;
}

.aportes-capital-item strong {
    font-size:10px;
    font-weight:900;
    color:#17345E;
    white-space:nowrap;
}

.aportes-capital-item.expense strong {
    color:#D64242;
}

.aportes-capital-item.net strong {
    color:#009B70;
}

.aportes-capital-divider {
    width:1px;
    height:18px;
    background:#E1E7ED;
}

.aportes-compact-total-value {
    font-size:20px;
    line-height:1;
    color:#17345E;
    font-weight:900;
    margin-top:3px;
}

/* ---------- cuerpo ---------- */
.aportes-compact-main {
    display:grid;
    grid-template-columns:1.08fr .92fr;
    gap:6px;
    align-items:center;
    padding:0 9px 3px;
}

.aportes-compact-chart {
    min-width:0;
}

.aportes-compact-summary {
    background:#FAFBFD;
    border:1px solid #E3EAF0;
    border-radius:11px;
    padding:7px 9px;
}

.aportes-compact-summary-title {
    font-size:10.5px;
    font-weight:900;
    color:#17345E;
    margin-bottom:4px;
}

.aportes-compact-summary-row {
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:5px;
    padding:6px 0;
    border-bottom:1px solid #EDF1F5;
}

.aportes-compact-summary-row:last-child {
    border-bottom:none;
}

.aportes-compact-summary-label {
    font-size:8.5px;
    color:#71839A;
}

.aportes-compact-summary-value {
    font-size:9.5px;
    font-weight:900;
    color:#17345E;
    white-space:nowrap;
}

.aportes-compact-summary-row.total .aportes-compact-summary-label,
.aportes-compact-summary-row.total .aportes-compact-summary-value {
    font-weight:900;
    color:#17345E;
}

.aportes-compact-summary-row.ratio .aportes-compact-summary-value {
    font-weight:900;
}

.aportes-compact-summary-row.ratio .aportes-compact-summary-value.positive {
    color:#009B70;
}

.aportes-compact-summary-row.ratio .aportes-compact-summary-value.negative {
    color:#D64242;
}
.aportes-compact-summary-row.debt {
    background:#FFF7F7;
    border-radius:6px;
    padding-left:6px;
    padding-right:6px;
}
.aportes-compact-summary-value.debt-value {
    color:#D64242;
}

/* ---------- adicionales ---------- */
.aportes-compact-additional {
    margin:3px 9px 9px;
    border-top:1px solid #E8EDF2;
    padding-top:7px;
}

.aportes-compact-additional-head {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:8px;
    margin-bottom:4px;
}

.aportes-compact-additional-title {
    font-size:9.5px;
    font-weight:900;
    color:#17345E;
}

.aportes-compact-additional-total {
    font-size:12px;
    font-weight:900;
    color:#7757C8;
}

.aportes-compact-additional.compact-note {
    padding-bottom:8px;
}

.aportes-compact-additional.compact-note .aportes-compact-additional-head {
    min-height:34px;
}

.aportes-compact-additional-sub {
    font-size:7px;
    color:#8795A8;
    margin-top:2px;
    margin-bottom:5px;
}

.aportes-compact-extra-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:8px;
    padding:6px 8px;
    margin-top:4px;
    border:1px solid #E7EDF3;
    border-radius:8px;
    background:#FFFFFF;
}

.aportes-compact-extra-name {
    font-size:8px;
    font-weight:750;
    color:#5F7189;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.aportes-compact-extra-value {
    font-size:9.5px;
    font-weight:900;
    color:#17345E;
    white-space:nowrap;
}

.aportes-card-body-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:7px;
    padding:0 9px 7px;
}

.aportes-mini-panel {
    background:#FAFBFD;
    border:1px solid #E3EAF0;
    border-radius:10px;
    padding:8px 9px;
    min-width:0;
}

.aportes-mini-panel-title {
    font-size:10.5px;
    font-weight:900;
    color:#17345E;
    margin-bottom:4px;
}

.aportes-mini-panel-sub {
    font-size:8px;
    color:#667A92;
    margin-bottom:5px;
}

.aportes-mini-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:5px;
    padding:4px 0;
    border-bottom:1px solid #EDF1F5;
}

.aportes-mini-row:last-child {
    border-bottom:none;
}

.aportes-mini-name {
    min-width:0;
    font-size:9px;
    color:#566B84;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.aportes-mini-value {
    font-size:19px;
    line-height:1;
    font-weight:950;
    color:#17345E;
    white-space:nowrap;
}

.aportes-mini-value.compact {
    font-size:15px;
    font-weight:900;
}

.aportes-category-value {
    font-size:11px;
    line-height:1;
    font-weight:900;
    color:#17345E;
    white-space:nowrap;
}

.aportes-category-row .aportes-mini-name {
    font-size:8.5px;
    font-weight:800;
    color:#566B84;
}

.aportes-mini-debt-value {
    font-size:14px;
    font-weight:900;
    color:#D64242;
    white-space:nowrap;
}

.aportes-mini-ratio {
    font-size:12px;
    font-weight:950;
    white-space:nowrap;
}

.aportes-mini-ratio.positive {
    color:#009B70;
}

.aportes-mini-ratio.negative {
    color:#D64242;
}

.aportes-mini-pct {
    font-size:8px;
    color:#71839A;
    margin-left:auto;
    margin-right:3px;
    white-space:nowrap;
}

.aportes-mini-total {
    margin-top:4px;
    padding-top:5px;
    border-top:1px solid #E4EAF0;
    display:flex;
    justify-content:space-between;
    gap:6px;
}

.aportes-mini-total-label {
    font-size:8.5px;
    font-weight:850;
    color:#586D86;
}

.aportes-mini-total-value {
    font-size:10px;
    font-weight:900;
    color:#7757C8;
}

.aportes-last-contrib {
    margin:0 9px 7px;
    padding:7px 9px;
    border:1px solid #E9DFF9;
    border-radius:9px;
    background:linear-gradient(90deg,#FBF8FF 0%,#F8F4FF 100%);
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:8px;
}

.aportes-last-contrib-left {
    display:flex;
    align-items:center;
    gap:7px;
    min-width:0;
}

.aportes-last-contrib-icon {
    width:24px;
    height:24px;
    border-radius:7px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#EEE5FF;
    font-size:13px;
    flex:0 0 24px;
}

.aportes-last-contrib-label {
    font-size:9px;
    font-weight:900;
    color:#586D86;
}

.aportes-last-contrib-date {
    font-size:8px;
    color:#71839A;
    margin-top:1px;
}

.aportes-last-contrib-value {
    font-size:11px;
    font-weight:900;
    color:#7757C8;
    white-space:nowrap;
}

.aportes-participation-panel {
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:12px 13px 8px;
    box-sizing:border-box;
}

.aportes-participation-title {
    font-size:13px;
    font-weight:900;
    color:#17345E;
}

.aportes-participation-sub {
    font-size:8px;
    color:#8A98AA;
    margin-top:3px;
    margin-bottom:4px;
}

.aportes-portfolio-panel {
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:12px 13px 11px;
    box-sizing:border-box;
}

.aportes-portfolio-title {
    font-size:13px;
    font-weight:900;
    color:#17345E;
}

.aportes-portfolio-sub {
    font-size:8px;
    color:#667A92;
    margin-top:3px;
    margin-bottom:8px;
}

.aportes-portfolio-grid {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:8px;
}

.aportes-portfolio-item {
    background:#FAFBFD;
    border:1px solid #DCE5EE;
    border-radius:10px;
    padding:9px 10px;
}

.aportes-portfolio-item.finca {
    border-top:3px solid #5DA7F4;
}

.aportes-portfolio-item.comercio {
    border-top:3px solid #FF5A73;
}

.aportes-portfolio-item.vehiculos {
    border-top:3px solid #43C995;
}

.aportes-portfolio-label {
    font-size:9px;
    font-weight:900;
    color:#17345E;
}

.aportes-portfolio-caption {
    font-size:7.5px;
    color:#667A92;
    margin-top:2px;
}

.aportes-portfolio-value {
    font-size:16px;
    font-weight:900;
    color:#17345E;
    margin-top:7px;
    white-space:nowrap;
}

.aportes-portfolio-pct {
    font-size:8px;
    color:#667A92;
    margin-top:2px;
}

.aportes-portfolio-pending {
    font-size:10px;
    font-weight:900;
    color:#8A98AA;
    margin-top:10px;
}

@media (max-width: 800px) {
    .aportes-portfolio-grid {
        grid-template-columns:1fr;
    }
}

/* ---------- detalle Finca Raíz ---------- */
.aportes-bottom-grid {
    display:grid;
    grid-template-columns:1.72fr .88fr;
    gap:12px;
    margin-top:12px;
}

.aportes-finca-summary-panel.compact {
    margin-top:0;
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:12px 13px 8px;
    box-sizing:border-box;
    overflow-x:auto;
}

.aportes-finca-summary-header.compact {
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:10px;
    margin-bottom:7px;
}

.aportes-finca-summary-title.compact {
    font-size:13px;
    font-weight:900;
    color:#17345E;
}

.aportes-finca-summary-sub.compact {
    font-size:8px;
    color:#8A98AA;
    margin-top:3px;
}

.aportes-finca-summary-total.compact {
    text-align:right;
    white-space:nowrap;
}

.aportes-finca-summary-total-label.compact {
    font-size:7px;
    color:#8290A4;
}

.aportes-finca-summary-total-value.compact {
    font-size:18px;
    font-weight:900;
    color:#17345E;
    line-height:1;
    margin-top:2px;
}

.aportes-finca-table.compact {
    width:100%;
    border-collapse:separate;
    border-spacing:0;
    font-size:8.5px;
    color:#50637B;
    min-width:620px;
}

.aportes-finca-table.compact th {
    background:#F4F7FA;
    color:#71839A;
    font-size:7px;
    font-weight:900;
    text-transform:uppercase;
    padding:7px 8px;
    border-bottom:1px solid #DCE5EE;
    text-align:right;
    white-space:nowrap;
}

.aportes-finca-table.compact th:first-child,
.aportes-finca-table.compact th:nth-child(2),
.aportes-finca-table.compact th:nth-child(3) {
    text-align:left;
}

.aportes-finca-table.compact td {
    padding:7px 8px;
    border-bottom:1px solid #EDF1F5;
    text-align:right;
    white-space:nowrap;
}

.aportes-finca-table.compact tr:last-child td { border-bottom:none; }

.aportes-finca-table.compact td:first-child {
    text-align:left;
    font-weight:850;
    color:#17345E;
}

.aportes-finca-table.compact td:nth-child(2),
.aportes-finca-table.compact td:nth-child(3) {
    text-align:left;
    color:#71839A;
}

.aportes-finca-value.compact {
    font-weight:900;
    color:#17345E;
}

.aportes-finca-pct.compact {
    font-weight:900;
    color:#5F7189;
}

.aportes-finca-debt.compact {
    font-weight:900;
    color:#D64242;
}

/* ---------- gráfico composición ---------- */
.aportes-composition-panel {
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:12px 12px 8px;
    box-sizing:border-box;
}

.aportes-composition-title {
    font-size:13px;
    font-weight:900;
    color:#17345E;
}

.aportes-composition-sub {
    font-size:8px;
    color:#8A98AA;
    margin-top:3px;
    margin-bottom:6px;
}

.aportes-composition-legend {
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin:3px 0 2px;
}

.aportes-composition-legend span {
    font-size:7px;
    color:#61738C;
    display:inline-flex;
    align-items:center;
    gap:4px;
}

.aportes-composition-dot {
    width:7px;
    height:7px;
    border-radius:50%;
    display:inline-block;
}

/* ---------- Negocios / otros ---------- */
.aportes-otros-panel {
    background:#FFFFFF;
    border:1px solid #DCE5EE;
    border-radius:14px;
    padding:12px 13px 8px;
    margin-top:12px;
    overflow-x:auto;
}

/* ---------- Responsive ---------- */
@media (max-width: 1150px) {
    .aportes-compact-grid { grid-template-columns:1fr; }
    .aportes-bottom-grid { grid-template-columns:1fr; }
}

@media (max-width: 800px) {
    .aportes-kpi-grid6 { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .aportes-compact-main { grid-template-columns:1fr; }
    .aportes-card-body-grid { grid-template-columns:1fr; }
}
</style>
""")

        # Las tarjetas de socios comienzan directamente debajo de los KPI.
        # Se elimina el encabezado intermedio y el selector de vista para
        # reducir espacio y mantener la pantalla más limpia.

        # --------------------------------------------------------
        # TRES TARJETAS
        # --------------------------------------------------------
        socio_cols = st.columns(3, gap="small")

        for idx, (_, socio_row) in enumerate(resumen_socios.iterrows()):

            nombre = socio_row["Nombre_Socio"]

            clase = (
                "diego"
                if "Diego" in nombre
                else "william"
                if "William" in nombre
                else "andres"
            )

            avatar = (
                "D"
                if "Diego" in nombre
                else "W"
                if "William" in nombre
                else "A"
            )

            total_socio = float(socio_row["Aportes"])
            patrimonio_bruto = float(socio_row["Patrimonio_Bruto"])
            deuda_socio = float(socio_row["Deuda_Actual"])
            deuda_principal = float(socio_row["Deuda_Principal"])
            deuda_adicional = float(socio_row["Deuda_Adicional"])
            patrimonio_neto = float(socio_row["Patrimonio_Neto"])
            patrimonio_neto_principal = float(
                socio_row["Patrimonio_Neto_Principal"]
            )
            # Alias para conservar el comportamiento visual existente.
            patrimonio_neto_conjunto = patrimonio_neto_principal
            ratio = float(socio_row["Neto_Conjunto_vs_Aportes"])
            ratio_icon = "↑" if ratio >= 0 else "↓"
            ratio_class = "positive" if ratio >= 0 else "negative"
            finca_total = float(socio_row["Finca_Raiz"])
            comercio_total_socio = float(socio_row["Comercio"])
            vehiculos_total_socio = float(socio_row["Vehiculos"])
            activos_principales_socio = float(socio_row["Activos_Principales"])
            adicionales_total = float(socio_row["Activos_Adicionales"])

            finca_socio_df = (
                activos_asociados[
                    activos_asociados["Nombre_Socio"] == nombre
                ]
                .groupby(
                    "Nombre_Entidad",
                    as_index=False
                )["Valor_Mercado_Socio"]
                .sum()
                .sort_values(
                    "Valor_Mercado_Socio",
                    ascending=False
                )
                .reset_index(drop=True)
            )

            # Los "Activos adicionales" son únicamente Finca Raíz
            # que no pertenece al patrimonio principal.
            adicional_socio_df = (
                activos_finca_adicional[
                    activos_finca_adicional["Nombre_Socio"] == nombre
                ]
                .groupby(
                    "Nombre_Entidad",
                    as_index=False
                )["Valor_Mercado_Socio"]
                .sum()
                .sort_values(
                    "Valor_Mercado_Socio",
                    ascending=False
                )
                .reset_index(drop=True)
            )

            # --------------------------------------------------------
            # TARJETA COMPACTA DEL SOCIO
            # Sin donut: resumen conjunto + categorías adicionales +
            # último aporte.
            # --------------------------------------------------------

            with socio_cols[idx]:

                with st.container(border=False):

                    ultima_fecha = socio_row["Ultimo_Aporte"]

                    ultimo_aporte_valor = float(
                        aportes_base[
                            (aportes_base["Nombre_Socio"] == nombre)
                            & (aportes_base["Fecha"] == ultima_fecha)
                        ]["Valor"].sum()
                    )

                    finca_rows_html = ""

                    if not finca_socio_df.empty:

                        finca_total_local = float(
                            finca_socio_df["Valor_Mercado_Socio"].sum()
                        )

                        for _, row in finca_socio_df.iterrows():

                            valor_activo = float(
                                row["Valor_Mercado_Socio"]
                            )

                            pct_activo = (
                                valor_activo
                                / finca_total_local
                                * 100
                                if finca_total_local
                                else 0
                            )

                            finca_rows_html += f"""
<div class="aportes-mini-row">
    <span class="aportes-mini-name">
        {escape_html(row["Nombre_Entidad"])}
    </span>
    <span class="aportes-mini-pct">
        {pct_activo:.1f}%
    </span>
    <span class="aportes-mini-value">
        {dinero_corto(valor_activo)}
    </span>
</div>
"""

                    adicional_rows_html = ""

                    if not adicional_socio_df.empty:

                        for _, row in adicional_socio_df.iterrows():

                            valor_categoria = float(
                                row["Valor_Mercado_Socio"]
                            )

                            adicional_rows_html += f"""
<div class="aportes-mini-row aportes-category-row">
    <span class="aportes-mini-name">
        🏠 {escape_html(row["Nombre_Entidad"])}
    </span>
    <span class="aportes-category-value">
        {dinero_corto(valor_categoria)}
    </span>
</div>
"""

                    if not adicional_rows_html:

                        adicional_rows_html = """
<div class="aportes-mini-row">
    <span class="aportes-mini-name">
        Sin activos adicionales
    </span>
    <span class="aportes-category-value">-</span>
</div>
"""

                    render_aportes_html(f"""
<div class="aportes-compact-card {clase}">

    <div class="aportes-compact-head">

        <div class="aportes-compact-name-wrap">

            <div class="aportes-compact-avatar {clase}">
                {avatar}
            </div>

            <div class="aportes-compact-name">
                {escape_html(nombre)}
            </div>

        </div>

        <div class="aportes-compact-total">

            <div class="aportes-header-patrimonio-label">
                Patrimonio neto
            </div>

            <div class="aportes-header-patrimonio-value">
                {dinero_corto(patrimonio_neto_conjunto)}
            </div>

            <div class="aportes-header-patrimonio-ratio {ratio_class}">
                {ratio_icon} {ratio:+.1f}% vs. capital neto
            </div>

            <div class="aportes-header-capital-label">
                Capital neto aportado
            </div>

            <div class="aportes-header-capital-value">
                {dinero_corto(total_socio)}
            </div>

        </div>

    </div>

    <div class="aportes-capital-breakdown">

        <div class="aportes-capital-item gross">
            <span class="aportes-capital-label">
                Brutos
            </span>
            <strong>
                {dinero_corto(float(socio_row["Aportes_Brutos"]))}
            </strong>
        </div>

        <div class="aportes-capital-divider"></div>

        <div class="aportes-capital-item expense">
            <span class="aportes-capital-label">
                Familiar
            </span>
            <strong>
                -{dinero_corto(float(socio_row["Gastos_Familiares"]))}
            </strong>
        </div>

        <div class="aportes-capital-divider"></div>

        <div class="aportes-capital-item expense">
            <span class="aportes-capital-label">
                Personal
            </span>
            <strong>
                -{dinero_corto(float(socio_row["Gastos_Personales"]))}
            </strong>
        </div>

        <div class="aportes-capital-divider"></div>

        <div class="aportes-capital-item net">
            <span class="aportes-capital-label">
                Neto
            </span>
            <strong>
                {dinero_corto(float(socio_row["Aportes"]))}
            </strong>
        </div>

    </div>

    <div class="aportes-card-body-grid">

        <div class="aportes-mini-panel">

            <div class="aportes-mini-panel-title">
                🏠 Activos
            </div>

            <div class="aportes-mini-panel-sub">
                Finca Raíz + Comercio + Vehículos
            </div>

            <div class="aportes-mini-row" style="padding:5px 0;">
                <span class="aportes-mini-name" style="font-size:9px;font-weight:850;">
                    🏠 Finca Raíz
                </span>
                <span class="aportes-mini-value compact">
                    {dinero_corto(finca_total)}
                </span>
            </div>

            <div class="aportes-mini-row" style="padding:5px 0;">
                <span class="aportes-mini-name" style="font-size:9px;font-weight:850;">
                    🏪 Comercio
                </span>
                <span class="aportes-mini-value compact">
                    {dinero_corto(comercio_total_socio)}
                </span>
            </div>

            <div class="aportes-mini-row" style="padding:5px 0;">
                <span class="aportes-mini-name" style="font-size:9px;font-weight:850;">
                    🚗 Vehículos
                </span>
                <span class="aportes-mini-value compact">
                    {dinero_corto(vehiculos_total_socio)}
                </span>
            </div>

            <div class="aportes-mini-row"
                 style="background:#FFF7F7;border-radius:7px;padding:8px 5px;margin-top:6px;border-bottom:none;">

                <span class="aportes-mini-name"
                      style="font-size:9px;font-weight:850;">
                    Deuda principal
                </span>

                <span class="aportes-mini-debt-value">
                    -{dinero_corto(deuda_principal)}
                </span>

            </div>

        </div>

        <div class="aportes-mini-panel">

            <div class="aportes-mini-panel-title">
                🔗 Activos adicionales
            </div>

            <div class="aportes-mini-panel-sub">
                Finca Raíz fuera del patrimonio principal
            </div>

            {adicional_rows_html}

            <div class="aportes-mini-total">

                <span class="aportes-mini-total-label">
                    Total Finca Raíz adicional
                </span>

                <span class="aportes-mini-total-value">
                    {dinero_corto(adicionales_total)}
                </span>

            </div>

        </div>

    </div>

    <div class="aportes-last-contrib">

        <div class="aportes-last-contrib-left">

            <div class="aportes-last-contrib-icon">
                📅
            </div>

            <div>

                <div class="aportes-last-contrib-label">
                    Último aporte
                </div>

                <div class="aportes-last-contrib-date">
                    {fecha_corta_es(ultima_fecha)}
                </div>

            </div>

        </div>

        <div class="aportes-last-contrib-value">
            {dinero_corto(ultimo_aporte_valor)}
        </div>

    </div>

</div>
""")

        # --------------------------------------------------------
        # DETALLE DE FINCA RAÍZ + COMPOSICIÓN DEL PATRIMONIO
        # --------------------------------------------------------
        finca_resumen = pd.DataFrame()

        if not activos_asociados.empty:

            # Deuda actual atribuible a la participación conjunta de los tres socios.
            deuda_finca = pd.DataFrame()

            if not creditos_prorrateados.empty:
                deuda_finca = (
                    creditos_prorrateados[
                        creditos_prorrateados["ID_Activo"].isin(activos_finca_ids)
                        & creditos_prorrateados["Nombre_Socio"].isin(nombres_socios_set)
                    ]
                    .groupby("ID_Activo", as_index=False)["Saldo_Actual_Prorrateado"]
                    .sum()
                    .rename(columns={"Saldo_Actual_Prorrateado": "Deuda_Actual"})
                )

            finca_resumen = (
                activos_asociados
                .groupby(
                    ["ID_Activo", "Nombre_Entidad", "Ciudad"],
                    as_index=False
                )["Valor_Mercado_Socio"]
                .sum()
                .rename(
                    columns={"Valor_Mercado_Socio": "Valor_Minimo"}
                )
                .sort_values("Valor_Minimo", ascending=False)
                .reset_index(drop=True)
            )

            finca_resumen["Pct_Conjunto"] = (
                finca_resumen["Valor_Minimo"]
                / valor_finca_total
                * 100
                if valor_finca_total
                else 0
            )

            finca_resumen["Tipo"] = "Finca Raíz"

            if not deuda_finca.empty:
                finca_resumen = finca_resumen.merge(
                    deuda_finca,
                    on="ID_Activo",
                    how="left"
                )
            else:
                finca_resumen["Deuda_Actual"] = 0

            finca_resumen["Deuda_Actual"] = (
                pd.to_numeric(
                    finca_resumen["Deuda_Actual"],
                    errors="coerce"
                )
                .fillna(0)
            )

            finca_resumen["Patrimonio_Neto"] = (
                finca_resumen["Valor_Minimo"]
                - finca_resumen["Deuda_Actual"]
            )

        # --------------------------------------------------------
        # BLOQUE INFERIOR:
        # PARTICIPACIÓN DE ACTIVOS + DETALLE DE FINCA RAÍZ
        # --------------------------------------------------------

        bottom_cols = st.columns([1.05, 1.35], gap="small")

        with bottom_cols[0]:

            # --------------------------------------------------------
            # COMPOSICIÓN DEL PORTAFOLIO
            # Ahora se calcula por la categoría maestra del activo:
            # Finca Raíz + Comercio + Vehículos.
            #
            # valor_finca_total = solo Finca Raíz conjunta.
            # Para la composición usamos TODO el portafolio actual
            # clasificado como Finca Raíz, sin mezclar RIE ni Carro
            # Padre con la Finca Raíz.
            # --------------------------------------------------------
            # Esta composición muestra exactamente los activos que
            # sí forman parte del patrimonio neto principal:
            # Finca Raíz conjunta + Comercio + Vehículos.
            valor_finca_portafolio = valor_finca_total
            valor_comercio = valor_comercio_total
            valor_vehiculos = valor_vehiculos_total
            valor_finca_adicional_portafolio = valor_adicional_total

            valor_portafolio_valorado = (
                valor_finca_portafolio
                + valor_comercio
                + valor_vehiculos
            )

            pct_finca_port = (
                valor_finca_portafolio
                / valor_portafolio_valorado
                * 100
                if valor_portafolio_valorado
                else 0
            )

            pct_comercio_port = (
                valor_comercio
                / valor_portafolio_valorado
                * 100
                if valor_portafolio_valorado
                else 0
            )

            pct_vehiculos_port = (
                valor_vehiculos
                / valor_portafolio_valorado
                * 100
                if valor_portafolio_valorado
                else 0
            )

            render_aportes_html(f"""
<div class="aportes-portfolio-panel">

    <div class="aportes-portfolio-title">
        📊 Composición de los activos
    </div>

    <div class="aportes-portfolio-sub">
        Composición de los activos que forman el patrimonio neto
    </div>

    <div class="aportes-portfolio-grid">

        <div class="aportes-portfolio-item finca">

            <div class="aportes-portfolio-label">
                🏠 Finca Raíz
            </div>

            <div class="aportes-portfolio-caption">
                Finca Raíz conjunta
            </div>

            <div class="aportes-portfolio-value">
                {dinero_corto(valor_finca_portafolio)}
            </div>

            <div class="aportes-portfolio-pct">
                {pct_finca_port:.1f}% del patrimonio principal
            </div>

        </div>

        <div class="aportes-portfolio-item comercio">

            <div class="aportes-portfolio-label">
                🏪 Comercio
            </div>

            <div class="aportes-portfolio-caption">
                RIE + Restaurante RIE
            </div>

            <div class="aportes-portfolio-value">
                {dinero_corto(valor_comercio)}
            </div>

            <div class="aportes-portfolio-pct">
                {pct_comercio_port:.1f}% del patrimonio principal
            </div>

        </div>

        <div class="aportes-portfolio-item vehiculos">

            <div class="aportes-portfolio-label">
                🚗 Vehículos
            </div>

            <div class="aportes-portfolio-caption">
                Activos muebles
            </div>

            <div class="aportes-portfolio-value">
                {dinero_corto(valor_vehiculos)}
            </div>

            <div class="aportes-portfolio-pct">
                {pct_vehiculos_port:.1f}% del patrimonio principal
            </div>

        </div>

    </div>

    <div style="margin-top:8px;padding:7px 9px;border:1px dashed #DCE5EE;border-radius:9px;background:#FAFBFD;font-size:8px;color:#667A92;">
        🏠 <b style="color:#17345E;">Finca Raíz adicional:</b>
        {dinero_corto(valor_finca_adicional_portafolio)}
        <span style="color:#8A98AA;">· fuera del patrimonio neto principal</span>
    </div>

</div>
""")
        with bottom_cols[1]:

            if not finca_resumen.empty:

                tabla_finca = f"""
<div class="aportes-finca-summary-panel compact">

    <div class="aportes-finca-summary-header compact">

        <div>

            <div class="aportes-finca-summary-title compact">
                🏠 Detalle de Finca Raíz conjunta
            </div>

            <div class="aportes-finca-summary-sub compact">
                Valor, deuda y patrimonio neto por predio
            </div>

        </div>

        <div class="aportes-finca-summary-total compact">

            <div class="aportes-finca-summary-total-label compact">
                Valor total
            </div>

            <div class="aportes-finca-summary-total-value compact">
                {dinero_corto(valor_finca_total)}
            </div>

        </div>

    </div>

    <table class="aportes-finca-table compact">

        <thead>

            <tr>
                <th>Predio</th>
                <th>Ciudad</th>
                <th>% conjunto</th>
                <th>Valor</th>
                <th>Deuda</th>
                <th>Neto</th>
            </tr>

        </thead>

        <tbody>
"""

                for _, row in finca_resumen.iterrows():

                    tabla_finca += f"""
<tr>

    <td>
        {escape_html(row["Nombre_Entidad"])}
    </td>

    <td>
        {escape_html(row["Ciudad"])}
    </td>

    <td>
        <span class="aportes-finca-pct compact">
            {float(row["Pct_Conjunto"]):.1f}%
        </span>
    </td>

    <td>
        <span class="aportes-finca-value compact">
            {dinero_corto(float(row["Valor_Minimo"]))}
        </span>
    </td>

    <td>
        <span class="aportes-finca-debt compact">
            -{dinero_corto(float(row["Deuda_Actual"]))}
        </span>
    </td>

    <td>
        <span class="aportes-finca-value compact">
            {dinero_corto(float(row["Patrimonio_Neto"]))}
        </span>
    </td>

</tr>
"""

                tabla_finca += """
        </tbody>
    </table>

</div>
"""

                render_aportes_html(tabla_finca)

            else:

                render_aportes_html("""
<div class="aportes-finca-summary-panel compact">

    <div class="aportes-finca-summary-title compact">
        🏠 Detalle de Finca Raíz conjunta
    </div>

    <div class="aportes-finca-summary-sub compact">
        Sin registros disponibles.
    </div>

</div>
""")

        # --------------------------------------------------------
        # FINCA RAÍZ ADICIONAL + DEUDA INDIVIDUAL
        # --------------------------------------------------------
        # Aquí salen únicamente los activos de Finca Raíz que quedan
        # fuera del patrimonio principal. Comercio y Vehículos ya están
        # integrados en "Activos" y no se repiten aquí.
        if not activos_finca_adicional.empty:

            adicionales_tabla = (
                activos_finca_adicional
                .groupby(
                    [
                        "ID_Activo",
                        "Nombre_Entidad",
                        "Ciudad",
                        "Nombre_Socio",
                    ],
                    as_index=False
                )["Valor_Mercado_Socio"]
                .sum()
                .rename(
                    columns={
                        "Valor_Mercado_Socio":
                            "Valor_Activo"
                    }
                )
            )

            if not creditos_prorrateados.empty:
                deuda_individual_tabla = (
                    creditos_prorrateados[
                        ~creditos_prorrateados["Es_Principal"]
                    ]
                    .groupby(
                        [
                            "ID_Activo",
                            "Nombre_Socio",
                        ],
                        as_index=False
                    )["Saldo_Actual_Prorrateado"]
                    .sum()
                    .rename(
                        columns={
                            "Saldo_Actual_Prorrateado":
                                "Deuda"
                        }
                    )
                )

                adicionales_tabla = adicionales_tabla.merge(
                    deuda_individual_tabla,
                    on=[
                        "ID_Activo",
                        "Nombre_Socio"
                    ],
                    how="left"
                )
            else:
                adicionales_tabla["Deuda"] = 0

            adicionales_tabla["Deuda"] = (
                pd.to_numeric(
                    adicionales_tabla["Deuda"],
                    errors="coerce"
                )
                .fillna(0)
            )

            adicionales_tabla["Patrimonio_Neto"] = (
                adicionales_tabla["Valor_Activo"]
                - adicionales_tabla["Deuda"]
            )

            adicionales_tabla = adicionales_tabla.sort_values(
                [
                    "Nombre_Socio",
                    "Valor_Activo"
                ],
                ascending=[True, False]
            )

            adicional_table_html = """
<div class="aportes-otros-panel">
    <div class="aportes-card-title2">🏠 Finca Raíz adicional y deuda</div>
    <div class="aportes-card-sub2">
        Activos inmobiliarios fuera del patrimonio neto principal · deuda atribuible a cada socio
    </div>

    <table class="aportes-table2">
        <thead>
            <tr>
                <th>Activo</th>
                <th>Socio</th>
                <th>Ciudad</th>
                <th>Valor</th>
                <th>Deuda</th>
                <th>Neto</th>
            </tr>
        </thead>
        <tbody>
"""

            for _, row in adicionales_tabla.iterrows():

                adicional_table_html += f"""
            <tr>
                <td>{escape_html(row["Nombre_Entidad"])}</td>
                <td>{escape_html(row["Nombre_Socio"])}</td>
                <td>{escape_html(row["Ciudad"])}</td>
                <td><span class="aportes-finca-value compact">{dinero_corto(float(row["Valor_Activo"]))}</span></td>
                <td><span class="aportes-finca-debt compact">-{dinero_corto(float(row["Deuda"]))}</span></td>
                <td><span class="aportes-finca-value compact">{dinero_corto(float(row["Patrimonio_Neto"]))}</span></td>
            </tr>
"""

            adicional_table_html += """
        </tbody>
    </table>

    <div class="aportes-note2">
        Los activos y deudas individuales se mantienen fuera del cálculo
        principal del patrimonio conjunto de los tres socios.
    </div>
</div>
"""

            render_aportes_html(adicional_table_html)

        # --------------------------------------------------------
        # BLOQUE INFERIOR: NEGOCIOS Y OTROS ACTIVOS
        # --------------------------------------------------------
        no_inmo = cargar_negocios_y_otros()
        if not no_inmo.empty:
            matriz_no_inmo = (
                no_inmo
                .pivot_table(
                    index=["Nombre", "Sector", "Ciudad"],
                    columns="Nombre_Socio",
                    values="Participaci__n",
                    aggfunc="sum",
                    fill_value=0
                )
                .reset_index()
            )

            cols_soc = [
                n for n in [
                    "Diego Camacho",
                    "William Camacho",
                    "Andres Camacho",
                    "Andrés Camacho",
                ]
                if n in matriz_no_inmo.columns
            ]

            table_html = """
<div class="aportes-otros-panel">
    <div class="aportes-card-title2">🏪 Negocios y otros activos</div>
    <div class="aportes-card-sub2">Activos no inmobiliarios · participación de cada socio · valoración pendiente</div>
    <table class="aportes-table2">
        <thead>
            <tr>
                <th>Activo</th>
                <th>Tipo</th>
                <th>Ciudad</th>
"""
            for n in cols_soc:
                corto = "Diego" if "Diego" in n else "William" if "William" in n else "Andrés"
                table_html += f"<th>{corto}</th>"

            table_html += """
                <th>Valor</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
"""

            for _, row in matriz_no_inmo.iterrows():
                tipo = str(row.get("Sector", "Otros") or "Otros").strip()
                table_html += "<tr>"
                table_html += f"<td>{escape_html(row.get('Nombre', ''))}</td>"
                table_html += f"<td><span class='aportes-badge'>{escape_html(tipo)}</span></td>"
                table_html += f"<td>{escape_html(row.get('Ciudad', ''))}</td>"

                for n in cols_soc:
                    raw = float(row.get(n, 0) or 0)
                    pct = raw if raw > 1.01 else raw * 100
                    table_html += f"<td>{'-' if pct == 0 else f'{pct:.1f}%'}</td>"

                table_html += "<td>-</td>"
                table_html += "<td><span class='aportes-badge'>Por valorar</span></td>"
                table_html += "</tr>"

            table_html += """
        </tbody>
    </table>
    <div class="aportes-note2"><b>Nota:</b> El patrimonio neto principal está compuesto por Finca Raíz conjunta + Comercio + Vehículos, menos la deuda asociada a esos activos. La Finca Raíz adicional queda fuera del patrimonio neto principal y se presenta por separado.</div>
</div>
"""
            render_aportes_html(table_html)
        else:
            render_aportes_html("""
<div class="aportes-otros-panel">
    <div class="aportes-card-title2">🏪 Negocios y otros activos</div>
    <div class="aportes-card-sub2">No hay participaciones no inmobiliarias disponibles todavía.</div>
</div>
""")



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

    # ========================================================
    # PROMEDIO MENSUAL DEL AÑO DEL FILTRO - YTD
    # ========================================================
    # Se conservan DOS indicadores:
    #
    # 1. Ingreso prom./mes
    #    Ingreso bruto promedio del año.
    #
    # 2. Airbnb comparable / mes
    #    Ingreso bruto promedio
    #    - aseos
    #    - internet
    #    - servicios públicos
    #
    # NO se descuenta administración/inmobiliaria porque ese costo
    # también puede existir en el modelo de renta tradicional.
    #
    # Para el año actual se usan los meses completos cerrados.
    # Ejemplo: octubre 2026 -> enero-septiembre / 9.
    #
    # Para años cerrados -> enero-diciembre / 12.

    anio_promedio = int(pd.Timestamp(fecha_fin).year)

    if anio_promedio == int(hoy.year):

        fecha_fin_ts = pd.Timestamp(fecha_fin)

        # Último mes completo disponible al día de hoy.
        ultimo_mes_cerrado_hoy = (
            pd.Timestamp(hoy.year, hoy.month, 1)
            - pd.offsets.MonthEnd(1)
        )

        # El filtro nunca puede usar meses futuros ni un mes
        # corriente parcialmente cerrado.
        fecha_corte_promedio = min(
            fecha_fin_ts,
            ultimo_mes_cerrado_hoy
        )

        if fecha_corte_promedio.year != anio_promedio:
            fecha_corte_promedio = pd.Timestamp(
                anio_promedio,
                1,
                31
            )
            meses_promedio_anual = 1
        else:
            meses_promedio_anual = int(
                fecha_corte_promedio.month
            )

    else:

        # Para un año cerrado se conserva el promedio anual completo.
        meses_promedio_anual = 12
        fecha_corte_promedio = pd.Timestamp(
            anio_promedio,
            12,
            31
        )

    df_anual_promedio = df[
        (df["Fecha"].dt.year == anio_promedio)
        & (
            df["Fecha"]
            <= fecha_corte_promedio
        )
    ].copy()

    # --------------------------------------------------------
    # PREPARAR CAMPOS PARA CLASIFICAR LOS GASTOS
    # --------------------------------------------------------
    # Se revisan Subcategoría + Detalle + Cuenta para no perder
    # proveedores o conceptos que no contengan literalmente
    # la palabra "internet".
    for col in [
        "Nombre_Subcategoria",
        "Detalle",
        "Nombre_Cuenta"
    ]:
        if col not in df_anual_promedio.columns:
            df_anual_promedio[col] = ""

        df_anual_promedio[col] = (
            df_anual_promedio[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df_anual_promedio["_Texto_Gasto"] = (
        df_anual_promedio["Nombre_Subcategoria"]
        + " "
        + df_anual_promedio["Detalle"]
        + " "
        + df_anual_promedio["Nombre_Cuenta"]
    ).str.lower()

    # --------------------------------------------------------
    # 1. INGRESO BRUTO ANUAL POR PROPIEDAD
    # --------------------------------------------------------
    promedio_anual = (
        df_anual_promedio
        .groupby(
            "Nombre_Propiedad",
            as_index=False
        )["Ingreso"]
        .sum()
        .rename(
            columns={
                "Ingreso":
                    "Ingreso_Anual_YTD"
            }
        )
    )

    # --------------------------------------------------------
    # 2. CLASIFICACIÓN EXCLUSIVA DE GASTOS COMPARABLES
    # --------------------------------------------------------
    # Cada registro entra a UNA SOLA categoría.
    # Administración/inmobiliaria/comisiones NO se descuentan.

    mascara_no_comparable = (
        df_anual_promedio["_Texto_Gasto"].str.contains(
            r"\badministraci[oó]n\b|\binmobiliaria\b|\bcomisi[oó]n\b",
            regex=True,
            na=False
        )
    )

    gastos_validos = (
        (df_anual_promedio["Gasto"] > 0)
        &
        (~mascara_no_comparable)
    )

    categoria_gasto = pd.Series(
        "",
        index=df_anual_promedio.index,
        dtype="object"
    )

    # Aseo / limpieza
    mascara_aseo = (
        gastos_validos
        &
        df_anual_promedio["_Texto_Gasto"].str.contains(
            r"\baseo\b|\blimpieza\b|\bcleaning\b",
            regex=True,
            na=False
        )
    )
    categoria_gasto.loc[mascara_aseo] = "ASEO"

    # Internet / Wi-Fi
    mascara_internet = (
        gastos_validos
        &
        (categoria_gasto == "")
        &
        df_anual_promedio["_Texto_Gasto"].str.contains(
            r"\binternet\b|\bwifi\b|\bwi[\s-]?fi\b",
            regex=True,
            na=False
        )
    )
    categoria_gasto.loc[mascara_internet] = "INTERNET"

    # Servicios públicos
    mascara_servicios = (
        gastos_validos
        &
        (categoria_gasto == "")
        &
        df_anual_promedio["_Texto_Gasto"].str.contains(
            (
                r"\bservicios?\s+p[úu]blicos?\b"
                r"|\benerg[ií]a\b"
                r"|\bagua\b"
                r"|\bacueducto\b"
                r"|\belectricidad\b"
                r"|\bluz\b"
                r"|\bgas\b"
            ),
            regex=True,
            na=False
        )
    )
    categoria_gasto.loc[mascara_servicios] = "SERVICIOS"

    # ESTA COLUMNA ERA LA QUE FALTABA EN LA VERSIÓN ANTERIOR.
    # El KeyError de tu captura venía exactamente de intentar
    # usar "_Categoria_Comparable" antes de crearla.
    df_anual_promedio["_Categoria_Comparable"] = categoria_gasto

    # --------------------------------------------------------
    # 3. GASTOS COMPARABLES ANUALES
    # --------------------------------------------------------
    gastos_comparables = (
        df_anual_promedio[
            df_anual_promedio["_Categoria_Comparable"] != ""
        ]
        .groupby(
            [
                "Nombre_Propiedad",
                "_Categoria_Comparable"
            ],
            as_index=False
        )["Gasto"]
        .sum()
        .pivot(
            index="Nombre_Propiedad",
            columns="_Categoria_Comparable",
            values="Gasto"
        )
        .reset_index()
    )

    for columna in [
        "ASEO",
        "INTERNET",
        "SERVICIOS"
    ]:
        if columna not in gastos_comparables.columns:
            gastos_comparables[columna] = 0

    gastos_comparables = gastos_comparables.rename(
        columns={
            "ASEO": "Aseo_Anual_YTD",
            "INTERNET": "Internet_Anual_YTD",
            "SERVICIOS": "Servicios_Anual_YTD"
        }
    )

    # --------------------------------------------------------
    # 4. ACQUA + TEMPUS 49
    # --------------------------------------------------------
    mask_acqua_tempus = promedio_anual[
        "Nombre_Propiedad"
    ].isin(
        [
            "Torre Acqua",
            "Tempus 49"
        ]
    )

    ingreso_combinado_anual = (
        promedio_anual.loc[
            mask_acqua_tempus,
            "Ingreso_Anual_YTD"
        ].sum()
    )

    proporcion_acqua = 0.703221459479914
    proporcion_tempus = 0.296778540520086

    promedio_anual.loc[
        promedio_anual["Nombre_Propiedad"] == "Torre Acqua",
        "Ingreso_Anual_YTD"
    ] = ingreso_combinado_anual * proporcion_acqua

    promedio_anual.loc[
        promedio_anual["Nombre_Propiedad"] == "Tempus 49",
        "Ingreso_Anual_YTD"
    ] = ingreso_combinado_anual * proporcion_tempus

    # --------------------------------------------------------
    # 5. PROMEDIO BRUTO MENSUAL
    # --------------------------------------------------------
    promedio_anual["Ingreso_Mensual_Medio_Anual"] = (
        promedio_anual["Ingreso_Anual_YTD"]
        / meses_promedio_anual
    )

    # --------------------------------------------------------
    # 6. CONSOLIDAR PRORRATEOS POR MES
    # --------------------------------------------------------
    # Los movimientos están prorrateados por socio.
    # Por eso un mismo mes puede tener 3 registros de $42k.
    #
    # El valor real de ese mes es:
    #   $42k + $42k + $42k = $126k
    #
    # Primero tomamos únicamente los gastos que fueron
    # clasificados como comparables.
    df_gastos_clasificados = (
        df_anual_promedio[
            df_anual_promedio["_Categoria_Comparable"] != ""
        ]
        .copy()
    )

    # Luego sumamos TODOS los registros de la misma categoría
    # dentro de cada mes. Los prorrateos del socio se consolidan
    # antes de calcular el promedio.
    df_gastos_clasificados["_Mes_Gasto"] = (
        df_gastos_clasificados["Fecha"]
        .dt.to_period("M")
        .astype(str)
    )

    gastos_mensuales = (
        df_gastos_clasificados
        .groupby(
            [
                "Nombre_Propiedad",
                "_Categoria_Comparable",
                "_Mes_Gasto"
            ],
            as_index=False
        )["Gasto"]
        .sum()
    )

    # --------------------------------------------------------
    # 7. PROMEDIO DE LOS MESES CON INFORMACIÓN
    # --------------------------------------------------------
    # Después de consolidar el mes, promediamos SOLO los meses
    # donde existe al menos un registro.
    #
    # Ejemplo Acqua Internet:
    #   Junio  = 41 + 41 + 41 = 123k
    #   Julio  = 42 + 42 + 42 = 126k
    #   Agosto = 43 + 43 + 43 = 129k
    #   Sept.  = 17k
    #
    #   Promedio = (123 + 126 + 129 + 17) / 4
    #            = 98.75k
    #
    # Un mes SIN registro no entra como cero y tampoco como dato.

    gastos_promedio_mensual = (
        gastos_mensuales
        .groupby(
            [
                "Nombre_Propiedad",
                "_Categoria_Comparable"
            ],
            as_index=False
        )
        .agg(
            Promedio_Mensual=("Gasto", "mean"),
            Meses_Con_Informacion=("_Mes_Gasto", "nunique")
        )
    )

    gastos_promedio_mensual = (
        gastos_promedio_mensual
        .pivot(
            index="Nombre_Propiedad",
            columns="_Categoria_Comparable",
            values="Promedio_Mensual"
        )
        .reset_index()
    )

    meses_con_info = (
        gastos_mensuales
        .groupby(
            [
                "Nombre_Propiedad",
                "_Categoria_Comparable"
            ],
            as_index=False
        )["_Mes_Gasto"]
        .nunique()
        .pivot(
            index="Nombre_Propiedad",
            columns="_Categoria_Comparable",
            values="_Mes_Gasto"
        )
        .reset_index()
    )

    for columna in [
        "ASEO",
        "INTERNET",
        "SERVICIOS"
    ]:
        if columna not in gastos_promedio_mensual.columns:
            gastos_promedio_mensual[columna] = pd.NA

        if columna not in meses_con_info.columns:
            meses_con_info[columna] = 0

    gastos_promedio_mensual = gastos_promedio_mensual.rename(
        columns={
            "ASEO": "Aseo_Mensual_Medio_Anual",
            "INTERNET": "Internet_Mensual_Medio_Anual",
            "SERVICIOS": "Servicios_Mensual_Medio_Anual"
        }
    )

    meses_con_info = meses_con_info.rename(
        columns={
            "ASEO": "Aseo_Meses_Con_Informacion",
            "INTERNET": "Internet_Meses_Con_Informacion",
            "SERVICIOS": "Servicios_Meses_Con_Informacion"
        }
    )

    promedio_anual = promedio_anual.merge(
        gastos_promedio_mensual[
            [
                "Nombre_Propiedad",
                "Aseo_Mensual_Medio_Anual",
                "Internet_Mensual_Medio_Anual",
                "Servicios_Mensual_Medio_Anual"
            ]
        ],
        on="Nombre_Propiedad",
        how="left"
    )

    promedio_anual = promedio_anual.merge(
        meses_con_info[
            [
                "Nombre_Propiedad",
                "Aseo_Meses_Con_Informacion",
                "Internet_Meses_Con_Informacion",
                "Servicios_Meses_Con_Informacion"
            ]
        ],
        on="Nombre_Propiedad",
        how="left"
    )

    for columna in [
        "Aseo_Mensual_Medio_Anual",
        "Internet_Mensual_Medio_Anual",
        "Servicios_Mensual_Medio_Anual"
    ]:
        promedio_anual[columna] = pd.to_numeric(
            promedio_anual[columna],
            errors="coerce"
        )

    for columna in [
        "Aseo_Meses_Con_Informacion",
        "Internet_Meses_Con_Informacion",
        "Servicios_Meses_Con_Informacion"
    ]:
        promedio_anual[columna] = pd.to_numeric(
            promedio_anual[columna],
            errors="coerce"
        ).fillna(0).astype(int)

    # --------------------------------------------------------
    # 8. AIRBNB COMPARABLE
    # --------------------------------------------------------
    # Si una propiedad no tiene registros de una categoría,
    # esa categoría vale 0 para el cálculo.
    for columna in [
        "Aseo_Mensual_Medio_Anual",
        "Internet_Mensual_Medio_Anual",
        "Servicios_Mensual_Medio_Anual"
    ]:
        promedio_anual[columna] = (
            pd.to_numeric(
                promedio_anual[columna],
                errors="coerce"
            ).fillna(0)
        )

    promedio_anual["Airbnb_Comparable_Mensual"] = (
        promedio_anual["Ingreso_Mensual_Medio_Anual"]
        - promedio_anual["Aseo_Mensual_Medio_Anual"]
        - promedio_anual["Internet_Mensual_Medio_Anual"]
        - promedio_anual["Servicios_Mensual_Medio_Anual"]
    )

    # Limpieza de columnas auxiliares.
    df_anual_promedio = df_anual_promedio.drop(
        columns=[
            "_Texto_Gasto"
        ],
        errors="ignore"
    )

    # Unir el promedio anual/YTD a la tabla principal.
    # Sin este merge, el HTML no encuentra la columna
    # `Ingreso_Mensual_Medio_Anual`.
    tabla = tabla.merge(
        promedio_anual[
            [
                "Nombre_Propiedad",
                "Ingreso_Anual_YTD",
                "Ingreso_Mensual_Medio_Anual",
                "Airbnb_Comparable_Mensual"
            ]
        ],
        on="Nombre_Propiedad",
        how="left"
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
                "Saldo_Usado",
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
    # CAPITAL PROPIO / CDT
    # ========================================================
    # Se incorpora el capital propio utilizado como base del
    # benchmark CDT. No se mezcla con la inversión total.
    tabla = tabla.merge(
        capital_cdt[[
            "Nombre_Propiedad",
            "Capital_Propio",
            "CDT_Promedio"
        ]],
        on="Nombre_Propiedad",
        how="left"
    )

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

    # Diferencia entre el retorno anualizado del activo y la
    # tasa promedio histórica de CDT utilizada en el benchmark.
    # Debe calcularse DESPUÉS de crear Retorno_Anualizado_Total.
    tabla["Diferencia_vs_CDT"] = (
        tabla["Retorno_Anualizado_Total"]
        - tabla["CDT_Promedio"]
    )

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
            return "-"
        return dinero_corto(valor)

    def porcentaje_tabla(valor, puntos=False):
        if pd.isna(valor):
            return '<span class="investment-muted">-</span>'
        clase = (
            "investment-flow-negative"
            if float(valor) < 0
            else "investment-flow-positive"
        )
        sufijo = " pp" if puntos else "%"
        return (
            f'<span class="{clase}">'
            f'{float(valor):.1f}{sufijo}'
            f'</span>'
        )

    # ========================================================
    # TABLA ÚNICA DE ANÁLISIS INMOBILIARIO
    # ========================================================
    # Se consolidan en una sola vista los datos que antes estaban
    # distribuidos entre tres tablas: inversión, retorno económico
    # y comparación contra CDT.

    html_tabla = """
<div class="investment-panel">

<div class="investment-title">
📊 Análisis inmobiliario
</div>

<div class="investment-subtitle">
Capital propio · inversión total · valor actual · deuda · patrimonio neto · ingreso promedio mensual YTD · Airbnb comparable mensual · flujo histórico · retorno anualizado · benchmark CDT
</div>

<table class="investment-table">
<thead>
<tr>
    <th>Propiedad</th>
    <th>Capital propio</th>
    <th>Inversión total</th>
    <th>Valor actual</th>
    <th>Deuda actual</th>
    <th>Patrimonio neto</th>
    <th>Flujo histórico</th>
    <th>Ingreso prom./mes</th>
    <th>Airbnb comparable / mes</th>
    <th>Flujo prom./mes</th>
    <th>Retorno anualizado</th>
    <th>CDT promedio</th>
    <th>Dif. vs CDT</th>
</tr>
</thead>
<tbody>
"""

    for _, row in tabla.iterrows():

        flujo = row["Flujo_Historico"]

        if pd.isna(flujo):
            flujo_html = '<span class="investment-muted">-</span>'
        else:
            clase = (
                "investment-flow-negative"
                if float(flujo) < 0
                else "investment-flow-positive"
            )
            flujo_html = (
                f'<span class="{clase}">'
                f'{dinero_corto(flujo)}'
                f'</span>'
            )

        retorno_html = porcentaje_tabla(
            row["Retorno_Anualizado_Total"]
        )

        cdt_html = porcentaje_tabla(
            row["CDT_Promedio"]
        )

        diferencia_html = porcentaje_tabla(
            row["Diferencia_vs_CDT"],
            puntos=True
        )

        html_tabla += f"""
<tr>
    <td>{row["Nombre_Propiedad"]}</td>
    <td><span class="investment-money">{valor_tabla(row["Capital_Propio"])}</span></td>
    <td><span class="investment-money">{valor_tabla(row["Inversion"])}</span></td>
    <td>{valor_tabla(row["Valor_Total_Actual"])}</td>
    <td>{valor_tabla(row["Saldo_Usado"] if "Saldo_Usado" in row.index else row["Saldo_Actual"])}</td>
    <td><span class="investment-money">{valor_tabla(row["Patrimonio_Actual"])}</span></td>
    <td>{flujo_html}</td>
    <td>{valor_tabla(row["Ingreso_Mensual_Medio_Anual"])}</td>
    <td>{valor_tabla(row["Airbnb_Comparable_Mensual"])}</td>
    <td>{valor_tabla(row["Flujo_Mensual_Promedio"])}</td>
    <td>{retorno_html}</td>
    <td>{cdt_html}</td>
    <td>{diferencia_html}</td>
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
    Inversión total = capital propio + financiación incluida en la inversión registrada.
    Patrimonio neto = valor actual del activo + equipamiento − deuda actual.
    Ingreso prom./mes = ingreso bruto promedio del año seleccionado; los gastos comparables se consolidan por mes y se promedian solo los meses con información.
    Airbnb comparable = ingreso prom./mes − aseos − internet − servicios públicos.
    No se descuenta administración/inmobiliaria en esta comparación.
    CDT promedio = benchmark histórico ponderado por capital y tiempo de exposición.
    La diferencia se expresa en puntos porcentuales frente al retorno anualizado.
</div>

</div>
"""

    html_tabla = "\n".join(
        linea.strip()
        for linea in html_tabla.splitlines()
    ).strip()

    # Mostrar nuevamente la tabla completa de análisis.
    # Conserva todos los indicadores financieros y deja únicamente
    # las dos columnas de ingresos importantes:
    #   - Ingreso prom./mes
    #   - Airbnb comparable / mes
    st.markdown(
        html_tabla,
        unsafe_allow_html=True
    )

# ============================================================
# VISTA ANÁLISIS - RADAR INMOBILIARIO
# ============================================================

elif st.session_state.vista_airbnb == "Análisis":

    st.markdown(
        """
<div class="section-title">
📊 Radar inmobiliario
</div>

<div class="section-subtitle">
Estudio de mercado + comportamiento del activo + posición estratégica del portafolio.
</div>
""",
        unsafe_allow_html=True
    )

    # ============================================================
    # ============================================================
    # RADAR EJECUTIVO - DECISIÓN DEL PORTAFOLIO
    # ============================================================

    estudio = cargar_estudio_mercado_inmobiliario()

    # Defensa adicional: aunque exista caché previo, el Radar nunca
    # debe mostrar Comercio ni Vehículos.
    if not estudio.empty:
        _categoria_radar_render = (
            estudio["Conjunto_Proyecto"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("ascii")
        )
        estudio = estudio[
            _categoria_radar_render.eq("finca raiz")
        ].copy()

    if not estudio.empty:
        html_decision = """
        <div class="radar-decision-panel">
            <div class="radar-decision-title">🎯 Radar de decisión</div>
            <div class="radar-decision-subtitle">Resumen ejecutivo: mercado estimado + Airbnb comparable + proyección + liquidez + estatus estratégico.</div>
            <table class="radar-decision-table">
                <thead><tr>
                    <th>Activo</th><th>Valor estimado</th><th>Renta amoblada</th><th>Airbnb comparable / mes</th><th>Proyección</th><th>Venta</th><th>Estatus</th><th>Lectura</th>
                </tr></thead><tbody>
        """
        orden_decision = {
            "ENT-0001": 1,
            "ENT-0002": 2,
            "ENT-0003": 3,
            "ENT-0004": 4,
            "ENT-0005": 5,
            "ENT-0006": 6,
            "ENT-0007": 7,
        }
        estudio["Orden"] = estudio["ID_Activo"].map(orden_decision).fillna(99)
        estudio = estudio.sort_values(["Orden", "Nombre_Entidad"])

        comparable_radar = calcular_airbnb_comparable_radar(
            df,
            fecha_fin
        )

        estudio = estudio.merge(
            comparable_radar,
            left_on="Nombre_Entidad",
            right_on="Nombre_Propiedad",
            how="left"
        )

        for _, row in estudio.iterrows():
            # La decisión funciona como semáforo estratégico.
            # Se calcula con los números visibles del Radar y con la
            # excepción explícita de Tempus por uso familiar.
            decision_label, lectura_radar = generar_decision_estrategica_radar(
                row,
                row.get("Airbnb_Comparable_Mensual", pd.NA)
            )

            valor_estimado = rango_millones(
                row["Venta_Min_M"],
                row["Venta_Max_M"]
            )
            renta_amoblada = rango_millones(
                row["Renta_Amoblada_Min_M"],
                row["Renta_Amoblada_Max_M"]
            )
            proyeccion = (
                "-"
                if pd.isna(row["Proyeccion_Zona_5A"])
                else f"{float(row['Proyeccion_Zona_5A']):.1f}/10"
            )
            venta_label = str(
                row.get("Facilidad_Venta", "-")
                or "-"
            )

            # Resolver el color de venta localmente para evitar
            # dependencias de funciones externas en el bloque Radar.
            venta_upper = venta_label.upper()

            if "BUENA" in venta_upper:
                venta_css = "radar-decision-good"
            elif "MEDIA" in venta_upper:
                venta_css = "radar-decision-medium"
            elif "BAJA" in venta_upper:
                venta_css = "radar-decision-low"
            else:
                venta_css = "radar-decision-neutral"

            decision_css = clase_decision(
                decision_label
            )

            comparable = row.get(
                "Airbnb_Comparable_Mensual",
                pd.NA
            )

            comparable_txt = (
                dinero_corto(comparable)
                if pd.notna(comparable)
                else "-"
            )

            html_decision += f"""
<tr>
    <td>{escape_html(row.get("Nombre_Entidad", "-"))}</td>
    <td><span class="radar-decision-value">{valor_estimado}</span></td>
    <td><span class="radar-decision-value">{renta_amoblada}</span></td>
    <td><span class="radar-decision-value">{comparable_txt}</span></td>
    <td><span class="radar-decision-projection">{proyeccion}</span></td>
    <td><span class="radar-decision-badge {venta_css}">{escape_html(venta_label)}</span></td>
    <td><span class="radar-decision-badge {decision_css}">{escape_html(decision_label)}</span></td>
    <td>{escape_html(lectura_radar)}</td>
</tr>
"""

        html_decision += """
                </tbody>
            </table>
            <div class="radar-note">
                <b>Decisión:</b> funciona como semáforo estratégico y se calcula con los números visibles del Radar.
                La señal económica no se confunde con la decisión patrimonial: Tempus 49, por ejemplo, conserva
                una señal de revisión económica, pero permanece en <b>MANTENER</b> mientras tenga uso familiar.
                <b>Airbnb comparable</b> = ingreso bruto promedio YTD menos aseo/limpieza, internet/wifi
                y servicios públicos identificados; los gastos prorrateados se consolidan primero por mes
                y luego se promedian solo los meses con información.
            </div>
        </div>
        """

        # IMPORTANTE: quitar toda la indentación antes de enviar
        # el HTML a Streamlit. De lo contrario, Markdown lo interpreta
        # como un bloque de código y muestra <tr>, <td>, etc.
        html_decision = "\n".join(
            linea.strip()
            for linea in html_decision.splitlines()
            if linea.strip()
        )

        st.markdown(
            html_decision,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="radar-decision-panel">
                <div class="radar-decision-title">🎯 Radar de decisión</div>
                <div class="radar-note">No hay datos disponibles en Estudio_Mercado_Inmobiliario.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ============================================================
    # CONCLUSIÓN EJECUTIVA DEL PORTAFOLIO
    # ============================================================
    # Esta conclusión usa únicamente los datos disponibles en
    # Estudio_Mercado_Inmobiliario. No pretende ser una señal automática
    # de venta ni reemplaza una revisión puntual del mercado externo.

    if not estudio.empty:
        estudio_conclusion = estudio.copy()
        estudio_conclusion["Proyeccion_Num"] = pd.to_numeric(
            estudio_conclusion["Proyeccion_Zona_5A"],
            errors="coerce"
        )

        proyeccion_promedio = estudio_conclusion["Proyeccion_Num"].mean()
        row_max = estudio_conclusion.loc[
            estudio_conclusion["Proyeccion_Num"].idxmax()
        ] if estudio_conclusion["Proyeccion_Num"].notna().any() else None

        candidatos_rotacion = estudio_conclusion[
            estudio_conclusion["Rol_Portafolio"].str.upper().str.contains(
                "VENDER|ROTAR", regex=True, na=False
            )
        ]

        activos_alta_proyeccion = estudio_conclusion[
            estudio_conclusion["Proyeccion_Num"] >= 8.5
        ]

        def nombres(df_tmp):
            if df_tmp.empty:
                return "ninguno"
            return ", ".join(df_tmp["Nombre_Entidad"].astype(str).tolist())

        rotacion_txt = nombres(candidatos_rotacion)
        alta_proj_txt = nombres(activos_alta_proyeccion)

        lectura_mercado = (
            f"El estudio sitúa la proyección media del portafolio en "
            f"{proyeccion_promedio:.1f}/10."
        )

        if row_max is not None:
            lectura_mercado += (
                f" {row_max['Nombre_Entidad']} lidera la proyección de zona con "
                f"{float(row_max['Proyeccion_Num']):.1f}/10."
            )

        lectura_rotacion = (
            f"El principal foco de rotación señalado por el estudio es {rotacion_txt}."
            if not candidatos_rotacion.empty
            else "El estudio no identifica actualmente un activo con señal explícita de venta/rotación."
        )

        lectura_oportunidades = (
            f"Los activos con proyección de zona igual o superior a 8.5/10 son {alta_proj_txt}, "
            "por lo que conviene priorizar su conservación y optimización antes de plantear una venta."
            if not activos_alta_proyeccion.empty
            else "No hay activos con una proyección de zona de 8.5/10 o superior según el estudio."
        )

        lectura_final = (
            "La lectura general favorece conservar los activos con mejor combinación de proyección, renta y liquidez, "
            "y estudiar una rotación únicamente donde el capital pueda tener un uso más atractivo. "
            "La decisión final debe contrastarse con deuda, flujo Airbnb, costo de salida y precio realmente negociable."
        )

        html_conclusion = f"""
<div class="radar-decision-panel">
    <div class="radar-decision-title">🧠 Conclusión ejecutiva</div>
    <div class="radar-decision-subtitle">Lectura automática construida a partir del estudio de mercado cargado en BigQuery.</div>
    <div class="radar-signal"><b>📊 Lectura de mercado:</b> {escape_html(lectura_mercado)}</div>
    <div class="radar-signal"><b>🎯 Rotación:</b> {escape_html(lectura_rotacion)}</div>
    <div class="radar-signal"><b>🚀 Activos a conservar:</b> {escape_html(lectura_oportunidades)}</div>
    <div class="radar-signal"><b>✅ Conclusión:</b> {escape_html(lectura_final)}</div>
    <div class="radar-note"><b>Nota:</b> esta conclusión usa el estudio disponible en BigQuery; no está haciendo una consulta en tiempo real a portales inmobiliarios ni pretende estimar precios de cierre.</div>
</div>
"""

        html_conclusion = "\n".join(
            linea.strip()
            for linea in html_conclusion.splitlines()
            if linea.strip()
        )

        st.markdown(
            html_conclusion,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
<div class="radar-decision-panel">
    <div class="radar-decision-title">🧠 Conclusión ejecutiva</div>
    <div class="radar-note">No hay información suficiente en Estudio_Mercado_Inmobiliario para generar una conclusión.</div>
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
