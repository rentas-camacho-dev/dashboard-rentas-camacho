import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import html

from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Rentas Cortas — Airbnb",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# ESTILOS GENERALES
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GENERAL
       ===================================================== */

    html, body, [class*="css"] {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Arial,
            sans-serif;
    }

    .stApp {
        background: #F4F6F8;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }


    /* =====================================================
       TÍTULO PRINCIPAL
       ===================================================== */

    .dashboard-header {
        background: #F4F6F8;
        padding: 8px 4px 22px 4px;
        margin-bottom: 4px;
    }

    .dashboard-title {
        color: #172B4D;
        font-size: 30px;
        font-weight: 600;
        line-height: 1.2;
        margin: 0 0 7px 0;
    }

    .dashboard-subtitle {
        color: #6B778C;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.4;
        margin: 0;
    }


    /* =====================================================
       SECCIONES
       ===================================================== */

    .section-title {
        color: #172B4D;
        font-size: 22px;
        font-weight: 600;
        line-height: 1.25;
        margin-top: 8px;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #6B778C;
        font-size: 12px;
        font-weight: 400;
        line-height: 1.4;
        margin-top: 0;
        margin-bottom: 12px;
    }


    /* =====================================================
       FILTROS
       ===================================================== */

    .filters-title {
        color: #172B4D;
        font-size: 22px;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stDateInput"] label {
        color: #52617A !important;
        font-size: 13px !important;
        font-weight: 400 !important;
    }


    /* =====================================================
       SELECTS
       ===================================================== */

    div[data-baseweb="select"] > div {
        background-color: #EEF1F5 !important;
        border: 1px solid #E1E5EA !important;
        border-radius: 9px !important;
        min-height: 44px !important;
    }


    /* =====================================================
       KPI
       ===================================================== */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E0E5EA;
        border-radius: 14px;
        padding: 17px 18px 15px 18px;
        min-height: 120px;
        box-shadow: 0 2px 7px rgba(23,43,77,0.04);
    }

    .kpi-title {
        color: #52617A;
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 7px;
    }

    .kpi-value {
        color: #172B4D;
        font-size: 27px;
        font-weight: 400;
        line-height: 1.15;
        margin-bottom: 9px;
    }

    .kpi-change {
        display: inline-block;
        border-radius: 14px;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 400;
    }

    .positive {
        color: #138A4B;
        background: #E7F7EE;
    }

    .negative {
        color: #D92D20;
        background: #FDE8E7;
    }

    .neutral {
        color: #52617A;
        background: #EEF1F5;
    }


    /* =====================================================
       TARJETAS PRINCIPALES
       ===================================================== */

    .dashboard-card {
        background: #F1F3F5;
        border: 1px solid #D5DCE3;
        border-radius: 13px;
        overflow: hidden;
        height: 500px;
        padding: 0;
    }


    /* =====================================================
       TABLA
       ===================================================== */

    .property-table {
        width: 100%;
        height: 500px;
        border: 1px solid #D5DCE3;
        border-radius: 13px;
        overflow: hidden;
        background: #F1F3F5;
    }

    .property-table table {
        width: 100%;
        border-collapse: collapse;
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Arial,
            sans-serif;
        font-size: 13px;
    }

    .property-table thead th {
        background: #008F83;
        color: white;
        font-size: 13px;
        font-weight: 400;
        padding: 12px 10px;
        text-align: center;
    }

    .property-table thead th:first-child {
        text-align: left;
    }

    .property-table tbody td {
        color: #344563;
        font-size: 13px;
        font-weight: 400;
        padding: 10px;
        border-bottom: 1px solid #E0E5EA;
        background: #F7F8FA;
        vertical-align: middle;
    }

    .property-table tbody tr:last-child td {
        border-bottom: none;
    }

    .property-name {
        color: #172B4D;
        font-weight: 400;
    }

    .income-text {
        color: #00875A;
        text-align: center;
        white-space: nowrap;
    }

    .expense-text {
        color: #DE350B;
        text-align: center;
        white-space: nowrap;
    }

    .flow-positive {
        color: #00875A;
        text-align: center;
        white-space: nowrap;
    }

    .flow-negative {
        color: #DE350B;
        text-align: center;
        white-space: nowrap;
    }

    .percent-cell {
        width: 27%;
    }

    .percent-value {
        color: #344563;
        font-size: 12px;
        text-align: right;
        margin-bottom: 3px;
    }

    .progress-background {
        height: 6px;
        width: 100%;
        background: #E5E9ED;
        border-radius: 5px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: #16B4D1;
        border-radius: 5px;
    }

    .progress-negative {
        height: 100%;
        width: 0%;
        background: #E5E9ED;
        border-radius: 5px;
    }

    .status-cell {
        text-align: center;
        font-size: 15px;
    }

    .total-row td {
        background: #EAF0F4 !important;
        border-top: 1px solid #CBD5DE;
        font-weight: 400 !important;
    }


    /* =====================================================
       GASTOS
       ===================================================== */

    .expense-card {
        height: 500px;
        background: #F1F3F5;
        border: 1px solid #D5DCE3;
        border-radius: 13px;
        padding: 14px 16px;
        overflow: hidden;
    }

    .expense-layout {
        display: flex;
        width: 100%;
        height: 450px;
        gap: 10px;
        align-items: flex-start;
    }

    .expense-chart {
        width: 48%;
        height: 450px;
        display: flex;
        align-items: flex-start;
        justify-content: center;
    }

    .expense-detail {
        width: 52%;
        height: 450px;
        padding: 5px 4px 0 4px;
    }

    .expense-total {
        color: #172B4D;
        font-size: 22px;
        font-weight: 400;
        margin-bottom: 4px;
    }

    .expense-total-subtitle {
        color: #7A869A;
        font-size: 10px;
        font-weight: 400;
        margin-bottom: 9px;
    }

    .expense-header {
        display: grid;
        grid-template-columns: 1fr 75px 38px;
        padding-bottom: 5px;
        border-bottom: 1px solid #DDE3E8;
        color: #52617A;
        font-size: 10px;
        font-weight: 400;
    }

    .expense-row {
        display: grid;
        grid-template-columns: 1fr 75px 38px;
        min-height: 31px;
        align-items: center;
        border-bottom: 1px solid #E2E6EA;
        color: #344563;
        font-size: 11px;
        font-weight: 400;
    }

    .expense-name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .expense-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        margin-right: 6px;
    }

    .expense-value {
        text-align: right;
        color: #172B4D;
        font-weight: 400;
    }

    .expense-percent {
        text-align: right;
        color: #7A869A;
        font-weight: 400;
    }

    .expense-highlight {
        margin-top: 12px;
        padding: 8px 9px;
        background: #EAF3FF;
        border: 1px solid #C7DDF8;
        border-radius: 7px;
        color: #52617A;
        font-size: 9px;
        font-weight: 400;
        line-height: 1.4;
    }

    .expense-highlight strong {
        color: #344563;
        font-weight: 400;
    }


    /* =====================================================
       ANALISIS ANUAL
       ===================================================== */

    .annual-card {
        background: #FFFFFF;
        border: 1px solid #DDE3E8;
        border-radius: 13px;
        padding: 14px;
    }


    /* =====================================================
       TABLA STREAMLIT
       ===================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }


    /* =====================================================
       ESPACIADO
       ===================================================== */

    div[data-testid="column"] {
        padding-left: 5px;
        padding-right: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CREDENCIALES BIGQUERY
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

def moneda(valor):

    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


def compacto(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)
    absoluto = abs(valor)

    if absoluto >= 1_000_000_000:
        return f"$ {valor / 1_000_000_000:.1f} B"

    if absoluto >= 1_000_000:
        return f"$ {valor / 1_000_000:.1f} M"

    if absoluto >= 1_000:
        return f"$ {valor / 1_000:.0f} mil"

    return f"$ {valor:,.0f}".replace(",", ".")


def porcentaje(valor):

    if pd.isna(valor):
        return "0.0%"

    return f"{valor:.1%}"


def porcentaje_cambio(actual, anterior):

    if anterior == 0:

        if actual > 0:
            return None

        return 0

    return (
        (actual - anterior)
        / abs(anterior)
    )


def format_percent(value):

    if pd.isna(value):
        return "0.0%"

    return f"{value:.1f}%"


# ============================================================
# CONSULTA BIGQUERY
# ============================================================

query = """

SELECT

    Fecha,
    Tipo,
    Tipo_de_Activo,
    Nombre_Tipo,
    Propiedad,
    Nombre_Propiedad,
    Propietario,
    Estado,
    Ciudad,
    Categoria,
    Nombre_Categoria,
    Subcategoria,
    Nombre_Subcategoria,
    Detalle,
    ID_Clave,
    Clave,
    ID_Proveedor,
    Proveedor,
    Cuenta,
    Nombre_Cuenta,
    Observaciones,
    Nombre_Socio,
    Porcentaje,
    Valor,
    Valor_Repartido,
    Ingreso,
    Gasto

FROM
    `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`

WHERE
    LOWER(TRIM(Nombre_Tipo)) = 'airbnb'

"""


@st.cache_data(ttl=300)
def cargar_datos():

    return client.query(query).to_dataframe()


df = cargar_datos()


# ============================================================
# PREPARACIÓN
# ============================================================

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    errors="coerce"
)

for columna in [
    "Valor",
    "Valor_Repartido",
    "Ingreso",
    "Gasto",
    "Porcentaje"
]:

    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).fillna(0)


df["Nombre_Propiedad"] = (
    df["Nombre_Propiedad"]
    .fillna("Sin propiedad")
    .astype(str)
)

df["Nombre_Socio"] = (
    df["Nombre_Socio"]
    .fillna("Sin socio")
    .astype(str)
)

df["Ciudad"] = (
    df["Ciudad"]
    .fillna("Sin ciudad")
    .astype(str)
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="dashboard-header">

        <div class="dashboard-title">
            🏠 Rentas Cortas — Airbnb
        </div>

        <div class="dashboard-subtitle">
            Ingresos, gastos y rentabilidad de tus propiedades
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="filters-title">🔎 Filtros</div>',
    unsafe_allow_html=True
)

f1, f2, f3, f4 = st.columns(
    [1, 1, 1, 1]
)


with f1:

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        index=0
    )


with f2:

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .unique()
        .tolist()
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades,
        index=0
    )


with f3:

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .unique()
        .tolist()
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios,
        index=0
    )


with f4:

    fecha_min = (
        df["Fecha"]
        .dropna()
        .min()
        .date()
    )

    fecha_max = (
        df["Fecha"]
        .dropna()
        .max()
        .date()
    )

    fecha_seleccionada = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# VALIDAR FECHAS
# ============================================================

if isinstance(
    fecha_seleccionada,
    tuple
) and len(fecha_seleccionada) == 2:

    fecha_inicio = pd.Timestamp(
        fecha_seleccionada[0]
    )

    fecha_fin = (
        pd.Timestamp(
            fecha_seleccionada[1]
        )
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

else:

    fecha_inicio = pd.Timestamp(
        fecha_min
    )

    fecha_fin = (
        pd.Timestamp(
            fecha_max
        )
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )


# ============================================================
# FILTRO BASE SIN FECHA
# ============================================================

df_graficos = df.copy()

if ciudad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Ciudad"] == ciudad
    ]

if propiedad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Nombre_Propiedad"]
        == propiedad
    ]

if socio != "Todos":

    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"]
        == socio
    ]


# ============================================================
# FILTRO FINAL CON FECHA
# ============================================================

df_filtrado = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio)
    &
    (df_graficos["Fecha"] <= fecha_fin)
].copy()


# ============================================================
# KPIs
# ============================================================

ingreso_total = (
    df_filtrado["Ingreso"].sum()
)

gasto_total = (
    df_filtrado["Gasto"].sum()
)

flujo_total = (
    ingreso_total
    - gasto_total
)

rentabilidad = (
    flujo_total / ingreso_total
    if ingreso_total != 0
    else 0
)


# ============================================================
# PERIODO ANTERIOR
# ============================================================

duracion = (
    fecha_fin - fecha_inicio
)

fecha_anterior_fin = (
    fecha_inicio
    - pd.Timedelta(days=1)
)

fecha_anterior_inicio = (
    fecha_anterior_fin
    - duracion
)


df_anterior = df_graficos[
    (df_graficos["Fecha"] >= fecha_anterior_inicio)
    &
    (df_graficos["Fecha"] <= fecha_anterior_fin)
]


ingreso_anterior = (
    df_anterior["Ingreso"].sum()
)

gasto_anterior = (
    df_anterior["Gasto"].sum()
)

flujo_anterior = (
    ingreso_anterior
    - gasto_anterior
)

rentabilidad_anterior = (
    flujo_anterior / ingreso_anterior
    if ingreso_anterior != 0
    else 0
)


cambio_ingreso = porcentaje_cambio(
    ingreso_total,
    ingreso_anterior
)

cambio_gasto = porcentaje_cambio(
    gasto_total,
    gasto_anterior
)

cambio_flujo = porcentaje_cambio(
    flujo_total,
    flujo_anterior
)


cambio_rentabilidad = (
    rentabilidad
    - rentabilidad_anterior
)


# ============================================================
# KPI FUNCTION
# ============================================================

def mostrar_kpi(
    titulo,
    valor,
    cambio,
    icono,
    porcentaje_pp=False
):

    if cambio is None:

        texto_cambio = "—"
        clase = "neutral"

    else:

        if porcentaje_pp:

            valor_cambio = (
                cambio * 100
            )

            texto_cambio = (
                f"↑ {valor_cambio:.1f} pp"
                if valor_cambio >= 0
                else
                f"↓ {abs(valor_cambio):.1f} pp"
            )

            clase = (
                "positive"
                if valor_cambio >= 0
                else
                "negative"
            )

        else:

            texto_cambio = (
                f"↑ {cambio:.1%}"
                if cambio >= 0
                else
                f"↓ {abs(cambio):.1%}"
            )

            clase = (
                "positive"
                if cambio >= 0
                else
                "negative"
            )

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                {icono} {titulo}
            </div>

            <div class="kpi-value">
                {moneda(valor)}
            </div>

            <span class="kpi-change {clase}">
                {texto_cambio}
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# KPI ROW
# ============================================================

k1, k2, k3, k4 = st.columns(
    [1, 1, 1, 1]
)


with k1:

    mostrar_kpi(
        "Ingreso Total",
        ingreso_total,
        cambio_ingreso,
        "💰"
    )


with k2:

    mostrar_kpi(
        "Gasto Total",
        gasto_total,
        cambio_gasto,
        "📄"
    )


with k3:

    mostrar_kpi(
        "Flujo",
        flujo_total,
        cambio_flujo,
        "💵"
    )


with k4:

    mostrar_kpi(
        "Rentabilidad",
        rentabilidad,
        cambio_rentabilidad,
        "🎯",
        porcentaje_pp=True
    )


st.markdown(
    "<div style='height:14px'></div>",
    unsafe_allow_html=True
)


# ============================================================
# RESUMEN POR PROPIEDAD + GASTOS
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.55, 1],
    gap="large"
)


# ============================================================
# TABLA PROPIEDADES
# ============================================================

with col_tabla:

    st.markdown(
        """
        <div class="section-title">
            🏢 Resumen por propiedad
        </div>

        <div class="section-subtitle">
            Desempeño financiero por propiedad en el periodo seleccionado
        </div>
        """,
        unsafe_allow_html=True
    )

    resumen_propiedad = (

        df_filtrado
        .groupby(
            "Nombre_Propiedad"
        )
        .agg(
            Ingreso=("Ingreso", "sum"),
            Gasto=("Gasto", "sum")
        )
        .reset_index()
    )

    resumen_propiedad["Flujo"] = (
        resumen_propiedad["Ingreso"]
        -
        resumen_propiedad["Gasto"]
    )

    resumen_propiedad["Rentabilidad"] = (
        resumen_propiedad["Flujo"]
        /
        resumen_propiedad["Ingreso"]
        .replace(0, pd
