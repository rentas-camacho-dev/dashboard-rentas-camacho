import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
       FUENTE GENERAL
       ===================================================== */

    html, body, [class*="css"], .stApp {
        font-family: Arial, Helvetica, sans-serif !important;
    }

    .stApp {
        background: #F4F6F8;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1800px;
    }

    /* =====================================================
       TÍTULO PRINCIPAL
       ===================================================== */

    .dashboard-header {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 22px 28px 20px 28px;
        margin-bottom: 26px;
        border: 1px solid #E3E8EE;
    }

    .dashboard-title {
        color: #19345D;
        font-size: 29px;
        font-weight: 700;
        line-height: 1.25;
        margin: 0;
        padding: 0;
    }

    .dashboard-subtitle {
        color: #718096;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.5;
        margin-top: 8px;
        padding: 0;
    }

    /* =====================================================
       TÍTULOS DE SECCIÓN
       ===================================================== */

    .section-title {
        color: #19345D;
        font-size: 22px;
        font-weight: 700;
        line-height: 1.25;
        margin: 0;
        padding: 0;
    }

    .section-subtitle {
        color: #718096;
        font-size: 13px;
        font-weight: 400;
        line-height: 1.45;
        margin-top: 6px;
        margin-bottom: 14px;
        padding: 0;
    }

    /* =====================================================
       FILTROS
       ===================================================== */

    .filter-title {
        color: #19345D;
        font-size: 21px;
        font-weight: 700;
        margin-top: 4px;
        margin-bottom: 10px;
    }

    /* =====================================================
       LABELS DE STREAMLIT
       ===================================================== */

    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        color: #435979 !important;
        font-size: 14px !important;
        font-weight: 400 !important;
    }

    /* =====================================================
       KPI
       ===================================================== */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #DCE3EA;
        border-radius: 14px;
        padding: 18px 20px 16px 20px;
        min-height: 118px;
        box-shadow: 0 2px 7px rgba(25,52,93,0.05);
    }

    .kpi-title {
        color: #435979;
        font-size: 15px;
        font-weight: 400;
        line-height: 1.3;
        margin-bottom: 8px;
    }

    .kpi-value {
        color: #293241;
        font-size: 27px;
        font-weight: 400;
        line-height: 1.25;
        margin-bottom: 8px;
    }

    .kpi-change {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 14px;
        font-size: 12px;
        font-weight: 400;
        line-height: 1.2;
    }

    .kpi-positive {
        background: #E7F7ED;
        color: #16843D;
    }

    .kpi-negative {
        background: #FDEAEA;
        color: #D93636;
    }

    .kpi-neutral {
        background: #EEF2F5;
        color: #6B778C;
    }

    /* =====================================================
       PANELES PRINCIPALES
       ===================================================== */

    .main-panel {
        background: #EEF1F4;
        border: 1px solid #D3DAE2;
        border-radius: 14px;
        padding: 16px;
        height: 570px;
        min-height: 570px;
        overflow: hidden;
    }

    .panel-inner {
        height: 100%;
    }

    /* =====================================================
       TABLA
       ===================================================== */

    .property-table-wrapper {
        height: 480px;
        overflow: hidden;
        background: #FFFFFF;
        border-radius: 11px;
        border: 1px solid #D8E0E7;
    }

    .property-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-family: Arial, Helvetica, sans-serif;
    }

    .property-table thead th {
        background: #008F83;
        color: white;
        font-size: 14px;
        font-weight: 400;
        padding: 12px 10px;
        text-align: left;
        border: none;
    }

    .property-table thead th:not(:first-child) {
        text-align: center;
    }

    .property-table tbody td {
        background: #FFFFFF;
        color: #19345D;
        font-size: 13px;
        font-weight: 400;
        padding: 10px 10px;
        border-bottom: 1px solid #E4E9EE;
        vertical-align: middle;
    }

    .property-table tbody td:not(:first-child) {
        text-align: center;
    }

    .property-table tbody tr:last-child td {
        border-bottom: none;
    }

    .property-table .total-row td {
        background: #EDF2F6;
        border-top: 2px solid #CCD6E0;
        font-weight: 400;
    }

    .income {
        color: #008F63 !important;
    }

    .expense {
        color: #E84C35 !important;
    }

    .flow-positive {
        color: #008F63 !important;
    }

    .flow-negative {
        color: #E84C35 !important;
    }

    .progress-container {
        width: 100%;
        height: 7px;
        background: #E8EDF1;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 5px;
    }

    .progress-bar {
        height: 100%;
        background: #13AFC9;
        border-radius: 8px;
    }

    .progress-empty {
        height: 100%;
        width: 0%;
        background: #E8EDF1;
    }

    /* =====================================================
       ESTADO
       ===================================================== */

    .estado {
        font-size: 16px;
        text-align: center;
    }

    /* =====================================================
       PANEL DE GASTOS
       ===================================================== */

    .expense-total {
        color: #19345D;
        font-size: 25px;
        font-weight: 400;
        line-height: 1.25;
        margin-top: 3px;
    }

    .expense-label {
        color: #718096;
        font-size: 12px;
        font-weight: 400;
        margin-top: 6px;
        margin-bottom: 12px;
    }

    .expense-header-row {
        display: grid;
        grid-template-columns: 1fr 95px 45px;
        gap: 8px;
        color: #718096;
        font-size: 12px;
        font-weight: 400;
        padding-bottom: 7px;
        border-bottom: 1px solid #DCE2E8;
    }

    .expense-row {
        display: grid;
        grid-template-columns: 1fr 95px 45px;
        gap: 8px;
        align-items: center;
        color: #435979;
        font-size: 12px;
        font-weight: 400;
        padding: 8px 0;
        border-bottom: 1px solid #E1E6EB;
    }

    .expense-name {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .expense-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex: 0 0 auto;
        background: #ED4B5C;
    }

    .expense-value {
        text-align: right;
        color: #19345D;
    }

    .expense-percent {
        text-align: right;
        color: #718096;
    }

    .expense-highlight {
        margin-top: 12px;
        background: #EAF3FF;
        border: 1px solid #BBD6F7;
        border-radius: 10px;
        padding: 10px 12px;
        color: #435979;
        font-size: 12px;
        font-weight: 400;
        line-height: 1.45;
    }

    /* =====================================================
       ANÁLISIS ANUAL
       ===================================================== */

    .annual-title {
        color: #19345D;
        font-size: 22px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 4px;
    }

    .annual-subtitle {
        color: #718096;
        font-size: 13px;
        font-weight: 400;
        margin-bottom: 14px;
    }

    .annual-card {
        background: #EEF1F4;
        border: 1px solid #D3DAE2;
        border-radius: 14px;
        padding: 18px;
    }

    /* =====================================================
       OCULTAR ELEMENTOS INNECESARIOS
       ===================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: visible;
    }

    </style>
    """,
    unsafe_allow_html=True
)


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

    numeric_cols = [
        "Porcentaje",
        "Valor",
        "Valor_Repartido",
        "Ingreso",
        "Gasto"
    ]

    for col in numeric_cols:
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

def formato_pesos(valor):

    valor = float(valor or 0)

    return "$" + f"{valor:,.0f}".replace(",", ".")


def formato_compacto(valor):

    valor = float(valor or 0)

    signo = "-" if valor < 0 else ""
    valor_abs = abs(valor)

    if valor_abs >= 1_000_000:
        return f"{signo}$ {valor_abs / 1_000_000:.1f} M"

    if valor_abs >= 1_000:
        return f"{signo}$ {valor_abs / 1_000:.0f} mil"

    return f"{signo}$ {valor_abs:,.0f}"


def formato_porcentaje(valor):

    if pd.isna(valor):
        return "-"

    return f"{valor:.1f}%"


def calcular_rentabilidad(ingreso, gasto):

    if ingreso == 0:
        return 0

    return (ingreso - gasto) / ingreso


def estado_propiedad(rentabilidad):

    if rentabilidad >= 0.50:
        return "⚡"

    if rentabilidad >= 0.15:
        return "🏆"

    return "🚩"


# ============================================================
# TÍTULO
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
    '<div class="filter-title">🔎 Filtros</div>',
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
    .tolist()
)

propiedades = sorted(
    df["Nombre_Propiedad"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

socios = sorted(
    df["Nombre_Socio"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


with col1:

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        key="filtro_ciudad"
    )


with col2:

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades,
        key="filtro_propiedad"
    )


with col3:

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios,
        key="filtro_socio"
    )


with col4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    rango_fecha = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        key="filtro_fecha"
    )


# ============================================================
# FILTROS BASE
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
# FILTRO DE FECHA PARA KPI Y RESUMEN
# ============================================================

if isinstance(rango_fecha, tuple) and len(rango_fecha) == 2:

    fecha_inicio = pd.Timestamp(rango_fecha[0])
    fecha_fin = pd.Timestamp(rango_fecha[1])

else:

    fecha_inicio = pd.Timestamp(fecha_min)
    fecha_fin = pd.Timestamp(fecha_max)


df_filtrado = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio) &
    (df_graficos["Fecha"] <= fecha_fin)
].copy()


# ============================================================
# KPI
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()
gasto_total = df_filtrado["Gasto"].sum()
flujo_total = ingreso_total - gasto_total

rentabilidad = calcular_rentabilidad(
    ingreso_total,
    gasto_total
)


# ============================================================
# COMPARACIÓN CON PERIODO ANTERIOR
# ============================================================

duracion = (fecha_fin - fecha_inicio).days + 1

fecha_fin_anterior = fecha_inicio - pd.Timedelta(days=1)
fecha_inicio_anterior = (
    fecha_inicio - pd.Timedelta(days=duracion)
)


df_anterior = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio_anterior) &
    (df_graficos["Fecha"] <= fecha_fin_anterior)
].copy()


ingreso_anterior = df_anterior["Ingreso"].sum()
gasto_anterior = df_anterior["Gasto"].sum()

flujo_anterior = (
    ingreso_anterior - gasto_anterior
)

rentabilidad_anterior = calcular_rentabilidad(
    ingreso_anterior,
    gasto_anterior
)


def variacion_porcentual(actual, anterior):

    if anterior == 0:

        if actual == 0:
            return 0

        return None

    return ((actual - anterior) / abs(anterior)) * 100


var_ingreso = variacion_porcentual(
    ingreso_total,
    ingreso_anterior
)

var_gasto = variacion_porcentual(
    gasto_total,
    gasto_anterior
)

var_flujo = variacion_porcentual(
    flujo_total,
    flujo_anterior
)

var_rentabilidad = (
    rentabilidad - rentabilidad_anterior
) * 100


def html_variacion(valor, tipo="porcentaje"):

    if valor is None:

        return """
        <span class="kpi-change kpi-neutral">
            — vs. periodo anterior
        </span>
        """

    if tipo == "pp":

        texto = f"{valor:+.1f} pp"

    else:

        texto = f"{valor:+.1f}%"


    clase = (
        "kpi-positive"
        if valor >= 0
        else
        "kpi-negative"
    )

    flecha = "↑" if valor >= 0 else "↓"

    return f"""
    <span class="kpi-change {clase}">
        {flecha} {texto}
    </span>
    """


# ============================================================
# KPI HTML
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(
    4,
    gap="large"
)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                💰 Ingreso Total
            </div>

            <div class="kpi-value">
                {formato_pesos(ingreso_total)}
            </div>

            {html_variacion(var_ingreso)}

        </div>
        """,
        unsafe_allow_html=True
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🧾 Gasto Total
            </div>

            <div class="kpi-value">
                {formato_pesos(gasto_total)}
            </div>

            {html_variacion(var_gasto)}

        </div>
        """,
        unsafe_allow_html=True
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                💵 Flujo
            </div>

            <div class="kpi-value">
                {formato_pesos(flujo_total)}
            </div>

            {html_variacion(var_flujo)}

        </div>
        """,
        unsafe_allow_html=True
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🎯 Rentabilidad
            </div>

            <div class="kpi-value">
                {rentabilidad * 100:.1f}%
            </div>

            {html_variacion(
                var_rentabilidad,
                "pp"
            )}

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RESUMEN POR PROPIEDAD + GASTOS
# ============================================================

st.write("")


left, right = st.columns(
    [1.55, 1],
    gap="large"
)


# ============================================================
# TABLA PROPIEDADES
# ============================================================

with left:

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


    resumen = (
        df_filtrado
        .groupby("Nombre_Propiedad", as_index=False)
        .agg(
            Ingreso=("Ingreso", "sum"),
            Gasto=("Gasto", "sum")
        )
    )


    resumen["Flujo"] = (
        resumen["Ingreso"] -
        resumen["Gasto"]
    )


    resumen["Rentabilidad"] = np.where(
        resumen["Ingreso"] != 0,
        resumen["Flujo"] / resumen["Ingreso"],
        0
    )


    resumen = resumen.sort_values(
        "Ingreso",
        ascending=False
    ).reset_index(drop=True)


    total_ingreso = resumen["Ingreso"].sum()
    total_gasto = resumen["Gasto"].sum()
    total_flujo = (
        total_ingreso -
        total_gasto
    )

    total_rentabilidad = calcular_rentabilidad(
        total_ingreso,
        total_gasto
    )


    html_table = """
    <div class="main-panel">

        <div class="property-table-wrapper">

            <table class="property-table">

                <thead>

                    <tr>
                        <th style="width:28%;">Propiedad</th>
                        <th style="width:16%;">Ingreso</th>
                        <th style="width:16%;">Gasto</th>
                        <th style="width:16%;">Flujo</th>
                        <th style="width:19%;">%</th>
                        <th style="width:5%;">Estado</th>
                    </tr>

                </thead>

                <tbody>
    """


    for _, row in resumen.iterrows():

        ingreso = row["Ingreso"]
        gasto = row["Gasto"]
        flujo = row["Flujo"]
        rent = row["Rentabilidad"]

        if rent > 0:

            bar_width = min(
                abs(rent) * 100,
                100
            )

        else:

            bar_width = 0


        flujo_class = (
            "flow-positive"
            if flujo >= 0
            else
            "flow-negative"
        )


        html_table += f"""

        <tr>

            <td>
                {row["Nombre_Propiedad"]}
            </td>

            <td class="income">
                {formato_compacto(ingreso)}
            </td>

            <td class="expense">
                {formato_compacto(gasto)}
            </td>

            <td class="{flujo_class}">
                {formato_compacto(flujo)}
            </td>

            <td>

                <div>
                    {rent * 100:.1f}%
                </div>

                <div class="progress-container">

                    <div
                        class="progress-bar"
                        style="width:{bar_width:.1f}%"
                    ></div>

                </div>

            </td>

            <td class="estado">
                {estado_propiedad(rent)}
            </td>

        </tr>
        """


    html_table += f"""

        <tr class="total-row">

            <td>
                Total
            </td>

            <td class="income">
                {formato_compacto(total_ingreso)}
            </td>

            <td class="expense">
                {formato_compacto(total_gasto)}
            </td>

            <td class="flow-positive">
                {formato_compacto(total_flujo)}
            </td>

            <td>

                <div>
                    {total_rentabilidad * 100:.1f}%
                </div>

                <div class="progress-container">

                    <div
                        class="progress-bar"
                        style="width:{min(max(total_rentabilidad * 100, 0), 100):.1f}%"
                    ></div>

                </div>

            </td>

            <td class="estado">
                🚩
            </td>

        </tr>

                </tbody>

            </table>

        </div>

    </div>
    """


    st.markdown(
        html_table,
        unsafe_allow_html=True
    )


# ============================================================
# DISTRIBUCIÓN DE GASTOS
# ============================================================

with right:

    st.markdown(
        """
        <div class="section-title">
            💸 Distribución de gastos
        </div>

        <div class="section-subtitle">
            Desglose por subcategoría de gasto en el periodo seleccionado
        </div>
        """,
        unsafe_allow_html=True
    )


    gastos = (
        df_filtrado[
            df_filtrado["Gasto"] > 0
        ]
        .groupby(
            "Nombre_Subcategoria",
            as_index=False
        )["Gasto"]
        .sum()
        .sort_values(
            "Gasto",
            ascending=False
        )
    )


    if gastos.empty:

        st.markdown(
            """
            <div class="main-panel">
                <div style="
                    color:#718096;
                    font-size:14px;
                    padding-top:30px;
                    text-align:center;
                ">
                    No hay gastos para el periodo seleccionado.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        total_gastos_grafico = gastos["Gasto"].sum()

        gastos["Porcentaje"] = (
            gastos["Gasto"] /
            total_gastos_grafico *
            100
        )


        # -----------------------------------------------
        # DONUT
        # -----------------------------------------------

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=gastos["Nombre_Subcategoria"],
                    values=gastos["Gasto"],
                    hole=0.58,
                    textinfo="none",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "$%{value:,.0f}<br>"
                        "%{percent}<extra></extra>"
                    ),
                    marker=dict(
                        line=dict(
                            color="#FFFFFF",
                            width=2
                        )
                    )
                )
            ]
        )


        principal = gastos.iloc[0]

        fig.update_layout(
            height=360,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),
            paper_bgcolor="#EEF1F4",
            plot_bgcolor="#EEF1F4",
            showlegend=False,
            font=dict(
                family="Arial",
                size=13,
                color="#19345D"
            ),
            annotations=[
                dict(
                    text=(
                        f"<b>{principal['Porcentaje']:.1f}%</b>"
                    ),
                    x=0.5,
                    y=0.54,
                    font=dict(
                        family="Arial",
                        size=25,
                        color="#19345D"
                    ),
                    showarrow=False
                ),
                dict(
                    text=str(
                        principal["Nombre_Subcategoria"]
                    ),
                    x=0.5,
                    y=0.43,
                    font=dict(
                        family="Arial",
                        size=11,
                        color="#718096"
                    ),
                    showarrow=False
                )
            ]
        )


        expense_rows = ""

        for _, row in gastos.iterrows():

            expense_rows += f"""
            <div class="expense-row">

                <div class="expense-name">

                    <span class="expense-dot"></span>

                    <span>
                        {row["Nombre_Subcategoria"]}
                    </span>

                </div>

                <div class="expense-value">
                    {formato_compacto(row["Gasto"])}
                </div>

                <div class="expense-percent">
                    {row["Porcentaje"]:.1f}%
                </div>

            </div>
            """


        gasto_principal = principal["Gasto"]
        porcentaje_principal = principal["Porcentaje"]
        nombre_principal = principal["Nombre_Subcategoria"]


        # -----------------------------------------------
        # PANEL COMPLETO
        # -----------------------------------------------

        st.markdown(
            """
            <div class="main-panel">
                <div class="panel-inner">
            """,
            unsafe_allow_html=True
        )


        chart_col, detail_col = st.columns(
            [1.05, 0.95],
            gap="medium"
        )


        with chart_col:

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


        with detail_col:

            st.markdown(
                f"""
                <div class="expense-total">
                    {formato_pesos(total_gastos_grafico)}
                </div>

                <div class="expense-label">
                    Total de egresos operativos
                </div>

                <div class="expense-header-row">

                    <div>
                        Subcategoría
                    </div>

                    <div style="text-align:right;">
                        Valor
                    </div>

                    <div style="text-align:right;">
                        %
                    </div>

                </div>

                {expense_rows}

                <div class="expense-highlight">

                    💡 Mayor centro de gasto:
                    <b>{nombre_principal}</b>
                    ({formato_compacto(gasto_principal)})

                    <br>

                    Representa el
                    {porcentaje_principal:.1f}%
                    del total de egresos operativos.

                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            """
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ANÁLISIS ANUAL
# ============================================================

st.markdown(
    """
    <div class="annual-title">
        📊 Análisis anual
    </div>

    <div class="annual-subtitle">
        Comparación mensual y desempeño promedio de las propiedades
    </div>
    """,
    unsafe_allow_html=True
)


años_disponibles = sorted(
    df_graficos["Fecha"]
    .dropna()
    .dt.year
    .unique()
    .tolist(),
    reverse=True
)


if años_disponibles:

    año_actual_sistema = pd.Timestamp.today().year

    if año_actual_sistema in años_disponibles:

        indice_default = años_disponibles.index(
            año_actual_sistema
        )

    else:

        indice_default = 0


    año_seleccionado = st.selectbox(
        "Año de análisis",
        años_disponibles,
        index=indice_default,
        key="selector_anual"
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

        mes_corte_anual = (
            fecha_corte_anual.month
        )

        dia_corte_anual = (
            fecha_corte_anual.day
        )

    else:

        mes_corte_anual = 12
        dia_corte_anual = 31


    if not datos_año_anterior.empty:

        fecha_limite_anterior = pd.Timestamp(
            year=año_anterior,
            month=mes_corte_anual,
            day=min(
                dia_corte_anual,
                pd.Period(
                    f"{año_anterior}-{mes_corte_anual}"
                ).days_in_month
            )
        )

        datos_año_anterior = datos_año_anterior[
            datos_año_anterior["Fecha"]
            <= fecha_limite_anterior
        ].copy()


    # ========================================================
    # AGRUPACIÓN MENSUAL
    # ========================================================

    meses = list(
        range(
            1,
            mes_corte_anual + 1
        )
    )


    actual_mensual = (
        datos_año
        .groupby(
            datos_año["Fecha"].dt.month
        )["Ingreso"]
        .sum()
    )


    anterior_mensual = (
        datos_año_anterior
        .groupby(
            datos_año_anterior["Fecha"].dt.month
        )["Ingreso"]
        .sum()
    )


    meses_nombre = [
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


    valores_actual = [
        actual_mensual.get(mes, 0)
        for mes in meses
    ]


    valores_anterior = [
        anterior_mensual.get(mes, 0)
        for mes in meses
    ]


    # ========================================================
    # GRÁFICO YTD
    # ========================================================

    fig_ytd = go.Figure()


    fig_ytd.add_trace(
        go.Bar(
            x=[
                meses_nombre[m - 1]
                for m in meses
            ],
            y=valores_actual,
            name=str(año_seleccionado),
            marker_color="#13AFC9"
        )
    )


    fig_ytd.add_trace(
        go.Bar(
            x=[
                meses_nombre[m - 1]
                for m in meses
            ],
            y=valores_anterior,
            name=str(año_anterior),
            marker_color="#AEB8C4"
        )
    )


    fig_ytd.update_layout(
        height=390,
        barmode="group",
        paper_bgcolor="#EEF1F4",
        plot_bgcolor="#EEF1F4",
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20
        ),
        font=dict(
            family="Arial",
            size=13,
            color="#435979"
        ),
        xaxis=dict(
            title="",
            showgrid=False
        ),
        yaxis=dict(
            title="Ingresos",
            gridcolor="#DDE3E8"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )


    # ========================================================
    # PROMEDIO MENSUAL POR PROPIEDAD
    # ========================================================

    datos_promedio = datos_año.copy()


    if not datos_promedio.empty:

        promedio = (
            datos_promedio
            .groupby(
                "Nombre_Propiedad",
                as_index=False
            )
            .agg(
                Ingreso=(
                    "Ingreso",
                    "sum"
                ),
                Fecha_Inicio=(
                    "Fecha",
                    "min"
                ),
                Fecha_Fin=(
                    "Fecha",
                    "max"
                )
            )
        )


        promedio["Meses_Transcurridos"] = (
            (
                promedio["Fecha_Fin"].dt.year -
                promedio["Fecha_Inicio"].dt.year
            ) * 12
            +
            (
                promedio["Fecha_Fin"].dt.month -
                promedio["Fecha_Inicio"].dt.month
            )
            + 1
        )


        promedio["Promedio_Mensual"] = np.where(
            promedio["Meses_Transcurridos"] > 0,
            promedio["Ingreso"] /
            promedio["Meses_Transcurridos"],
            0
        )


        promedio = promedio.sort_values(
            "Promedio_Mensual",
            ascending=True
        )


    else:

        promedio = pd.DataFrame(
            columns=[
                "Nombre_Propiedad",
                "Promedio_Mensual"
            ]
        )


    fig_promedio = go.Figure()


    if not promedio.empty:

        fig_promedio.add_trace(
            go.Bar(
                x=promedio["Promedio_Mensual"],
                y=promedio["Nombre_Propiedad"],
                orientation="h",
                marker_color="#13AFC9",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "$%{x:,.0f}"
                    "<extra></extra>"
                )
            )
        )


    fig_promedio.update_layout(
        height=390,
        paper_bgcolor="#EEF1F4",
        plot_bgcolor="#EEF1F4",
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20
        ),
        font=dict(
            family="Arial",
            size=13,
            color="#435979"
        ),
        xaxis=dict(
            title="Promedio mensual",
            gridcolor="#DDE3E8"
        ),
        yaxis=dict(
            title=""
        ),
        showlegend=False
    )


    # ========================================================
    # DOS GRÁFICOS DEL MISMO TAMAÑO
    # ========================================================

    anual1, anual2 = st.columns(
        2,
        gap="large"
    )


    with anual1:

        st.markdown(
            f"""
            <div class="annual-card">

                <div style="
                    color:#19345D;
                    font-size:16px;
                    font-weight:400;
                    margin-bottom:8px;
                ">
                    Ingreso mensual:
                    {año_seleccionado}
                    vs.
                    {año_anterior}
                </div>
            """,
            unsafe_allow_html=True
        )


        st.plotly_chart(
            fig_ytd,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )


    with anual2:

        st.markdown(
            f"""
            <div class="annual-card">

                <div style="
                    color:#19345D;
                    font-size:16px;
                    font-weight:400;
                    margin-bottom:8px;
                ">
                    Promedio mensual por propiedad —
                    {año_seleccionado}
                </div>
            """,
            unsafe_allow_html=True
        )


        st.plotly_chart(
            fig_promedio,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # TABLA PEQUEÑA PROMEDIO
    # ========================================================

    if not promedio.empty:

        st.write("")


        promedio_mostrar = promedio.copy()

        promedio_mostrar["Promedio mensual"] = (
            promedio_mostrar["Promedio_Mensual"]
            .apply(formato_pesos)
        )


        promedio_mostrar = promedio_mostrar[
            [
                "Nombre_Propiedad",
                "Promedio mensual"
            ]
        ].sort_values(
            "Promedio mensual",
            ascending=False
        )


        st.markdown(
            f"""
            <div class="section-title"
                 style="font-size:18px;">
                Promedio mensual por propiedad
            </div>

            <div class="section-subtitle">
                Calculado sobre los meses transcurridos
                dentro de {año_seleccionado}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.dataframe(
            promedio_mostrar,
            use_container_width=True,
            hide_index=True
        )
