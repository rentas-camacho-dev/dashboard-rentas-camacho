import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date
from textwrap import dedent


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Airbnb Financial Hub",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.hero {
    background: white;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 22px;
    border: 1px solid #eeeeee;
    box-shadow: 0 4px 18px rgba(0,0,0,0.04);
}

.hero-title {
    font-size: 30px;
    font-weight: 700;
    color: #222222;
    margin-bottom: 4px;
}

.hero-subtitle {
    font-size: 15px;
    color: #777777;
    margin-bottom: 20px;
}

.status {
    color: #25a244;
    font-size: 13px;
    font-weight: 600;
}

.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #eeeeee;
    box-shadow: 0 3px 12px rgba(0,0,0,0.035);
    min-height: 120px;
}

.kpi-title {
    font-size: 13px;
    color: #777777;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 27px;
    font-weight: 700;
    color: #222222;
}

.kpi-positive {
    color: #1f9d55;
}

.property-card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #eeeeee;
    box-shadow: 0 3px 14px rgba(0,0,0,0.035);
    min-height: 365px;
    margin-bottom: 18px;
}

.property-name {
    font-size: 19px;
    font-weight: 700;
    color: #222222;
    margin-bottom: 2px;
}

.property-city {
    font-size: 13px;
    color: #888888;
    margin-bottom: 18px;
}

.metric-label {
    font-size: 12px;
    color: #888888;
    margin-top: 7px;
}

.metric-value {
    font-size: 21px;
    font-weight: 700;
    color: #222222;
}

.metric-average {
    font-size: 11px;
    color: #999999;
    margin-bottom: 8px;
}

.occupancy-box {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid #eeeeee;
}

.occupancy-label {
    font-size: 12px;
    color: #888888;
}

.occupancy-value {
    font-size: 23px;
    font-weight: 700;
    color: #e63946;
}

.occupancy-detail {
    font-size: 11px;
    color: #999999;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #222222;
    margin-top: 18px;
    margin-bottom: 14px;
}

.mini-indicator {
    text-align: right;
}

.mini-label {
    font-size: 11px;
    color: #999999;
}

.mini-value {
    font-size: 17px;
    font-weight: 700;
    color: #222222;
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
# CARGAR DATOS FINANCIEROS
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
    FROM
        `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    WHERE
        LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
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

    return df


# ============================================================
# CARGAR OCUPACIÓN
# ============================================================

@st.cache_data(ttl=300)
def cargar_ocupacion(fecha_inicio, fecha_fin):

    query = """
    DECLARE p_fecha_inicio DATE DEFAULT @fecha_inicio;
    DECLARE p_fecha_fin DATE DEFAULT @fecha_fin;

    WITH mapa AS (

        SELECT
            LOWER(TRIM(Anuncio)) AS anuncio_key,
            ANY_VALUE(Nombre) AS Nombre_Propiedad,
            ANY_VALUE(Ciudad) AS Ciudad

        FROM
            `rentascamacho.rentas_cortas.Participaciones`

        WHERE
            Anuncio IS NOT NULL
            AND TRIM(Anuncio) <> ''

        GROUP BY
            LOWER(TRIM(Anuncio))
    ),

    reservas_unicas AS (

        SELECT
            C__digo_de_confirmaci__n AS Codigo_Reserva,

            ANY_VALUE(Anuncio) AS Anuncio,

            ANY_VALUE(
                DATE(Fecha_de_inicio)
            ) AS Fecha_Inicio,

            ANY_VALUE(
                DATE(Fecha_de_finalizaci__n)
            ) AS Fecha_Fin

        FROM
            `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

        WHERE
            LOWER(TRIM(Tipo)) = 'reservación'

            AND C__digo_de_confirmaci__n IS NOT NULL

            AND Fecha_de_inicio IS NOT NULL

            AND Fecha_de_finalizaci__n IS NOT NULL

        GROUP BY
            C__digo_de_confirmaci__n
    ),

    reservas_periodo AS (

        SELECT
            Codigo_Reserva,
            Anuncio,
            Fecha_Inicio,
            Fecha_Fin,

            GREATEST(
                DATE_DIFF(
                    LEAST(
                        Fecha_Fin,
                        DATE_ADD(
                            p_fecha_fin,
                            INTERVAL 1 DAY
                        )
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
            Fecha_Inicio <
                DATE_ADD(
                    p_fecha_fin,
                    INTERVAL 1 DAY
                )

            AND Fecha_Fin >
                p_fecha_inicio
    ),

    reservas_mapeadas AS (

        SELECT
            r.Codigo_Reserva,
            r.Anuncio,
            r.Noches_Periodo,
            m.Nombre_Propiedad,
            m.Ciudad

        FROM
            reservas_periodo r

        INNER JOIN mapa m
            ON LOWER(TRIM(r.Anuncio))
             = m.anuncio_key

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
            DATE_ADD(
                p_fecha_fin,
                INTERVAL 1 DAY
            ),
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
                    DATE_ADD(
                        p_fecha_fin,
                        INTERVAL 1 DAY
                    ),
                    p_fecha_inicio,
                    DAY
                )
            ) * 100,
            1
        ) AS Ocupacion_Porcentaje

    FROM
        propiedades p

    LEFT JOIN resumen_reservas r
        ON p.Nombre_Propiedad = r.Nombre_Propiedad
        AND p.Ciudad = r.Ciudad

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
# FORMATO DE DINERO
# ============================================================

def dinero(valor):

    return f"${valor:,.0f}".replace(",", ".")


def dinero_corto(valor):

    valor = float(valor)

    if abs(valor) >= 1_000_000:

        return f"${valor / 1_000_000:.1f}M"

    elif abs(valor) >= 1_000:

        return f"${valor / 1_000:.0f}k"

    else:

        return f"${valor:,.0f}".replace(",", ".")


# ============================================================
# CARGAR FINANZAS
# ============================================================

df = cargar_datos_financieros()


# ============================================================
# FECHAS
# ============================================================

hoy = date.today()

inicio_mes = date(
    hoy.year,
    hoy.month,
    1
)


# ============================================================
# INDICADORES ANUALES
# ============================================================

df_ytd = df[
    (df["Fecha"] >= pd.Timestamp(hoy.year, 1, 1))
    &
    (
        df["Fecha"]
        <
        pd.Timestamp(hoy)
        + pd.Timedelta(days=1)
    )
]

ingreso_ytd = df_ytd["Ingreso"].sum()
gasto_ytd = df_ytd["Gasto"].sum()
flujo_ytd = ingreso_ytd - gasto_ytd

rentabilidad_ytd = (
    flujo_ytd / ingreso_ytd * 100
    if ingreso_ytd != 0
    else 0
)


# ============================================================
# HEADER
# ============================================================

header_html = f"""
<div class="hero">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <div class="hero-title">
                🏠 Airbnb Financial Hub
            </div>
            <div class="hero-subtitle">
                Rentabilidad financiera · Solo Airbnb
            </div>
        </div>

        <div style="display:flex; gap:35px;">

            <div class="mini-indicator">
                <div class="mini-label">
                    Ingresos {hoy.year}
                </div>
                <div class="mini-value">
                    {dinero_corto(ingreso_ytd)}
                </div>
            </div>

            <div class="mini-indicator">
                <div class="mini-label">
                    Flujo {hoy.year}
                </div>
                <div class="mini-value">
                    {dinero_corto(flujo_ytd)}
                </div>
            </div>

            <div class="mini-indicator">
                <div class="mini-label">
                    Rentabilidad {hoy.year}
                </div>
                <div class="mini-value">
                    {rentabilidad_ytd:.1f}%
                </div>
            </div>

        </div>
    </div>

    <div class="status">
        ● Información actualizada
    </div>
</div>
"""

st.markdown(
    dedent(header_html),
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="section-title">Filtros</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .unique()
        .tolist()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades
    )


with col2:

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .unique()
        .tolist()
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades
    )


with col3:

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .unique()
        .tolist()
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios
    )


with col4:

    rango = st.date_input(
        "Período de análisis",
        value=(inicio_mes, hoy)
    )


# ============================================================
# VALIDAR FECHAS
# ============================================================

if isinstance(rango, tuple) and len(rango) == 2:

    fecha_inicio = rango[0]
    fecha_fin = rango[1]

else:

    fecha_inicio = rango
    fecha_fin = rango


# ============================================================
# FILTRO FINANCIERO
# ============================================================

df_f = df[
    (df["Fecha"] >= pd.Timestamp(fecha_inicio))
    &
    (
        df["Fecha"]
        <
        pd.Timestamp(fecha_fin)
        + pd.Timedelta(days=1)
    )
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


st.markdown(
    '<div class="section-title">Resumen del período</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)


k1_html = f"""
<div class="kpi-card">
    <div class="kpi-title">
        Ingresos Brutos
    </div>
    <div class="kpi-value">
        {dinero(ingresos)}
    </div>
</div>
"""

k1.markdown(
    dedent(k1_html),
    unsafe_allow_html=True
)


k2_html = f"""
<div class="kpi-card">
    <div class="kpi-title">
        Gastos Operativos
    </div>
    <div class="kpi-value">
        {dinero(gastos)}
    </div>
</div>
"""

k2.markdown(
    dedent(k2_html),
    unsafe_allow_html=True
)


k3_html = f"""
<div class="kpi-card">
    <div class="kpi-title">
        Flujo
    </div>
    <div class="kpi-value kpi-positive">
        {dinero(flujo)}
    </div>
</div>
"""

k3.markdown(
    dedent(k3_html),
    unsafe_allow_html=True
)


k4_html = f"""
<div class="kpi-card">
    <div class="kpi-title">
        Rentabilidad
    </div>
    <div class="kpi-value">
        {rentabilidad:.1f}%
    </div>
</div>
"""

k4.markdown(
    dedent(k4_html),
    unsafe_allow_html=True
)


# ============================================================
# PROMEDIOS MENSUALES
# ============================================================

meses_cerrados = max(
    hoy.month - 1,
    0
)

inicio_anio = pd.Timestamp(
    hoy.year,
    1,
    1
)

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
)

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

    promedios["Ingreso_Promedio"] /= meses_cerrados
    promedios["Gasto_Promedio"] /= meses_cerrados

    promedios["Flujo_Promedio"] = (
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
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
)

resumen["Flujo"] = (
    resumen["Ingreso"]
    -
    resumen["Gasto"]
)

resumen["Rentabilidad"] = resumen.apply(
    lambda row:
        (
            row["Flujo"]
            /
            row["Ingreso"]
            * 100
        )
        if row["Ingreso"] != 0
        else 0,
    axis=1
)

resumen = resumen.merge(
    promedios,
    on=[
        "Nombre_Propiedad",
        "Ciudad"
    ],
    how="left"
)


# ============================================================
# OCUPACIÓN
# ============================================================

ocupacion = cargar_ocupacion(
    fecha_inicio,
    fecha_fin
)


# ============================================================
# UNIR OCUPACIÓN
# ============================================================

resumen = resumen.merge(
    ocupacion[
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
# TÍTULO PROPIEDADES
# ============================================================

st.markdown(
    '<div class="section-title">Rentabilidad por propiedad</div>',
    unsafe_allow_html=True
)


# ============================================================
# TARJETAS
# ============================================================

if resumen.empty:

    st.info(
        "No hay información para los filtros seleccionados."
    )

else:

    for i in range(
        0,
        len(resumen),
        3
    ):

        fila = resumen.iloc[
            i:i + 3
        ]

        cols = st.columns(3)

        for col, (_, row) in zip(
            cols,
            fila.iterrows()
        ):

            ingreso_prom = row.get(
                "Ingreso_Promedio",
                0
            )

            gasto_prom = row.get(
                "Gasto_Promedio",
                0
            )

            flujo_prom = row.get(
                "Flujo_Promedio",
                0
            )

            ocup = row.get(
                "Ocupacion_Porcentaje",
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

                ocupacion_html = """
<div class="occupancy-box">
    <div class="occupancy-label">
        Ocupación
    </div>

    <div class="occupancy-value">
        —
    </div>

    <div class="occupancy-detail">
        Sin anuncio asociado
    </div>
</div>
"""

            else:

                ocupacion_html = f"""
<div class="occupancy-box">
    <div class="occupancy-label">
        Ocupación
    </div>

    <div class="occupancy-value">
        {float(ocup):.1f}%
    </div>

    <div class="occupancy-detail">
        {int(reservas)} reservas · {int(noches)} noches
    </div>
</div>
"""

            tarjeta_html = f"""
<div class="property-card">

    <div class="property-name">
        {row["Nombre_Propiedad"]}
    </div>

    <div class="property-city">
        {row["Ciudad"]}
    </div>

    <div class="metric-label">
        Ingresos
    </div>

    <div class="metric-value">
        {dinero(row["Ingreso"])}
    </div>

    <div class="metric-average">
        Prom. mes {dinero_corto(ingreso_prom)}
    </div>

    <div class="metric-label">
        Gastos
    </div>

    <div class="metric-value">
        {dinero(row["Gasto"])}
    </div>

    <div class="metric-average">
        Prom. mes {dinero_corto(gasto_prom)}
    </div>

    <div class="metric-label">
        Flujo
    </div>

    <div class="metric-value">
        {dinero(row["Flujo"])}
    </div>

    <div class="metric-average">
        Prom. mes {dinero_corto(flujo_prom)}
    </div>

    <div class="metric-label">
        Rentabilidad
    </div>

    <div class="metric-value">
        {row["Rentabilidad"]:.1f}%
    </div>

    {ocupacion_html}

</div>
"""

            col.markdown(
                dedent(tarjeta_html),
                unsafe_allow_html=True
            )
