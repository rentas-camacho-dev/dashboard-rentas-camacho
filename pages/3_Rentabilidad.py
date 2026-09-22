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

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 3.8rem !important;
    padding-bottom: 1.2rem !important;
    max-width: 1500px !important;
}

/* Ocultar elementos de Streamlit */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* =========================
   HEADER SUPERIOR
   ========================= */

.top-row {
    display: flex;
    align-items: stretch;
    gap: 10px;
    margin-top: 4px;
    margin-bottom: 12px;
}

.brand-card {
    background: white;
    border: 1px solid #DCE5EE;
    border-radius: 18px;
    height: 94px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    box-sizing: border-box;
}

.logo-box {
    width: 58px;
    height: 58px;
    border-radius: 16px;
    background: #FF214B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 31px;
    flex-shrink: 0;
    margin-right: 14px;
}

.brand-title {
    font-size: 23px;
    line-height: 1.05;
    font-weight: 850;
    color: #19345C;
    white-space: nowrap;
}

.brand-title-red {
    color: #FF3155;
}

.brand-sub {
    font-size: 11px;
    color: #8290A4;
    margin-top: 7px;
    white-space: nowrap;
}

/* =========================
   TARJETAS DE GRÁFICOS
   ========================= */

.chart-button {
    background: white;
    border: 1px solid #DCE5EE;
    border-radius: 18px;
    height: 94px;
    padding: 0 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-sizing: border-box;
}

.chart-button-title {
    font-size: 17px;
    color: #536783;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chart-button-icon {
    font-size: 20px;
    margin-right: 7px;
}

.chart-arrow {
    font-size: 18px;
    color: #536783;
}

/* =========================
   FILTROS
   ========================= */

.filter-title {
    font-size: 13px;
    font-weight: 700;
    color: #71809A;
    margin-bottom: 5px;
}

div[data-baseweb="select"] > div {
    background-color: #F0F3F7 !important;
    border: none !important;
    border-radius: 11px !important;
    min-height: 52px !important;
}

div[data-baseweb="select"] span {
    font-size: 16px !important;
}

div[data-testid="stDateInput"] input {
    background-color: #F0F3F7 !important;
    border: none !important;
    border-radius: 11px !important;
    min-height: 52px !important;
    font-size: 16px !important;
}

/* =========================
   FILA KPI + NAVEGACIÓN
   ========================= */

.kpi-card {
    background: white;
    border: 1px solid #DCE5EE;
    border-radius: 18px;
    height: 108px;
    padding: 16px 20px;
    box-sizing: border-box;
}

.kpi-title {
    font-size: 12px;
    font-weight: 700;
    color: #7C8CA2;
}

.kpi-value {
    font-size: 31px;
    font-weight: 850;
    color: #19345C;
    margin-top: 8px;
    line-height: 1;
}

.kpi-value.green {
    color: #009B70;
}

.kpi-value.red {
    color: #E94332;
}

.nav-card {
    background: white;
    border: 1px solid #DCE5EE;
    border-radius: 18px;
    height: 108px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
}

.nav-card-text {
    font-size: 18px;
    color: #536783;
    white-space: nowrap;
}

/* =========================
   TÍTULO PORTAFOLIO
   ========================= */

.portfolio-title {
    font-size: 30px;
    font-weight: 850;
    color: #19345C;
    margin-top: 22px;
    margin-bottom: 2px;
}

.portfolio-subtitle {
    font-size: 14px;
    color: #8290A4;
    margin-bottom: 16px;
}

/* =========================
   PROPIEDADES
   ========================= */

.property-card {
    background: white;
    border: 1px solid #DCE5EE;
    border-radius: 20px;
    padding: 17px;
    min-height: 365px;
    box-sizing: border-box;
    box-shadow: 0 4px 12px rgba(20,40,70,0.035);
}

.property-card.bad {
    border: 1.5px solid #FF6262;
}

.property-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.property-name {
    font-size: 19px;
    font-weight: 850;
    color: #19345C;
}

.property-city {
    font-size: 12px;
    color: #7B8BA2;
    margin-top: 5px;
}

.property-profit {
    font-size: 18px;
    font-weight: 850;
}

.property-profit.good {
    color: #00A878;
}

.property-profit.bad {
    color: #F04438;
}

.accumulated {
    font-size: 9px;
    color: #91A0B3;
    margin-top: 3px;
    text-align: right;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 17px;
}

.metric-box {
    background: #F5F7F9;
    border-radius: 11px;
    padding: 9px 8px;
}

.metric-label {
    font-size: 10px;
    color: #7B8BA2;
}

.metric-value {
    font-size: 14px;
    font-weight: 850;
    margin-top: 5px;
}

.metric-value.income {
    color: #009B70;
}

.metric-value.expense {
    color: #F04438;
}

.metric-value.flow {
    color: #0877C9;
}

.metric-average {
    font-size: 8px;
    color: #91A0B3;
    margin-top: 3px;
}

.profit-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
}

.profit-label {
    font-size: 11px;
    color: #7B8BA2;
}

.progress-bg {
    height: 7px;
    border-radius: 10px;
    background: #E7ECF1;
    margin-top: 7px;
    overflow: hidden;
}

.progress-good {
    height: 100%;
    background: #00A878;
    border-radius: 10px;
}

.progress-bad {
    height: 100%;
    background: #FF4A4A;
    border-radius: 10px;
}

.target-good,
.target-bad {
    font-size: 10px;
    font-weight: 700;
    margin-top: 7px;
}

.target-good {
    color: #009A6C;
}

.target-bad {
    color: #E53B24;
}

.occupancy-box {
    background: #F5F7F9;
    border-radius: 12px;
    padding: 10px 11px;
    margin-top: 11px;
}

.occupancy-title {
    font-size: 10px;
    color: #7B8BA2;
}

.occupancy-value {
    font-size: 16px;
    font-weight: 850;
    color: #7256E8;
    margin-top: 4px;
}

.occupancy-detail {
    font-size: 9px;
    color: #91A0B3;
    margin-top: 3px;
}

/* =========================
   TABLA
   ========================= */

.table-card {
    background: white;
    border: 1px solid #DCE5EE;
    border-radius: 18px;
    padding: 16px;
    margin-top: 18px;
}

.table-title {
    font-size: 19px;
    font-weight: 800;
    color: #19345C;
    margin-bottom: 12px;
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

def dinero(valor):
    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


def dinero_corto(valor):
    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"${valor/1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"${valor/1_000:.0f}k"

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
# RESERVAS AIRBNB
# ============================================================

@st.cache_data(ttl=300)
def cargar_reservas(fecha_inicio, fecha_fin):

    query = """
    WITH mapa AS (

        SELECT
            LOWER(TRIM(Anuncio)) AS anuncio_key,
            Nombre AS Nombre_Propiedad,
            Ciudad

        FROM
            `rentascamacho.rentas_cortas.Participaciones`

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

        FROM
            `rentascamacho.rentas_cortas.Airbnb_Prorrateado`

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
                DATE_ADD(@fecha_fin, INTERVAL 1 DAY)
            ) AS Fin_Overlap

        FROM reservas

        WHERE
            Fecha_Inicio < DATE_ADD(
                @fecha_fin,
                INTERVAL 1 DAY
            )

            AND Fecha_Fin > @fecha_inicio
    )

    SELECT

        Nombre_Propiedad,
        Ciudad,

        COUNT(DISTINCT Codigo_Reserva) AS Reservas,

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

inicio_anio = pd.Timestamp(
    hoy.year,
    1,
    1
)

inicio_mes = date(
    hoy.year,
    hoy.month,
    1
)

fin_hoy = pd.Timestamp(hoy) + pd.Timedelta(days=1)


# ============================================================
# YTD
# ============================================================

df_ytd = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < fin_hoy)
].copy()

ingresos_ytd = df_ytd["Ingreso"].sum()
gastos_ytd = df_ytd["Gasto"].sum()

flujo_ytd = ingresos_ytd - gastos_ytd

rentabilidad_ytd = (
    flujo_ytd / ingresos_ytd * 100
    if ingresos_ytd != 0
    else 0
)


# ============================================================
# GRÁFICO INGRESO MENSUAL
# ============================================================

df_anio = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < fin_hoy)
].copy()

df_anio["Mes"] = df_anio["Fecha"].dt.month

mensual = (
    df_anio
    .groupby("Mes", as_index=False)["Ingreso"]
    .sum()
)

meses = list(range(1, hoy.month + 1))

mensual = (
    pd.DataFrame({"Mes": meses})
    .merge(mensual, on="Mes", how="left")
    .fillna(0)
)

max_ingreso = mensual["Ingreso"].max()

if max_ingreso > 0:
    mensual["altura"] = (
        mensual["Ingreso"] / max_ingreso * 32
    )
else:
    mensual["altura"] = 4


barras_ingreso = ""

for _, row in mensual.iterrows():

    altura = max(
        3,
        min(
            32,
            float(row["altura"])
        )
    )

    barras_ingreso += (
        f'<div class="mini-bar" '
        f'style="height:{altura:.0f}px;"></div>'
    )


# ============================================================
# FILTROS
# ============================================================

f1, f2, f3, f4, f5 = st.columns(
    [1.55, 0.82, 0.82, 0.95, 1.05],
    gap="small"
)

with f1:

    st.markdown(
        """
        <div class="brand-card">
            <div class="logo-box">🏢</div>
            <div>
                <div class="brand-title">
                    Airbnb <span class="brand-title-red">Financial Hub</span>
                </div>
                <div class="brand-sub">
                    Rentabilidad financiera · Solo Airbnb
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with f2:

    st.markdown(
        """
        <div class="chart-button">
            <div>
                <span class="chart-button-icon">📊</span>
                <span class="chart-button-title">Ingreso mensual</span>
            </div>
            <span class="chart-arrow">⌄</span>
        </div>
        """,
        unsafe_allow_html=True
    )


with f3:

    st.markdown(
        """
        <div class="chart-button">
            <div>
                <span class="chart-button-icon">🏢</span>
                <span class="chart-button-title">Ingresos propiedad</span>
            </div>
            <span class="chart-arrow">⌄</span>
        </div>
        """,
        unsafe_allow_html=True
    )


with f4:

    st.markdown(
        '<div class="filter-title">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .astype(str)
        .unique()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades,
        label_visibility="collapsed"
    )


with f5:

    st.markdown(
        '<div class="filter-title">🏢 Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades,
        label_visibility="collapsed"
    )


# Fecha en fila compacta debajo de propiedad/ciudad
c_fecha = st.columns([3.05, 1.05])[1]

with c_fecha:

    st.markdown(
        '<div class="filter-title">📅 Período</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Período",
        value=(inicio_mes, hoy),
        label_visibility="collapsed"
    )


if isinstance(periodo, tuple) and len(periodo) == 2:

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


# ============================================================
# KPIs + NAVEGACIÓN
# ============================================================

ingresos = df_f["Ingreso"].sum()
gastos = df_f["Gasto"].sum()

flujo = ingresos - gastos

rentabilidad = (
    flujo / ingresos * 100
    if ingresos != 0
    else 0
)

k1, k2, k3, n1, n2, n3 = st.columns(
    [1, 1, 1, 0.95, 0.95, 0.95],
    gap="small"
)


with k1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">INGRESOS 2026</div>
            <div class="kpi-value">{dinero_corto(ingresos_ytd)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">FLUJO 2026</div>
            <div class="kpi-value green">
                {dinero_corto(flujo_ytd)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with k3:

    color = (
        "#009B70"
        if rentabilidad_ytd >= 35
        else "#E94332"
    )

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">RENTABILIDAD 2026</div>
            <div class="kpi-value" style="color:{color};">
                {rentabilidad_ytd:.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with n1:

    st.markdown(
        """
        <div class="nav-card">
            <div class="nav-card-text">🏢 Propiedades</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with n2:

    st.markdown(
        """
        <div class="nav-card">
            <div class="nav-card-text">💰 Financiero</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with n3:

    st.markdown(
        """
        <div class="nav-card">
            <div class="nav-card-text">📊 Ocupación</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    """
    <div class="portfolio-title">
        🏢 Tu portafolio
    </div>
    <div class="portfolio-subtitle">
        Desempeño financiero de tus propiedades Airbnb en el período seleccionado.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RESUMEN PROPIEDADES
# ============================================================

resumen = (
    df_f
    .groupby(
        ["Nombre_Propiedad", "Ciudad"],
        as_index=False
    )
    .agg(
        Ingresos=("Ingreso", "sum"),
        Gastos=("Gasto", "sum")
    )
)

resumen["Flujo"] = (
    resumen["Ingresos"] -
    resumen["Gastos"]
)

resumen["Rentabilidad"] = resumen.apply(
    lambda x:
        x["Flujo"] / x["Ingresos"] * 100
        if x["Ingresos"] != 0
        else 0,
    axis=1
)


# ============================================================
# PROMEDIOS MENSUALES
# ============================================================

meses_cerrados = max(
    hoy.month - 1,
    0
)

inicio_mes_actual = pd.Timestamp(
    hoy.year,
    hoy.month,
    1
)

df_cerrado = df[
    (df["Fecha"] >= inicio_anio) &
    (df["Fecha"] < inicio_mes_actual)
].copy()


if meses_cerrados > 0:

    promedios = (
        df_cerrado
        .groupby(
            ["Nombre_Propiedad", "Ciudad"],
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
        promedios["Ingreso_Promedio"] -
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

try:

    df_ocupacion = cargar_reservas(
        fecha_inicio,
        fecha_fin
    )

except Exception:

    df_ocupacion = pd.DataFrame(
        columns=[
            "Nombre_Propiedad",
            "Ciudad",
            "Reservas",
            "Noches_Reservadas",
            "Noches_Disponibles"
        ]
    )


if not df_ocupacion.empty:

    df_ocupacion[
        "Ocupacion_Porcentaje"
    ] = (
        df_ocupacion["Noches_Reservadas"]
        /
        df_ocupacion["Noches_Disponibles"]
        * 100
    )


resumen = resumen.merge(
    df_ocupacion,
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
# TARJETAS DE PROPIEDADES
# ============================================================

for inicio in range(
    0,
    len(resumen),
    3
):

    fila = resumen.iloc[
        inicio:inicio + 3
    ]

    cols = st.columns(
        3,
        gap="small"
    )

    for col, (_, row) in zip(
        cols,
        fila.iterrows()
    ):

        rent = float(
            row["Rentabilidad"]
        )

        es_buena = rent >= 35

        card_class = (
            ""
            if es_buena
            else "bad"
        )

        profit_class = (
            "good"
            if es_buena
            else "bad"
        )

        progress = min(
            max(rent, 0),
            100
        )

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

        ocupacion = row.get(
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

        ocupacion_txt = (
            "—"
            if pd.isna(ocupacion)
            else f"{float(ocupacion):.1f}%"
        )

        reservas_txt = (
            "—"
            if pd.isna(reservas)
            else f"{int(reservas)} reservas"
        )

        noches_txt = (
            "—"
            if pd.isna(noches)
            else f"{int(noches)} noches"
        )

        objetivo = (
            "✓ Sobre objetivo"
            if es_buena
            else "⚠ Bajo objetivo"
        )

        objetivo_class = (
            "target-good"
            if es_buena
            else "target-bad"
        )

        html_card = f"""
<div class="property-card {card_class}">

    <div class="property-header">

        <div>

            <div class="property-name">
                {row["Nombre_Propiedad"]}
            </div>

            <div class="property-city">
                📍 {row["Ciudad"]}
            </div>

        </div>

        <div>

            <div class="property-profit {profit_class}">
                {rent:.1f}%
            </div>

            <div class="accumulated">
                Rentabilidad
            </div>

        </div>

    </div>


    <div class="metric-grid">

        <div class="metric-box">

            <div class="metric-label">
                Ingresos
            </div>

            <div class="metric-value income">
                {dinero_corto(row["Ingresos"])}
            </div>

            <div class="metric-average">
                {dinero_corto(ingreso_prom)}/mes
            </div>

        </div>


        <div class="metric-box">

            <div class="metric-label">
                Gastos
            </div>

            <div class="metric-value expense">
                {dinero_corto(row["Gastos"])}
            </div>

            <div class="metric-average">
                {dinero_corto(gasto_prom)}/mes
            </div>

        </div>


        <div class="metric-box">

            <div class="metric-label">
                Flujo
            </div>

            <div class="metric-value flow">
                {dinero_corto(row["Flujo"])}
            </div>

            <div class="metric-average">
                {dinero_corto(flujo_prom)}/mes
            </div>

        </div>

    </div>


    <div class="profit-row">

        <div class="profit-label">
            Rentabilidad
        </div>

        <div class="property-profit {profit_class}">
            {rent:.1f}%
        </div>

    </div>


    <div class="progress-bg">

        <div
            class="progress-{'good' if es_buena else 'bad'}"
            style="width:{progress:.1f}%;">
        </div>

    </div>


    <div class="{objetivo_class}">
        {objetivo}
    </div>


    <div class="occupancy-box">

        <div class="occupancy-title">
            Ocupación Airbnb
        </div>

        <div class="occupancy-value">
            {ocupacion_txt}
        </div>

        <div class="occupancy-detail">
            {reservas_txt} · {noches_txt}
        </div>

    </div>

</div>
"""

        with col:

            st.markdown(
                html_card,
                unsafe_allow_html=True
            )


# ============================================================
# COMPARATIVO
# ============================================================

st.markdown(
    """
    <div class="table-card">
        <div class="table-title">
            📋 Comparativo del portafolio
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


tabla = resumen[
    [
        "Nombre_Propiedad",
        "Ciudad",
        "Ingresos",
        "Gastos",
        "Flujo",
        "Rentabilidad",
        "Ocupacion_Porcentaje"
    ]
].copy()


tabla.columns = [
    "Propiedad",
    "Ciudad",
    "Ingresos",
    "Gastos",
    "Flujo",
    "Rentabilidad",
    "Ocupación"
]


tabla["Ingresos"] = tabla["Ingresos"].apply(
    dinero_corto
)

tabla["Gastos"] = tabla["Gastos"].apply(
    dinero_corto
)

tabla["Flujo"] = tabla["Flujo"].apply(
    dinero_corto
)

tabla["Rentabilidad"] = tabla[
    "Rentabilidad"
].apply(
    lambda x: f"{x:.1f}%"
)

tabla["Ocupación"] = tabla[
    "Ocupación"
].apply(
    lambda x:
        "—"
        if pd.isna(x)
        else f"{x:.1f}%"
)


st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True
)
