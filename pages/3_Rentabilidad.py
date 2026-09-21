# ============================================================
# pages/3_Rentabilidad.py
# AIRBNB FINANCIAL HUB
# ============================================================

import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


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
# ESTILOS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 4.8rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1500px !important;
}


/* ============================================================
   HEADER
============================================================ */

.app-header {
    background: #FFFFFF;
    border: 1px solid #E3E8EF;
    border-radius: 18px;
    padding: 14px 20px;
    margin-bottom: 14px;

    display: flex;
    align-items: center;
    gap: 14px;

    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
}

.app-icon {
    width: 52px;
    height: 52px;
    min-width: 52px;

    border-radius: 14px;

    background: linear-gradient(
        135deg,
        #FF385C,
        #FF0A45
    );

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 26px;
}

.app-name {
    color: #172B4D;
    font-size: 24px;
    font-weight: 700;
    line-height: 1.05;
}

.app-name span {
    color: #FF385C;
}

.app-subtitle {
    color: #6B778C;
    font-size: 13px;
    margin-top: 4px;
}

.connection {
    margin-left: auto;
    color: #00875A;
    font-size: 12px;
    font-weight: 600;
}


/* ============================================================
   FILTROS
============================================================ */

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label {
    font-size: 12px !important;
    color: #6B778C !important;
    font-weight: 500 !important;
}


/* ============================================================
   KPI
============================================================ */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E3E8EF;
    border-radius: 16px;

    padding: 14px 17px;

    min-height: 105px;

    box-shadow: 0 3px 10px rgba(0,0,0,0.035);
}

.kpi-label {
    color: #6B778C;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
}

.kpi-value {
    color: #172B4D;
    font-size: 25px;
    font-weight: 700;
    line-height: 1.1;
}

.kpi-sub {
    color: #8A94A6;
    font-size: 11px;
    margin-top: 6px;
}


/* ============================================================
   SECCIONES
============================================================ */

.section-title {
    color: #172B4D;
    font-size: 21px;
    font-weight: 700;

    margin-top: 16px;
    margin-bottom: 2px;
}

.section-subtitle {
    color: #6B778C;
    font-size: 12px;
    margin-bottom: 10px;
}


/* ============================================================
   PROPIEDADES
============================================================ */

.property-card {
    background: #FFFFFF;

    border: 1px solid #E0E6ED;
    border-radius: 16px;

    padding: 14px 15px;
    margin-bottom: 12px;

    box-shadow: 0 3px 10px rgba(0,0,0,0.035);
}

.property-card.alert {
    border: 1.5px solid #FF7777;
}

.property-name {
    color: #172B4D;
    font-size: 16px;
    font-weight: 700;
}

.property-location {
    color: #6B778C;
    font-size: 10px;
    margin-top: 2px;
}

.property-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);

    gap: 7px;
    margin-top: 11px;
}

.metric-box {
    background: #F7F9FB;
    border-radius: 9px;

    padding: 7px 8px;
}

.metric-label {
    color: #6B778C;
    font-size: 9px;
}

.metric-income {
    color: #00875A;
    font-size: 12px;
    font-weight: 600;
    margin-top: 2px;
}

.metric-expense {
    color: #DE350B;
    font-size: 12px;
    font-weight: 600;
    margin-top: 2px;
}

.metric-flow {
    color: #0065BD;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}

.margin-row {
    display: flex;
    justify-content: space-between;
    align-items: center;

    margin-top: 9px;
}

.margin-label {
    color: #6B778C;
    font-size: 10px;
}

.margin-value {
    font-size: 14px;
    font-weight: 700;
}

.progress-bg {
    width: 100%;
    height: 5px;

    background: #E8EDF2;

    border-radius: 10px;

    overflow: hidden;

    margin-top: 5px;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
}

.status {
    font-size: 9px;
    margin-top: 6px;
    font-weight: 600;
}

.status-ok {
    color: #00875A;
}

.status-alert {
    color: #DE350B;
}


/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 1100px) {

    .property-name {
        font-size: 15px;
    }

    .metric-income,
    .metric-expense,
    .metric-flow {
        font-size: 11px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CONEXIÓN BIGQUERY
# ============================================================

try:

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

except Exception as e:

    st.error(f"No fue posible conectar con BigQuery: {e}")
    st.stop()


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data(ttl=300)
def cargar_datos():

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

    return client.query(query).to_dataframe()


try:

    df = cargar_datos()

except Exception as e:

    st.error(
        f"Error consultando Movimientos_Operativos_Reparto: {e}"
    )

    st.stop()


# ============================================================
# VALIDACIÓN
# ============================================================

if df.empty:

    st.warning(
        "BigQuery está conectado, pero no hay registros "
        "donde Nombre_Tipo = Airbnb."
    )

    st.stop()


# ============================================================
# LIMPIEZA
# ============================================================

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
    .fillna("Sin propiedad")
    .astype(str)
)

df["Ciudad"] = (
    df["Ciudad"]
    .fillna("Sin ciudad")
    .astype(str)
)

df["Nombre_Socio"] = (
    df["Nombre_Socio"]
    .fillna("Sin socio")
    .astype(str)
)

df = df.dropna(
    subset=["Fecha"]
)


# ============================================================
# FORMATO DINERO
# ============================================================

def dinero(valor):

    return f"${valor:,.0f}".replace(",", ".")


# ============================================================
# HEADER
# ============================================================

st.markdown(
"""<div class="app-header">
<div class="app-icon">🏢</div>
<div>
<div class="app-name">Airbnb <span>Financial Hub</span></div>
<div class="app-subtitle">Rentabilidad financiera · BigQuery · Solo Airbnb</div>
</div>
<div class="connection">● BigQuery conectado</div>
</div>""",
unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    ciudades = (
        ["Todas"]
        +
        sorted(
            df["Ciudad"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    ciudad = st.selectbox(
        "Ciudad",
        ciudades
    )


with col2:

    propiedades = (
        ["Todas"]
        +
        sorted(
            df["Nombre_Propiedad"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    propiedad = st.selectbox(
        "Propiedad",
        propiedades
    )


with col3:

    socios = (
        ["Todos"]
        +
        sorted(
            df["Nombre_Socio"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    socio = st.selectbox(
        "Socio",
        socios
    )


with col4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    fechas = st.date_input(
        "Periodo",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_f = df.copy()


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


if isinstance(fechas, tuple) and len(fechas) == 2:

    fecha_inicio = pd.Timestamp(
        fechas[0]
    )

    fecha_fin = (
        pd.Timestamp(fechas[1])
        +
        pd.Timedelta(days=1)
    )

    df_f = df_f[
        (df_f["Fecha"] >= fecha_inicio)
        &
        (df_f["Fecha"] < fecha_fin)
    ]


if df_f.empty:

    st.warning(
        "No existen datos para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# KPI
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = ingresos - gastos

rentabilidad = (
    flujo / ingresos * 100
    if ingresos != 0
    else 0
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    st.markdown(
f"""<div class="kpi-card">
<div class="kpi-label">💰 INGRESOS BRUTOS</div>
<div class="kpi-value">{dinero(ingresos)}</div>
<div class="kpi-sub">Ingresos registrados</div>
</div>""",
unsafe_allow_html=True
    )


with k2:

    st.markdown(
f"""<div class="kpi-card">
<div class="kpi-label">🧾 GASTOS OPERATIVOS</div>
<div class="kpi-value">{dinero(gastos)}</div>
<div class="kpi-sub">Egresos registrados</div>
</div>""",
unsafe_allow_html=True
    )


with k3:

    color_flujo = (
        "#00875A"
        if flujo >= 0
        else "#DE350B"
    )

    st.markdown(
f"""<div class="kpi-card">
<div class="kpi-label">💵 FLUJO</div>
<div class="kpi-value" style="color:{color_flujo};">{dinero(flujo)}</div>
<div class="kpi-sub">Ingresos − gastos</div>
</div>""",
unsafe_allow_html=True
    )


with k4:

    color_rentabilidad = (
        "#00875A"
        if rentabilidad >= 35
        else "#DE350B"
    )

    st.markdown(
f"""<div class="kpi-card">
<div class="kpi-label">🎯 RENTABILIDAD</div>
<div class="kpi-value" style="color:{color_rentabilidad};">{rentabilidad:.1f}%</div>
<div class="kpi-sub">Objetivo: 35%</div>
</div>""",
unsafe_allow_html=True
    )


# ============================================================
# PROPIEDADES
# ============================================================

st.markdown(
"""<div class="section-title">🏢 Rentabilidad por propiedad</div>
<div class="section-subtitle">Desempeño financiero de cada propiedad en el periodo seleccionado</div>""",
unsafe_allow_html=True
)


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
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
)


resumen["Flujo"] = (
    resumen["Ingreso"]
    -
    resumen["Gasto"]
)


resumen["Rentabilidad"] = (
    resumen["Flujo"]
    /
    resumen["Ingreso"]
    *
    100
).fillna(0)


resumen = resumen.sort_values(
    "Rentabilidad",
    ascending=False
)


# ============================================================
# 3 PROPIEDADES POR FILA
# ============================================================

for inicio in range(
    0,
    len(resumen),
    3
):

    columnas = st.columns(3)

    for posicion in range(3):

        indice = inicio + posicion

        if indice >= len(resumen):
            continue

        fila = resumen.iloc[indice]

        nombre = str(
            fila["Nombre_Propiedad"]
        )

        ciudad_nombre = str(
            fila["Ciudad"]
        )

        ingreso_prop = float(
            fila["Ingreso"]
        )

        gasto_prop = float(
            fila["Gasto"]
        )

        flujo_prop = float(
            fila["Flujo"]
        )

        margen_prop = float(
            fila["Rentabilidad"]
        )


        if margen_prop >= 35:

            color = "#00A878"

            estado = "✓ Sobre objetivo"

            clase_tarjeta = ""

            clase_estado = "status-ok"

        else:

            color = "#EF4444"

            estado = "⚠ Bajo objetivo"

            clase_tarjeta = "alert"

            clase_estado = "status-alert"


        progreso = max(
            0,
            min(
                margen_prop,
                100
            )
        )


        tarjeta = f"""<div class="property-card {clase_tarjeta}">

<div style="display:flex;justify-content:space-between;align-items:flex-start;">

<div>

<div class="property-name">
{nombre}
</div>

<div class="property-location">
📍 {ciudad_nombre}
</div>

</div>

<div class="margin-value" style="color:{color};">
{margen_prop:.1f}%
</div>

</div>


<div class="property-metrics">

<div class="metric-box">

<div class="metric-label">
Ingresos
</div>

<div class="metric-income">
{dinero(ingreso_prop)}
</div>

</div>


<div class="metric-box">

<div class="metric-label">
Gastos
</div>

<div class="metric-expense">
{dinero(gasto_prop)}
</div>

</div>


<div class="metric-box">

<div class="metric-label">
Flujo
</div>

<div class="metric-flow">
{dinero(flujo_prop)}
</div>

</div>

</div>


<div class="margin-row">

<div class="margin-label">
Rentabilidad
</div>

<div class="margin-value" style="color:{color};">
{margen_prop:.1f}%
</div>

</div>


<div class="progress-bg">

<div class="progress-fill"
style="width:{progreso}%;background:{color};">
</div>

</div>


<div class="status {clase_estado}">
{estado}
</div>

</div>"""


        with columnas[posicion]:

            st.markdown(
                tarjeta,
                unsafe_allow_html=True
            )


# ============================================================
# PIE
# ============================================================

st.markdown("---")

st.caption(
    f"Airbnb Financial Hub · "
    f"BigQuery · "
    f"{len(df_f):,} registros · "
    f"{len(resumen)} propiedades"
)
