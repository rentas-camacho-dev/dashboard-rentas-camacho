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

/* Títulos */
.main-title {
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 4px;
}

.subtitle {
    color: #777777;
    font-size: 14px;
    margin-bottom: 8px;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 12px;
}

/* Indicadores */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #eeeeee;
    border-radius: 14px;
    padding: 14px;
}

/* Tarjetas */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 18px;
    border: 1px solid #eeeeee;
}

/* Separador */
.card-separator {
    border-top: 1px solid #eeeeee;
    margin-top: 12px;
    margin-bottom: 12px;
}

/* Ocupación */
.occupancy-title {
    color: #777777;
    font-size: 12px;
}

.occupancy-number {
    font-size: 24px;
    font-weight: 700;
}

.occupancy-detail {
    color: #888888;
    font-size: 12px;
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
# OCUPACIÓN AIRBNB
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
            ANY_VALUE(DATE(Fecha_de_inicio)) AS Fecha_Inicio,
            ANY_VALUE(DATE(Fecha_de_finalizaci__n)) AS Fecha_Fin

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
            r.Noches_Periodo,
            m.Nombre_Propiedad,
            m.Ciudad

        FROM
            reservas_periodo r

        INNER JOIN mapa m
            ON LOWER(TRIM(r.Anuncio)) = m.anuncio_key

        WHERE
            r.Noches_Periodo > 0
    ),

    resumen_reservas AS (

        SELECT
            Nombre_Propiedad,
            Ciudad,
            COUNT(DISTINCT Codigo_Reserva) AS Reservas,
            SUM(Noches_Periodo) AS Noches_Reservadas

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
# FORMATOS
# ============================================================

def dinero(valor):
    return f"${valor:,.0f}".replace(",", ".")


def dinero_corto(valor):

    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"${valor / 1_000:.0f}k"

    return f"${valor:,.0f}".replace(",", ".")


# ============================================================
# CARGAR
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
# HEADER
# ============================================================

header = st.container(border=True)

with header:

    titulo, indicador1, indicador2, indicador3 = st.columns(
        [2.5, 1, 1, 1]
    )

    with titulo:

        st.markdown(
            "### 🏠 Airbnb Financial Hub"
        )

        st.caption(
            "Rentabilidad financiera · Solo Airbnb"
        )

        st.success(
            "● Información actualizada",
            icon="●"
        )

    # YTD

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

    with indicador1:

        st.metric(
            f"Ingresos {hoy.year}",
            dinero_corto(ingreso_ytd)
        )

    with indicador2:

        st.metric(
            f"Flujo {hoy.year}",
            dinero_corto(flujo_ytd)
        )

    with indicador3:

        st.metric(
            f"Rentabilidad {hoy.year}",
            f"{rentabilidad_ytd:.1f}%"
        )


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    "### Filtros"
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
# FECHAS SELECCIONADAS
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
    "### Resumen del período"
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Ingresos Brutos",
        dinero(ingresos)
    )

with k2:
    st.metric(
        "Gastos Operativos",
        dinero(gastos)
    )

with k3:
    st.metric(
        "Flujo",
        dinero(flujo)
    )

with k4:
    st.metric(
        "Rentabilidad",
        f"{rentabilidad:.1f}%"
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
            Ingreso_Promedio=("Ingreso", "sum"),
            Gasto_Promedio=("Gasto", "sum")
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
# UNIR
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
# PROPIEDADES
# ============================================================

st.markdown(
    "### Rentabilidad por propiedad"
)


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

            with col:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"#### {row['Nombre_Propiedad']}"
                    )

                    st.caption(
                        row["Ciudad"]
                    )

                    st.markdown("---")

                    st.metric(
                        "Ingresos",
                        dinero(row["Ingreso"]),
                        f"Prom. mes {dinero_corto(row['Ingreso_Promedio'])}"
                    )

                    st.metric(
                        "Gastos",
                        dinero(row["Gasto"]),
                        f"Prom. mes {dinero_corto(row['Gasto_Promedio'])}"
                    )

                    st.metric(
                        "Flujo",
                        dinero(row["Flujo"]),
                        f"Prom. mes {dinero_corto(row['Flujo_Promedio'])}"
                    )

                    st.metric(
                        "Rentabilidad",
                        f"{row['Rentabilidad']:.1f}%"
                    )

                    st.markdown("---")

                    ocup = row["Ocupacion_Porcentaje"]

                    if pd.isna(ocup):

                        st.caption(
                            "Ocupación"
                        )

                        st.markdown(
                            "### —"
                        )

                        st.caption(
                            "Sin anuncio asociado"
                        )

                    else:

                        st.caption(
                            "Ocupación"
                        )

                        st.markdown(
                            f"### {float(ocup):.1f}%"
                        )

                        st.caption(
                            f"{int(row['Reservas'])} reservas · "
                            f"{int(row['Noches_Reservadas'])} noches"
                        )
