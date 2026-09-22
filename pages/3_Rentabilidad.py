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
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   GENERAL
   ============================================================ */

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1500px !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.header-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, #FF385C, #FF0A45);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    margin-top: 2px;
}

.app-name {
    color: #172B4D;
    font-size: 23px;
    font-weight: 700;
    line-height: 1.05;
    margin-top: 4px;
    white-space: nowrap;
}

.app-name span {
    color: #FF385C;
}

.app-subtitle {
    color: #6B778C;
    font-size: 11px;
    margin-top: 5px;
    white-space: nowrap;
}


/* ============================================================
   TARJETAS ANUALES
   ============================================================ */

.annual-card {
    background: #F7F9FB;
    border: 1px solid #E7EBF0;
    border-radius: 11px;
    padding: 8px 12px;
    height: 64px;
    box-sizing: border-box;
}

.annual-label {
    color: #8A94A6;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    white-space: nowrap;
}

.annual-value {
    color: #172B4D;
    font-size: 14px;
    font-weight: 700;
    margin-top: 5px;
    white-space: nowrap;
}


/* ============================================================
   BOTONES MINI DE GRÁFICOS
   ============================================================ */

.chart-button-wrapper {
    height: 64px;
}

div[data-testid="stButton"] > button {
    height: 64px !important;
    min-height: 64px !important;

    border-radius: 11px !important;

    border: 1px solid #E7EBF0 !important;

    background: #F7F9FB !important;

    color: #172B4D !important;

    font-size: 10px !important;

    font-weight: 600 !important;

    text-align: left !important;

    padding: 8px 12px !important;

    box-shadow: none !important;

    white-space: nowrap !important;

    overflow: hidden !important;

    text-overflow: ellipsis !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #D5DCE5 !important;

    background: #F7F9FB !important;

    color: #172B4D !important;
}

div[data-testid="stButton"] > button:focus {
    box-shadow: none !important;
}


/* ============================================================
   DIÁLOGOS / POPUPS
   ============================================================ */

div[data-testid="stDialog"] {
    border-radius: 18px !important;
}

div[data-testid="stDialog"] > div {
    border-radius: 18px !important;
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

.metric-average {
    color: #8A94A6;
    font-size: 8px;
    margin-top: 3px;
}


/* ============================================================
   RENTABILIDAD
   ============================================================ */

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
   OCUPACIÓN
   ============================================================ */

.occupancy-row {
    display: flex;
    gap: 7px;
    margin-top: 8px;
}

.occupancy-box {
    background: #F7F9FB;
    border-radius: 9px;
    padding: 7px 8px;
    flex: 1;
}

.occupancy-label {
    color: #6B778C;
    font-size: 9px;
}

.occupancy-value {
    color: #7C3AED;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}

.occupancy-detail {
    color: #8A94A6;
    font-size: 9px;
    margin-top: 1px;
}

.accumulated-label {
    color: #8A94A6;
    font-size: 9px;
    margin-top: 1px;
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

    st.error(
        f"No fue posible conectar con BigQuery: {e}"
    )

    st.stop()


# ============================================================
# DATOS FINANCIEROS
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

    return client.query(
        query
    ).to_dataframe()


# ============================================================
# OCUPACIÓN AIRBNB
# ============================================================

@st.cache_data(ttl=300)
def cargar_ocupacion(
    fecha_inicio,
    fecha_fin_exclusiva
):

    query = """

    DECLARE p_fecha_inicio DATE DEFAULT @fecha_inicio;

    DECLARE p_fecha_fin_exclusiva DATE
        DEFAULT @fecha_fin_exclusiva;


    WITH mapa AS (

        SELECT

            LOWER(
                TRIM(Anuncio)
            ) AS anuncio_key,

            ANY_VALUE(Nombre)
                AS Nombre_Propiedad,

            ANY_VALUE(Ciudad)
                AS Ciudad

        FROM
            `rentascamacho.rentas_cortas.Participaciones`

        WHERE
            Anuncio IS NOT NULL

            AND TRIM(Anuncio) <> ''

        GROUP BY
            LOWER(
                TRIM(Anuncio)
            )
    ),


    reservas_unicas AS (

        SELECT

            C__digo_de_confirmaci__n
                AS Codigo_Reserva,

            ANY_VALUE(Anuncio)
                AS Anuncio,

            ANY_VALUE(
                DATE(Fecha_de_inicio)
            ) AS Fecha_Inicio,

            ANY_VALUE(
                DATE(Fecha_de_finalizaci__n)
            ) AS Fecha_Fin

        FROM
            `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

        WHERE

            LOWER(
                TRIM(Tipo)
            ) = 'reservación'

            AND C__digo_de_confirmaci__n
                IS NOT NULL

            AND Fecha_de_inicio
                IS NOT NULL

            AND Fecha_de_finalizaci__n
                IS NOT NULL

        GROUP BY
            C__digo_de_confirmaci__n
    ),


    reservas_periodo AS (

        SELECT

            Codigo_Reserva,

            Anuncio,

            GREATEST(

                DATE_DIFF(

                    LEAST(
                        Fecha_Fin,
                        p_fecha_fin_exclusiva
                    ),

                    GREATEST(
                        Fecha_Inicio,
                        p_fecha_inicio
                    ),

                    DAY
                ),

                0

            ) AS Noches_Periodo

        FROM
            reservas_unicas

        WHERE

            Fecha_Inicio
                < p_fecha_fin_exclusiva

            AND Fecha_Fin
                > p_fecha_inicio
    ),


    reservas_mapeadas AS (

        SELECT

            r.Codigo_Reserva,

            r.Noches_Periodo,

            m.Nombre_Propiedad,

            m.Ciudad

        FROM
            reservas_periodo r

        INNER JOIN mapa m

            ON LOWER(
                TRIM(r.Anuncio)
            ) = m.anuncio_key

        WHERE
            r.Noches_Periodo > 0
    ),


    resumen_reservas AS (

        SELECT

            Nombre_Propiedad,

            Ciudad,

            COUNT(
                DISTINCT Codigo_Reserva
            ) AS Reservas,

            SUM(
                Noches_Periodo
            ) AS Noches_Reservadas

        FROM
            reservas_mapeadas

        GROUP BY
            Nombre_Propiedad,
            Ciudad
    ),


    propiedades AS (

        SELECT DISTINCT

            Nombre_Propiedad,

            Ciudad

        FROM
            mapa
    )


    SELECT

        p.Nombre_Propiedad,

        p.Ciudad,

        COALESCE(
            r.Reservas,
            0
        ) AS Reservas,

        COALESCE(
            r.Noches_Reservadas,
            0
        ) AS Noches_Reservadas,

        DATE_DIFF(

            p_fecha_fin_exclusiva,

            p_fecha_inicio,

            DAY

        ) AS Noches_Disponibles,

        ROUND(

            SAFE_DIVIDE(

                COALESCE(
                    r.Noches_Reservadas,
                    0
                ),

                DATE_DIFF(

                    p_fecha_fin_exclusiva,

                    p_fecha_inicio,

                    DAY

                )

            ) * 100,

            1

        ) AS Ocupacion_Porcentaje

    FROM
        propiedades p

    LEFT JOIN resumen_reservas r

        ON p.Nombre_Propiedad
            = r.Nombre_Propiedad

        AND p.Ciudad
            = r.Ciudad

    ORDER BY
        p.Nombre_Propiedad

    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[

            bigquery.ScalarQueryParameter(
                "fecha_inicio",
                "DATE",
                fecha_inicio
            ),

            bigquery.ScalarQueryParameter(
                "fecha_fin_exclusiva",
                "DATE",
                fecha_fin_exclusiva
            )

        ]
    )

    return client.query(
        query,
        job_config=job_config
    ).to_dataframe()


# ============================================================
# FORMATOS
# ============================================================

def dinero(valor):

    return f"${valor:,.0f}".replace(
        ",",
        "."
    )


def dinero_corto(valor):

    if pd.isna(valor):
        return "$0"

    valor = float(valor)

    if abs(valor) >= 1_000_000:

        return f"${valor / 1_000_000:.1f}M"

    elif abs(valor) >= 1_000:

        return f"${valor / 1_000:.0f}k"

    return f"${valor:,.0f}".replace(
        ",",
        "."
    )


# ============================================================
# CARGAR DATOS
# ============================================================

try:

    df = cargar_datos()

except Exception as e:

    st.error(
        "Error consultando "
        "Movimientos_Operativos_Reparto: "
        f"{e}"
    )

    st.stop()


if df.empty:

    st.warning(
        "No hay registros disponibles para Airbnb."
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
# FECHAS
# ============================================================

hoy = date.today()

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

meses_cerrados = max(
    hoy.month - 1,
    0
)

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
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
    ingresos_ytd
    -
    gastos_ytd
)

rentabilidad_ytd = (
    flujo_ytd
    /
    ingresos_ytd
    *
    100
    if ingresos_ytd != 0
    else 0
)

color_flujo_ytd = (
    "#00875A"
    if flujo_ytd >= 0
    else "#DE350B"
)

color_rentabilidad_ytd = (
    "#00875A"
    if rentabilidad_ytd >= 0
    else "#DE350B"
)


# ============================================================
# GRÁFICO INGRESO MENSUAL
# ============================================================

df_mensual = df.copy()

df_mensual["Año"] = (
    df_mensual["Fecha"].dt.year
)

df_mensual["Mes"] = (
    df_mensual["Fecha"].dt.month
)

grafico_mensual = (
    df_mensual
    .groupby(
        ["Año", "Mes"],
        as_index=False
    )
    .agg(
        Ingreso=(
            "Ingreso",
            "sum"
        )
    )
)

tabla_mensual = (
    grafico_mensual
    .pivot(
        index="Mes",
        columns="Año",
        values="Ingreso"
    )
    .fillna(0)
)

for año in [2025, 2026]:

    if año not in tabla_mensual.columns:
        tabla_mensual[año] = 0

tabla_mensual = (
    tabla_mensual
    .reindex(
        range(1, 13),
        fill_value=0
    )
)

tabla_mensual.index = [
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

tabla_mensual = tabla_mensual[
    [2025, 2026]
]


# ============================================================
# PROMEDIO MENSUAL POR PROPIEDAD
# ============================================================

df_cerrado_header = df[
    (df["Fecha"] >= inicio_anio)
    &
    (df["Fecha"] < inicio_mes_actual)
].copy()

if meses_cerrados > 0:

    promedio_header = (
        df_cerrado_header
        .groupby(
            [
                "Nombre_Propiedad",
                "Ciudad"
            ],
            as_index=False
        )
        .agg(
            Ingreso_Total=(
                "Ingreso",
                "sum"
            )
        )
    )

    promedio_header[
        "Ingreso_Promedio"
    ] = (
        promedio_header["Ingreso_Total"]
        /
        meses_cerrados
    )

else:

    promedio_header = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Ingreso_Promedio"
        ]
    )


# ============================================================
# DIÁLOGO — INGRESO MENSUAL
# ============================================================

@st.dialog("Ingreso mensual")
def mostrar_ingreso_mensual():

    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:700;
            color:#172B4D;
            margin-bottom:4px;
        ">
            Ingreso mensual
        </div>

        <div style="
            font-size:12px;
            color:#6B778C;
            margin-bottom:15px;
        ">
            Comparación de ingresos mensuales · 2025 vs 2026
        </div>
        """,
        unsafe_allow_html=True
    )

    st.line_chart(
        tabla_mensual,
        height=350
    )


# ============================================================
# DIÁLOGO — PROMEDIO MENSUAL
# ============================================================

@st.dialog("Promedio mensual")
def mostrar_promedio_mensual():

    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:700;
            color:#172B4D;
            margin-bottom:4px;
        ">
            Promedio mensual por propiedad
        </div>

        <div style="
            font-size:12px;
            color:#6B778C;
            margin-bottom:15px;
        ">
            Ingreso promedio mensual de los meses cerrados
        </div>
        """,
        unsafe_allow_html=True
    )

    if not promedio_header.empty:

        grafico_propiedades = (
            promedio_header
            .sort_values(
                "Ingreso_Promedio",
                ascending=False
            )
            .set_index(
                "Nombre_Propiedad"
            )[["Ingreso_Promedio"]]
        )

        st.bar_chart(
            grafico_propiedades,
            height=380
        )

        st.markdown(
            "### Detalle por propiedad"
        )

        tabla_popup = (
            promedio_header[
                [
                    "Nombre_Propiedad",
                    "Ciudad",
                    "Ingreso_Promedio"
                ]
            ]
            .sort_values(
                "Ingreso_Promedio",
                ascending=False
            )
            .rename(
                columns={
                    "Nombre_Propiedad":
                        "Propiedad",

                    "Ingreso_Promedio":
                        "Promedio mensual"
                }
            )
        )

        st.dataframe(
            tabla_popup,
            hide_index=True,
            use_container_width=True
        )

    else:

        st.info(
            "Todavía no hay meses cerrados "
            "para calcular el promedio."
        )


# ============================================================
# HEADER
# ============================================================

header_cols = st.columns(
    [
        0.34,
        1.65,
        1.0,
        1.0,
        1.0,
        1.05,
        1.05
    ],
    gap="small"
)


# ============================================================
# ICONO
# ============================================================

with header_cols[0]:

    st.markdown(
        '<div class="header-icon">🏢</div>',
        unsafe_allow_html=True
    )


# ============================================================
# NOMBRE
# ============================================================

with header_cols[1]:

    st.markdown(
        '<div class="app-name">'
        'Airbnb <span>Financial Hub</span>'
        '</div>'

        '<div class="app-subtitle">'
        'Rentabilidad financiera · Solo Airbnb'
        '</div>',

        unsafe_allow_html=True
    )


# ============================================================
# INGRESOS 2026
# ============================================================

with header_cols[2]:

    st.markdown(
        '<div class="annual-card">'

        '<div class="annual-label">'
        f'Ingresos {hoy.year}'
        '</div>'

        '<div class="annual-value">'
        f'{dinero(ingresos_ytd)}'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


# ============================================================
# FLUJO 2026
# ============================================================

with header_cols[3]:

    st.markdown(
        '<div class="annual-card">'

        '<div class="annual-label">'
        f'Flujo {hoy.year}'
        '</div>'

        f'<div class="annual-value" '
        f'style="color:{color_flujo_ytd};">'
        f'{dinero(flujo_ytd)}'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


# ============================================================
# RENTABILIDAD 2026
# ============================================================

with header_cols[4]:

    st.markdown(
        '<div class="annual-card">'

        '<div class="annual-label">'
        f'Rentabilidad {hoy.year}'
        '</div>'

        f'<div class="annual-value" '
        f'style="color:{color_rentabilidad_ytd};">'
        f'{rentabilidad_ytd:.1f}%'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


# ============================================================
# MINI TARJETA — INGRESO MENSUAL
# ============================================================

with header_cols[5]:

    if st.button(
        "📈  Ingreso mensual",
        key="btn_ingreso_mensual",
        use_container_width=True
    ):

        mostrar_ingreso_mensual()


# ============================================================
# MINI TARJETA — PROMEDIO MENSUAL
# ============================================================

with header_cols[6]:

    if st.button(
        "📊  Promedio mensual",
        key="btn_promedio_mensual",
        use_container_width=True
    ):

        mostrar_promedio_mensual()


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

    inicio_mes = hoy.replace(
        day=1
    )

    fecha_min = (
        df["Fecha"]
        .min()
        .date()
    )

    fecha_max = max(
        df["Fecha"].max().date(),
        hoy
    )

    fechas = st.date_input(
        "Período de análisis",

        value=(
            inicio_mes,
            hoy
        ),

        min_value=fecha_min,

        max_value=fecha_max,

        format="DD/MM/YYYY",

        key="periodo_analisis"
    )


# ============================================================
# VALIDAR FECHAS
# ============================================================

if (
    isinstance(fechas, tuple)
    and len(fechas) == 2
):

    fecha_inicio = pd.Timestamp(
        fechas[0]
    )

    fecha_fin = (
        pd.Timestamp(fechas[1])
        +
        pd.Timedelta(days=1)
    )

else:

    fecha_inicio = pd.Timestamp(
        fechas
    )

    fecha_fin = (
        fecha_inicio
        +
        pd.Timedelta(days=1)
    )


# ============================================================
# FILTRAR FINANZAS
# ============================================================

df_f = df[
    (df["Fecha"] >= fecha_inicio)
    &
    (df["Fecha"] < fecha_fin)
].copy()


if ciudad != "Todas":

    df_f = df_f[
        df_f["Ciudad"] == ciudad
    ]


if propiedad != "Todas":

    df_f = df_f[
        df_f["Nombre_Propiedad"]
        == propiedad
    ]


if socio != "Todos":

    df_f = df_f[
        df_f["Nombre_Socio"]
        == socio
    ]


if df_f.empty:

    st.warning(
        "No existen datos para los filtros seleccionados."
    )

    st.stop()


# ============================================================
# OCUPACIÓN
# ============================================================

try:

    df_ocupacion = cargar_ocupacion(
        fecha_inicio.date(),
        fecha_fin.date()
    )

except Exception:

    df_ocupacion = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas",
            "Noches_Disponibles",
            "Ocupacion_Porcentaje"
        ]
    )


# ============================================================
# KPI DEL PERÍODO
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = (
    ingresos
    -
    gastos
)

rentabilidad = (
    flujo
    /
    ingresos
    *
    100
    if ingresos != 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4)


with k1:

    st.markdown(
        '<div class="kpi-card">'

        '<div class="kpi-label">'
        '💰 INGRESOS BRUTOS'
        '</div>'

        f'<div class="kpi-value">'
        f'{dinero(ingresos)}'
        f'</div>'

        '<div class="kpi-sub">'
        'Ingresos registrados'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        '<div class="kpi-card">'

        '<div class="kpi-label">'
        '🧾 GASTOS OPERATIVOS'
        '</div>'

        f'<div class="kpi-value">'
        f'{dinero(gastos)}'
        f'</div>'

        '<div class="kpi-sub">'
        'Egresos registrados'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


with k3:

    color_flujo = (
        "#00875A"
        if flujo >= 0
        else "#DE350B"
    )

    st.markdown(
        '<div class="kpi-card">'

        '<div class="kpi-label">'
        '💵 FLUJO'
        '</div>'

        f'<div class="kpi-value" '
        f'style="color:{color_flujo};">'

        f'{dinero(flujo)}'

        '</div>'

        '<div class="kpi-sub">'
        'Ingresos − gastos'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


with k4:

    color_rentabilidad = (
        "#00875A"
        if rentabilidad >= 35
        else "#DE350B"
    )

    st.markdown(
        '<div class="kpi-card">'

        '<div class="kpi-label">'
        '🎯 RENTABILIDAD'
        '</div>'

        f'<div class="kpi-value" '
        f'style="color:{color_rentabilidad};">'

        f'{rentabilidad:.1f}%'

        '</div>'

        '<div class="kpi-sub">'
        'Objetivo: 35%'
        '</div>'

        '</div>',

        unsafe_allow_html=True
    )


# ============================================================
# PROMEDIOS MENSUALES
# ============================================================

df_cerrado = df[
    (df["Fecha"] >= inicio_anio)
    &
    (df["Fecha"] < inicio_mes_actual)
].copy()


if meses_cerrados > 0:

    promedios = (
        df_cerrado
        .groupby(
            [
                "Nombre_Propiedad",
                "Ciudad"
            ],
            as_index=False
        )
        .agg(
            Ingreso_Promedio=(
                "Ingreso",
                "sum"
            ),

            Gasto_Promedio=(
                "Gasto",
                "sum"
            )
        )
    )

    promedios[
        "Ingreso_Promedio"
    ] = (
        promedios["Ingreso_Promedio"]
        /
        meses_cerrados
    )

    promedios[
        "Gasto_Promedio"
    ] = (
        promedios["Gasto_Promedio"]
        /
        meses_cerrados
    )

    promedios[
        "Flujo_Promedio"
    ] = (
        promedios["Ingreso_Promedio"]
        -
        promedios["Gasto_Promedio"]
    )

else:

    promedios = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Ingreso_Promedio",
            "Gasto_Promedio",
            "Flujo_Promedio"
        ]
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
        Ingreso=(
            "Ingreso",
            "sum"
        ),

        Gasto=(
            "Gasto",
            "sum"
        )
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


# ============================================================
# ACUMULADO 2026
# ============================================================

resumen_ytd = (
    df_ytd
    .groupby(
        [
            "Nombre_Propiedad",
            "Ciudad"
        ],
        as_index=False
    )
    .agg(
        Ingreso_YTD=(
            "Ingreso",
            "sum"
        ),

        Gasto_YTD=(
            "Gasto",
            "sum"
        )
    )
)

resumen_ytd["Flujo_YTD"] = (
    resumen_ytd["Ingreso_YTD"]
    -
    resumen_ytd["Gasto_YTD"]
)

resumen_ytd["Rentabilidad_YTD"] = (
    resumen_ytd["Flujo_YTD"]
    /
    resumen_ytd["Ingreso_YTD"]
    *
    100
).fillna(0)


# ============================================================
# UNIR INFORMACIÓN
# ============================================================

resumen = resumen.merge(
    promedios,
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)

resumen = resumen.merge(
    resumen_ytd[
        [
            "Nombre_Propiedad",
            "Ciudad",
            "Ingreso_YTD",
            "Gasto_YTD",
            "Flujo_YTD",
            "Rentabilidad_YTD"
        ]
    ],
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)

resumen = resumen.merge(
    df_ocupacion[
        [
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas",
            "Noches_Disponibles",
            "Ocupacion_Porcentaje"
        ]
    ],
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)


# ============================================================
# ORDEN
# ============================================================

resumen = resumen.sort_values(
    "Rentabilidad",
    ascending=False
)


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🏢 Rentabilidad por propiedad'
    '</div>'

    '<div class="section-subtitle">'
    'Desempeño financiero de cada propiedad '
    'en el período seleccionado'
    '</div>',

    unsafe_allow_html=True
)


# ============================================================
# TARJETAS DE PROPIEDADES
# ============================================================

for inicio in range(
    0,
    len(resumen),
    3
):

    columnas = st.columns(3)

    for posicion in range(3):

        indice = (
            inicio
            +
            posicion
        )

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

        margen_ytd = float(
            fila["Rentabilidad_YTD"]
            if not pd.isna(
                fila["Rentabilidad_YTD"]
            )
            else 0
        )

        ingreso_promedio = float(
            fila["Ingreso_Promedio"]
            if not pd.isna(
                fila["Ingreso_Promedio"]
            )
            else 0
        )

        gasto_promedio = float(
            fila["Gasto_Promedio"]
            if not pd.isna(
                fila["Gasto_Promedio"]
            )
            else 0
        )

        flujo_promedio = float(
            fila["Flujo_Promedio"]
            if not pd.isna(
                fila["Flujo_Promedio"]
            )
            else 0
        )


        # ----------------------------------------------------
        # OCUPACIÓN
        # ----------------------------------------------------

        reservas_prop = (
            0
            if pd.isna(
                fila.get("Reservas")
            )
            else int(
                fila["Reservas"]
            )
        )

        noches_prop = (
            0
            if pd.isna(
                fila.get("Noches_Reservadas")
            )
            else int(
                fila["Noches_Reservadas"]
            )
        )

        ocupacion_prop = fila.get(
            "Ocupacion_Porcentaje"
        )

        if pd.isna(
            ocupacion_prop
        ):

            ocupacion_texto = "—"

            ocupacion_detalle = (
                "Sin anuncio asociado"
            )

        else:

            ocupacion_texto = (
                f"{float(ocupacion_prop):.1f}%"
            )

            ocupacion_detalle = (
                f"{reservas_prop} reservas · "
                f"{noches_prop} noches"
            )


        # ----------------------------------------------------
        # COLORES
        # ----------------------------------------------------

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


        color_ytd = (
            "#00A878"
            if margen_ytd >= 35
            else "#EF4444"
        )

        progreso = max(
            0,
            min(
                margen_prop,
                100
            )
        )


        # ----------------------------------------------------
        # TARJETA
        # ----------------------------------------------------

        tarjeta = (

            f'<div class="property-card '
            f'{clase_tarjeta}">'

            '<div style="display:flex;'
            'justify-content:space-between;'
            'align-items:flex-start;">'

            '<div>'

            f'<div class="property-name">'
            f'{nombre}'
            f'</div>'

            f'<div class="property-location">'
            f'📍 {ciudad_nombre}'
            f'</div>'

            '</div>'

            '<div style="text-align:right;">'

            f'<div class="margin-value" '
            f'style="color:{color_ytd};">'

            f'{margen_ytd:.1f}%'

            '</div>'

            '<div class="accumulated-label">'

            f'Acumulada {hoy.year}'

            '</div>'

            '</div>'

            '</div>'


            # ------------------------------------------------
            # MÉTRICAS
            # ------------------------------------------------

            '<div class="property-metrics">'

            '<div class="metric-box">'

            '<div class="metric-label">'
            'Ingresos'
            '</div>'

            f'<div class="metric-income">'
            f'{dinero(ingreso_prop)}'
            f'</div>'

            f'<div class="metric-average">'
            f'Prom. mes '
            f'{dinero_corto(ingreso_promedio)}'
            f'</div>'

            '</div>'


            '<div class="metric-box">'

            '<div class="metric-label">'
            'Gastos'
            '</div>'

            f'<div class="metric-expense">'
            f'{dinero(gasto_prop)}'
            f'</div>'

            f'<div class="metric-average">'
            f'Prom. mes '
            f'{dinero_corto(gasto_promedio)}'
            f'</div>'

            '</div>'


            '<div class="metric-box">'

            '<div class="metric-label">'
            'Flujo'
            '</div>'

            f'<div class="metric-flow">'
            f'{dinero(flujo_prop)}'
            f'</div>'

            f'<div class="metric-average">'
            f'Prom. mes '
            f'{dinero_corto(flujo_promedio)}'
            f'</div>'

            '</div>'

            '</div>'


            # ------------------------------------------------
            # RENTABILIDAD
            # ------------------------------------------------

            '<div class="margin-row">'

            '<div class="margin-label">'
            'Rentabilidad período'
            '</div>'

            f'<div class="margin-value" '
            f'style="color:{color};">'

            f'{margen_prop:.1f}%'

            '</div>'

            '</div>'


            '<div class="progress-bg">'

            f'<div class="progress-fill" '
            f'style="width:{progreso}%;'
            f'background:{color};">'
            '</div>'

            '</div>'


            f'<div class="status '
            f'{clase_estado}">'

            f'{estado}'

            '</div>'


            # ------------------------------------------------
            # OCUPACIÓN
            # ------------------------------------------------

            '<div class="occupancy-row">'

            '<div class="occupancy-box">'

            '<div class="occupancy-label">'
            'Ocupación Airbnb'
            '</div>'

            f'<div class="occupancy-value">'
            f'{ocupacion_texto}'
            f'</div>'

            f'<div class="occupancy-detail">'
            f'{ocupacion_detalle}'
            f'</div>'

            '</div>'

            '</div>'

            '</div>'
        )


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
    f"{len(df_f):,} registros · "
    f"{len(resumen)} propiedades"
)
