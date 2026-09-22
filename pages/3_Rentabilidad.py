import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GENERAL
    ======================================================== */

    .stApp {
        background: #F4F7FA;
    }

    .block-container {
        max-width: 1500px !important;
        padding-top: 0.4rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2.8rem !important;
        padding-right: 2.8rem !important;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ========================================================
       HEADER SUPERIOR DE STREAMLIT
    ======================================================== */

    header[data-testid="stHeader"] {
        height: 42px !important;
        min-height: 42px !important;
        background: white !important;
        border-bottom: 1px solid #E8EDF2 !important;
    }

    header[data-testid="stHeader"] > div {
        height: 42px !important;
    }

    div[data-testid="stToolbar"] {
        height: 42px !important;
    }

    div[data-testid="stDecoration"] {
        display: none !important;
    }


    /* ========================================================
       TITULOS
    ======================================================== */

    .hub-title {
        font-size: 26px;
        font-weight: 850;
        line-height: 1.05;
        color: #17345E;
        margin: 0;
    }

    .hub-title-red {
        color: #FF3155;
    }

    .hub-subtitle {
        font-size: 11px;
        color: #8290A4;
        margin-top: 6px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 850;
        color: #17345E;
        margin-top: 12px;
        margin-bottom: 2px;
    }

    .section-subtitle {
        font-size: 11px;
        color: #8290A4;
        margin-bottom: 9px;
    }


    /* ========================================================
       LOGO
    ======================================================== */

    .logo-box {
        width: 58px;
        height: 58px;
        background: #FF214B;
        border-radius: 15px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 31px;
    }


    /* ========================================================
       ETIQUETAS FILTROS
    ======================================================== */

    .filter-label {
        font-size: 10px;
        font-weight: 800;
        color: #71839A;
        margin-bottom: 3px;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        display: none !important;
    }

    div[data-baseweb="select"] > div {
        background: #F1F4F7 !important;
        border: 1px solid #E0E6EC !important;
        border-radius: 9px !important;
        min-height: 37px !important;
        height: 37px !important;
    }

    div[data-baseweb="select"] span {
        font-size: 12px !important;
        color: #374151 !important;
    }

    div[data-testid="stDateInput"] > div {
        background: #F1F4F7 !important;
        border: 1px solid #E0E6EC !important;
        border-radius: 9px !important;
        min-height: 37px !important;
        height: 37px !important;
    }

    div[data-testid="stDateInput"] input {
        font-size: 12px !important;
        color: #374151 !important;
    }


    /* ========================================================
       BOTONES NAVEGACIÓN
    ======================================================== */

    div.stButton > button {
        height: 76px !important;
        min-height: 76px !important;

        border: 1px solid #DCE5EE !important;
        border-radius: 13px !important;

        background: white !important;

        color: #50637B !important;

        font-size: 15px !important;
        font-weight: 750 !important;
    }

    div.stButton > button:hover {
        border-color: #17345E !important;
        color: #17345E !important;
        background: #F8FAFC !important;
    }


    /* ========================================================
       TARJETAS GENERALES
    ======================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #DCE5EE !important;
        border-radius: 14px !important;
        background: white !important;
    }


    /* ========================================================
       KPI
    ======================================================== */

    .kpi-label {
        font-size: 10px;
        font-weight: 800;
        color: #8290A4;
        margin-bottom: 6px;
    }

    .kpi-number {
        font-size: 28px;
        font-weight: 850;
        line-height: 1;
        color: #17345E;
    }

    .kpi-number-green {
        color: #009B70;
    }

    .kpi-number-red {
        color: #E84235;
    }

    .kpi-description {
        font-size: 9px;
        color: #8A98AA;
        margin-top: 8px;
    }


    /* ========================================================
       PROPIEDAD
    ======================================================== */

    .property-title {
        font-size: 18px;
        font-weight: 850;
        color: #17345E;
        line-height: 1.1;
    }

    .property-city {
        font-size: 10px;
        color: #8290A4;
        margin-top: 4px;
    }

    .property-profit {
        font-size: 20px;
        font-weight: 850;
        text-align: right;
    }

    .property-profit-label {
        font-size: 8px;
        color: #9AA5B4;
        text-align: right;
        margin-top: 3px;
    }

    .good {
        color: #009B70;
    }

    .bad {
        color: #E84235;
    }


    /* ========================================================
       METRICAS INTERNAS
    ======================================================== */

    .metric-title {
        font-size: 9px;
        color: #8290A4;
    }

    .metric-number {
        font-size: 16px;
        font-weight: 850;
        margin-top: 4px;
    }

    .income {
        color: #009B70;
    }

    .expense {
        color: #EF4338;
    }

    .flow {
        color: #0878D2;
    }


    /* ========================================================
       OCUPACIÓN
    ======================================================== */

    .occupancy-title {
        font-size: 9px;
        color: #8290A4;
    }

    .occupancy-number {
        font-size: 18px;
        font-weight: 850;
        color: #6954E6;
    }

    .occupancy-detail {
        font-size: 9px;
        color: #96A1AF;
        margin-top: 3px;
    }


    /* ========================================================
       TEXTO PEQUEÑO
    ======================================================== */

    .mini-text {
        font-size: 9px;
        color: #8A98AA;
    }


    /* ========================================================
       PORTAFOLIO
    ======================================================== */

    .portfolio-title {
        font-size: 20px;
        font-weight: 850;
        color: white;
    }

    .portfolio-subtitle {
        font-size: 9px;
        color: #B9C8DA;
        margin-top: 3px;
    }

    .portfolio-main {
        font-size: 32px;
        font-weight: 850;
        color: white;
        margin-top: 18px;
    }

    .portfolio-label {
        font-size: 9px;
        color: #B9C8DA;
    }

    .portfolio-small-label {
        font-size: 9px;
        color: #B9C8DA;
    }

    .portfolio-small-number {
        font-size: 17px;
        font-weight: 800;
        color: white;
    }

    .portfolio-small-number.green {
        color: #52D7B0;
    }


    /* ========================================================
       SEPARACIÓN
    ======================================================== */

    .tight-space {
        height: 5px;
    }


    /* ========================================================
       POPOVER
    ======================================================== */

    div[data-testid="stPopover"] {
        width: 100%;
    }

    div[data-testid="stPopover"] button {
        height: 76px !important;
        min-height: 76px !important;

        width: 100% !important;

        background: white !important;

        border: 1px solid #DCE5EE !important;

        border-radius: 13px !important;

        color: #50637B !important;

        font-size: 14px !important;
        font-weight: 750 !important;

        text-align: left !important;
    }


    /* ========================================================
       RESPONSIVE
    ======================================================== */

    @media (max-width: 1100px) {

        .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


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


def dinero_completo(valor):

    if pd.isna(valor):
        valor = 0

    return f"${float(valor):,.0f}".replace(",", ".")


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
    FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    WHERE LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
    """

    resultado = client.query(query).to_dataframe()

    resultado["Fecha"] = pd.to_datetime(
        resultado["Fecha"],
        errors="coerce"
    )

    resultado["Ingreso"] = pd.to_numeric(
        resultado["Ingreso"],
        errors="coerce"
    ).fillna(0)

    resultado["Gasto"] = pd.to_numeric(
        resultado["Gasto"],
        errors="coerce"
    ).fillna(0)

    resultado["Nombre_Propiedad"] = (
        resultado["Nombre_Propiedad"]
        .fillna("Sin información")
        .astype(str)
    )

    resultado["Ciudad"] = (
        resultado["Ciudad"]
        .fillna("Sin información")
        .astype(str)
    )

    resultado["Nombre_Socio"] = (
        resultado["Nombre_Socio"]
        .fillna("Sin información")
        .astype(str)
    )

    return resultado


# ============================================================
# RESERVAS AIRBNB
# ============================================================

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

fin_hoy = pd.Timestamp(hoy) + pd.Timedelta(days=1)


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
    ingresos_ytd -
    gastos_ytd
)

rentabilidad_ytd = (
    flujo_ytd / ingresos_ytd * 100
    if ingresos_ytd != 0
    else 0
)


# ============================================================
# FILA 1
# MARCA + GRÁFICOS + FILTROS
# ============================================================

c1, c2, c3, c4, c5, c6 = st.columns(
    [
        1.65,
        0.95,
        0.95,
        1.00,
        1.00,
        1.35
    ],
    gap="small"
)


# ============================================================
# MARCA
# ============================================================

with c1:

    with st.container(border=True):

        logo, marca = st.columns(
            [0.35, 1],
            vertical_alignment="center"
        )

        with logo:

            st.markdown(
                '<div class="logo-box">🏢</div>',
                unsafe_allow_html=True
            )

        with marca:

            st.markdown(
                """
                <div class="hub-title">
                    Airbnb <span class="hub-title-red">
                    Financial Hub
                    </span>
                </div>

                <div class="hub-subtitle">
                    Rentabilidad financiera · Solo Airbnb
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# GRÁFICO MENSUAL
# ============================================================

with c2:

    mensual = (
        df_ytd
        .assign(
            Mes_Num=df_ytd["Fecha"].dt.month
        )
        .groupby(
            "Mes_Num",
            as_index=False
        )
        .agg(
            Ingresos=("Ingreso", "sum")
        )
        .sort_values("Mes_Num")
    )

    nombres_meses = {
        1: "Ene",
        2: "Feb",
        3: "Mar",
        4: "Abr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dic"
    }

    mensual["Mes"] = (
        mensual["Mes_Num"]
        .map(nombres_meses)
    )

    mensual["Acumulado"] = (
        mensual["Ingresos"]
        .cumsum()
    )

    with st.popover(
        "📊  Ingreso mensual",
        use_container_width=True
    ):

        st.subheader(
            "Ingreso mensual"
        )

        st.caption(
            "Barras = ingreso mensual · "
            "Línea = acumulado 2026"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=mensual["Mes"],
                y=mensual["Ingresos"],
                name="Ingreso",
                marker_color="#27B68D"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=mensual["Mes"],
                y=mensual["Acumulado"],
                name="Acumulado",
                mode="lines+markers",
                line=dict(
                    color="#17345E",
                    width=3
                ),
                marker=dict(size=7),
                yaxis="y2"
            )
        )

        fig.update_layout(
            height=380,
            margin=dict(
                l=45,
                r=45,
                t=25,
                b=45
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                showgrid=False
            ),
            yaxis=dict(
                tickprefix="$",
                tickformat=",.0f",
                gridcolor="#E8EDF2"
            ),
            yaxis2=dict(
                overlaying="y",
                side="right",
                showgrid=False,
                tickprefix="$",
                tickformat=",.0f"
            ),
            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


# ============================================================
# GRÁFICO PROPIEDADES
# ============================================================

with c3:

    propiedades_grafico = (
        df_ytd
        .groupby(
            "Nombre_Propiedad",
            as_index=False
        )
        .agg(
            Ingresos=("Ingreso", "sum")
        )
        .sort_values(
            "Ingresos",
            ascending=False
        )
    )

    promedio = (
        propiedades_grafico["Ingresos"].mean()
        if not propiedades_grafico.empty
        else 0
    )

    with st.popover(
        "🏢  Ingresos propiedad",
        use_container_width=True
    ):

        st.subheader(
            "Ingresos por propiedad"
        )

        st.caption(
            "Barras = ingresos · "
            "Línea = promedio"
        )

        fig2 = go.Figure()

        fig2.add_trace(
            go.Bar(
                x=propiedades_grafico[
                    "Nombre_Propiedad"
                ],
                y=propiedades_grafico[
                    "Ingresos"
                ],
                name="Ingresos",
                marker_color="#7965D9"
            )
        )

        fig2.add_trace(
            go.Scatter(
                x=propiedades_grafico[
                    "Nombre_Propiedad"
                ],
                y=[
                    promedio
                ] * len(
                    propiedades_grafico
                ),
                name="Promedio",
                mode="lines",
                line=dict(
                    color="#EF4338",
                    width=3,
                    dash="dash"
                )
            )
        )

        fig2.update_layout(
            height=380,
            margin=dict(
                l=45,
                r=25,
                t=25,
                b=100
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                showgrid=False,
                tickangle=-35
            ),
            yaxis=dict(
                tickprefix="$",
                tickformat=",.0f",
                gridcolor="#E8EDF2"
            ),
            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


# ============================================================
# FILTRO CIUDAD
# ============================================================

with c4:

    st.markdown(
        '<div class="filter-label">📍 Ciudad</div>',
        unsafe_allow_html=True
    )

    ciudad = st.selectbox(
        "Ciudad",
        [
            "Todas"
        ]
        +
        sorted(
            df["Ciudad"]
            .dropna()
            .unique()
            .tolist()
        ),
        label_visibility="collapsed"
    )


# ============================================================
# FILTRO PROPIEDAD
# ============================================================

with c5:

    st.markdown(
        '<div class="filter-label">🏢 Propiedad</div>',
        unsafe_allow_html=True
    )

    propiedad = st.selectbox(
        "Propiedad",
        [
            "Todas"
        ]
        +
        sorted(
            df["Nombre_Propiedad"]
            .dropna()
            .unique()
            .tolist()
        ),
        label_visibility="collapsed"
    )


# ============================================================
# FILTRO FECHA
# ============================================================

with c6:

    st.markdown(
        '<div class="filter-label">📅 Período</div>',
        unsafe_allow_html=True
    )

    periodo = st.date_input(
        "Período",
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
    isinstance(periodo, (tuple, list))
    and len(periodo) == 2
):

    fecha_inicio = periodo[0]
    fecha_fin = periodo[1]

else:

    fecha_inicio = inicio_mes
    fecha_fin = hoy


# ============================================================
# FILTRAR DATOS
# ============================================================

df_f = df[
    (df["Fecha"].dt.date >= fecha_inicio)
    &
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
# TOTALES
# ============================================================

ingresos = df_f["Ingreso"].sum()

gastos = df_f["Gasto"].sum()

flujo = ingresos - gastos

rentabilidad = (
    flujo / ingresos * 100
    if ingresos != 0
    else 0
)


# ============================================================
# RESUMEN PROPIEDADES
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
        Ingresos=("Ingreso", "sum"),
        Gastos=("Gasto", "sum")
    )
)

resumen["Flujo"] = (
    resumen["Ingresos"]
    -
    resumen["Gastos"]
)

resumen["Rentabilidad"] = (
    resumen["Flujo"]
    /
    resumen["Ingresos"]
    *
    100
).fillna(0)


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
        df_ocupacion["Noches_Reservadas"]
        /
        df_ocupacion["Noches_Disponibles"]
        *
        100
    )

    resumen = resumen.merge(
        df_ocupacion,
        on=[
            "Nombre_Propiedad",
            "Ciudad"
        ],
        how="left"
    )

else:

    resumen["Ocupacion"] = None
    resumen["Reservas"] = None
    resumen["Noches_Reservadas"] = None


# ============================================================
# ORDEN
# ============================================================

resumen = (
    resumen
    .sort_values(
        "Rentabilidad",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# ESTADO NAVEGACIÓN
# ============================================================

if "vista_airbnb" not in st.session_state:

    st.session_state.vista_airbnb = "Propiedades"


# ============================================================
# FILA INDICADORES + NAVEGACIÓN
# ============================================================

r1, r2, r3, r4, r5, r6 = st.columns(
    [
        1.05,
        1.05,
        1.05,
        1,
        1,
        1
    ],
    gap="small"
)


# ============================================================
# INDICADOR INGRESOS
# ============================================================

with r1:

    with st.container(border=True):

        st.markdown(
            '<div class="kpi-label">INGRESOS 2026</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="kpi-number">{dinero_corto(ingresos_ytd)}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# INDICADOR FLUJO
# ============================================================

with r2:

    with st.container(border=True):

        st.markdown(
            '<div class="kpi-label">FLUJO 2026</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="kpi-number kpi-number-green">{dinero_corto(flujo_ytd)}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# INDICADOR RENTABILIDAD
# ============================================================

with r3:

    with st.container(border=True):

        st.markdown(
            '<div class="kpi-label">RENTABILIDAD 2026</div>',
            unsafe_allow_html=True
        )

        color = (
            "kpi-number-green"
            if rentabilidad_ytd >= 35
            else "kpi-number-red"
        )

        st.markdown(
            f'<div class="kpi-number {color}">{rentabilidad_ytd:.1f}%</div>',
            unsafe_allow_html=True
        )


# ============================================================
# NAVEGACIÓN PROPIEDADES
# ============================================================

with r4:

    if st.button(
        "🏢  Propiedades",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Propiedades"

        st.rerun()


# ============================================================
# NAVEGACIÓN FINANCIERO
# ============================================================

with r5:

    if st.button(
        "💰  Financiero",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Financiero"

        st.rerun()


# ============================================================
# NAVEGACIÓN OCUPACIÓN
# ============================================================

with r6:

    if st.button(
        "📊  Ocupación",
        use_container_width=True
    ):

        st.session_state.vista_airbnb = "Ocupación"

        st.rerun()


# ============================================================
# VISTA PROPIEDADES
# ============================================================

if st.session_state.vista_airbnb == "Propiedades":

    st.markdown(
        """
        <div class="section-title">
            🏢 Tu portafolio
        </div>

        <div class="section-subtitle">
            Desempeño financiero de tus propiedades Airbnb
            en el período seleccionado.
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # KPI PERÍODO
    # ========================================================

    k1, k2, k3, k4 = st.columns(
        4,
        gap="small"
    )


    with k1:

        with st.container(border=True):

            st.markdown(
                '<div class="kpi-label">INGRESOS</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="kpi-number">{dinero_corto(ingresos)}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="kpi-description">Ingresos registrados</div>',
                unsafe_allow_html=True
            )


    with k2:

        with st.container(border=True):

            st.markdown(
                '<div class="kpi-label">GASTOS OPERATIVOS</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="kpi-number">{dinero_corto(gastos)}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="kpi-description">Egresos registrados</div>',
                unsafe_allow_html=True
            )


    with k3:

        with st.container(border=True):

            st.markdown(
                '<div class="kpi-label">FLUJO</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="kpi-number kpi-number-green">{dinero_corto(flujo)}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="kpi-description">Ingresos − gastos</div>',
                unsafe_allow_html=True
            )


    with k4:

        with st.container(border=True):

            st.markdown(
                '<div class="kpi-label">RENTABILIDAD</div>',
                unsafe_allow_html=True
            )

            color = (
                "kpi-number-green"
                if rentabilidad >= 35
                else "kpi-number-red"
            )

            st.markdown(
                f'<div class="kpi-number {color}">{rentabilidad:.1f}%</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="kpi-description">Objetivo: 35%</div>',
                unsafe_allow_html=True
            )


    # ========================================================
    # PROPIEDADES - 4 POR FILA
    # ========================================================

    propiedades = list(
        resumen.iterrows()
    )


    for inicio in range(
        0,
        len(propiedades),
        4
    ):

        grupo = propiedades[
            inicio:inicio + 4
        ]

        columnas = st.columns(
            4,
            gap="small"
        )


        for columna, (_, row) in zip(
            columnas,
            grupo
        ):

            with columna:

                with st.container(
                    border=True
                ):

                    # ----------------------------------------
                    # CABECERA
                    # ----------------------------------------

                    h1, h2 = st.columns(
                        [1.7, 0.8],
                        vertical_alignment="top"
                    )

                    with h1:

                        st.markdown(
                            f"""
                            <div class="property-title">
                                {row["Nombre_Propiedad"]}
                            </div>

                            <div class="property-city">
                                📍 {row["Ciudad"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with h2:

                        rent = float(
                            row["Rentabilidad"]
                        )

                        clase = (
                            "good"
                            if rent >= 35
                            else "bad"
                        )

                        st.markdown(
                            f"""
                            <div class="property-profit {clase}">
                                {rent:.1f}%
                            </div>

                            <div class="property-profit-label">
                                Rentabilidad
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    st.write("")


                    # ----------------------------------------
                    # MÉTRICAS
                    # ----------------------------------------

                    m1, m2, m3 = st.columns(
                        3,
                        gap="small"
                    )


                    with m1:

                        st.markdown(
                            '<div class="metric-title">Ingresos</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="metric-number income">{dinero_corto(row["Ingresos"])}</div>',
                            unsafe_allow_html=True
                        )


                    with m2:

                        st.markdown(
                            '<div class="metric-title">Gastos</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="metric-number expense">{dinero_corto(row["Gastos"])}</div>',
                            unsafe_allow_html=True
                        )


                    with m3:

                        st.markdown(
                            '<div class="metric-title">Flujo</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="metric-number flow">{dinero_corto(row["Flujo"])}</div>',
                            unsafe_allow_html=True
                        )


                    st.write("")


                    # ----------------------------------------
                    # RENTABILIDAD
                    # ----------------------------------------

                    p1, p2 = st.columns(
                        [1.4, 0.6]
                    )

                    with p1:

                        st.markdown(
                            '<div class="mini-text">Rentabilidad</div>',
                            unsafe_allow_html=True
                        )

                    with p2:

                        st.markdown(
                            f"""
                            <div style="
                                text-align:right;
                                font-size:13px;
                                font-weight:850;
                                color:{'#009B70' if rent >= 35 else '#E84235'};
                            ">
                                {rent:.1f}%
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    progreso = min(
                        max(rent, 0),
                        100
                    )


                    st.progress(
                        progreso / 100
                    )


                    # ----------------------------------------
                    # OCUPACIÓN
                    # ----------------------------------------

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


                    o1, o2 = st.columns(
                        [1.3, 0.7]
                    )


                    with o1:

                        st.markdown(
                            '<div class="occupancy-title">Ocupación Airbnb</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f'<div class="occupancy-detail">{detalle}</div>',
                            unsafe_allow_html=True
                        )


                    with o2:

                        st.markdown(
                            f"""
                            <div style="
                                text-align:right;
                                font-size:18px;
                                font-weight:850;
                                color:#6954E6;
                            ">
                                {ocup_text}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


    # ========================================================
    # PORTAFOLIO + TOP INGRESOS
    # ========================================================

    st.write("")

    p1, p2 = st.columns(
        [1.3, 1],
        gap="small"
    )


    with p1:

        with st.container(border=True):

            st.markdown(
                """
                <div class="portfolio-title"
                     style="color:#17345E;">
                    🏢 Portafolio
                </div>

                <div class="portfolio-subtitle"
                     style="color:#8290A4;">
                    Todas las propiedades seleccionadas
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="
                    font-size:32px;
                    font-weight:850;
                    color:#17345E;
                    margin-top:12px;
                ">
                    {dinero_corto(ingresos)}
                </div>

                <div class="portfolio-label">
                    Ingresos del período
                </div>
                """,
                unsafe_allow_html=True
            )


            a1, a2, a3 = st.columns(3)


            with a1:

                st.markdown(
                    '<div class="mini-text">Gastos</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="metric-number expense">{dinero_corto(gastos)}</div>',
                    unsafe_allow_html=True
                )


            with a2:

                st.markdown(
                    '<div class="mini-text">Flujo</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="metric-number flow">{dinero_corto(flujo)}</div>',
                    unsafe_allow_html=True
                )


            with a3:

                st.markdown(
                    '<div class="mini-text">Rentabilidad</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="metric-number income">{rentabilidad:.1f}%</div>',
                    unsafe_allow_html=True
                )


    with p2:

        with st.container(border=True):

            st.markdown(
                """
                <div class="portfolio-title"
                     style="color:#17345E;">
                    🏆 Top por ingresos
                </div>

                <div class="portfolio-subtitle"
                     style="color:#8290A4;">
                    Período seleccionado
                </div>
                """,
                unsafe_allow_html=True
            )


            ranking = (
                resumen
                .sort_values(
                    "Ingresos",
                    ascending=False
                )
                .head(5)
            )


            max_ingreso = (
                ranking["Ingresos"].max()
                if not ranking.empty
                else 1
            )


            for _, row in ranking.iterrows():

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        margin-top:8px;
                    ">

                        <div style="
                            width:105px;
                            font-size:9px;
                            color:#66788F;
                            white-space:nowrap;
                            overflow:hidden;
                            text-overflow:ellipsis;
                        ">
                            {row["Nombre_Propiedad"]}
                        </div>

                        <div style="
                            flex:1;
                            height:8px;
                            background:#EDF0F4;
                            border-radius:8px;
                            overflow:hidden;
                        ">

                            <div style="
                                width:{
                                    (
                                        row["Ingresos"]
                                        /
                                        max_ingreso
                                        *
                                        100
                                    )
                                    if max_ingreso
                                    else 0
                                }%;
                                height:100%;
                                background:#7964DD;
                                border-radius:8px;
                            "></div>

                        </div>

                        <div style="
                            width:45px;
                            text-align:right;
                            font-size:9px;
                            color:#66788F;
                        ">
                            {dinero_corto(row["Ingresos"])}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# VISTA FINANCIERO
# ============================================================

elif st.session_state.vista_airbnb == "Financiero":

    st.markdown(
        """
        <div class="section-title">
            💰 Financiero
        </div>

        <div class="section-subtitle">
            Evolución mensual de ingresos, gastos y flujo.
        </div>
        """,
        unsafe_allow_html=True
    )


    financiero = df[
        (df["Fecha"] >= inicio_anio)
        &
        (df["Fecha"] < fin_hoy)
    ].copy()


    financiero["Mes_Num"] = (
        financiero["Fecha"].dt.month
    )

    financiero["Mes"] = (
        financiero["Fecha"]
        .dt.strftime("%b")
    )


    mensual_fin = (
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


    mensual_fin["Flujo"] = (
        mensual_fin["Ingresos"]
        -
        mensual_fin["Gastos"]
    )


    fig_fin = go.Figure()


    fig_fin.add_trace(
        go.Bar(
            x=mensual_fin["Mes"],
            y=mensual_fin["Ingresos"],
            name="Ingresos",
            marker_color="#27B68D"
        )
    )


    fig_fin.add_trace(
        go.Bar(
            x=mensual_fin["Mes"],
            y=mensual_fin["Gastos"],
            name="Gastos",
            marker_color="#EF4338"
        )
    )


    fig_fin.add_trace(
        go.Scatter(
            x=mensual_fin["Mes"],
            y=mensual_fin["Flujo"],
            name="Flujo",
            mode="lines+markers",
            line=dict(
                color="#17345E",
                width=3
            )
        )
    )


    fig_fin.update_layout(
        height=470,
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
            l=50,
            r=30,
            t=40,
            b=40
        ),
        yaxis=dict(
            tickprefix="$",
            tickformat=",.0f",
            gridcolor="#E8EDF2"
        ),
        xaxis=dict(
            showgrid=False
        )
    )


    st.plotly_chart(
        fig_fin,
        use_container_width=True
    )


# ============================================================
# VISTA OCUPACIÓN
# ============================================================

elif st.session_state.vista_airbnb == "Ocupación":

    st.markdown(
        """
        <div class="section-title">
            📊 Ocupación Airbnb
        </div>

        <div class="section-subtitle">
            Reservas y noches ocupadas durante el período.
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
            ocupacion["Noches_Reservadas"]
            /
            ocupacion["Noches_Disponibles"]
            *
            100
        )


        total_reservas = (
            ocupacion["Reservas"].sum()
        )

        total_noches = (
            ocupacion["Noches_Reservadas"].sum()
        )

        total_disponibles = (
            ocupacion["Noches_Disponibles"].sum()
        )

        ocupacion_total = (
            total_noches
            /
            total_disponibles
            *
            100
            if total_disponibles
            else 0
        )


        a, b, c = st.columns(
            3,
            gap="small"
        )


        with a:

            with st.container(border=True):

                st.markdown(
                    '<div class="kpi-label">OCUPACIÓN PORTAFOLIO</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="kpi-number"
                         style="color:#6954E6;">
                        {ocupacion_total:.1f}%
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        with b:

            with st.container(border=True):

                st.markdown(
                    '<div class="kpi-label">RESERVAS</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="kpi-number">
                        {int(total_reservas)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        with c:

            with st.container(border=True):

                st.markdown(
                    '<div class="kpi-label">NOCHES RESERVADAS</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="kpi-number">
                        {int(total_noches)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        st.write("")


        # ====================================================
        # OCUPACIÓN POR PROPIEDAD
        # ====================================================

        filas = list(
            ocupacion.iterrows()
        )


        for inicio in range(
            0,
            len(filas),
            4
        ):

            grupo = filas[
                inicio:inicio + 4
            ]

            columnas = st.columns(
                4,
                gap="small"
            )


            for columna, (_, row) in zip(
                columnas,
                grupo
            ):

                with columna:

                    with st.container(
                        border=True
                    ):

                        porcentaje = float(
                            row["Ocupacion"]
                        )


                        h1, h2 = st.columns(
                            [1.7, 0.8]
                        )


                        with h1:

                            st.markdown(
                                f"""
                                <div class="property-title">
                                    {row["Nombre_Propiedad"]}
                                </div>

                                <div class="property-city">
                                    📍 {row["Ciudad"]}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                        with h2:

                            st.markdown(
                                f"""
                                <div class="property-profit"
                                     style="color:#6954E6;">
                                    {porcentaje:.1f}%
                                </div>

                                <div class="property-profit-label">
                                    Ocupación
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                        st.write("")


                        st.markdown(
                            '<div class="metric-title">NOCHES RESERVADAS</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"""
                            <div style="
                                font-size:26px;
                                font-weight:850;
                                color:#17345E;
                            ">
                                {int(row["Noches_Reservadas"])}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        st.progress(
                            min(
                                max(
                                    porcentaje / 100,
                                    0
                                ),
                                1
                            )
                        )


                        st.markdown(
                            f"""
                            <div class="occupancy-detail">
                                {int(row["Reservas"])} reservas ·
                                {int(row["Noches_Disponibles"])}
                                noches disponibles
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
