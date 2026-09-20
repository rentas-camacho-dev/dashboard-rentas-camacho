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
# ESTILOS
# ============================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Arial, Helvetica, sans-serif;
}

.stApp {
    background-color: #F4F6F8;
    color: #172B4D;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100%;
}

/* ----------------------------------------------------------
   TITULO
---------------------------------------------------------- */

.dashboard-title {
    font-size: 30px;
    font-weight: 700;
    color: #172B4D;
    margin-top: 5px;
    margin-bottom: 4px;
    line-height: 1.2;
}

.dashboard-subtitle {
    color: #6B778C;
    font-size: 14px;
    margin-top: 0;
    margin-bottom: 25px;
    line-height: 1.5;
}

/* ----------------------------------------------------------
   TITULOS DE SECCIÓN
---------------------------------------------------------- */

.section-title {
    font-size: 23px;
    font-weight: 600;
    color: #172B4D;
    margin-top: 4px;
    margin-bottom: 2px;
    line-height: 1.2;
}

.section-subtitle {
    color: #6B778C;
    font-size: 13px;
    font-weight: 400;
    margin-top: 5px;
    margin-bottom: 14px;
    line-height: 1.4;
}

/* ----------------------------------------------------------
   FILTROS
---------------------------------------------------------- */

.filter-title {
    font-size: 22px;
    font-weight: 600;
    color: #172B4D;
    margin-top: 8px;
    margin-bottom: 15px;
}

.filter-label {
    font-size: 14px;
    color: #52617A;
    margin-bottom: 5px;
}

/* ----------------------------------------------------------
   KPI
---------------------------------------------------------- */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DDE2E7;
    border-radius: 12px;
    padding: 17px 20px;
    min-height: 112px;
    box-shadow: 0 2px 6px rgba(9, 30, 66, 0.04);
}

.kpi-title {
    font-size: 15px;
    color: #52617A;
    font-weight: 400;
    margin-bottom: 7px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 500;
    line-height: 1.15;
    color: #172B4D;
    margin-bottom: 9px;
}

.kpi-green {
    color: #00875A;
}

.kpi-red {
    color: #DE350B;
}

.kpi-blue {
    color: #0065FF;
}

.kpi-purple {
    color: #6554C0;
}

.kpi-change {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 12px;
    display: inline-block;
    font-weight: 400;
}

.kpi-positive {
    color: #00875A;
    background: #E3FCEF;
}

.kpi-negative {
    color: #DE350B;
    background: #FFEBE6;
}

.kpi-neutral {
    color: #6B778C;
    background: #F1F2F4;
}

/* ----------------------------------------------------------
   TABLA / GASTOS
---------------------------------------------------------- */

.dashboard-card {
    background: #F7F9FB;
    border: 1px solid #DDE2E7;
    border-radius: 12px;
    box-sizing: border-box;
}

.equal-card {
    min-height: 545px;
    height: 545px;
}

.expense-card {
    min-height: 545px;
    height: 545px;
    padding: 16px 18px;
    box-sizing: border-box;
}

/* ----------------------------------------------------------
   TABLA
---------------------------------------------------------- */

.property-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border: 1px solid #DDE2E7;
    border-radius: 11px;
    background: #FFFFFF;
    font-size: 13px;
}

.property-table th {
    background: #008F83;
    color: white;
    font-weight: 500;
    padding: 11px 10px;
    text-align: left;
    border: none;
}

.property-table th:not(:first-child) {
    text-align: center;
}

.property-table td {
    padding: 10px 10px;
    color: #172B4D;
    border-bottom: 1px solid #E3E7EB;
    font-weight: 400;
}

.property-table td:not(:first-child) {
    text-align: center;
}

.property-table tr:last-child td {
    border-bottom: none;
}

.property-total {
    background: #EDF2F7;
}

.property-total td {
    font-weight: 500;
    border-top: 1px solid #CBD5E0;
}

.income-text {
    color: #00875A;
}

.expense-text {
    color: #DE350B;
}

.flow-positive {
    color: #00875A;
}

.flow-negative {
    color: #DE350B;
}

.progress-bg {
    width: 100%;
    height: 6px;
    background: #E9EEF2;
    border-radius: 5px;
    overflow: hidden;
    margin-top: 4px;
}

.progress-fill {
    height: 100%;
    background: #12B5CB;
    border-radius: 5px;
}

.progress-negative {
    background: #E9EEF2;
}

/* ----------------------------------------------------------
   GASTOS
---------------------------------------------------------- */

.expense-total {
    font-size: 24px;
    font-weight: 500;
    color: #172B4D;
    margin-bottom: 2px;
}

.expense-total-label {
    font-size: 11px;
    color: #7A869A;
    margin-bottom: 12px;
}

.expense-header {
    display: grid;
    grid-template-columns: 1fr 90px 45px;
    padding-bottom: 6px;
    border-bottom: 1px solid #DDE2E7;
    color: #52617A;
    font-size: 11px;
}

.expense-row {
    display: grid;
    grid-template-columns: 1fr 90px 45px;
    align-items: center;
    min-height: 32px;
    border-bottom: 1px solid #E8EBEE;
    font-size: 12px;
    color: #52617A;
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
    flex-shrink: 0;
}

.expense-value {
    text-align: right;
    color: #172B4D;
}

.expense-percent {
    text-align: right;
    color: #7A869A;
}

.expense-highlight {
    margin-top: 15px;
    padding: 10px 12px;
    background: #EAF3FF;
    border: 1px solid #B3D4FF;
    border-radius: 9px;
    color: #52617A;
    font-size: 11px;
    line-height: 1.35;
}

/* ----------------------------------------------------------
   ANALISIS ANUAL
---------------------------------------------------------- */

.analysis-space {
    margin-top: 28px;
}

.chart-card {
    background: #FFFFFF;
    border: 1px solid #DDE2E7;
    border-radius: 12px;
    padding: 8px 10px 3px 10px;
}

/* ----------------------------------------------------------
   PIE FINAL
---------------------------------------------------------- */

.footer-dashboard {
    background: #FFFFFF;
    border: 1px solid #DDE2E7;
    border-radius: 12px;
    padding: 14px 20px;
    margin-top: 25px;
    color: #52617A;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

.footer-item {
    white-space: nowrap;
}

.footer-value {
    font-weight: 500;
    color: #172B4D;
}

.footer-green {
    color: #00875A;
}

/* ----------------------------------------------------------
   STREAMLIT
---------------------------------------------------------- */

div[data-testid="stSelectbox"] {
    margin-bottom: 0;
}

div[data-testid="stDateInput"] {
    margin-bottom: 0;
}

div[data-testid="stVerticalBlock"] > div {
    gap: 0.4rem;
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

    return client.query(query).to_dataframe()


df = cargar_datos()


# ============================================================
# LIMPIEZA
# ============================================================

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    errors="coerce"
)

for columna in [
    "Porcentaje",
    "Valor",
    "Valor_Repartido",
    "Ingreso",
    "Gasto"
]:
    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).fillna(0)

df = df.dropna(
    subset=["Fecha"]
).copy()


# ============================================================
# FUNCIONES
# ============================================================

def formato_numero(valor):

    if pd.isna(valor):
        return "$0"

    valor = float(valor)

    negativo = valor < 0
    valor = abs(valor)

    if valor >= 1_000_000:
        texto = f"${valor / 1_000_000:.1f} M"

    elif valor >= 1_000:
        texto = f"${valor / 1_000:.0f} mil"

    else:
        texto = f"${valor:,.0f}".replace(",", ".")

    if negativo:
        return "-" + texto

    return texto


def moneda(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    texto = f"${valor:,.0f}"

    return texto.replace(",", ".")


def porcentaje(valor):

    if pd.isna(valor):
        return "0.0%"

    return f"{valor:.1f}%"


def porcentaje_safe(valor):

    if pd.isna(valor) or np.isinf(valor):
        return "—"

    return f"{valor:.1f}%"


# ============================================================
# TITULO
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        🏠 Rentas Cortas — Airbnb
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        Ingresos, gastos y rentabilidad de tus propiedades
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

    st.markdown(
        '<div class="filter-label">Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        label_visibility="collapsed"
    )

with col2:

    st.markdown(
        '<div class="filter-label">Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades,
        label_visibility="collapsed"
    )

with col3:

    st.markdown(
        '<div class="filter-label">Socio</div>',
        unsafe_allow_html=True
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios,
        label_visibility="collapsed"
    )

with col4:

    st.markdown(
        '<div class="filter-label">Fecha</div>',
        unsafe_allow_html=True
    )

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    rango_fecha = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        label_visibility="collapsed"
    )


# ============================================================
# FILTRO BASE
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
# FILTRO DE FECHA
# ============================================================

if isinstance(rango_fecha, tuple) and len(rango_fecha) == 2:

    fecha_inicio = pd.Timestamp(rango_fecha[0])
    fecha_fin = (
        pd.Timestamp(rango_fecha[1])
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

else:

    fecha_inicio = pd.Timestamp(fecha_min)
    fecha_fin = (
        pd.Timestamp(fecha_max)
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )


df_filtrado = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio)
    & (df_graficos["Fecha"] <= fecha_fin)
].copy()


# ============================================================
# KPIs
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()
gasto_total = df_filtrado["Gasto"].sum()
flujo_total = ingreso_total - gasto_total

if ingreso_total != 0:
    rentabilidad = flujo_total / ingreso_total
else:
    rentabilidad = 0


# ============================================================
# PERIODO ANTERIOR
# ============================================================

dias_periodo = (
    fecha_fin.normalize()
    - fecha_inicio.normalize()
).days + 1

fecha_fin_anterior = fecha_inicio - pd.Timedelta(days=1)
fecha_inicio_anterior = (
    fecha_fin_anterior
    - pd.Timedelta(days=dias_periodo - 1)
)

df_anterior = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio_anterior)
    & (df_graficos["Fecha"] <= fecha_fin_anterior)
].copy()

ingreso_anterior = df_anterior["Ingreso"].sum()
gasto_anterior = df_anterior["Gasto"].sum()

flujo_anterior = (
    ingreso_anterior - gasto_anterior
)

if ingreso_anterior != 0:
    rentabilidad_anterior = (
        flujo_anterior / ingreso_anterior
    )
else:
    rentabilidad_anterior = 0


def cambio_porcentual(actual, anterior):

    if anterior == 0:

        if actual == 0:
            return 0

        return np.nan

    return ((actual - anterior) / abs(anterior)) * 100


cambio_ingreso = cambio_porcentual(
    ingreso_total,
    ingreso_anterior
)

cambio_gasto = cambio_porcentual(
    gasto_total,
    gasto_anterior
)

cambio_flujo = cambio_porcentual(
    flujo_total,
    flujo_anterior
)

cambio_rentabilidad = (
    (rentabilidad - rentabilidad_anterior)
    * 100
)


def html_cambio(valor, tipo="porcentaje"):

    if pd.isna(valor):
        return (
            '<span class="kpi-change kpi-neutral">'
            '—'
            '</span>'
        )

    if tipo == "pp":

        texto = f"{abs(valor):.1f} pp"

    else:

        texto = f"{abs(valor):.1f}%"

    if valor > 0:

        return (
            '<span class="kpi-change kpi-positive">'
            f"↑ {texto}"
            '</span>'
        )

    elif valor < 0:

        return (
            '<span class="kpi-change kpi-negative">'
            f"↓ {texto}"
            '</span>'
        )

    return (
        '<span class="kpi-change kpi-neutral">'
        f"{texto}"
        '</span>"
    )


# ============================================================
# KPIs EN HTML
# ============================================================

k1, k2, k3, k4 = st.columns(
    [1, 1, 1, 1],
    gap="large"
)

with k1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                💰 Ingreso Total
            </div>

            <div class="kpi-value kpi-green">
                {moneda(ingreso_total)}
            </div>

            {html_cambio(cambio_ingreso)}

            <span style="
                color:#8793A5;
                font-size:12px;
                margin-left:5px;
            ">
                vs. periodo anterior
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

with k2:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🧾 Gasto Total
            </div>

            <div class="kpi-value kpi-red">
                {moneda(gasto_total)}
            </div>

            {html_cambio(cambio_gasto)}

            <span style="
                color:#8793A5;
                font-size:12px;
                margin-left:5px;
            ">
                vs. periodo anterior
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

with k3:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                💵 Flujo
            </div>

            <div class="kpi-value kpi-blue">
                {moneda(flujo_total)}
            </div>

            {html_cambio(cambio_flujo)}

            <span style="
                color:#8793A5;
                font-size:12px;
                margin-left:5px;
            ">
                vs. periodo anterior
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

with k4:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                🎯 Rentabilidad
            </div>

            <div class="kpi-value kpi-purple">
                {rentabilidad * 100:.1f}%
            </div>

            {html_cambio(cambio_rentabilidad, "pp")}

            <span style="
                color:#8793A5;
                font-size:12px;
                margin-left:5px;
            ">
                vs. periodo anterior
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ESPACIO
# ============================================================

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)


# ============================================================
# RESUMEN POR PROPIEDAD + DISTRIBUCIÓN DE GASTOS
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

    resumen = (
        df_filtrado
        .groupby("Nombre_Propiedad", dropna=False)
        .agg(
            Ingreso=("Ingreso", "sum"),
            Gasto=("Gasto", "sum")
        )
        .reset_index()
    )

    resumen["Flujo"] = (
        resumen["Ingreso"]
        - resumen["Gasto"]
    )

    resumen["Rentabilidad"] = np.where(
        resumen["Ingreso"] != 0,
        resumen["Flujo"] / resumen["Ingreso"],
        np.nan
    )

    resumen = resumen.sort_values(
        "Ingreso",
        ascending=False
    )

    filas_html = ""

    for _, fila in resumen.iterrows():

        propiedad_nombre = fila["Nombre_Propiedad"]

        ingreso = fila["Ingreso"]
        gasto = fila["Gasto"]
        flujo = fila["Flujo"]
        rent = fila["Rentabilidad"]

        rent_texto = porcentaje_safe(
            rent * 100
            if not pd.isna(rent)
            else np.nan
        )

        if pd.isna(rent):

            ancho = 0

        else:

            ancho = min(
                max(rent * 100, 0),
                100
            )

        if flujo >= 0:

            flujo_html = (
                f'<span class="flow-positive">'
                f'{formato_numero(flujo)}'
                '</span>'
            )

        else:

            flujo_html = (
                f'<span class="flow-negative">'
                f'{formato_numero(flujo)}'
                '</span>'
            )

        estado = "🚩"

        if rent >= 0.60:
            estado = "🏆"

        elif rent >= 0.40:
            estado = "⚡"

        filas_html += f"""
        <tr>

            <td>
                {propiedad_nombre}
            </td>

            <td>
                <span class="income-text">
                    {formato_numero(ingreso)}
                </span>
            </td>

            <td>
                <span class="expense-text">
                    {formato_numero(gasto)}
                </span>
            </td>

            <td>
                {flujo_html}
            </td>

            <td style="width:24%;">

                <div style="
                    display:flex;
                    justify-content:flex-end;
                    align-items:center;
                    gap:8px;
                ">

                    <span>
                        {rent_texto}
                    </span>

                </div>

                <div class="progress-bg">

                    <div
                        class="progress-fill"
                        style="width:{ancho}%;">
                    </div>

                </div>

            </td>

            <td>
                {estado}
            </td>

        </tr>
        """

    # TOTAL
    total_rent = (
        flujo_total / ingreso_total
        if ingreso_total != 0
        else np.nan
    )

    total_ancho = min(
        max(total_rent * 100, 0)
        if not pd.isna(total_rent)
        else 0,
        100
    )

    total_rent_texto = porcentaje_safe(
        total_rent * 100
        if not pd.isna(total_rent)
        else np.nan
    )

    tabla_html = f"""
    <div class="dashboard-card equal-card">

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

                    <th style="width:20%;">
                        %
                    </th>

                    <th style="width:5%;">
                        Estado
                    </th>

                </tr>

            </thead>

            <tbody>

                {filas_html}

                <tr class="property-total">

                    <td>
                        Total
                    </td>

                    <td>
                        <span class="income-text">
                            {formato_numero(ingreso_total)}
                        </span>
                    </td>

                    <td>
                        <span class="expense-text">
                            {formato_numero(gasto_total)}
                        </span>
                    </td>

                    <td>
                        <span class="flow-positive">
                            {formato_numero(flujo_total)}
                        </span>
                    </td>

                    <td>

                        <div style="
                            display:flex;
                            justify-content:flex-end;
                        ">
                            {total_rent_texto}
                        </div>

                        <div class="progress-bg">

                            <div
                                class="progress-fill"
                                style="width:{total_ancho}%;">
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
# DISTRIBUCIÓN DE GASTOS
# ============================================================

with col_gastos:

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

    gasto_sub = (
        df_filtrado[
            df_filtrado["Gasto"] > 0
        ]
        .groupby("Nombre_Subcategoria")["Gasto"]
        .sum()
        .sort_values(ascending=False)
    )

    # Si no existen gastos
    if gasto_sub.empty:

        gasto_sub = pd.Series(
            dtype=float
        )

    colores = [
        "#E51C2A",
        "#ED334B",
        "#EF465A",
        "#F05A6A",
        "#F36E7C",
        "#F68793",
        "#F9A0AA",
        "#F5C9CD",
        "#E8D7D9"
    ]

    if not gasto_sub.empty:

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=gasto_sub.index.tolist(),
                    values=gasto_sub.values.tolist(),
                    hole=0.58,
                    sort=False,
                    marker=dict(
                        colors=colores[:len(gasto_sub)],
                        line=dict(
                            color="#FFFFFF",
                            width=2
                        )
                    ),
                    textinfo="none",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "$%{value:,.0f}<br>"
                        "%{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )

        categoria_principal = gasto_sub.index[0]
        valor_principal = gasto_sub.iloc[0]

        porcentaje_principal = (
            valor_principal / gasto_sub.sum()
            if gasto_sub.sum() != 0
            else 0
        )

        fig.add_annotation(
            text=(
                f"<b>{porcentaje_principal:.1%}</b>"
                f"<br><span style='font-size:10px;'>"
                f"{categoria_principal}"
                f"</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                size=22,
                color="#172B4D"
            )
        )

        fig.update_layout(
            height=335,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),
            paper_bgcolor="#F7F9FB",
            plot_bgcolor="#F7F9FB",
            showlegend=False
        )

    else:

        fig = go.Figure()

        fig.update_layout(
            height=335,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),
            paper_bgcolor="#F7F9FB",
            plot_bgcolor="#F7F9FB"
        )

    # --------------------------------------------------------
    # CONTENEDOR DEL GASTO
    # --------------------------------------------------------

    st.markdown(
        '<div class="dashboard-card expense-card">',
        unsafe_allow_html=True
    )

    gasto_col1, gasto_col2 = st.columns(
        [1.05, 1],
        gap="medium"
    )

    with gasto_col1:

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
            key="grafico_gastos"
        )

    with gasto_col2:

        st.markdown(
            f"""
            <div class="expense-total">
                {moneda(gasto_total)}
            </div>

            <div class="expense-total-label">
                Total de egresos operativos
            </div>

            <div class="expense-header">

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
            """,
            unsafe_allow_html=True
        )

        if not gasto_sub.empty:

            total_gastos = gasto_sub.sum()

            for i, (nombre, valor) in enumerate(
                gasto_sub.head(8).items()
            ):

                porcentaje_gasto = (
                    valor / total_gastos
                    if total_gastos != 0
                    else 0
                )

                color_punto = colores[
                    min(i, len(colores) - 1)
                ]

                st.markdown(
                    f"""
                    <div class="expense-row">

                        <div class="expense-name">

                            <span
                                class="expense-dot"
                                style="
                                    background:{color_punto};
                                ">
                            </span>

                            <span>
                                {nombre}
                            </span>

                        </div>

                        <div class="expense-value">
                            {formato_numero(valor)}
                        </div>

                        <div class="expense-percent">
                            {porcentaje_gasto:.1%}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                f"""
                <div class="expense-highlight">
                    💡 Mayor centro de gasto:
                    <strong>{categoria_principal}</strong>
                    ({formato_numero(valor_principal)})
                    <br>
                    Representa el
                    {porcentaje_principal:.1%}
                    del total.
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# ANALISIS ANUAL
# ============================================================

st.markdown(
    '<div class="analysis-space"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-title">
        📊 Análisis anual
    </div>

    <div class="section-subtitle">
        Comparación mensual y desempeño promedio de las propiedades
    </div>
    """,
    unsafe_allow_html=True
)


años_disponibles = sorted(
    df_graficos["Fecha"]
    .dropna()
    .dt.year
    .unique(),
    reverse=True
)

if len(años_disponibles) > 0:

    año_actual_sistema = pd.Timestamp.now().year

    if año_actual_sistema in años_disponibles:

        indice_default = años_disponibles.index(
            año_actual_sistema
        )

    else:

        indice_default = 0

    año_seleccionado = st.selectbox(
        "Año de análisis",
        años_disponibles,
        index=indice_default
    )

    año_anterior = año_seleccionado - 1

else:

    año_seleccionado = pd.Timestamp.now().year
    año_anterior = año_seleccionado - 1


# ============================================================
# DATOS AÑO ACTUAL / ANTERIOR
# ============================================================

datos_año = df_graficos[
    df_graficos["Fecha"].dt.year == año_seleccionado
].copy()

datos_año_anterior = df_graficos[
    df_graficos["Fecha"].dt.year == año_anterior
].copy()


# ============================================================
# INGRESOS MENSUALES
# ============================================================

meses = pd.DataFrame({
    "Mes_num": range(1, 13),
    "Mes": [
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
})


if not datos_año.empty:

    ingresos_actual = (
        datos_año
        .groupby(
            datos_año["Fecha"].dt.month
        )["Ingreso"]
        .sum()
        .reset_index()
    )

    ingresos_actual.columns = [
        "Mes_num",
        "Ingreso"
    ]

else:

    ingresos_actual = pd.DataFrame(
        columns=[
            "Mes_num",
            "Ingreso"
        ]
    )


if not datos_año_anterior.empty:

    ingresos_anterior_mensual = (
        datos_año_anterior
        .groupby(
            datos_año_anterior["Fecha"].dt.month
        )["Ingreso"]
        .sum()
        .reset_index()
    )

    ingresos_anterior_mensual.columns = [
        "Mes_num",
        "Ingreso"
    ]

else:

    ingresos_anterior_mensual = pd.DataFrame(
        columns=[
            "Mes_num",
            "Ingreso"
        ]
    )


# ------------------------------------------------------------
# MES DE CORTE
# ------------------------------------------------------------

if not datos_año.empty:

    mes_corte = datos_año[
        "Fecha"
    ].max().month

else:

    mes_corte = 12


meses_comparacion = meses[
    meses["Mes_num"] <= mes_corte
].copy()


meses_comparacion = meses_comparacion.merge(
    ingresos_actual,
    on="Mes_num",
    how="left"
)

meses_comparacion = meses_comparacion.merge(
    ingresos_anterior_mensual,
    on="Mes_num",
    how="left",
    suffixes=("_Actual", "_Anterior")
)

meses_comparacion["Ingreso_Actual"] = (
    meses_comparacion["Ingreso_Actual"]
    .fillna(0)
)

meses_comparacion["Ingreso_Anterior"] = (
    meses_comparacion["Ingreso_Anterior"]
    .fillna(0)
)


# ============================================================
# PROMEDIO MENSUAL POR PROPIEDAD
# ============================================================

if not datos_año.empty:

    promedio_propiedad = (
        datos_año
        .groupby("Nombre_Propiedad")
        .agg(
            Ingreso=("Ingreso", "sum"),
            Fecha_Inicio=("Fecha", "min"),
            Fecha_Fin=("Fecha", "max")
        )
        .reset_index()
    )

    promedio_propiedad["Meses"] = (
        (
            promedio_propiedad["Fecha_Fin"].dt.year
            - promedio_propiedad["Fecha_Inicio"].dt.year
        ) * 12
        +
        (
            promedio_propiedad["Fecha_Fin"].dt.month
            - promedio_propiedad["Fecha_Inicio"].dt.month
        )
        + 1
    )

    promedio_propiedad["Promedio"] = np.where(
        promedio_propiedad["Meses"] > 0,
        promedio_propiedad["Ingreso"]
        / promedio_propiedad["Meses"],
        0
    )

    promedio_propiedad = promedio_propiedad.sort_values(
        "Promedio",
        ascending=False
    )

else:

    promedio_propiedad = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ingreso",
            "Promedio"
        ]
    )


# ============================================================
# GRAFICOS ANUALES
# ============================================================

grafico1, grafico2 = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# GRAFICO INGRESOS MENSUALES
# ============================================================

with grafico1:

    fig_mensual = go.Figure()

    fig_mensual.add_trace(
        go.Bar(
            x=meses_comparacion["Mes"],
            y=meses_comparacion["Ingreso_Actual"],
            name=str(año_seleccionado),
            marker_color="#35B58A",
            opacity=0.95
        )
    )

    fig_mensual.add_trace(
        go.Scatter(
            x=meses_comparacion["Mes"],
            y=meses_comparacion["Ingreso_Anterior"],
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

    fig_mensual.update_layout(
        height=360,
        margin=dict(
            l=15,
            r=15,
            t=10,
            b=10
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            size=12,
            color="#52617A"
        ),
        legend=dict(
            orientation="h",
            y=1.08,
            x=0
        ),
        xaxis=dict(
            title=None,
            showgrid=False
        ),
        yaxis=dict(
            title=None,
            gridcolor="#E5E9ED",
            tickprefix="$ "
        )
    )

    st.markdown(
        """
        <div class="section-title">
            📊 Ingresos mensuales
        </div>

        <div class="section-subtitle">
            Comparativo de ingresos del año seleccionado contra el año anterior
        </div>
        """,
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_mensual,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
        key="grafico_ingresos_mensuales"
    )


# ============================================================
# GRAFICO PROMEDIO PROPIEDAD
# ============================================================

with grafico2:

    fig_promedio = go.Figure()

    if not promedio_propiedad.empty:

        fig_promedio.add_trace(
            go.Bar(
                x=promedio_propiedad[
                    "Nombre_Propiedad"
                ],
                y=promedio_propiedad[
                    "Promedio"
                ],
                marker_color="#7565D8",
                text=[
                    formato_numero(v)
                    for v in promedio_propiedad[
                        "Promedio"
                    ]
                ],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "$%{y:,.0f}"
                    "<extra></extra>"
                )
            )
        )

    fig_promedio.update_layout(
        height=360,
        margin=dict(
            l=15,
            r=15,
            t=10,
            b=10
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            size=12,
            color="#52617A"
        ),
        xaxis=dict(
            title=None,
            showgrid=False
        ),
        yaxis=dict(
            title=None,
            gridcolor="#E5E9ED",
            tickprefix="$ "
        )
    )

    st.markdown(
        f"""
        <div class="section-title">
            🏠 Promedio mensual por propiedad — {año_seleccionado}
        </div>

        <div class="section-subtitle">
            Ingreso promedio mensual por propiedad
        </div>
        """,
        unsafe_allow_html=True
    )

    st.plotly_chart(
        fig_promedio,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
        key="grafico_promedio_propiedad"
    )


# ============================================================
# PIE FINAL
# ============================================================

propiedades_analizadas = (
    df_filtrado["Nombre_Propiedad"]
    .dropna()
    .nunique()
)

socios_analizados = (
    df_filtrado["Nombre_Socio"]
    .dropna()
    .nunique()
)


st.markdown(
    f"""
    <div class="footer-dashboard">

        <div class="footer-item">
            🟢
            <strong class="footer-green">
                {moneda(flujo_total)}
            </strong>
            &nbsp;
            Flujo positivo en el periodo
        </div>

        <div class="footer-item">
            🏢
            <strong class="footer-value">
                {propiedades_analizadas}
            </strong>
            &nbsp;
            Propiedades analizadas
        </div>

        <div class="footer-item">
            👥
            <strong class="footer-value">
                {socios_analizados}
            </strong>
            &nbsp;
            Socios
        </div>

        <div class="footer-item">
            📊
            “Más que propiedades, mejores decisiones”
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
