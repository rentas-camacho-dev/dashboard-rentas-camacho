import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import html

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

st.markdown("""
<style>

    /* ========================================================
       GENERAL
    ======================================================== */

    .stApp {
        background-color: #F5F7FA;
    }

    .block-container {
        max-width: 100%;
        padding-top: 0.75rem;
        padding-bottom: 0.8rem;
        padding-left: 1.15rem;
        padding-right: 1.15rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }


    /* ========================================================
       TÍTULOS
    ======================================================== */

    .main-title {
        font-size: 30px;
        font-weight: 750;
        color: #172B4D;
        line-height: 1.1;
        margin-bottom: 3px;
    }

    .subtitle {
        font-size: 14px;
        color: #6B778C;
        margin-bottom: 12px;
    }

    .section-title {
        font-size: 19px;
        font-weight: 750;
        color: #172B4D;
        margin-top: 11px;
        margin-bottom: 7px;
    }

    .section-subtitle {
        font-size: 12px;
        color: #6B778C;
        margin-top: -4px;
        margin-bottom: 8px;
    }


    /* ========================================================
       FILTROS
    ======================================================== */

    .filter-box {
        background: white;
        border: 1px solid #E4E8ED;
        border-radius: 14px;
        padding: 7px 10px 2px 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,.025);
        margin-bottom: 10px;
    }


    /* ========================================================
       KPIs
    ======================================================== */

    .kpi-card {
        background: white;
        border: 1px solid #E3E7EC;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,.035);
        min-height: 105px;
    }

    .kpi-title {
        font-size: 12px;
        color: #6B778C;
        margin-bottom: 5px;
    }

    .kpi-value {
        font-size: 27px;
        font-weight: 750;
        line-height: 1.15;
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


    /* ========================================================
       MINI METRICS
    ======================================================== */

    .mini-card {
        background: white;
        border: 1px solid #E4E8ED;
        border-radius: 12px;
        padding: 11px 14px;
        min-height: 70px;
    }

    .mini-label {
        color: #6B778C;
        font-size: 11px;
        margin-bottom: 3px;
    }

    .mini-value {
        color: #172B4D;
        font-size: 18px;
        font-weight: 700;
    }


    /* ========================================================
       SELECTORES
    ======================================================== */

    div[data-baseweb="select"] {
        border-radius: 8px;
    }

    div[data-baseweb="input"] {
        border-radius: 8px;
    }

    label {
        font-size: 12px !important;
        color: #344563 !important;
    }


    /* ========================================================
       DOWNLOAD BUTTON
    ======================================================== */

    .stDownloadButton button {
        border-radius: 8px;
        border: 1px solid #D7DEE7;
        background: white;
        color: #172B4D;
        font-size: 12px;
        padding: 5px 11px;
    }


    /* ========================================================
       DATAFRAME DETALLE
    ======================================================== */

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* ========================================================
       BOTONES STREAMLIT
    ======================================================== */

    .stButton button {
        border-radius: 8px;
    }


    /* ========================================================
       SEPARACIÓN
    ======================================================== */

    hr {
        border-color: #E6E9EF;
        margin: 8px 0;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# BIGQUERY
# ============================================================

QUERY = """
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


@st.cache_data(ttl=300, show_spinner=False)
def cargar_datos():

    credentials = (
        service_account.Credentials
        .from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
        )
    )

    client = bigquery.Client(
        credentials=credentials,
        project="rentascamacho"
    )

    datos = client.query(
        QUERY
    ).to_dataframe()

    return datos


with st.spinner("Cargando información de Airbnb..."):
    df = cargar_datos()


# ============================================================
# PREPARACIÓN
# ============================================================

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

for columna in columnas_numericas:

    df[columna] = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).fillna(0)

df = df.dropna(
    subset=["Fecha"]
)


# ============================================================
# FUNCIONES
# ============================================================

def formato_moneda(valor):

    return (
        f"${valor:,.0f}"
        .replace(",", ".")
    )


def formato_compacto(valor):

    valor = float(valor)

    signo = "-" if valor < 0 else ""
    valor_abs = abs(valor)

    if valor_abs >= 1_000_000_000:

        return (
            f"{signo}$ {valor_abs / 1_000_000_000:.1f} B"
        )

    if valor_abs >= 1_000_000:

        return (
            f"{signo}$ {valor_abs / 1_000_000:.1f} M"
        )

    if valor_abs >= 1_000:

        return (
            f"{signo}$ {valor_abs / 1_000:.0f} mil"
        )

    return (
        f"{signo}${valor_abs:,.0f}"
        .replace(",", ".")
    )


def estado_porcentaje(porcentaje):

    if porcentaje >= 0.80:
        return "🏆"

    if porcentaje >= 0.50:
        return "⚡"

    return "🚩"


def color_delta(valor):

    if valor > 0:
        return "#00875A"

    if valor < 0:
        return "#DE350B"

    return "#6B778C"


def porcentaje_cambio(actual, anterior):

    if anterior == 0:
        return None

    return (
        (actual - anterior)
        / abs(anterior)
    )


# ============================================================
# ENCABEZADO
# ============================================================

fecha_max_global = df["Fecha"].max()

fecha_texto = (
    fecha_max_global
    .strftime("%d %b %Y")
    if not pd.isna(fecha_max_global)
    else "—"
)

header_col1, header_col2 = st.columns(
    [2.4, 1]
)

with header_col1:

    st.markdown(
        '<div class="main-title">🏠 Rentas Cortas — Airbnb</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Ingresos, gastos y rentabilidad de tus propiedades</div>',
        unsafe_allow_html=True
    )


with header_col2:

    st.markdown(
        f"""
        <div style="
            text-align:right;
            padding-top:5px;
            font-size:11px;
            color:#6B778C;">
            Último dato disponible
        </div>
        <div style="
            text-align:right;
            color:#172B4D;
            font-size:13px;
            font-weight:600;">
            📅 {fecha_texto}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Filtros</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(
    [1, 1, 1, 1]
)


with col1:

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .astype(str)
        .unique()
    )

    ciudad_seleccionada = st.multiselect(
        "Ciudad",
        ciudades,
        placeholder="Todas"
    )


with col2:

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
    )

    propiedad_seleccionada = st.multiselect(
        "Propiedad",
        propiedades,
        placeholder="Todas"
    )


with col3:

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .astype(str)
        .unique()
    )

    socio_seleccionado = st.multiselect(
        "Socio",
        socios,
        placeholder="Todos"
    )


with col4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    rango_fecha = st.date_input(
        "Fecha",
        value=(
            fecha_min,
            fecha_max
        ),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# FILTROS BASE
# ============================================================

df_graficos = df.copy()


if ciudad_seleccionada:

    df_graficos = df_graficos[
        df_graficos["Ciudad"]
        .astype(str)
        .isin(
            ciudad_seleccionada
        )
    ]


if propiedad_seleccionada:

    df_graficos = df_graficos[
        df_graficos[
            "Nombre_Propiedad"
        ]
        .astype(str)
        .isin(
            propiedad_seleccionada
        )
    ]


if socio_seleccionado:

    df_graficos = df_graficos[
        df_graficos[
            "Nombre_Socio"
        ]
        .astype(str)
        .isin(
            socio_seleccionado
        )
    ]


# ============================================================
# FECHA
# ============================================================

df_filtrado = df_graficos.copy()

if (
    isinstance(rango_fecha, tuple)
    and len(rango_fecha) == 2
):

    fecha_inicio = pd.Timestamp(
        rango_fecha[0]
    )

    fecha_fin = (
        pd.Timestamp(
            rango_fecha[1]
        )
        + pd.Timedelta(days=1)
    )

    df_filtrado = df_filtrado[
        (
            df_filtrado["Fecha"]
            >= fecha_inicio
        )
        &
        (
            df_filtrado["Fecha"]
            < fecha_fin
        )
    ]


# ============================================================
# PERIODO ANTERIOR
# ============================================================

delta_income = None
delta_expense = None
delta_flow = None
delta_profit = None

if (
    isinstance(rango_fecha, tuple)
    and len(rango_fecha) == 2
):

    inicio_periodo = pd.Timestamp(
        rango_fecha[0]
    )

    fin_periodo = pd.Timestamp(
        rango_fecha[1]
    )

    dias_periodo = (
        fin_periodo -
        inicio_periodo
    ).days + 1

    fin_anterior = (
        inicio_periodo
        - pd.Timedelta(days=1)
    )

    inicio_anterior = (
        fin_anterior
        - pd.Timedelta(days=dias_periodo - 1)
    )

    df_anterior = df_graficos[
        (
            df_graficos["Fecha"]
            >= inicio_anterior
        )
        &
        (
            df_graficos["Fecha"]
            <= fin_anterior
        )
    ]

    if (
        not df_anterior.empty
        and inicio_anterior >= df["Fecha"].min()
    ):

        ingreso_actual = (
            df_filtrado["Ingreso"].sum()
        )

        ingreso_anterior = (
            df_anterior["Ingreso"].sum()
        )

        gasto_actual = (
            df_filtrado["Gasto"].sum()
        )

        gasto_anterior = (
            df_anterior["Gasto"].sum()
        )

        flujo_actual = (
            ingreso_actual -
            gasto_actual
        )

        flujo_anterior = (
            ingreso_anterior -
            gasto_anterior
        )

        rent_actual = (
            flujo_actual /
            ingreso_actual
            if ingreso_actual != 0
            else 0
        )

        rent_anterior = (
            flujo_anterior /
            ingreso_anterior
            if ingreso_anterior != 0
            else 0
        )

        delta_income = porcentaje_cambio(
            ingreso_actual,
            ingreso_anterior
        )

        delta_expense = porcentaje_cambio(
            gasto_actual,
            gasto_anterior
        )

        delta_flow = porcentaje_cambio(
            flujo_actual,
            flujo_anterior
        )

        delta_profit = (
            rent_actual -
            rent_anterior
        )


# ============================================================
# KPIs
# ============================================================

ingreso_total = (
    df_filtrado["Ingreso"].sum()
)

gasto_total = (
    df_filtrado["Gasto"].sum()
)

flujo_total = (
    ingreso_total -
    gasto_total
)

rentabilidad = (
    flujo_total /
    ingreso_total
    if ingreso_total != 0
    else 0
)


k1, k2, k3, k4 = st.columns(4)


def render_kpi(
    titulo,
    valor,
    clase,
    delta=None,
    pp=False
):

    delta_html = ""

    if delta is not None:

        if pp:

            texto_delta = (
                f"{delta * 100:+.1f} pp"
            )

        else:

            texto_delta = (
                f"{delta * 100:+.1f}%"
            )

        flecha = (
            "↑"
            if delta >= 0
            else
            "↓"
        )

        delta_html = f"""
        <div style="
            margin-top:7px;
            font-size:11px;
            color:{color_delta(delta)};">
            {flecha} {texto_delta}
            <span style="color:#97A0AF;">
                vs periodo anterior
            </span>
        </div>
        """

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                {titulo}
            </div>

            <div class="kpi-value {clase}">
                {valor}
            </div>

            {delta_html}

        </div>
        """,
        unsafe_allow_html=True
    )


with k1:

    render_kpi(
        "Ingreso Total",
        formato_moneda(
            ingreso_total
        ),
        "kpi-green",
        delta_income
    )


with k2:

    render_kpi(
        "Gasto Total",
        formato_moneda(
            gasto_total
        ),
        "kpi-red",
        delta_expense
    )


with k3:

    render_kpi(
        "Flujo",
        formato_moneda(
            flujo_total
        ),
        "kpi-blue",
        delta_flow
    )


with k4:

    render_kpi(
        "Rentabilidad",
        f"{rentabilidad:.1%}",
        "kpi-purple",
        delta_profit,
        pp=True
    )


# ============================================================
# TABLA + GASTOS
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.55, 1],
    gap="medium"
)


# ============================================================
# RESUMEN POR PROPIEDAD
# ============================================================

with col_tabla:

    st.markdown(
        '<div class="section-title">🏢 Resumen por propiedad</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Desempeño financiero por propiedad en el periodo seleccionado</div>',
        unsafe_allow_html=True
    )

    if not df_filtrado.empty:

        resumen_propiedad = (
            df_filtrado
            .groupby(
                "Nombre_Propiedad",
                dropna=False
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
            .reset_index()
        )

        resumen_propiedad[
            "Flujo"
        ] = (
            resumen_propiedad[
                "Ingreso"
            ]
            -
            resumen_propiedad[
                "Gasto"
            ]
        )

        resumen_propiedad[
            "%"
        ] = resumen_propiedad.apply(
            lambda row:
            (
                row["Flujo"] /
                row["Ingreso"]
            )
            if row["Ingreso"] != 0
            else 0,
            axis=1
        )

        resumen_propiedad = (
            resumen_propiedad
            .sort_values(
                "Ingreso",
                ascending=False
            )
        )


        # ====================================================
        # HTML TABLA
        # ====================================================

        html_tabla = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                padding: 0;
                background: transparent;
                font-family:
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }

            .card {
                width: 100%;
                background: white;
                border: 1px solid #E1E5EA;
                border-radius: 13px;
                overflow: hidden;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }

            thead th {
                background: #008577;
                color: white;
                padding: 10px 10px;
                font-size: 12px;
                font-weight: 700;
                text-align: left;
            }

            thead th:nth-child(1) {
                width: 24%;
            }

            thead th:nth-child(2),
            thead th:nth-child(3),
            thead th:nth-child(4) {
                width: 15%;
                text-align: right;
            }

            thead th:nth-child(5) {
                width: 22%;
                text-align: right;
            }

            thead th:nth-child(6) {
                width: 9%;
                text-align: center;
            }

            tbody td {
                padding: 9px 10px;
                border-bottom: 1px solid #EDF0F2;
                font-size: 12px;
                color: #172B4D;
                vertical-align: middle;
            }

            tbody tr:last-child td {
                border-bottom: none;
            }

            .property {
                font-weight: 600;
            }

            .num {
                text-align: right;
                white-space: nowrap;
            }

            .income {
                color: #00875A;
                font-weight: 600;
            }

            .expense {
                color: #DE350B;
                font-weight: 600;
            }

            .positive {
                color: #00875A;
                font-weight: 700;
            }

            .negative {
                color: #DE350B;
                font-weight: 700;
            }

            .pct-box {
                width: 100%;
            }

            .pct-row {
                display: flex;
                justify-content: flex-end;
                margin-bottom: 3px;
                font-size: 11px;
                font-weight: 600;
            }

            .bar-bg {
                width: 100%;
                height: 7px;
                background: #EDF1F5;
                border-radius: 4px;
                overflow: hidden;
            }

            .bar-fill {
                height: 100%;
                background: #16B5D1;
                border-radius: 4px;
            }

            .status {
                text-align: center;
                font-size: 17px;
            }

            .total td {
                background: #F8FAFC;
                border-top: 2px solid #DCE3EA;
                font-weight: 700;
            }

        </style>
        </head>

        <body>

        <div class="card">

        <table>

        <thead>
        <tr>
            <th>Propiedad</th>
            <th>Ingreso</th>
            <th>Gasto</th>
            <th>Flujo</th>
            <th>%</th>
            <th>Estado</th>
        </tr>
        </thead>

        <tbody>
        """


        # ====================================================
        # FILAS
        # ====================================================

        for _, row in resumen_propiedad.iterrows():

            nombre = html.escape(
                str(
                    row["Nombre_Propiedad"]
                )
            )

            ingreso = float(
                row["Ingreso"]
            )

            gasto = float(
                row["Gasto"]
            )

            flujo = float(
                row["Flujo"]
            )

            pct = float(
                row["%"]
            )

            pct_width = min(
                max(
                    pct * 100,
                    0
                ),
                100
            )

            estado = estado_porcentaje(
                pct
            )

            flujo_class = (
                "positive"
                if flujo >= 0
                else
                "negative"
            )


            html_tabla += f"""
            <tr>

                <td class="property">
                    {nombre}
                </td>

                <td class="num income">
                    {formato_compacto(ingreso)}
                </td>

                <td class="num expense">
                    {formato_compacto(gasto)}
                </td>

                <td class="num {flujo_class}">
                    {formato_compacto(flujo)}
                </td>

                <td class="num">

                    <div class="pct-box">

                        <div class="pct-row">
                            {pct:.1%}
                        </div>

                        <div class="bar-bg">

                            <div
                                class="bar-fill"
                                style="
                                    width:{pct_width}%;
                                ">
                            </div>

                        </div>

                    </div>

                </td>

                <td class="status">
                    {estado}
                </td>

            </tr>
            """


        # ====================================================
        # TOTAL
        # ====================================================

        total_ingreso = (
            resumen_propiedad[
                "Ingreso"
            ].sum()
        )

        total_gasto = (
            resumen_propiedad[
                "Gasto"
            ].sum()
        )

        total_flujo = (
            resumen_propiedad[
                "Flujo"
            ].sum()
        )

        total_pct = (
            total_flujo /
            total_ingreso
            if total_ingreso != 0
            else 0
        )

        total_pct_width = min(
            max(
                total_pct * 100,
                0
            ),
            100
        )

        total_estado = (
            estado_porcentaje(
                total_pct
            )
        )


        html_tabla += f"""
        <tr class="total">

            <td>
                Total
            </td>

            <td class="num income">
                {formato_compacto(total_ingreso)}
            </td>

            <td class="num expense">
                {formato_compacto(total_gasto)}
            </td>

            <td class="num positive">
                {formato_compacto(total_flujo)}
            </td>

            <td class="num">

                <div class="pct-box">

                    <div class="pct-row">
                        {total_pct:.1%}
                    </div>

                    <div class="bar-bg">
                        <div
                            class="bar-fill"
                            style="
                                width:{total_pct_width}%;
                            ">
                        </div>
                    </div>

                </div>

            </td>

            <td class="status">
                {total_estado}
            </td>

        </tr>

        </tbody>

        </table>

        </div>

        </body>
        </html>
        """


        altura_tabla = (
            48
            +
            (
                len(
                    resumen_propiedad
                )
                * 49
            )
            +
            49
        )

        components.html(
            html_tabla,
            height=min(
                max(
                    altura_tabla,
                    180
                ),
                650
            ),
            scrolling=False
        )


        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        csv_propiedades = (
            resumen_propiedad
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )

        st.download_button(
            "⬇️ Exportar resumen",
            data=csv_propiedades,
            file_name="resumen_propiedades.csv",
            mime="text/csv",
            key="download_propiedades"
        )

    else:

        st.info(
            "No hay datos para los filtros seleccionados."
        )


# ============================================================
# DISTRIBUCIÓN DE GASTOS
# ============================================================

with col_gastos:

    st.markdown(
        '<div class="section-title">💸 Distribución de gastos</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Desglose por subcategoría en el periodo seleccionado</div>',
        unsafe_allow_html=True
    )


    gastos_subcategoria = (
        df_filtrado[
            df_filtrado["Gasto"] > 0
        ]
        .groupby(
            "Nombre_Subcategoria"
        )["Gasto"]
        .sum()
        .reset_index()
        .sort_values(
            "Gasto",
            ascending=False
        )
    )


    if not gastos_subcategoria.empty:

        gasto_total_grafico = (
            gastos_subcategoria[
                "Gasto"
            ].sum()
        )


        # ====================================================
        # TOP 7 + OTROS
        # ====================================================

        top_n = 7

        if (
            len(gastos_subcategoria)
            > top_n
        ):

            principales = (
                gastos_subcategoria
                .head(top_n)
                .copy()
            )

            otros_valor = (
                gastos_subcategoria
                .iloc[top_n:]["Gasto"]
                .sum()
            )

            otros = pd.DataFrame(
                {
                    "Nombre_Subcategoria": [
                        "Otros"
                    ],

                    "Gasto": [
                        otros_valor
                    ]
                }
            )

            gastos_pie = pd.concat(
                [
                    principales,
                    otros
                ],
                ignore_index=True
            )

        else:

            gastos_pie = (
                gastos_subcategoria
                .copy()
            )


        # ====================================================
        # MAYOR GASTO
        # ====================================================

        mayor = (
            gastos_pie.iloc[0]
        )

        mayor_categoria = str(
            mayor[
                "Nombre_Subcategoria"
            ]
        )

        mayor_valor = float(
            mayor["Gasto"]
        )

        mayor_pct = (
            mayor_valor /
            gasto_total_grafico
            if gasto_total_grafico != 0
            else 0
        )


        # ====================================================
        # COLORES
        # ====================================================

        colores = [
            "#D9232E",
            "#ED1C24",
            "#E83B5A",
            "#F05A66",
            "#F57A87",
            "#F99BA5",
            "#F7BDC3",
            "#EAD5D8"
        ]


        # ====================================================
        # DONA
        # ====================================================

        fig_gastos = go.Figure()

        fig_gastos.add_trace(
            go.Pie(
                labels=gastos_pie[
                    "Nombre_Subcategoria"
                ],
                values=gastos_pie[
                    "Gasto"
                ],
                hole=0.64,
                sort=False,
                direction="clockwise",
                textinfo="none",
                marker=dict(
                    colors=colores[
                        :len(gastos_pie)
                    ],
                    line=dict(
                        color="white",
                        width=3
                    )
                ),
                hovertemplate=
                "<b>%{label}</b><br>"
                "$%{value:,.0f}<br>"
                "%{percent}"
                "<extra></extra>"
            )
        )


        fig_gastos.add_annotation(
            x=0.5,
            y=0.55,
            text=f"<b>{mayor_pct:.1%}</b>",
            showarrow=False,
            font=dict(
                size=19,
                color="#172B4D"
            )
        )

        fig_gastos.add_annotation(
            x=0.5,
            y=0.43,
            text=html.escape(
                mayor_categoria
            ),
            showarrow=False,
            font=dict(
                size=10,
                color="#7A869A"
            )
        )

        fig_gastos.update_layout(
            height=285,
            margin=dict(
                l=0,
                r=0,
                t=2,
                b=2
            ),
            showlegend=False,
            template="plotly_white"
        )


        dona_col, lista_col = st.columns(
            [0.93, 1.07],
            gap="small"
        )


        # ====================================================
        # DONA
        # ====================================================

        with dona_col:

            st.plotly_chart(
                fig_gastos,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


        # ====================================================
        # LISTA
        # ====================================================

        with lista_col:

            html_gastos = """
            <!DOCTYPE html>
            <html>

            <head>

            <style>

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    background: transparent;
                    font-family:
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        Arial,
                        sans-serif;
                }

                .box {
                    background: white;
                    border: 1px solid #E1E5EA;
                    border-radius: 12px;
                    padding: 10px 12px;
                }

                .total {
                    font-size: 16px;
                    font-weight: 700;
                    color: #172B4D;
                    margin-bottom: 2px;
                }

                .caption {
                    font-size: 11px;
                    color: #7A869A;
                    margin-bottom: 7px;
                }

                .row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #F0F2F4;
                    padding: 5px 0;
                    gap: 8px;
                }

                .row:last-child {
                    border-bottom: none;
                }

                .left {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    color: #344563;
                    font-size: 11px;
                    min-width: 0;
                }

                .dot {
                    width: 8px;
                    height: 8px;
                    min-width: 8px;
                    border-radius: 50%;
                }

                .name {
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                }

                .right {
                    white-space: nowrap;
                    color: #172B4D;
                    font-size: 11px;
                    font-weight: 600;
                }

                .pct {
                    color: #7A869A;
                    margin-left: 5px;
                    font-weight: 400;
                }

                .highlight {
                    background: #F5F9FF;
                    border-radius: 6px;
                    padding: 3px 4px;
                }

            </style>

            </head>

            <body>

            <div class="box">

            <div class="total">
            """


            html_gastos += (
                formato_moneda(
                    gasto_total_grafico
                )
            )


            html_gastos += """
            </div>

            <div class="caption">
                Total de egresos operativos
            </div>
            """


            for i, (_, row) in enumerate(
                gastos_pie.iterrows()
            ):

                categoria = html.escape(
                    str(
                        row[
                            "Nombre_Subcategoria"
                        ]
                    )
                )

                valor = float(
                    row["Gasto"]
                )

                pct = (
                    valor /
                    gasto_total_grafico
                )

                highlight = (
                    "highlight"
                    if i == 0
                    else ""
                )


                html_gastos += f"""

                <div class="row {highlight}">

                    <div class="left">

                        <span
                            class="dot"
                            style="
                                background:
                                {colores[i]};
                            ">
                        </span>

                        <span class="name">
                            {categoria}
                        </span>

                    </div>

                    <div class="right">

                        {formato_compacto(valor)}

                        <span class="pct">
                            {pct:.1%}
                        </span>

                    </div>

                </div>
                """


            html_gastos += """
            </div>

            </body>
            </html>
            """


            components.html(
                html_gastos,
                height=300,
                scrolling=False
            )


# ============================================================
# ANÁLISIS ANUAL
# ============================================================

st.markdown(
    '<div class="section-title">📊 Análisis anual</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Comparación mensual y desempeño promedio de las propiedades</div>',
    unsafe_allow_html=True
)


# ============================================================
# SELECTOR AÑO
# ============================================================

años_disponibles = sorted(
    df["Fecha"]
    .dropna()
    .dt.year
    .unique(),
    reverse=True
)


if años_disponibles:

    año_actual_sistema = (
        pd.Timestamp.now().year
    )

    if (
        año_actual_sistema
        in años_disponibles
    ):

        año_default = (
            año_actual_sistema
        )

    else:

        año_default = (
            años_disponibles[0]
        )


    indice_default = (
        años_disponibles.index(
            año_default
        )
    )


    año_seleccionado = st.selectbox(
        "Año de análisis",
        años_disponibles,
        index=indice_default
    )


    año_anterior = (
        año_seleccionado -
        1
    )


    # ========================================================
    # DATOS AÑO
    # ========================================================

    datos_año = df_graficos[
        df_graficos[
            "Fecha"
        ].dt.year
        ==
        año_seleccionado
    ].copy()


    datos_año_anterior = (
        df_graficos[
            df_graficos[
                "Fecha"
            ].dt.year
            ==
            año_anterior
        ]
        .copy()
    )


    # ========================================================
    # CORTE
    # ========================================================

    if not datos_año.empty:

        fecha_corte_anual = (
            datos_año[
                "Fecha"
            ].max()
        )

        mes_corte_anual = (
            fecha_corte_anual.month
        )

    else:

        mes_corte_anual = 12


    # ========================================================
    # INGRESOS MENSUALES
    # ========================================================

    ingresos_actual = (
        datos_año
        .groupby(
            datos_año[
                "Fecha"
            ].dt.month
        )["Ingreso"]
        .sum()
    )


    ingresos_anterior = (
        datos_año_anterior
        .groupby(
            datos_año_anterior[
                "Fecha"
            ].dt.month
        )["Ingreso"]
        .sum()
    )


    meses_nombres = {
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


    comparacion_mensual = []


    for mes in range(
        1,
        mes_corte_anual + 1
    ):

        ingreso_actual_mes = float(
            ingresos_actual.get(
                mes,
                0
            )
        )

        ingreso_anterior_mes = float(
            ingresos_anterior.get(
                mes,
                0
            )
        )


        comparacion_mensual.append(
            {
                "Mes":
                    meses_nombres[mes],

                str(
                    año_seleccionado
                ):
                    ingreso_actual_mes,

                str(
                    año_anterior
                ):
                    ingreso_anterior_mes
            }
        )


    df_comparacion = (
        pd.DataFrame(
            comparacion_mensual
        )
    )


    # ========================================================
    # GRÁFICO MENSUAL
    # ========================================================

    fig_mensual = go.Figure()


    fig_mensual.add_trace(
        go.Bar(
            x=df_comparacion[
                "Mes"
            ],

            y=df_comparacion[
                str(
                    año_seleccionado
                )
            ],

            name=str(
                año_seleccionado
            ),

            marker_color="#00875A",

            opacity=0.88,

            hovertemplate=
            f"<b>{año_seleccionado}</b><br>"
            "%{x}<br>"
            "$%{y:,.0f}"
            "<extra></extra>"
        )
    )


    fig_mensual.add_trace(
        go.Scatter(
            x=df_comparacion[
                "Mes"
            ],

            y=df_comparacion[
                str(
                    año_anterior
                )
            ],

            name=str(
                año_anterior
            ),

            mode="lines+markers",

            line=dict(
                color="#1565C0",
                width=3
            ),

            marker=dict(
                size=6
            ),

            hovertemplate=
            f"<b>{año_anterior}</b><br>"
            "%{x}<br>"
            "$%{y:,.0f}"
            "<extra></extra>"
        )
    )


    fig_mensual.update_layout(
        height=300,

        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5
        ),

        template="plotly_white",

        hovermode="x unified",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="center",
            x=0.5
        ),

        xaxis=dict(
            title=None,
            showgrid=False
        ),

        yaxis=dict(
            title=None,
            tickformat=",.0f",
            gridcolor="#EAEAEA"
        ),

        bargap=0.18
    )


    # ========================================================
    # PROMEDIO POR PROPIEDAD
    # ========================================================

    datos_promedio = df_graficos[
        df_graficos[
            "Fecha"
        ].dt.year
        ==
        año_seleccionado
    ].copy()


    grafico_promedio = None
    promedio_propiedad = None


    if not datos_promedio.empty:

        promedio_propiedad = (
            datos_promedio
            .groupby(
                "Nombre_Propiedad"
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
            .reset_index()
        )


        promedio_propiedad[
            "Meses"
        ] = (

            (
                promedio_propiedad[
                    "Fecha_Fin"
                ].dt.year

                -

                promedio_propiedad[
                    "Fecha_Inicio"
                ].dt.year
            )
            * 12

            +

            (
                promedio_propiedad[
                    "Fecha_Fin"
                ].dt.month

                -

                promedio_propiedad[
                    "Fecha_Inicio"
                ].dt.month
            )

            + 1

        )


        promedio_propiedad[
            "Promedio_Mensual"
        ] = (

            promedio_propiedad[
                "Ingreso"
            ]

            /

            promedio_propiedad[
                "Meses"
            ]

        )


        promedio_propiedad = (
            promedio_propiedad
            .sort_values(
                "Promedio_Mensual",
                ascending=False
            )
        )


        # ====================================================
        # BARRA PROMEDIO
        # ====================================================

        grafico_promedio = go.Figure()


        grafico_promedio.add_trace(
            go.Bar(
                x=promedio_propiedad[
                    "Nombre_Propiedad"
                ],

                y=promedio_propiedad[
                    "Promedio_Mensual"
                ],

                marker_color="#6554C0",

                opacity=0.88,

                hovertemplate=
                "<b>%{x}</b><br>"
                "Promedio mensual: "
                "$%{y:,.0f}"
                "<extra></extra>"
            )
        )


        grafico_promedio.update_layout(
            height=300,

            margin=dict(
                l=5,
                r=5,
                t=10,
                b=5
            ),

            template="plotly_white",

            xaxis=dict(
                title=None,
                showgrid=False
            ),

            yaxis=dict(
                title=None,
                tickformat=",.0f",
                gridcolor="#EAEAEA"
            )
        )


    # ========================================================
    # GRÁFICAS LADO A LADO
    # ========================================================

    col_grafico1, col_grafico2 = st.columns(
        [1, 1],
        gap="medium"
    )


    with col_grafico1:

        st.markdown(
            f"**Ingresos {año_seleccionado} vs {año_anterior}**"
        )

        st.caption(
            "Barras = año seleccionado · "
            "Línea = año anterior"
        )

        st.plotly_chart(
            fig_mensual,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    with col_grafico2:

        st.markdown(
            f"**Promedio mensual por propiedad — {año_seleccionado}**"
        )

        st.caption(
            "Ingreso promedio mensual calculado "
            "sobre los meses con datos"
        )

        if grafico_promedio is not None:

            st.plotly_chart(
                grafico_promedio,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

        else:

            st.info(
                f"No hay datos para {año_seleccionado}."
            )


    # ========================================================
    # RESUMEN YTD
    # ========================================================

    total_actual = (
        df_comparacion[
            str(
                año_seleccionado
            )
        ].sum()
    )


    total_anterior = (
        df_comparacion[
            str(
                año_anterior
            )
        ].sum()
    )


    diferencia = (
        total_actual -
        total_anterior
    )


    st.markdown(
        "#### 💰 Resumen YTD"
    )


    y1, y2, y3 = st.columns(3)


    with y1:

        st.markdown(
            f"""
            <div class="mini-card">
                <div class="mini-label">
                    Ingresos {año_seleccionado}
                </div>

                <div class="mini-value">
                    {formato_moneda(total_actual)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with y2:

        st.markdown(
            f"""
            <div class="mini-card">
                <div class="mini-label">
                    Ingresos {año_anterior}
                </div>

                <div class="mini-value">
                    {formato_moneda(total_anterior)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with y3:

        color_diff = (
            "#00875A"
            if diferencia >= 0
            else
            "#DE350B"
        )

        st.markdown(
            f"""
            <div class="mini-card">

                <div class="mini-label">
                    Diferencia
                </div>

                <div class="mini-value"
                    style="color:{color_diff};">
                    {formato_moneda(diferencia)}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # TABLA PROMEDIO
    # ========================================================

    if promedio_propiedad is not None:

        st.markdown(
            f"#### 🏠 Detalle por propiedad — {año_seleccionado}"
        )


        tabla_promedio = (
            promedio_propiedad[
                [
                    "Nombre_Propiedad",
                    "Ingreso",
                    "Meses",
                    "Promedio_Mensual"
                ]
            ]
            .copy()
        )


        tabla_promedio = (
            tabla_promedio
            .rename(
                columns={
                    "Nombre_Propiedad":
                        "Propiedad",

                    "Ingreso":
                        "Ingreso Total",

                    "Meses":
                        "Meses con datos",

                    "Promedio_Mensual":
                        "Promedio Mensual"
                }
            )
        )


        tabla_promedio[
            "Ingreso Total"
        ] = (
            tabla_promedio[
                "Ingreso Total"
            ]
            .apply(
                formato_moneda
            )
        )


        tabla_promedio[
            "Promedio Mensual"
        ] = (
            tabla_promedio[
                "Promedio Mensual"
            ]
            .apply(
                formato_moneda
            )
        )


        st.dataframe(
            tabla_promedio,
            use_container_width=True,
            hide_index=True,
            height=250
        )


        csv_promedio = (
            tabla_promedio
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )


        st.download_button(
            "⬇️ Exportar detalle anual",
            data=csv_promedio,
            file_name=(
                f"detalle_promedio_{año_seleccionado}.csv"
            ),
            mime="text/csv",
            key="download_promedio"
        )


# ============================================================
# PIE DE DASHBOARD
# ============================================================

cantidad_propiedades = (
    df_filtrado[
        "Nombre_Propiedad"
    ]
    .nunique()
)

cantidad_socios = (
    df_filtrado[
        "Nombre_Socio"
    ]
    .nunique()
)


st.markdown("---")


f1, f2, f3, f4 = st.columns(4)


with f1:

    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-label">
                Flujo del periodo
            </div>
            <div class="mini-value"
                 style="color:#00875A;">
                {formato_compacto(flujo_total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with f2:

    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-label">
                Propiedades analizadas
            </div>
            <div class="mini-value">
                {cantidad_propiedades}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with f3:

    st.markdown(
        f"""
        <div class="mini-card">
            <div class="mini-label">
                Socios
            </div>
            <div class="mini-value">
                {cantidad_socios}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with f4:

    st.markdown(
        """
        <div class="mini-card">

            <div class="mini-label">
                Enfoque
            </div>

            <div class="mini-value"
                 style="
                    font-size:15px;
                    color:#52617A;">
                Más que propiedades,
                mejores decisiones.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )
