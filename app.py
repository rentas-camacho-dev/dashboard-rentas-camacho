# ============================================================
# pages/2_📊_Vista_Nueva.py
#
# RENTAS CORTAS — AIRBNB
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit.components.v1 as components
import html


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
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif !important;
}

.stApp {
    background: #F4F6F8;
}

.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}


/* ============================================================
   TÍTULO
   ============================================================ */

.main-title {
    color: #172B4D;
    font-size: 30px;
    font-weight: 600;
    line-height: 1.2;
    margin: 0 0 4px 0;
}

.main-subtitle {
    color: #6B778C;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.4;
    margin: 0 0 28px 0;
}


/* ============================================================
   TÍTULOS DE SECCIÓN
   ============================================================ */

.section-title {
    color: #172B4D;
    font-size: 22px;
    font-weight: 600;
    line-height: 1.2;
    margin: 0 0 5px 0;
}

.section-subtitle {
    color: #6B778C;
    font-size: 12px;
    font-weight: 400;
    line-height: 1.4;
    margin: 0 0 14px 0;
}


/* ============================================================
   FILTROS
   ============================================================ */

.filter-title {
    color: #172B4D;
    font-size: 22px;
    font-weight: 600;
    margin: 0 0 12px 0;
}

label {
    color: #52617A !important;
    font-size: 13px !important;
    font-weight: 400 !important;
}

div[data-baseweb="select"] > div {
    background: #EEF1F5;
    border: none;
    border-radius: 9px;
    min-height: 42px;
}

div[data-testid="stDateInput"] > div {
    background: #EEF1F5;
    border-radius: 9px;
}


/* ============================================================
   KPI NATIVOS
   ============================================================ */

div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DDE2E7;
    border-radius: 14px;
    padding: 16px 18px;
    min-height: 120px;
    box-shadow:
        0 2px 8px rgba(9,30,66,0.04);
}

div[data-testid="stMetricLabel"] {
    color: #52617A !important;
    font-size: 14px !important;
    font-weight: 400 !important;
}

div[data-testid="stMetricValue"] {
    color: #172B4D !important;
    font-size: 27px !important;
    font-weight: 500 !important;
}

div[data-testid="stMetricDelta"] {
    font-size: 12px !important;
    font-weight: 400 !important;
}


/* ============================================================
   ESPACIOS
   ============================================================ */

.section-space {
    height: 18px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CREDENCIALES BIGQUERY
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

def moneda(valor):

    if pd.isna(valor):
        valor = 0

    return f"${valor:,.0f}".replace(",", ".")


def compacto(valor):

    if pd.isna(valor):
        valor = 0

    valor = float(valor)

    signo = "-" if valor < 0 else ""

    valor_abs = abs(valor)

    if valor_abs >= 1_000_000_000:
        return f"{signo}$ {valor_abs / 1_000_000_000:.1f} B"

    elif valor_abs >= 1_000_000:
        return f"{signo}$ {valor_abs / 1_000_000:.1f} M"

    elif valor_abs >= 1_000:
        return f"{signo}$ {valor_abs / 1_000:.0f} mil"

    else:
        return f"{signo}$ {valor_abs:,.0f}"


def bandera(porcentaje):

    if pd.isna(porcentaje):
        return "🚩"

    porcentaje = float(porcentaje)

    if porcentaje >= 0.80:
        return "🏆"

    elif porcentaje >= 0.50:
        return "⚡"

    else:
        return "🚩"


def variacion(actual, anterior):

    if anterior == 0:

        if actual == 0:
            return 0

        return np.nan

    return (actual - anterior) / abs(anterior)


# ============================================================
# CARGAR DATOS
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

    FROM
        `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`

    WHERE
        LOWER(TRIM(Nombre_Tipo)) = 'airbnb'

    """

    return client.query(query).to_dataframe()


df = cargar_datos()


if df.empty:

    st.warning("No se encontraron datos de Airbnb.")

    st.stop()


# ============================================================
# LIMPIEZA
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
# TÍTULO PRINCIPAL
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🏠 Rentas Cortas — Airbnb
    </div>

    <div class="main-subtitle">
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


f1, f2, f3, f4 = st.columns(
    [1, 1, 1, 1],
    gap="medium"
)


with f1:

    ciudades = sorted(
        [
            x for x in
            df["Ciudad"]
            .dropna()
            .astype(str)
            .unique()
            if x.strip()
        ]
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades
    )


with f2:

    propiedades = sorted(
        [
            x for x in
            df["Nombre_Propiedad"]
            .dropna()
            .astype(str)
            .unique()
            if x.strip()
        ]
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades
    )


with f3:

    socios = sorted(
        [
            x for x in
            df["Nombre_Socio"]
            .dropna()
            .astype(str)
            .unique()
            if x.strip()
        ]
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios
    )


with f4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    fechas = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# FILTRO GENERAL
# ============================================================

df_graficos = df.copy()


if ciudad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Ciudad"]
        .astype(str)
        .eq(ciudad)
    ]


if propiedad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Nombre_Propiedad"]
        .astype(str)
        .eq(propiedad)
    ]


if socio != "Todos":

    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"]
        .astype(str)
        .eq(socio)
    ]


if isinstance(fechas, tuple) and len(fechas) == 2:

    fecha_inicio = pd.Timestamp(fechas[0])
    fecha_fin = pd.Timestamp(fechas[1])

else:

    fecha_inicio = pd.Timestamp(fecha_min)
    fecha_fin = pd.Timestamp(fecha_max)


df_filtrado = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio)
    &
    (df_graficos["Fecha"] <= fecha_fin)
].copy()


# ============================================================
# KPI
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()

gasto_total = df_filtrado["Gasto"].sum()

flujo_total = ingreso_total - gasto_total

rentabilidad = (
    flujo_total / ingreso_total
    if ingreso_total != 0
    else 0
)


# ============================================================
# PERIODO ANTERIOR
# ============================================================

dias_periodo = (
    fecha_fin - fecha_inicio
).days + 1


fecha_anterior_fin = (
    fecha_inicio -
    pd.Timedelta(days=1)
)


fecha_anterior_inicio = (
    fecha_anterior_fin -
    pd.Timedelta(days=dias_periodo - 1)
)


df_anterior = df_graficos[
    (df_graficos["Fecha"] >= fecha_anterior_inicio)
    &
    (df_graficos["Fecha"] <= fecha_anterior_fin)
]


ingreso_anterior = df_anterior["Ingreso"].sum()

gasto_anterior = df_anterior["Gasto"].sum()

flujo_anterior = (
    ingreso_anterior -
    gasto_anterior
)


rentabilidad_anterior = (

    flujo_anterior /
    ingreso_anterior

    if ingreso_anterior != 0
    else 0
)


var_ingreso = variacion(
    ingreso_total,
    ingreso_anterior
)

var_gasto = variacion(
    gasto_total,
    gasto_anterior
)

var_flujo = variacion(
    flujo_total,
    flujo_anterior
)

dif_rentabilidad = (
    rentabilidad -
    rentabilidad_anterior
)


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(
    [1, 1, 1, 1],
    gap="medium"
)


with k1:

    delta = (
        f"{var_ingreso:.1%}"
        if not pd.isna(var_ingreso)
        else None
    )

    st.metric(
        label="💰 Ingreso Total",
        value=moneda(ingreso_total),
        delta=delta
    )


with k2:

    delta = (
        f"{var_gasto:.1%}"
        if not pd.isna(var_gasto)
        else None
    )

    st.metric(
        label="🧾 Gasto Total",
        value=moneda(gasto_total),
        delta=delta
    )


with k3:

    delta = (
        f"{var_flujo:.1%}"
        if not pd.isna(var_flujo)
        else None
    )

    st.metric(
        label="💵 Flujo",
        value=moneda(flujo_total),
        delta=delta
    )


with k4:

    delta = (
        f"{dif_rentabilidad:.1%}"
        if not pd.isna(dif_rentabilidad)
        else None
    )

    st.metric(
        label="🎯 Rentabilidad",
        value=f"{rentabilidad:.1%}",
        delta=delta
    )


# ============================================================
# ESPACIO
# ============================================================

st.markdown(
    '<div style="height:18px;"></div>',
    unsafe_allow_html=True
)


# ============================================================
# ALTURA DE LAS DOS TARJETAS
# ============================================================

ALTURA_TARJETAS = 500


# ============================================================
# DOS COLUMNAS PRINCIPALES
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.55, 1],
    gap="medium"
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

        .groupby(
            "Nombre_Propiedad"
        )

        .agg(
            Ingreso=("Ingreso", "sum"),
            Gasto=("Gasto", "sum")
        )

        .reset_index()
    )


    resumen["Flujo"] = (
        resumen["Ingreso"] -
        resumen["Gasto"]
    )


    resumen["Rentabilidad"] = np.where(

        resumen["Ingreso"] != 0,

        resumen["Flujo"] /
        resumen["Ingreso"],

        0
    )


    resumen = resumen.sort_values(
        "Ingreso",
        ascending=False
    )


    filas = ""


    for _, row in resumen.iterrows():

        pct = float(
            row["Rentabilidad"]
        )

        ancho = min(
            max(pct * 100, 0),
            100
        )

        flujo = float(
            row["Flujo"]
        )

        color_flujo = (
            "#00875A"
            if flujo >= 0
            else "#DE350B"
        )


        filas += f"""

        <tr>

            <td>
                {html.escape(
                    str(row["Nombre_Propiedad"])
                )}
            </td>

            <td class="right green">
                {compacto(row["Ingreso"])}
            </td>

            <td class="right red">
                {compacto(row["Gasto"])}
            </td>

            <td
                class="right"
                style="color:{color_flujo};">
                {compacto(flujo)}
            </td>

            <td>

                <div class="pct-text">
                    {pct:.1%}
                </div>

                <div class="progress">

                    <div
                        class="progress-fill"
                        style="width:{ancho}%;">
                    </div>

                </div>

            </td>

            <td class="status">
                {bandera(pct)}
            </td>

        </tr>

        """


    total_pct = (

        flujo_total /
        ingreso_total

        if ingreso_total != 0
        else 0
    )


    total_ancho = min(
        max(total_pct * 100, 0),
        100
    )


    tabla_html = f"""

    <html>

    <head>

    <style>

    * {{
        box-sizing:border-box;

        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Arial,
            sans-serif;
    }}

    body {{
        margin:0;
        padding:0;
        background:transparent;
        overflow:hidden;
    }}

    .card {{

        width:100%;

        height:{ALTURA_TARJETAS}px;

        background:#F1F3F5;

        border:1px solid #D7DDE3;

        border-radius:12px;

        overflow:hidden;
    }}

    table {{

        width:100%;

        height:100%;

        border-collapse:collapse;

        table-layout:fixed;
    }}

    th {{

        background:#008F83;

        color:white;

        height:39px;

        padding:7px 10px;

        font-size:12px;

        font-weight:500;

        text-align:left;
    }}

    th:nth-child(1) {{
        width:27%;
    }}

    th:nth-child(2),
    th:nth-child(3),
    th:nth-child(4) {{

        width:13%;

        text-align:right;
    }}

    th:nth-child(5) {{

        width:24%;

        text-align:right;
    }}

    th:nth-child(6) {{

        width:10%;

        text-align:center;
    }}

    td {{

        height:42px;

        padding:7px 10px;

        border-bottom:
            1px solid #DDE2E7;

        background:#F8F9FA;

        color:#172B4D;

        font-size:12px;

        font-weight:400;
    }}

    .right {{
        text-align:right;
    }}

    .green {{
        color:#00875A;
    }}

    .red {{
        color:#DE350B;
    }}

    .pct-text {{

        text-align:right;

        font-size:11px;

        margin-bottom:3px;

        color:#344563;
    }}

    .progress {{

        width:100%;

        height:6px;

        border-radius:5px;

        background:#E3E8ED;

        overflow:hidden;
    }}

    .progress-fill {{

        height:100%;

        background:#16B5D1;

        border-radius:5px;
    }}

    .status {{

        text-align:center;

        font-size:14px;
    }}

    .total td {{

        background:#E8EDF1;

        border-top:
            2px solid #CDD5DC;

        font-weight:500;

        height:48px;
    }}

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

                {filas}

                <tr class="total">

                    <td>Total</td>

                    <td class="right green">
                        {compacto(ingreso_total)}
                    </td>

                    <td class="right red">
                        {compacto(gasto_total)}
                    </td>

                    <td
                        class="right"
                        style="color:#00875A;">
                        {compacto(flujo_total)}
                    </td>

                    <td>

                        <div class="pct-text">
                            {total_pct:.1%}
                        </div>

                        <div class="progress">

                            <div
                                class="progress-fill"
                                style="width:{total_ancho}%;">
                            </div>

                        </div>

                    </td>

                    <td class="status">
                        {bandera(total_pct)}
                    </td>

                </tr>

            </tbody>

        </table>

    </div>

    </body>

    </html>
    """


    components.html(
        tabla_html,
        height=ALTURA_TARJETAS,
        scrolling=False
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


    gastos = (

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


    if not gastos.empty:

        total_gastos = gastos["Gasto"].sum()


        if len(gastos) > 7:

            gastos_top = gastos.head(7).copy()

            otros_valor = (
                gastos.iloc[7:]["Gasto"].sum()
            )

            gastos_otros = pd.DataFrame({

                "Nombre_Subcategoria":
                    ["Otros"],

                "Gasto":
                    [otros_valor]

            })

            gastos_pie = pd.concat(
                [
                    gastos_top,
                    gastos_otros
                ],
                ignore_index=True
            )

        else:

            gastos_pie = gastos.copy()


        colores = [
            "#D9232E",
            "#ED1C24",
            "#E83B5A",
            "#F05A66",
            "#F57A87",
            "#F99BA5",
            "#F7BDC3",
            "#E7D3D7"
        ]


        mayor_nombre = str(
            gastos_pie.iloc[0][
                "Nombre_Subcategoria"
            ]
        )

        mayor_valor = float(
            gastos_pie.iloc[0]["Gasto"]
        )

        mayor_pct = (
            mayor_valor /
            total_gastos
        )


        # ====================================================
        # DONA
        # ====================================================

        fig = go.Figure()


        fig.add_trace(
            go.Pie(

                labels=
                    gastos_pie[
                        "Nombre_Subcategoria"
                    ],

                values=
                    gastos_pie["Gasto"],

                hole=0.60,

                textinfo="none",

                sort=False,

                marker=dict(

                    colors=
                        colores[
                            :len(gastos_pie)
                        ],

                    line=dict(
                        color="#FFFFFF",
                        width=2
                    )
                ),

                hovertemplate=
                    "<b>%{label}</b><br>"
                    "$%{value:,.0f}<br>"
                    "%{percent}"
                    "<extra></extra>"
            )
        )


        fig.add_annotation(

            x=0.5,
            y=0.54,

            text=f"<b>{mayor_pct:.1%}</b>",

            showarrow=False,

            font=dict(
                family="Arial",
                size=22,
                color="#172B4D"
            )
        )


        fig.add_annotation(

            x=0.5,
            y=0.42,

            text=html.escape(
                mayor_nombre
            ),

            showarrow=False,

            font=dict(
                family="Arial",
                size=9,
                color="#7A869A"
            )
        )


        fig.update_layout(

            height=380,

            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),

            showlegend=False,

            paper_bgcolor="#F1F3F5",

            plot_bgcolor="#F1F3F5"
        )


        # ====================================================
        # DETALLE DE GASTOS
        # ====================================================

        filas_detalle = ""


        for i, (_, row) in enumerate(
            gastos_pie.iterrows()
        ):

            nombre = html.escape(
                str(
                    row[
                        "Nombre_Subcategoria"
                    ]
                )
            )

            valor = float(
                row["Gasto"]
            )

            porcentaje = (
                valor /
                total_gastos
            )


            filas_detalle += f"""

            <div class="expense-row">

                <div class="expense-name">

                    <span
                        class="dot"
                        style="
                        background:{colores[i]};
                        ">
                    </span>

                    {nombre}

                </div>

                <div class="expense-value">
                    {compacto(valor)}
                </div>

                <div class="expense-percent">
                    {porcentaje:.1%}
                </div>

            </div>

            """


        detalle_html = f"""

        <html>

        <head>

        <style>

        * {{

            box-sizing:border-box;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Arial,
                sans-serif;
        }}

        body {{

            margin:0;

            padding:0;

            background:transparent;

            overflow:hidden;
        }}

        .detalle {{

            padding:
                10px
                8px
                0
                8px;
        }}

        .total {{

            font-size:21px;

            font-weight:400;

            color:#172B4D;

            margin-bottom:5px;
        }}

        .subtitulo {{

            color:#7A869A;

            font-size:10px;

            font-weight:400;

            margin-bottom:9px;
        }}

        .headers {{

            display:grid;

            grid-template-columns:
                1fr 72px 36px;

            color:#52617A;

            font-size:10px;

            font-weight:400;

            padding-bottom:5px;

            border-bottom:
                1px solid #DDE3E8;
        }}

        .expense-row {{

            display:grid;

            grid-template-columns:
                1fr 72px 36px;

            min-height:31px;

            align-items:center;

            border-bottom:
                1px solid #E2E6EA;

            font-size:11px;

            font-weight:400;

            color:#344563;
        }}

        .expense-name {{

            white-space:nowrap;

            overflow:hidden;

            text-overflow:ellipsis;
        }}

        .dot {{

            display:inline-block;

            width:7px;

            height:7px;

            border-radius:50%;

            margin-right:6px;
        }}

        .expense-value {{

            text-align:right;

            color:#172B4D;

            font-weight:400;
        }}

        .expense-percent {{

            text-align:right;

            color:#7A869A;

            font-weight:400;
        }}

        .highlight {{

            margin-top:12px;

            padding:8px 9px;

            background:#EAF3FF;

            border:
                1px solid #C7DDF8;

            border-radius:7px;

            color:#52617A;

            font-size:9px;

            line-height:1.4;
        }}

        .highlight strong {{

            color:#344563;

            font-weight:500;
        }}

        </style>

        </head>

        <body>

        <div class="detalle">

            <div class="total">
                {moneda(total_gastos)}
            </div>

            <div class="subtitulo">
                Total de egresos operativos
            </div>

            <div class="headers">

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

            {filas_detalle}

            <div class="highlight">

                💡 Mayor centro de gasto:

                <strong>
                    {html.escape(mayor_nombre)}
                </strong>

                ({compacto(mayor_valor)})

                <br>

                Representa el
                {mayor_pct:.1%}
                del total.

            </div>

        </div>

        </body>

        </html>
        """


        # ====================================================
        # TARJETA GASTOS
        # ====================================================

        st.markdown(
            f"""
            <div style="
                height:{ALTURA_TARJETAS}px;
                background:#F1F3F5;
                border:1px solid #D7DDE3;
                border-radius:12px;
                padding:12px;
                overflow:hidden;
            ">
            """,
            unsafe_allow_html=True
        )


        gc1, gc2 = st.columns(
            [0.95, 1.05],
            gap="small"
        )


        with gc1:

            st.plotly_chart(

                fig,

                use_container_width=True,

                config={
                    "displayModeBar": False
                },

                key="gastos_donut"
            )


        with gc2:

            components.html(
                detalle_html,
                height=450,
                scrolling=False
            )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    else:

        st.markdown(
            f"""
            <div style="
                height:{ALTURA_TARJETAS}px;
                background:#F1F3F5;
                border:1px solid #D7DDE3;
                border-radius:12px;
                padding:25px;
                color:#6B778C;
            ">
                No hay gastos para mostrar en el periodo seleccionado.
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ANÁLISIS ANUAL
# ============================================================

st.markdown(
    '<div style="height:22px;"></div>',
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


# ============================================================
# AÑO
# ============================================================

años_disponibles = sorted(

    df_graficos[
        "Fecha"
    ]
    .dropna()
    .dt.year
    .unique(),

    reverse=True
)


if len(años_disponibles) == 0:

    st.info("No hay años disponibles.")

    st.stop()


año_sistema = pd.Timestamp.today().year


if año_sistema in años_disponibles:

    indice_default = años_disponibles.index(
        año_sistema
    )

else:

    indice_default = 0


año_seleccionado = st.selectbox(

    "Año de análisis",

    años_disponibles,

    index=indice_default
)


año_anterior = año_seleccionado - 1


# ============================================================
# DATOS ANUALES
# ============================================================

datos_año = df_graficos[
    df_graficos["Fecha"].dt.year
    == año_seleccionado
].copy()


datos_año_anterior = df_graficos[
    df_graficos["Fecha"].dt.year
    == año_anterior
].copy()


if not datos_año.empty:

    fecha_corte_anual = (
        datos_año["Fecha"].max()
    )

    mes_corte_anual = (
        fecha_corte_anual.month
    )

else:

    mes_corte_anual = 12


datos_año["Mes"] = (
    datos_año["Fecha"].dt.month
)

datos_año_anterior["Mes"] = (
    datos_año_anterior["Fecha"].dt.month
)


ingresos_mes_actual = (

    datos_año

    .groupby("Mes")["Ingreso"]

    .sum()
)


ingresos_mes_anterior = (

    datos_año_anterior

    .groupby("Mes")["Ingreso"]

    .sum()
)


meses = list(
    range(
        1,
        mes_corte_anual + 1
    )
)


nombres_meses = [
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

    ingresos_mes_actual.get(
        mes,
        0
    )

    for mes in meses
]


valores_anterior = [

    ingresos_mes_anterior.get(
        mes,
        0
    )

    for mes in meses
]


# ============================================================
# GRÁFICO MENSUAL
# ============================================================

fig_comparacion = go.Figure()


fig_comparacion.add_trace(

    go.Bar(

        x=[
            nombres_meses[i - 1]
            for i in meses
        ],

        y=valores_actual,

        name=str(
            año_seleccionado
        ),

        marker_color="#18A77A",

        opacity=0.85
    )
)


fig_comparacion.add_trace(

    go.Scatter(

        x=[
            nombres_meses[i - 1]
            for i in meses
        ],

        y=valores_anterior,

        name=str(
            año_anterior
        ),

        mode="lines+markers",

        line=dict(
            color="#1769E0",
            width=3
        ),

        marker=dict(
            size=6
        )
    )
)


fig_comparacion.update_layout(

    height=370,

    margin=dict(
        l=10,
        r=10,
        t=35,
        b=10
    ),

    paper_bgcolor="#F1F3F5",

    plot_bgcolor="#F1F3F5",

    font=dict(
        family="Arial",
        color="#52617A"
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),

    xaxis=dict(
        showgrid=False
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#DDE3E8",
        tickprefix="$ "
    ),

    bargap=0.25
)


# ============================================================
# PROMEDIO MENSUAL
# ============================================================

datos_promedio = df_graficos[
    df_graficos["Fecha"].dt.year
    == año_seleccionado
].copy()


if not datos_promedio.empty:

    promedio = (

        datos_promedio

        .groupby(
            "Nombre_Propiedad"
        )

        .agg(

            Ingreso=(
                "Ingreso",
                "sum"
            ),

            FechaInicio=(
                "Fecha",
                "min"
            ),

            FechaFin=(
                "Fecha",
                "max"
            )

        )

        .reset_index()
    )


    promedio["Meses"] = (

        (
            promedio["FechaFin"].dt.year
            -
            promedio["FechaInicio"].dt.year
        )
        * 12

        +

        (
            promedio["FechaFin"].dt.month
            -
            promedio["FechaInicio"].dt.month
        )

        + 1
    )


    promedio["PromedioMensual"] = np.where(

        promedio["Meses"] > 0,

        promedio["Ingreso"] /
        promedio["Meses"],

        promedio["Ingreso"]
    )


    promedio = promedio.sort_values(
        "PromedioMensual",
        ascending=False
    )

else:

    promedio = pd.DataFrame()


# ============================================================
# GRÁFICO PROMEDIO
# ============================================================

fig_promedio = go.Figure()


if not promedio.empty:

    fig_promedio.add_trace(

        go.Bar(

            x=promedio[
                "Nombre_Propiedad"
            ],

            y=promedio[
                "PromedioMensual"
            ],

            marker_color="#7565D9",

            text=[
                compacto(x)
                for x in
                promedio[
                    "PromedioMensual"
                ]
            ],

            textposition="outside",

            textfont=dict(
                size=11,
                color="#172B4D"
            )
        )
    )


fig_promedio.update_layout(

    height=370,

    margin=dict(
        l=10,
        r=10,
        t=35,
        b=55
    ),

    paper_bgcolor="#F1F3F5",

    plot_bgcolor="#F1F3F5",

    font=dict(
        family="Arial",
        color="#52617A"
    ),

    xaxis=dict(
        showgrid=False
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#DDE3E8",
        tickprefix="$ "
    )
)


# ============================================================
# GRÁFICAS ANUALES
# ============================================================

grafico1, grafico2 = st.columns(
    [1, 1],
    gap="medium"
)


with grafico1:

    st.markdown(
        f"""
        <div class="section-title">
            📊 Ingresos mensuales
        </div>

        <div class="section-subtitle">
            Comparativo de ingresos de {año_seleccionado}
            contra {año_anterior}
        </div>
        """,
        unsafe_allow_html=True
    )


    st.plotly_chart(

        fig_comparacion,

        use_container_width=True,

        config={
            "displayModeBar": False
        },

        key="grafico_ingresos_anuales"
    )


with grafico2:

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

    df_filtrado[
        "Nombre_Propiedad"
    ]

    .nunique()
)


socios_analizados = (

    df_filtrado[
        "Nombre_Socio"
    ]

    .nunique()
)


st.markdown(
    f"""
    <div style="
        background:#FFFFFF;
        border:1px solid #DDE2E7;
        border-radius:12px;
        padding:14px 20px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        color:#52617A;
        font-size:13px;
    ">

        <div>
            🟢
            <strong style="color:#00875A;">
                {moneda(flujo_total)}
            </strong>
            &nbsp;
            Flujo positivo en el periodo
        </div>

        <div>
            🏢
            <strong style="color:#172B4D;">
                {propiedades_analizadas}
            </strong>
            &nbsp;
            Propiedades analizadas
        </div>

        <div>
            👥
            <strong style="color:#172B4D;">
                {socios_analizados}
            </strong>
            &nbsp;
            Socios
        </div>

        <div style="
            color:#6B778C;
            font-style:italic;
        ">
            “Más que propiedades, mejores decisiones”
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
