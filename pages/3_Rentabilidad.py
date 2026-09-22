import streamlit as st
import pandas as pd
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
# CSS
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
    padding-top: 4.2rem !important;
    padding-bottom: 1rem !important;
}

#MainMenu,
footer {
    visibility: hidden;
}


/* ============================================================
   HEADER
============================================================ */

.header {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 17px;
    padding: 9px 14px;
    margin-bottom: 8px;
    box-shadow: 0 3px 14px rgba(24,52,94,.04);
}

.logo-box {
    width: 50px;
    height: 50px;
    border-radius: 14px;
    background: #FF214B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 27px;
    flex-shrink: 0;
}

.brand-title {
    font-size: 24px;
    line-height: 1.05;
    font-weight: 850;
    color: #17345E;
}

.brand-title span {
    color: #FF3155;
}

.brand-subtitle {
    font-size: 10px;
    color: #8290A4;
    margin-top: 4px;
}

.top-kpi {
    height: 62px;
    background: #F7F9FC;
    border: 1px solid #E0E7EE;
    border-radius: 11px;
    padding: 8px 10px;
    box-sizing: border-box;
}

.top-kpi-label {
    font-size: 7px;
    font-weight: 800;
    color: #8492A7;
}

.top-kpi-value {
    font-size: 17px;
    font-weight: 850;
    color: #17345E;
    margin-top: 6px;
}

.top-kpi-value.green {
    color: #009B70;
}

.top-kpi-value.red {
    color: #E84235;
}


/* ============================================================
   NAVEGACIÓN + FILTROS
============================================================ */

.filter-label {
    font-size: 10px;
    font-weight: 800;
    color: #667991;
    margin-bottom: 3px;
}


/* botones navegación */

div.stButton > button {
    height: 36px !important;
    min-height: 36px !important;
    padding: 0 7px !important;
    border: 1px solid #DCE5EE !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    color: #50637B !important;
    font-size: 11px !important;
    font-weight: 700 !important;
}

div.stButton > button:hover {
    border-color: #17345E !important;
    color: #17345E !important;
}


/* select */

div[data-baseweb="select"] > div {
    background: #F2F5F8 !important;
    border: 1px solid #E0E6ED !important;
    border-radius: 8px !important;
    min-height: 36px !important;
    height: 36px !important;
}

div[data-baseweb="select"] span {
    font-size: 12px !important;
}


/* fecha */

div[data-testid="stDateInput"] > div {
    background: #F2F5F8 !important;
    border: 1px solid #E0E6ED !important;
    border-radius: 8px !important;
    min-height: 36px !important;
    height: 36px !important;
}

div[data-testid="stDateInput"] input {
    font-size: 12px !important;
}


/* ============================================================
   TÍTULOS
============================================================ */

.section-title {
    font-size: 23px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.05;
}

.section-subtitle {
    font-size: 10px;
    color: #8290A4;
    margin-top: 3px;
    margin-bottom: 9px;
}


/* ============================================================
   KPI DEL PERÍODO
============================================================ */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 13px;
    height: 82px;
    padding: 11px 14px;
    box-sizing: border-box;
}

.kpi-label {
    font-size: 8px;
    font-weight: 800;
    color: #7E8EA4;
}

.kpi-value {
    font-size: 23px;
    line-height: 1;
    font-weight: 850;
    color: #17345E;
    margin-top: 8px;
}

.kpi-value.green {
    color: #009B70;
}

.kpi-value.red {
    color: #E84235;
}

.kpi-sub {
    font-size: 8px;
    color: #8B98A9;
    margin-top: 6px;
}


/* ============================================================
   GRID PROPIEDADES
============================================================ */

.properties-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-top: 8px;
}


/* ============================================================
   TARJETA PROPIEDAD
============================================================ */

.property-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 15px;
    padding: 12px 13px;
    height: 225px;
    box-sizing: border-box;
    box-shadow: 0 3px 11px rgba(24,52,94,.035);
}

.property-card.negative {
    border-color: #FF8A83;
}


/* encabezado */

.property-header {
    height: 39px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.property-name {
    font-size: 16px;
    font-weight: 850;
    color: #17345E;
    line-height: 1.1;
}

.property-city {
    font-size: 9px;
    color: #8290A4;
    margin-top: 4px;
}

.property-profit {
    text-align: right;
}

.property-profit-value {
    font-size: 17px;
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
    font-size: 7px;
    color: #9AA5B4;
    margin-top: 4px;
}


/* métricas */

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin-top: 8px;
}

.metric-box {
    background: #F5F7F9;
    border-radius: 9px;
    padding: 7px 8px;
    height: 51px;
    box-sizing: border-box;
}

.metric-label {
    font-size: 7px;
    color: #8290A4;
}

.metric-value {
    font-size: 13px;
    font-weight: 850;
    margin-top: 5px;
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


/* rentabilidad */

.profit-section {
    margin-top: 8px;
}

.profit-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.profit-label {
    font-size: 8px;
    color: #8290A4;
}

.profit-number {
    font-size: 11px;
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
    height: 5px;
    background: #E7EDF1;
    border-radius: 5px;
    margin-top: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #00AC7C;
    border-radius: 5px;
}

.progress-fill.bad {
    background: #EF4A42;
}


/* ocupación */

.occupancy-box {
    background: #F5F7FA;
    border-radius: 9px;
    margin-top: 8px;
    padding: 7px 9px;
    height: 42px;
    box-sizing: border-box;
}

.occupancy-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.occupancy-label {
    font-size: 7px;
    color: #8290A4;
}

.occupancy-value {
    font-size: 13px;
    font-weight: 850;
    color: #6954E6;
}

.occupancy-detail {
    font-size: 7px;
    color: #96A1AF;
    margin-top: 3px;
}


/* ============================================================
   TARJETA PORTAFOLIO
============================================================ */

.portfolio-card {
    background: #17345E;
    border-radius: 15px;
    padding: 14px;
    height: 225px;
    box-sizing: border-box;
    color: #FFFFFF;
}

.portfolio-title {
    font-size: 17px;
    font-weight: 850;
}

.portfolio-subtitle {
    font-size: 8px;
    color: #B9C8DA;
    margin-top: 3px;
}

.portfolio-main {
    font-size: 28px;
    font-weight: 850;
    margin-top: 18px;
}

.portfolio-main-label {
    font-size: 8px;
    color: #B9C8DA;
}

.portfolio-row {
    display: flex;
    justify-content: space-between;
    margin-top: 12px;
}

.portfolio-mini-label {
    font-size: 7px;
    color: #B9C8DA;
}

.portfolio-mini-value {
    font-size: 14px;
    font-weight: 800;
    margin-top: 2px;
}

.portfolio-profit {
    color: #52D7B0;
}


/* ============================================================
   PANELES INFERIORES
============================================================ */

.side-card {
    background: #FFFFFF;
    border: 1px solid #DCE5EE;
    border-radius: 13px;
    padding: 11px 13px;
    margin-top: 10px;
}

.side-title {
    font-size: 12px;
    font-weight: 850;
    color: #17345E;
}

.side-subtitle {
    font-size: 8px;
    color: #8A98AA;
    margin-top: 3px;
}


/* ranking */

.rank {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 7px;
}

.rank-name {
    width: 80px;
    font-size: 7px;
    color: #61738C;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rank-background {
    flex: 1;
    height: 7px;
    background: #EDF0F4;
    border-radius: 7px;
    overflow: hidden;
}

.rank-fill {
    height: 100%;
    background: #7964DD;
    border-radius: 7px;
}

.rank-number {
    width: 35px;
    text-align: right;
    font-size: 7px;
    color: #697A91;
}


/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 1200px) {

    .properties-grid {
        grid-template-columns: repeat(3, 1fr);
    }

}

@media (max-width: 900px) {

    .properties-grid {
        grid-template-columns: repeat(2, 1fr);
    }

}

@media (max-width: 650px) {

    .properties-grid {
        grid-template-columns: 1fr;
    }

}

</style>
""", unsafe_allow_html=True)


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
# FUNCIONES
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
# CARGA
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
    + pd.Timedelta(days=1)
)


# ============================================================
# YTD
# ============================================================

df_ytd = df[
    (df["Fecha"] >= inicio_anio) &
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
# MINI GRÁFICO INGRESO MENSUAL
# ============================================================

monthly_header = (
    df_ytd
    .assign(
        Mes=df_ytd["Fecha"].dt.month
    )
    .groupby("Mes")["Ingreso"]
    .sum()
)

max_month = (
    monthly_header.max()
    if not monthly_header.empty
    else 1
)

bars_month = ""

for mes in range(
    1,
    hoy.month + 1
):

    valor = monthly_header.get(
        mes,
        0
    )

    altura = max(
        4,
        int(
            valor /
            max_month *
            29
        )
    )

    bars_month += f"""
    <div style="
        width:7px;
        height:{altura}px;
        background:#27B68D;
        border-radius:3px 3px 0 0;
    "></div>
    """


# ============================================================
# MINI GRÁFICO PROPIEDADES
# ============================================================

prop_header = (
    df_ytd
    .groupby(
        "Nombre_Propiedad"
    )["Ingreso"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(7)
)

max_prop = (
    prop_header.max()
    if not prop_header.empty
    else 1
)

bars_prop = ""

for valor in prop_header.values:

    altura = max(
        4,
        int(
            valor /
            max_prop *
            29
        )
    )

    bars_prop += f"""
    <div style="
        width:7px;
        height:{altura}px;
        background:#7965D9;
        border-radius:3px 3px 0 0;
    "></div>
    """


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
<div class="header">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div class="logo-box">
🏢
</div>

<div style="
width:290px;
flex-shrink:0;
">

<div class="brand-title">
Airbnb <span>Financial Hub</span>
</div>

<div class="brand-subtitle">
Rentabilidad financiera · Solo Airbnb
</div>

</div>


<div class="top-kpi" style="flex:1;">

<div class="top-kpi-label">
INGRESOS 2026
</div>

<div class="top-kpi-value">
{dinero_corto(ingresos_ytd)}
</div>

</div>


<div class="top-kpi" style="flex:1;">

<div class="top-kpi-label">
FLUJO 2026
</div>

<div class="top-kpi-value green">
{dinero_corto(flujo_ytd)}
</div>

</div>


<div class="top-kpi" style="flex:1;">

<div class="top-kpi-label">
RENTABILIDAD 2026
</div>

<div class="top-kpi-value {'green' if rentabilidad_ytd >= 35 else 'red'}">
{rentabilidad_ytd:.1f}%
</div>

</div>


<div class="top-kpi" style="flex:1;">

<div class="top-kpi-label">
INGRESO MENSUAL
</div>

<div style="
display:flex;
align-items:flex-end;
gap:3px;
height:30px;
margin-top:2px;
">
{bars_month}
</div>

</div>


<div class="top-kpi" style="flex:1;">

<div class="top-kpi-label">
PROMEDIO PROPIEDAD
</div>

<div style="
display:flex;
align-items:flex-end;
gap:3px;
height:30px;
margin-top:2px;
">
{bars_prop}
</div>

</div>

</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# ESTADO DE LA VISTA
# ============================================================

if "vista_airbnb" not in st.session_state:

    st.session_state.vista_airbnb = "Resumen"


# ============================================================
# NAVEGACIÓN + FILTROS
# TODO EN UNA SOLA FILA
# ============================================================

nav = st.columns(
    [
        0.85,
        1.05,
        1.00,
        0.95,
        1.25,
        1.45,
        1.20,
        1.75
    ],
    gap="small"
)


# ------------------------------------------------------------
# RESUMEN
# ------------------------------------------------------------

with nav[0]:

    if st.button(
        "🏠 Resumen",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Resumen"

        st.rerun()


# ------------------------------------------------------------
# PROPIEDADES
# ------------------------------------------------------------

with nav[1]:

    if st.button(
        "🏢 Propiedades",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Propiedades"

        st.rerun()


# ------------------------------------------------------------
# FINANCIERO
# ------------------------------------------------------------

with nav[2]:

    if st.button(
        "💰 Financiero",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Financiero"

        st.rerun()


# ------------------------------------------------------------
# OCUPACIÓN
# ------------------------------------------------------------

with nav[3]:

    if st.button(
        "📊 Ocupación",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Ocupación"

        st.rerun()


# ------------------------------------------------------------
# CIUDAD
# ------------------------------------------------------------

with nav[4]:

    st.markdown(
        '<div class="filter-label">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] +
        sorted(
            df["Ciudad"].unique()
        ),
        label_visibility="collapsed"
    )


# ------------------------------------------------------------
# PROPIEDAD
# ------------------------------------------------------------

with nav[5]:

    st.markdown(
        '<div class="filter-label">🏢 Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] +
        sorted(
            df["Nombre_Propiedad"].unique()
        ),
        label_visibility="collapsed"
    )


# ------------------------------------------------------------
# SOCIO
# ------------------------------------------------------------

with nav[6]:

    st.markdown(
        '<div class="filter-label">👥 Socio</div>',
        unsafe_allow_html=True
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] +
        sorted(
            df["Nombre_Socio"].unique()
        ),
        label_visibility="collapsed"
    )


# ------------------------------------------------------------
# PERÍODO
# ------------------------------------------------------------

with nav[7]:

    st.markdown(
        '<div class="filter-label">📅 Período</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Periodo",
        value=(
            inicio_mes,
            hoy
        ),
        label_visibility="collapsed"
    )


# ============================================================
# FECHAS
# ============================================================

if (
    isinstance(periodo, tuple)
    and len(periodo) == 2
):

    fecha_inicio = periodo[0]

    fecha_fin = periodo[1]

else:

    fecha_inicio = inicio_mes

    fecha_fin = hoy


# ============================================================
# FILTRO FINANCIERO
# ============================================================

df_f = df[
    (df["Fecha"].dt.date >= fecha_inicio) &
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


if socio != "Todos":

    df_f = df_f[
        df_f["Nombre_Socio"] == socio
    ]


# ============================================================
# KPIs
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
    resumen["Ingresos"] -
    resumen["Gastos"]
)

resumen["Rentabilidad"] = resumen.apply(
    lambda x:
        (
            x["Flujo"] /
            x["Ingresos"] *
            100
        )
        if x["Ingresos"] != 0
        else 0,
    axis=1
)


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
        df_ocupacion[
            "Noches_Reservadas"
        ]
        /
        df_ocupacion[
            "Noches_Disponibles"
        ]
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

        detalle = (
            "Sin datos de Airbnb"
        )

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

    return f"""

<div class="portfolio-card">

<div class="portfolio-title">
🏢 Portafolio
</div>

<div class="portfolio-subtitle">
Todas las propiedades seleccionadas
</div>


<div class="portfolio-main">
{dinero_corto(ingresos)}
</div>

<div class="portfolio-main-label">
Ingresos del período
</div>


<div class="portfolio-row">

<div>

<div class="portfolio-mini-label">
Gastos
</div>

<div class="portfolio-mini-value">
{dinero_corto(gastos)}
</div>

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


<div class="portfolio-row">

<div>

<div class="portfolio-mini-label">
Rentabilidad
</div>

<div class="portfolio-mini-value portfolio-profit">
{rentabilidad:.1f}%
</div>

</div>


<div>

<div class="portfolio-mini-label">
Objetivo
</div>

<div class="portfolio-mini-value">
35%
</div>

</div>

</div>

</div>
"""


# ============================================================
# VISTA RESUMEN
# ============================================================

vista = st.session_state.vista_airbnb


if vista == "Resumen":

    st.markdown(
        """
<div style="margin-top:8px;">

<div class="section-title">
🏢 Tu portafolio
</div>

<div class="section-subtitle">
Desempeño financiero de tus propiedades Airbnb en el período seleccionado.
</div>

</div>
""",
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    k1, k2, k3, k4 = st.columns(
        4,
        gap="small"
    )


    with k1:

        st.markdown(
            f"""
<div class="kpi-card">

<div class="kpi-label">
INGRESOS
</div>

<div class="kpi-value">
{dinero_corto(ingresos)}
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

<div class="kpi-label">
GASTOS OPERATIVOS
</div>

<div class="kpi-value">
{dinero_corto(gastos)}
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

<div class="kpi-label">
FLUJO
</div>

<div class="kpi-value green">
{dinero_corto(flujo)}
</div>

<div class="kpi-sub">
Ingresos − gastos
</div>

</div>
""",
            unsafe_allow_html=True
        )


    with k4:

        st.markdown(
            f"""
<div class="kpi-card">

<div class="kpi-label">
RENTABILIDAD
</div>

<div class="kpi-value {'green' if rentabilidad >= 35 else 'red'}">
{rentabilidad:.1f}%
</div>

<div class="kpi-sub">
Objetivo: 35%
</div>

</div>
""",
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # TARJETAS
    # --------------------------------------------------------

    cards_html = (
        '<div class="properties-grid">'
    )


    for _, row in resumen.iterrows():

        cards_html += (
            tarjeta_propiedad(row)
        )


    cards_html += (
        tarjeta_portafolio()
    )


    cards_html += (
        "</div>"
    )


    st.markdown(
        cards_html,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # TOP + ACUMULADO
    # --------------------------------------------------------

    left, right = st.columns(
        [1.7, 1],
        gap="small"
    )


    with left:

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


    with right:

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
font-size:25px;
font-weight:850;
color:#17345E;
margin-top:9px;
">
{dinero_corto(ingresos_ytd)}
</div>

<div class="side-subtitle">
Ingresos
</div>


<div style="
font-size:23px;
font-weight:850;
color:#009B70;
margin-top:8px;
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
# VISTA PROPIEDADES
# ============================================================

elif vista == "Propiedades":

    st.markdown(
        """
<div class="section-title">
🏢 Propiedades
</div>

<div class="section-subtitle">
Detalle financiero y ocupación de cada propiedad.
</div>
""",
        unsafe_allow_html=True
    )


    cards_html = (
        '<div class="properties-grid">'
    )


    for _, row in resumen.iterrows():

        cards_html += (
            tarjeta_propiedad(row)
        )


    cards_html += "</div>"


    st.markdown(
        cards_html,
        unsafe_allow_html=True
    )


# ============================================================
# VISTA FINANCIERO
# ============================================================

elif vista == "Financiero":

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
        (df["Fecha"] >= inicio_anio) &
        (df["Fecha"] < fin_hoy)
    ].copy()


    financiero["Mes_Num"] = (
        financiero["Fecha"].dt.month
    )

    financiero["Mes"] = (
        financiero["Fecha"]
        .dt.strftime("%b")
    )


    mensual = (
        financiero
        .groupby(
            [
                "Mes_Num",
                "Mes"
            ],
            as_index=False
        )
        .agg(
            Ingresos=("Ingreso", "sum"),
            Gastos=("Gasto", "sum")
        )
        .sort_values("Mes_Num")
    )


    mensual["Flujo"] = (
        mensual["Ingresos"] -
        mensual["Gastos"]
    )


    html = """
<div class="side-card">

<div class="side-title">
📋 Evolución mensual
</div>

<table style="
width:100%;
border-collapse:collapse;
margin-top:8px;
">

<tr>

<th style="
text-align:left;
font-size:9px;
color:#8290A4;
padding:6px;
">
Mes
</th>

<th style="
text-align:right;
font-size:9px;
color:#8290A4;
padding:6px;
">
Ingresos
</th>

<th style="
text-align:right;
font-size:9px;
color:#8290A4;
padding:6px;
">
Gastos
</th>

<th style="
text-align:right;
font-size:9px;
color:#8290A4;
padding:6px;
">
Flujo
</th>

</tr>
"""


    for _, row in mensual.iterrows():

        html += f"""

<tr>

<td style="
font-size:10px;
padding:6px;
color:#17345E;
font-weight:700;
">
{row["Mes"]}
</td>

<td style="
font-size:10px;
padding:6px;
text-align:right;
color:#009B70;
font-weight:800;
">
{dinero_corto(row["Ingresos"])}
</td>

<td style="
font-size:10px;
padding:6px;
text-align:right;
color:#EF4338;
font-weight:800;
">
{dinero_corto(row["Gastos"])}
</td>

<td style="
font-size:10px;
padding:6px;
text-align:right;
color:#0878D2;
font-weight:800;
">
{dinero_corto(row["Flujo"])}
</td>

</tr>
"""


    html += "</table></div>"


    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# VISTA OCUPACIÓN
# ============================================================

elif vista == "Ocupación":

    st.markdown(
        """
<div class="section-title">
📊 Ocupación Airbnb
</div>

<div class="section-subtitle">
Reservas y noches ocupadas en el período seleccionado.
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
            ocupacion[
                "Noches_Reservadas"
            ]
            /
            ocupacion[
                "Noches_Disponibles"
            ]
            *
            100
        )


        total_reservas = (
            ocupacion["Reservas"].sum()
        )

        total_noches = (
            ocupacion[
                "Noches_Reservadas"
            ].sum()
        )

        total_disponibles = (
            ocupacion[
                "Noches_Disponibles"
            ].sum()
        )


        ocupacion_total = (
            total_noches /
            total_disponibles *
            100
            if total_disponibles
            else 0
        )


        a, b, c = st.columns(
            3
        )


        with a:

            st.markdown(
                f"""
<div class="kpi-card">

<div class="kpi-label">
OCUPACIÓN PORTAFOLIO
</div>

<div class="kpi-value"
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


        ocupacion = ocupacion.sort_values(
            "Ocupacion",
            ascending=False
        )


        cards_html = (
            '<div class="properties-grid">'
        )


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
margin-top:10px;
">

<div class="metric-label">
NOCHES RESERVADAS
</div>

<div style="
font-size:25px;
font-weight:850;
color:#17345E;
margin-top:4px;
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

<div
class="occupancy-value">
{int(row["Reservas"])}
</div>

</div>

<div class="occupancy-detail">
{int(row["Noches_Disponibles"])}
noches disponibles
</div>

</div>

</div>
"""


        cards_html += "</div>"


        st.markdown(
            cards_html,
            unsafe_allow_html=True
        )
