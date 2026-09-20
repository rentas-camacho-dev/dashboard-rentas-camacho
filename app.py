import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import timedelta


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
# ESTILOS
# ============================================================

st.markdown("""
<style>

    /* -------------------------------------------------------
       GENERAL
    ------------------------------------------------------- */

    html, body, [class*="css"] {
        font-family: Arial, Helvetica, sans-serif !important;
    }

    .stApp {
        background-color: #F4F6F8;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 1800px;
    }

    /* -------------------------------------------------------
       TITULO
    ------------------------------------------------------- */

    .dashboard-header {
        background: #FFFFFF;
        border: 1px solid #E3E8EF;
        border-radius: 16px;
        padding: 22px 28px 20px 28px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(15, 35, 60, 0.04);
    }

    .dashboard-title {
        font-size: 30px;
        font-weight: 700;
        color: #17365D;
        line-height: 1.15;
        margin: 0 0 8px 0;
    }

    .dashboard-subtitle {
        color: #718096;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.5;
        margin: 0;
    }

    /* -------------------------------------------------------
       SECCIONES
    ------------------------------------------------------- */

    .section-title {
        color: #17365D;
        font-size: 23px;
        font-weight: 700;
        line-height: 1.25;
        margin-top: 4px;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #718096;
        font-size: 13px;
        font-weight: 400;
        line-height: 1.5;
        margin-top: 0;
        margin-bottom: 14px;
    }

    /* -------------------------------------------------------
       FILTROS
    ------------------------------------------------------- */

    .filters-title {
        color: #17365D;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        color: #43526B !important;
        font-size: 14px !important;
        font-weight: 400 !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: #E0E6ED !important;
        background: #FFFFFF !important;
        min-height: 44px !important;
    }

    /* -------------------------------------------------------
       KPI
    ------------------------------------------------------- */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E1E6EC;
        border-radius: 15px;
        padding: 19px 21px;
        min-height: 132px;
        box-shadow: 0 2px 8px rgba(15, 35, 60, 0.045);
    }

    .kpi-title {
        color: #52617A;
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 27px;
        font-weight: 500;
        line-height: 1.15;
        color: #26364D;
        margin-bottom: 11px;
    }

    .kpi-green {
        color: #00875A;
    }

    .kpi-red {
        color: #E33B22;
    }

    .kpi-blue {
        color: #1167D8;
    }

    .kpi-purple {
        color: #6855C7;
    }

    .kpi-change {
        display: inline-block;
        border-radius: 14px;
        padding: 4px 9px;
        font-size: 12px;
        font-weight: 400;
    }

    .kpi-positive {
        color: #087A45;
        background: #E7F7EE;
    }

    .kpi-negative {
        color: #D73737;
        background: #FDEAEA;
    }

    .kpi-neutral {
        color: #68778C;
        background: #EEF2F6;
    }

    /* -------------------------------------------------------
       PANELES PRINCIPALES
    ------------------------------------------------------- */

    .main-panel {
        background: #EEF1F4;
        border: 1px solid #D5DCE4;
        border-radius: 15px;
        padding: 14px;
        min-height: 560px;
        box-sizing: border-box;
    }

    .panel-inner {
        background: #EEF1F4;
    }

    /* -------------------------------------------------------
       TABLA
    ------------------------------------------------------- */

    .property-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: #FFFFFF;
        border: 1px solid #D8E0E8;
        border-radius: 13px;
        overflow: hidden;
        font-size: 13px;
    }

    .property-table th {
        background: #008F83;
        color: #FFFFFF;
        font-weight: 500;
        padding: 12px 10px;
        text-align: center;
        border: none;
    }

    .property-table th:first-child {
        text-align: left;
    }

    .property-table td {
        padding: 11px 10px;
        border-bottom: 1px solid #E5E9EE;
        color: #243B5A;
        background: #FFFFFF;
        text-align: center;
        font-weight: 400;
    }

    .property-table td:first-child {
        text-align: left;
    }

    .property-table tr:last-child td {
        border-bottom: none;
    }

    .property-table .total-row td {
        background: #F1F5F8;
        border-top: 1px solid #CBD5E0;
        font-weight: 500;
    }

    .income {
        color: #00875A !important;
    }

    .expense {
        color: #E33B22 !important;
    }

    .flow-positive {
        color: #00875A !important;
    }

    .flow-negative {
        color: #E33B22 !important;
    }

    .progress-bg {
        width: 100%;
        height: 6px;
        background: #E7EDF2;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 4px;
    }

    .progress-bar {
        height: 100%;
        background: #16B5D0;
        border-radius: 10px;
    }

    /* -------------------------------------------------------
       GASTOS
    ------------------------------------------------------- */

    .expense-total {
        font-size: 25px;
        color: #17365D;
        font-weight: 500;
        margin-bottom: 2px;
    }

    .expense-label {
        color: #718096;
        font-size: 12px;
        margin-bottom: 13px;
    }

    .expense-list {
        width: 100%;
    }

    .expense-row {
        display: flex;
        align-items: center;
        min-height: 34px;
        border-bottom: 1px solid #E1E6EC;
        font-size: 12px;
        color: #43526B;
    }

    .expense-name {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
    }

    .expense-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }

    .expense-value {
        width: 105px;
        text-align: right;
        color: #243B5A;
        font-weight: 400;
    }

    .expense-percent {
        width: 50px;
        text-align: right;
        color: #718096;
    }

    .expense-highlight {
        margin-top: 14px;
        background: #EAF3FF;
        border: 1px solid #BFD9FF;
        border-radius: 9px;
        padding: 10px 12px;
        color: #43526B;
        font-size: 12px;
        line-height: 1.45;
    }

    /* -------------------------------------------------------
       ANÁLISIS ANUAL
    ------------------------------------------------------- */

    .annual-card {
        background: #FFFFFF;
        border: 1px solid #DCE3EA;
        border-radius: 15px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(15, 35, 60, 0.035);
    }

    /* -------------------------------------------------------
       STREAMLIT
    ------------------------------------------------------- */

    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    .stPlotlyChart {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# CONEXIÓN BIGQUERY
# ============================================================

@st.cache_resource
def get_bigquery_client():

    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
    )

    return bigquery.Client(
        credentials=credentials,
        project="rentascamacho"
    )


client = get_bigquery_client()


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data(ttl=300)
def cargar_datos():

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
    FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    WHERE LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
    """

    df = client.query(query).to_dataframe()

    if df.empty:
        return df

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    columnas_numericas = [
        "Porcentaje",
        "Valor",
        "Valor_Repartido",
        "Ingreso",
        "Gasto"
    ]

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    return df


df = cargar_datos()


if df.empty:
    st.warning("No se encontraron datos de Airbnb.")
    st.stop()


# ============================================================
# FUNCIONES
# ============================================================

def formato_moneda(valor):

    valor = float(valor or 0)

    return "$" + f"{valor:,.0f}".replace(",", ".")


def formato_millones(valor):

    valor = float(valor or 0)

    signo = "-" if valor < 0 else ""
    valor_abs = abs(valor)

    if valor_abs >= 1_000_000_000:
        return f"{signo}$ {valor_abs / 1_000_000_000:.1f} B"

    if valor_abs >= 1_000_000:
        return f"{signo}$ {valor_abs / 1_000_000:.1f} M"

    if valor_abs >= 1_000:
        return f"{signo}$ {valor_abs / 1_000:.0f} mil"

    return f"{signo}$ {valor_abs:,.0f}"


def safe_pct(valor):

    if pd.isna(valor) or np.isinf(valor):
        return 0

    return float(valor)


def variacion_porcentual(actual, anterior):

    if anterior == 0:

        if actual == 0:
            return 0

        return None

    return ((actual - anterior) / abs(anterior)) * 100


def calcular_periodo_anterior(fecha_inicio, fecha_fin):

    dias = (fecha_fin - fecha_inicio).days + 1

    anterior_fin = fecha_inicio - timedelta(days=1)
    anterior_inicio = anterior_fin - timedelta(days=dias - 1)

    return anterior_inicio, anterior_fin


def color_variacion(valor):

    if valor is None:
        return "neutral"

    if valor > 0:
        return "positive"

    if valor < 0:
        return "negative"

    return "neutral"


# ============================================================
# TITULO
# ============================================================

st.markdown("""
<div class="dashboard-header">

    <div class="dashboard-title">
        🏠 Rentas Cortas — Airbnb
    </div>

    <div class="dashboard-subtitle">
        Ingresos, gastos y rentabilidad de tus propiedades
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="filters-title">🔎 Filtros</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(
    [1, 1, 1, 1],
    gap="large"
)


ciudades = sorted(
    df["Ciudad"]
    .dropna()
    .astype(str)
    .unique()
)

propiedades = sorted(
    df["Nombre_Propiedad"]
    .dropna()
    .astype(str)
    .unique()
)

socios = sorted(
    df["Nombre_Socio"]
    .dropna()
    .astype(str)
    .unique()
)


with col1:

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades
    )


with col2:

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades
    )


with col3:

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios
    )


with col4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    fecha_seleccionada = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


if isinstance(fecha_seleccionada, tuple):

    if len(fecha_seleccionada) == 2:
        fecha_inicio = pd.Timestamp(fecha_seleccionada[0])
        fecha_fin = pd.Timestamp(fecha_seleccionada[1])

    else:
        fecha_inicio = pd.Timestamp(fecha_seleccionada[0])
        fecha_fin = fecha_inicio

else:

    fecha_inicio = pd.Timestamp(fecha_seleccionada)
    fecha_fin = fecha_inicio


# ============================================================
# FILTRO GENERAL
# ============================================================

df_graficos = df.copy()

if ciudad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Ciudad"].astype(str) == ciudad
    ]


if propiedad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Nombre_Propiedad"].astype(str) == propiedad
    ]


if socio != "Todos":

    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"].astype(str) == socio
    ]


# ============================================================
# PERIODO SELECCIONADO
# ============================================================

df_filtrado = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio) &
    (df_graficos["Fecha"] <= fecha_fin)
].copy()


# ============================================================
# PERIODO ANTERIOR
# ============================================================

fecha_anterior_inicio, fecha_anterior_fin = calcular_periodo_anterior(
    fecha_inicio,
    fecha_fin
)


df_anterior = df_graficos[
    (df_graficos["Fecha"] >= fecha_anterior_inicio) &
    (df_graficos["Fecha"] <= fecha_anterior_fin)
].copy()


# ============================================================
# KPIs
# ============================================================

ingreso = df_filtrado["Ingreso"].sum()
gasto = df_filtrado["Gasto"].sum()
flujo = ingreso - gasto

rentabilidad = (
    flujo / ingreso * 100
    if ingreso != 0
    else 0
)


ingreso_ant = df_anterior["Ingreso"].sum()
gasto_ant = df_anterior["Gasto"].sum()
flujo_ant = ingreso_ant - gasto_ant

rentabilidad_ant = (
    flujo_ant / ingreso_ant * 100
    if ingreso_ant != 0
    else 0
)


var_ingreso = variacion_porcentual(
    ingreso,
    ingreso_ant
)

var_gasto = variacion_porcentual(
    gasto,
    gasto_ant
)

var_flujo = variacion_porcentual(
    flujo,
    flujo_ant
)

var_rentabilidad = rentabilidad - rentabilidad_ant


# ============================================================
# KPI HTML
# ============================================================

def kpi_html(
    titulo,
    valor,
    variacion,
    clase,
    icono,
    porcentaje=True
):

    if variacion is None:

        texto = "—"
        clase_variacion = "neutral"

    else:

        if porcentaje:

            texto = (
                f"↑ {variacion:+.1f}%"
                if variacion >= 0
                else f"↓ {abs(variacion):.1f}%"
            )

        else:

            texto = (
                f"↑ {variacion:+.1f} pp"
                if variacion >= 0
                else f"↓ {abs(variacion):.1f} pp"
            )

        clase_variacion = color_variacion(variacion)

    return f"""
    <div class="kpi-card">

        <div class="kpi-title">
            {icono} {titulo}
        </div>

        <div class="kpi-value {clase}">
            {valor}
        </div>

        <span class="kpi-change kpi-{clase_variacion}">
            {texto}
        </span>

        <span style="
            color:#8793A5;
            font-size:12px;
            margin-left:5px;
        ">
            vs. periodo anterior
        </span>

    </div>
    """


k1, k2, k3, k4 = st.columns(
    4,
    gap="large"
)


with k1:

    st.markdown(
        kpi_html(
            "Ingreso Total",
            formato_moneda(ingreso),
            var_ingreso,
            "kpi-green",
            "💰"
        ),
        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        kpi_html(
            "Gasto Total",
            formato_moneda(gasto),
            var_gasto,
            "kpi-red",
            "🧾"
        ),
        unsafe_allow_html=True
    )


with k3:

    st.markdown(
        kpi_html(
            "Flujo",
            formato_moneda(flujo),
            var_flujo,
            "kpi-blue",
            "💵"
        ),
        unsafe_allow_html=True
    )


with k4:

    st.markdown(
        kpi_html(
            "Rentabilidad",
            f"{rentabilidad:.1f}%",
            var_rentabilidad,
            "kpi-purple",
            "🎯",
            porcentaje=False
        ),
        unsafe_allow_html=True
    )


st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)


# ============================================================
# TABLA POR PROPIEDAD
# ============================================================

df_prop = (
    df_filtrado
    .groupby("Nombre_Propiedad", dropna=False)
    .agg(
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
    .reset_index()
)

df_prop["Flujo"] = (
    df_prop["Ingreso"] -
    df_prop["Gasto"]
)

df_prop["Rentabilidad"] = np.where(
    df_prop["Ingreso"] != 0,
    df_prop["Flujo"] /
    df_prop["Ingreso"] * 100,
    0
)

df_prop = df_prop.sort_values(
    "Ingreso",
    ascending=False
)


# ============================================================
# GASTOS
# ============================================================

df_gastos = (
    df_filtrado[
        df_filtrado["Gasto"] > 0
    ]
    .groupby("Nombre_Subcategoria")
    ["Gasto"]
    .sum()
    .reset_index()
)

df_gastos = df_gastos.rename(
    columns={
        "Nombre_Subcategoria": "Subcategoria"
    }
)

df_gastos = df_gastos.sort_values(
    "Gasto",
    ascending=False
)

total_gastos = df_gastos["Gasto"].sum()

if total_gastos > 0:

    df_gastos["Porcentaje"] = (
        df_gastos["Gasto"] /
        total_gastos * 100
    )

else:

    df_gastos["Porcentaje"] = 0


# ============================================================
# DOS PANELES PRINCIPALES
# ============================================================

panel_left, panel_right = st.columns(
    [1.55, 1],
    gap="large"
)


# ============================================================
# PANEL IZQUIERDO — TABLA
# ============================================================

with panel_left:

    st.markdown("""
    <div class="section-title">
        🏢 Resumen por propiedad
    </div>

    <div class="section-subtitle">
        Desempeño financiero por propiedad en el periodo seleccionado
    </div>
    """, unsafe_allow_html=True)

    filas = ""

    max_rentabilidad = max(
        df_prop["Rentabilidad"].max()
        if not df_prop.empty else 0,
        1
    )

    for _, row in df_prop.iterrows():

        flujo_val = row["Flujo"]
        rent = row["Rentabilidad"]

        if rent > 0:

            ancho = min(
                max(rent / max_rentabilidad * 100, 0),
                100
            )

        else:

            ancho = 0

        flujo_class = (
            "flow-positive"
            if flujo_val >= 0
            else "flow-negative"
        )

        if rent < 0:

            rent_text = f"{rent:.1f}%"

        else:

            rent_text = f"{rent:.1f}%"

        filas += f"""
        <tr>

            <td>
                {row['Nombre_Propiedad']}
            </td>

            <td class="income">
                {formato_millones(row['Ingreso'])}
            </td>

            <td class="expense">
                {formato_millones(row['Gasto'])}
            </td>

            <td class="{flujo_class}">
                {formato_millones(flujo_val)}
            </td>

            <td>

                <div style="
                    display:flex;
                    flex-direction:column;
                    align-items:flex-end;
                ">

                    <span>
                        {rent_text}
                    </span>

                    <div class="progress-bg">

                        <div
                            class="progress-bar"
                            style="width:{ancho}%"
                        >
                        </div>

                    </div>

                </div>

            </td>

            <td>
                {"🏆" if rent >= 70 else "⚡" if rent >= 40 else "🚩"}
            </td>

        </tr>
        """

    total_flujo = df_prop["Flujo"].sum()

    total_rent = (
        total_flujo /
        df_prop["Ingreso"].sum() * 100
        if df_prop["Ingreso"].sum() != 0
        else 0
    )

    tabla_html = f"""
    <div class="main-panel">

        <table class="property-table">

            <thead>

                <tr>

                    <th style="width:30%;">
                        Propiedad
                    </th>

                    <th style="width:15%;">
                        Ingreso
                    </th>

                    <th style="width:15%;">
                        Gasto
                    </th>

                    <th style="width:15%;">
                        Flujo
                    </th>

                    <th style="width:18%;">
                        %
                    </th>

                    <th style="width:7%;">
                        Estado
                    </th>

                </tr>

            </thead>

            <tbody>

                {filas}

                <tr class="total-row">

                    <td>
                        Total
                    </td>

                    <td class="income">
                        {formato_millones(df_prop["Ingreso"].sum())}
                    </td>

                    <td class="expense">
                        {formato_millones(df_prop["Gasto"].sum())}
                    </td>

                    <td class="flow-positive">
                        {formato_millones(total_flujo)}
                    </td>

                    <td>

                        <div>
                            {total_rent:.1f}%

                            <div class="progress-bg">

                                <div
                                    class="progress-bar"
                                    style="width:{min(max(total_rent,0),100)}%"
                                >
                                </div>

                            </div>

                        </div>

                    </td>

                    <td>
                        🚩
                    </td>

                </tr>

            </tbody>

        </table>

    </div>
    """

    st.markdown(
        tabla_html,
        unsafe_allow_html=True
    )


# ============================================================
# PANEL DERECHO — GASTOS
# ============================================================

with panel_right:

    st.markdown("""
    <div class="section-title">
        💸 Distribución de gastos
    </div>

    <div class="section-subtitle">
        Desglose por subcategoría de gasto en el periodo seleccionado
    </div>
    """, unsafe_allow_html=True)

    expense_html_top = f"""
    <div class="main-panel">

        <div style="
            display:flex;
            gap:20px;
            align-items:flex-start;
        ">

            <div style="
                width:48%;
                display:flex;
                justify-content:center;
                align-items:center;
            " id="expense-chart-space">
            </div>

            <div style="
                width:52%;
                padding:4px 0 0 0;
            ">

                <div class="expense-total">
                    {formato_moneda(total_gastos)}
                </div>

                <div class="expense-label">
                    Total de egresos operativos
                </div>

                <div style="
                    display:flex;
                    color:#718096;
                    font-size:12px;
                    padding-bottom:7px;
                    border-bottom:1px solid #DCE3EA;
                ">

                    <div style="flex:1;">
                        Subcategoría
                    </div>

                    <div style="
                        width:105px;
                        text-align:right;
                    ">
                        Valor
                    </div>

                    <div style="
                        width:50px;
                        text-align:right;
                    ">
                        %
                    </div>

                </div>
    """

    expense_rows = ""

    if not df_gastos.empty:

        colores = [
            "#D71920",
            "#E51E2A",
            "#ED334F",
            "#F05262",
            "#F56B78",
            "#F78591",
            "#F9A2AB",
            "#FAC0C7",
            "#E9D9DB"
        ]

        for i, (_, row) in enumerate(
            df_gastos.head(10).iterrows()
        ):

            color = colores[
                min(i, len(colores) - 1)
            ]

            expense_rows += f"""
            <div class="expense-row">

                <div class="expense-name">

                    <span
                        class="expense-dot"
                        style="background:{color};"
                    >
                    </span>

                    <span>
                        {row['Subcategoria']}
                    </span>

                </div>

                <div class="expense-value">
                    {formato_millones(row['Gasto'])}
                </div>

                <div class="expense-percent">
                    {row['Porcentaje']:.1f}%
                </div>

            </div>
            """

    if not df_gastos.empty:

        mayor = df_gastos.iloc[0]

        mayor_nombre = mayor["Subcategoria"]
        mayor_valor = mayor["Gasto"]
        mayor_pct = mayor["Porcentaje"]

    else:

        mayor_nombre = "Sin información"
        mayor_valor = 0
        mayor_pct = 0


    expense_html_bottom = f"""

                <div class="expense-list">

                    {expense_rows}

                </div>

                <div class="expense-highlight">

                    💡 Mayor centro de gasto:
                    <strong>
                        {mayor_nombre}
                    </strong>
                    ({formato_millones(mayor_valor)})

                    <br>

                    <span style="color:#6B778C;">
                        Representa el {mayor_pct:.1f}%
                        del total de egresos operativos.
                    </span>

                </div>

            </div>

        </div>

    </div>
    """

    # --------------------------------------------------------
    # CONTENEDOR GRIS
    # --------------------------------------------------------

    st.markdown(
        expense_html_top,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # GRAFICO DONUT
    # --------------------------------------------------------

    if not df_gastos.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Pie(
                labels=df_gastos["Subcategoria"],
                values=df_gastos["Gasto"],
                hole=0.58,
                sort=False,
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "$%{value:,.0f}<br>"
                    "%{percent}"
                    "<extra></extra>"
                ),
                marker=dict(
                    colors=[
                        "#D71920",
                        "#E51E2A",
                        "#ED334F",
                        "#F05262",
                        "#F56B78",
                        "#F78591",
                        "#F9A2AB",
                        "#FAC0C7",
                        "#E9D9DB"
                    ],
                    line=dict(
                        color="#EEF1F4",
                        width=2
                    )
                )
            )
        )

        fig.add_annotation(
            text=(
                f"<b>{mayor_pct:.1f}%</b>"
                f"<br><span style='font-size:11px'>{mayor_nombre}</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                size=20,
                color="#17365D",
                family="Arial"
            )
        )

        fig.update_layout(
            height=400,
            margin=dict(
                l=5,
                r=5,
                t=5,
                b=5
            ),
            paper_bgcolor="#EEF1F4",
            plot_bgcolor="#EEF1F4",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    st.markdown(
        expense_html_bottom,
        unsafe_allow_html=True
    )


# ============================================================
# ANÁLISIS ANUAL
# ============================================================

st.markdown(
    "<div style='height:25px'></div>",
    unsafe_allow_html=True
)

st.markdown("""
<div class="section-title">
    📊 Análisis anual
</div>

<div class="section-subtitle">
    Comparación mensual y desempeño promedio de las propiedades
</div>
""", unsafe_allow_html=True)


años_disponibles = sorted(
    df["Fecha"]
    .dropna()
    .dt.year
    .unique(),
    reverse=True
)


if años_disponibles:

    año_actual_sistema = pd.Timestamp.now().year

    if año_actual_sistema in años_disponibles:

        año_default = año_actual_sistema

    else:

        año_default = años_disponibles[0]


    indice_default = años_disponibles.index(
        año_default
    )


    año_seleccionado = st.selectbox(
        "Año de análisis",
        años_disponibles,
        index=indice_default
    )


    año_anterior = año_seleccionado - 1


    datos_año = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_seleccionado
    ].copy()


    datos_año_anterior = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_anterior
    ].copy()


    # ========================================================
    # YTD
    # ========================================================

    if not datos_año.empty:

        fecha_corte_anual = datos_año["Fecha"].max()

        mes_corte_anual = fecha_corte_anual.month

        dia_corte_anual = fecha_corte_anual.day

    else:

        mes_corte_anual = 12
        dia_corte_anual = 31


    datos_año = datos_año[
        datos_año["Fecha"].dt.month <=
        mes_corte_anual
    ]


    datos_año_anterior = datos_año_anterior[
        datos_año_anterior["Fecha"].dt.month <=
        mes_corte_anual
    ]


    mensual_actual = (
        datos_año
        .groupby(
            datos_año["Fecha"].dt.month
        )["Ingreso"]
        .sum()
    )


    mensual_anterior = (
        datos_año_anterior
        .groupby(
            datos_año_anterior["Fecha"].dt.month
        )["Ingreso"]
        .sum()
    )


    meses = list(
        range(
            1,
            mes_corte_anual + 1
        )
    )


    nombres_meses = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic"
    ]


    valores_actuales = [
        mensual_actual.get(m, 0)
        for m in meses
    ]


    valores_anteriores = [
        mensual_anterior.get(m, 0)
        for m in meses
    ]


    labels_meses = [
        nombres_meses[m - 1]
        for m in meses
    ]


    # ========================================================
    # PROMEDIO MENSUAL
    # ========================================================

    datos_promedio = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_seleccionado
    ].copy()


    promedio_prop = []


    for nombre_propiedad, grupo in datos_promedio.groupby(
        "Nombre_Propiedad"
    ):

        ingreso_prop = grupo["Ingreso"].sum()

        fecha_min_prop = grupo["Fecha"].min()
        fecha_max_prop = grupo["Fecha"].max()


        if pd.isna(fecha_min_prop) or pd.isna(fecha_max_prop):

            meses_transcurridos = 1

        else:

            meses_transcurridos = (
                (
                    fecha_max_prop.year -
                    fecha_min_prop.year
                ) * 12
                +
                (
                    fecha_max_prop.month -
                    fecha_min_prop.month
                )
                + 1
            )

            meses_transcurridos = max(
                meses_transcurridos,
                1
            )


        promedio_mensual = (
            ingreso_prop /
            meses_transcurridos
        )


        promedio_prop.append(
            {
                "Propiedad": nombre_propiedad,
                "Ingreso": ingreso_prop,
                "Promedio": promedio_mensual
            }
        )


    df_promedio = pd.DataFrame(
        promedio_prop
    )


    if not df_promedio.empty:

        df_promedio = df_promedio.sort_values(
            "Promedio",
            ascending=False
        )


    # ========================================================
    # GRAFICO INGRESOS MENSUALES
    # ========================================================

    anual_col1, anual_col2 = st.columns(
        [1, 1],
        gap="large"
    )


    with anual_col1:

        st.markdown(
            f"""
            <div class="annual-card">

                <div class="section-title"
                     style="font-size:18px;">

                    📊 Ingresos mensuales

                </div>

                <div class="section-subtitle">

                    Comparativo de ingresos del año
                    seleccionado contra el año anterior

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        fig_anual = go.Figure()


        fig_anual.add_trace(
            go.Bar(
                x=labels_meses,
                y=valores_actuales,
                name=str(año_seleccionado),
                marker_color="#1FA97A"
            )
        )


        fig_anual.add_trace(
            go.Scatter(
                x=labels_meses,
                y=valores_anteriores,
                name=str(año_anterior),
                mode="lines+markers",
                line=dict(
                    color="#1565D8",
                    width=3
                ),
                marker=dict(
                    size=7
                )
            )
        )


        fig_anual.update_layout(
            height=330,
            margin=dict(
                l=20,
                r=20,
                t=10,
                b=20
            ),
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                y=1.12,
                x=0
            ),
            font=dict(
                family="Arial",
                color="#52617A"
            )
        )


        fig_anual.update_yaxes(
            tickprefix="$ ",
            tickformat=",.0f",
            gridcolor="#E7ECF1"
        )


        fig_anual.update_xaxes(
            showgrid=False
        )


        st.plotly_chart(
            fig_anual,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    # ========================================================
    # GRAFICO PROMEDIO
    # ========================================================

    with anual_col2:

        st.markdown(
            f"""
            <div class="annual-card">

                <div class="section-title"
                     style="font-size:18px;">

                    🏠 Promedio mensual por propiedad —
                    {año_seleccionado}

                </div>

                <div class="section-subtitle">

                    Ingreso promedio mensual por propiedad

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        if not df_promedio.empty:

            fig_promedio = go.Figure()


            fig_promedio.add_trace(
                go.Bar(
                    x=df_promedio["Propiedad"],
                    y=df_promedio["Promedio"],
                    marker_color="#7566D9",
                    text=[
                        formato_millones(x)
                        for x in df_promedio["Promedio"]
                    ],
                    textposition="outside",
                    textfont=dict(
                        size=11,
                        color="#17365D"
                    ),
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Promedio: $%{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )


            fig_promedio.update_layout(
                height=330,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=50
                ),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(
                    family="Arial",
                    color="#52617A"
                )
            )


            fig_promedio.update_yaxes(
                tickprefix="$ ",
                tickformat=",.0f",
                gridcolor="#E7ECF1"
            )


            fig_promedio.update_xaxes(
                showgrid=False
            )


            st.plotly_chart(
                fig_promedio,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


# ============================================================
# PIE DE DASHBOARD
# ============================================================

st.markdown(
    "<div style='height:30px'></div>",
    unsafe_allow_html=True
)

st.markdown("""
<div style="
    border-top:1px solid #DCE3EA;
    padding-top:15px;
    color:#7B8798;
    font-size:12px;
    text-align:center;
">
    Rentas Cortas — Airbnb
</div>
""", unsafe_allow_html=True)
