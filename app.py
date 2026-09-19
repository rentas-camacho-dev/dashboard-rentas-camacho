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
# ESTILO GENERAL
# ============================================================

st.markdown(
"""
<style>

/* ==========================================================
   FUENTE GENERAL
   ========================================================== */

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif !important;
}


/* ==========================================================
   FONDO
   ========================================================== */

.stApp {
    background: #F5F7FA;
}


/* ==========================================================
   CONTENEDOR
   ========================================================== */

.block-container {
    max-width: 100%;
    padding-top: 3.2rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.7rem !important;
    padding-right: 0.7rem !important;
}


/* ==========================================================
   ESPACIADO GENERAL
   ========================================================== */

div[data-testid="stVerticalBlock"] {
    gap: 0.3rem;
}


/* ==========================================================
   TÍTULOS
   ========================================================== */

.section-title {
    color: #172B4D;
    font-size: 19px;
    font-weight: 700;
    line-height: 1.25;
    margin-top: 8px;
    margin-bottom: 6px;
}

.section-subtitle {
    color: #6B778C;
    font-size: 11px;
    font-weight: 400;
    line-height: 1.35;
    margin-top: 0;
    margin-bottom: 9px;
}


/* ==========================================================
   FILTROS
   ========================================================== */

label {
    font-size: 12px !important;
    color: #344563 !important;
    font-weight: 400 !important;
}

div[data-baseweb="select"] {
    border-radius: 8px;
}


/* ==========================================================
   KPI
   ========================================================== */

div[data-testid="stMetric"] {

    background: white;

    border: 1px solid #E1E5EA;

    border-radius: 13px;

    padding: 9px 14px;

    box-shadow: 0 2px 7px rgba(0,0,0,.035);
}

div[data-testid="stMetricLabel"] {

    font-size: 11px !important;

    font-weight: 400 !important;
}

div[data-testid="stMetricValue"] {

    font-size: 24px !important;

    font-weight: 400 !important;
}


/* ==========================================================
   TARJETAS
   ========================================================== */

div[data-testid="stVerticalBlockBorderWrapper"] {

    background: white !important;

    border: 1px solid #E1E5EA !important;

    border-radius: 13px !important;
}


/* ==========================================================
   PLOTLY
   ========================================================== */

div[data-testid="stPlotlyChart"] {

    margin-top: -4px;

    margin-bottom: -8px;
}


/* ==========================================================
   SEPARADORES
   ========================================================== */

hr {

    margin: 7px 0;

    border-color: #E3E7EC;
}

</style>
""",
unsafe_allow_html=True
)


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


# ============================================================
# CONEXIÓN BIGQUERY
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def cargar_datos():

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

    return client.query(
        QUERY
    ).to_dataframe()


# ============================================================
# CARGAR DATOS
# ============================================================

with st.spinner(
    "Cargando información de Airbnb..."
):

    df = cargar_datos()


# ============================================================
# PREPARACIÓN
# ============================================================

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    errors="coerce"
)


for col in [
    "Porcentaje",
    "Valor",
    "Valor_Repartido",
    "Ingreso",
    "Gasto"
]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)


df = df.dropna(
    subset=["Fecha"]
)


# ============================================================
# FUNCIONES
# ============================================================

def moneda(valor):

    return (
        f"${valor:,.0f}"
        .replace(",", ".")
    )


def compacto(valor):

    valor = float(valor)

    signo = "-" if valor < 0 else ""

    valor = abs(valor)

    if valor >= 1_000_000_000:

        return (
            f"{signo}$ {valor / 1_000_000_000:.1f} B"
        )

    elif valor >= 1_000_000:

        return (
            f"{signo}$ {valor / 1_000_000:.1f} M"
        )

    elif valor >= 1_000:

        return (
            f"{signo}$ {valor / 1_000:.0f} mil"
        )

    else:

        return (
            f"{signo}${valor:,.0f}"
            .replace(",", ".")
        )


def cambio(actual, anterior):

    if anterior == 0:

        return None

    return (
        (actual - anterior)
        /
        abs(anterior)
    )


def bandera(porcentaje):

    if porcentaje >= 0.80:

        return "🏆"

    elif porcentaje >= 0.50:

        return "⚡"

    else:

        return "🚩"


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
"""
<div style="
    margin-top:8px;
    margin-bottom:24px;
">

<h1 style="
    color:#172B4D;
    font-size:30px;
    font-weight:700;
    margin:0;
    padding:0;
    line-height:1.2;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
">
🏠 Rentas Cortas — Airbnb
</h1>

<div style="
    color:#6B778C;
    font-size:13px;
    font-weight:400;
    margin-top:7px;
    line-height:1.4;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
">
Ingresos, gastos y rentabilidad de tus propiedades
</div>

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


f1, f2, f3, f4 = st.columns(
    4,
    gap="medium"
)


# ------------------------------------------------------------
# CIUDAD
# ------------------------------------------------------------

with f1:

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .astype(str)
        .unique()
    )

    ciudad_seleccionada = st.multiselect(

        "Ciudad",

        ciudades,

        placeholder="Todas",

        key="filtro_ciudad"
    )


# ------------------------------------------------------------
# PROPIEDAD
# ------------------------------------------------------------

with f2:

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
    )

    propiedad_seleccionada = st.multiselect(

        "Propiedad",

        propiedades,

        placeholder="Todas",

        key="filtro_propiedad"
    )


# ------------------------------------------------------------
# SOCIO
# ------------------------------------------------------------

with f3:

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .astype(str)
        .unique()
    )

    socio_seleccionado = st.multiselect(

        "Socio",

        socios,

        placeholder="Todos",

        key="filtro_socio"
    )


# ------------------------------------------------------------
# FECHA
# ------------------------------------------------------------

with f4:

    fecha_min = (
        df["Fecha"]
        .min()
        .date()
    )

    fecha_max = (
        df["Fecha"]
        .max()
        .date()
    )

    rango_fecha = st.date_input(

        "Fecha",

        value=(
            fecha_min,
            fecha_max
        ),

        min_value=fecha_min,

        max_value=fecha_max,

        key="filtro_fecha"
    )


# ============================================================
# FILTROS BASE
# ============================================================

df_base = df.copy()


if ciudad_seleccionada:

    df_base = df_base[
        df_base["Ciudad"]
        .astype(str)
        .isin(
            ciudad_seleccionada
        )
    ]


if propiedad_seleccionada:

    df_base = df_base[
        df_base["Nombre_Propiedad"]
        .astype(str)
        .isin(
            propiedad_seleccionada
        )
    ]


if socio_seleccionado:

    df_base = df_base[
        df_base["Nombre_Socio"]
        .astype(str)
        .isin(
            socio_seleccionado
        )
    ]


# ============================================================
# FILTRO DE FECHA
# ============================================================

df_filtrado = df_base.copy()


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

        +

        pd.Timedelta(
            days=1
        )
    )

    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= fecha_inicio)
        &
        (df_filtrado["Fecha"] < fecha_fin)
    ]


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

    ingreso_total
    -
    gasto_total
)


rentabilidad = (

    flujo_total
    /
    ingreso_total

    if ingreso_total != 0

    else 0
)


# ============================================================
# PERIODO ANTERIOR
# ============================================================

delta_ingreso = None
delta_gasto = None
delta_flujo = None
delta_rentabilidad = None


if (
    isinstance(rango_fecha, tuple)
    and len(rango_fecha) == 2
):

    inicio_actual = pd.Timestamp(
        rango_fecha[0]
    )

    fin_actual = pd.Timestamp(
        rango_fecha[1]
    )

    dias_periodo = (

        fin_actual
        -
        inicio_actual
    ).days + 1


    fin_anterior = (

        inicio_actual
        -
        pd.Timedelta(
            days=1
        )
    )


    inicio_anterior = (

        fin_anterior
        -
        pd.Timedelta(
            days=dias_periodo - 1
        )
    )


    df_anterior = df_base[
        (df_base["Fecha"] >= inicio_anterior)
        &
        (df_base["Fecha"] <= fin_anterior)
    ]


    if not df_anterior.empty:

        ingreso_anterior = (
            df_anterior["Ingreso"].sum()
        )

        gasto_anterior = (
            df_anterior["Gasto"].sum()
        )

        flujo_anterior = (

            ingreso_anterior
            -
            gasto_anterior
        )


        rent_anterior = (

            flujo_anterior
            /
            ingreso_anterior

            if ingreso_anterior != 0

            else 0
        )


        delta_ingreso = cambio(
            ingreso_total,
            ingreso_anterior
        )


        delta_gasto = cambio(
            gasto_total,
            gasto_anterior
        )


        delta_flujo = cambio(
            flujo_total,
            flujo_anterior
        )


        delta_rentabilidad = (

            rentabilidad
            -
            rent_anterior
        )


# ============================================================
# KPIs
# ============================================================

k1, k2, k3, k4 = st.columns(
    4,
    gap="medium"
)


with k1:

    st.metric(

        "💰 Ingreso Total",

        moneda(
            ingreso_total
        ),

        (
            f"{delta_ingreso:+.1%}"

            if delta_ingreso is not None

            else None
        )
    )


with k2:

    st.metric(

        "🧾 Gasto Total",

        moneda(
            gasto_total
        ),

        (
            f"{delta_gasto:+.1%}"

            if delta_gasto is not None

            else None
        )
    )


with k3:

    st.metric(

        "💵 Flujo",

        moneda(
            flujo_total
        ),

        (
            f"{delta_flujo:+.1%}"

            if delta_flujo is not None

            else None
        )
    )


with k4:

    st.metric(

        "🎯 Rentabilidad",

        f"{rentabilidad:.1%}",

        (
            f"{delta_rentabilidad * 100:+.1f} pp"

            if delta_rentabilidad is not None

            else None
        )
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

        resumen = (

            df_filtrado

            .groupby(
                "Nombre_Propiedad"
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


        resumen["Flujo"] = (

            resumen["Ingreso"]
            -
            resumen["Gasto"]
        )


        resumen["Rentabilidad"] = (

            resumen["Flujo"]
            /
            resumen["Ingreso"]

        ).fillna(0)


        resumen = (

            resumen

            .sort_values(
                "Ingreso",
                ascending=False
            )
        )


        filas = ""


        for _, row in resumen.iterrows():

            nombre = html.escape(
                str(
                    row[
                        "Nombre_Propiedad"
                    ]
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
                row["Rentabilidad"]
            )


            ancho = min(
                max(
                    pct * 100,
                    0
                ),
                100
            )


            color_flujo = (

                "#00875A"

                if flujo >= 0

                else "#DE350B"
            )


            filas += f"""
<tr>

<td class="propiedad">
{nombre}
</td>

<td class="num ingreso">
{compacto(ingreso)}
</td>

<td class="num gasto">
{compacto(gasto)}
</td>

<td
class="num flujo"
style="color:{color_flujo};">
{compacto(flujo)}
</td>

<td>

<div class="pct">
{pct:.1%}
</div>

<div class="barra">

<div
class="barra-fill"
style="width:{ancho}%;">
</div>

</div>

</td>

<td class="estado">
{bandera(pct)}
</td>

</tr>
"""


        total_ingreso = (
            resumen["Ingreso"].sum()
        )

        total_gasto = (
            resumen["Gasto"].sum()
        )

        total_flujo = (
            resumen["Flujo"].sum()
        )


        total_pct = (

            total_flujo
            /
            total_ingreso

            if total_ingreso != 0

            else 0
        )


        total_ancho = min(

            max(
                total_pct * 100,
                0
            ),

            100
        )


        tabla_html = f"""

<style>

* {{

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    box-sizing:border-box;

}}

.tabla-card {{

    background:white;

    border:1px solid #E1E5EA;

    border-radius:12px;

    overflow:hidden;

    width:100%;

}}

.tabla-card table {{

    width:100%;

    border-collapse:collapse;

    table-layout:fixed;

}}

.tabla-card th {{

    background:#008A7A;

    color:white;

    padding:8px 8px;

    font-size:11px;

    font-weight:600;

    text-align:left;

}}

.tabla-card th:nth-child(1) {{
    width:23%;
}}

.tabla-card th:nth-child(2),
.tabla-card th:nth-child(3),
.tabla-card th:nth-child(4) {{

    width:14%;

    text-align:right;

}}

.tabla-card th:nth-child(5) {{

    width:25%;

    text-align:right;

}}

.tabla-card th:nth-child(6) {{

    width:10%;

    text-align:center;

}}

.tabla-card td {{

    padding:6px 8px;

    border-bottom:1px solid #EDF0F2;

    font-size:11px;

    font-weight:400;

    color:#172B4D;

    height:31px;

}}

.propiedad {{

    font-weight:400;

    white-space:nowrap;

    overflow:hidden;

    text-overflow:ellipsis;

}}

.num {{

    text-align:right;

    white-space:nowrap;

    font-weight:400;

}}

.ingreso {{

    color:#00875A;

}}

.gasto {{

    color:#DE350B;

}}

.flujo {{

    font-weight:400;

}}

.pct {{

    text-align:right;

    font-size:10px;

    font-weight:400;

    margin-bottom:2px;

}}

.barra {{

    width:100%;

    height:5px;

    background:#EDF1F5;

    border-radius:5px;

    overflow:hidden;

}}

.barra-fill {{

    height:100%;

    background:#16B5D1;

    border-radius:5px;

}}

.estado {{

    text-align:center;

    font-size:13px;

    font-weight:400;

}}

.total-row td {{

    background:#F8FAFC;

    border-top:2px solid #DCE3EA;

    font-weight:500;

}}

</style>


<div class="tabla-card">

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

<tr class="total-row">

<td>
Total
</td>

<td class="num ingreso">
{compacto(total_ingreso)}
</td>

<td class="num gasto">
{compacto(total_gasto)}
</td>

<td
class="num"
style="color:#00875A;">
{compacto(total_flujo)}
</td>

<td>

<div class="pct">
{total_pct:.1%}
</div>

<div class="barra">

<div
class="barra-fill"
style="width:{total_ancho}%;">
</div>

</div>

</td>

<td class="estado">
{bandera(total_pct)}
</td>

</tr>

</tbody>

</table>

</div>
"""


        components.html(

            tabla_html,

            height=390,

            scrolling=False
        )


    else:

        st.info(
            "No hay información para el periodo seleccionado."
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
        '<div class="section-subtitle">Desglose por subcategoría de gasto en el periodo seleccionado</div>',
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

        total_gastos = (
            gastos["Gasto"].sum()
        )


        # ====================================================
        # TOP 7 + OTROS
        # ====================================================

        if len(gastos) > 7:

            top = (
                gastos
                .head(7)
                .copy()
            )


            otros_valor = (

                gastos
                .iloc[7:]["Gasto"]
                .sum()
            )


            otros = pd.DataFrame({

                "Nombre_Subcategoria":
                    ["Otros"],

                "Gasto":
                    [otros_valor]

            })


            gastos_pie = pd.concat(

                [
                    top,
                    otros
                ],

                ignore_index=True
            )

        else:

            gastos_pie = gastos.copy()


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
        # MAYOR GASTO
        # ====================================================

        mayor_valor = float(
            gastos_pie.iloc[0]["Gasto"]
        )


        mayor_nombre = str(
            gastos_pie.iloc[0][
                "Nombre_Subcategoria"
            ]
        )


        mayor_pct = (

            mayor_valor
            /
            total_gastos
        )


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

                hole=0.63,

                textinfo="none",

                sort=False,

                marker=dict(

                    colors=colores[
                        :len(gastos_pie)
                    ],

                    line=dict(

                        color="white",

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


        fig_gastos.add_annotation(

            x=0.5,

            y=0.55,

            text=(
                f"<b>{mayor_pct:.1%}</b>"
            ),

            showarrow=False,

            font=dict(

                size=21,

                color="#172B4D",

                family=
                "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
            )
        )


        fig_gastos.add_annotation(

            x=0.5,

            y=0.43,

            text=html.escape(
                mayor_nombre
            ),

            showarrow=False,

            font=dict(

                size=10,

                color="#7A869A",

                family=
                "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
            )
        )


        fig_gastos.update_layout(

            height=285,

            margin=dict(

                l=0,

                r=0,

                t=0,

                b=0
            ),

            showlegend=False,

            template="plotly_white",

            font=dict(

                family=
                "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",

                color="#172B4D"
            )
        )


        # ====================================================
        # TARJETA ÚNICA
        # ====================================================

        with st.container(

            border=True,

            height=390
        ):

            gc1, gc2 = st.columns(

                [1.0, 1.25],

                gap="small"
            )


            # ------------------------------------------------
            # DONA
            # ------------------------------------------------

            with gc1:

                st.plotly_chart(

                    fig_gastos,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    },

                    key="grafico_gastos"
                )


            # ------------------------------------------------
            # DETALLE
            # ------------------------------------------------

            with gc2:

                st.markdown(

                    f"""
<div style="
font-family:
-apple-system,
BlinkMacSystemFont,
'Segoe UI',
sans-serif;

padding:8px 3px 0 0;
font-weight:400;
">

<div style="
font-size:20px;
font-weight:400;
color:#172B4D;
line-height:1.1;
">

{moneda(total_gastos)}

</div>

<div style="
font-size:11px;
font-weight:400;
color:#7A869A;
margin-top:4px;
margin-bottom:8px;
">

Total de egresos operativos

</div>

<div style="
display:grid;
grid-template-columns:1fr 72px 34px;

font-size:10px;

font-weight:400;

color:#52617A;

padding-bottom:5px;

border-bottom:1px solid #E3E7EC;
">

<div>
Subcategoría
</div>

<div style="
text-align:right;
">
Valor
</div>

<div style="
text-align:right;
">
%
</div>

</div>

</div>
""",

                    unsafe_allow_html=True
                )


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

                        valor
                        /
                        total_gastos
                    )


                    st.markdown(

                        f"""
<div style="
font-family:
-apple-system,
BlinkMacSystemFont,
'Segoe UI',
sans-serif;

display:grid;

grid-template-columns:
1fr 72px 34px;

align-items:center;

min-height:25px;

border-bottom:
1px solid #F0F2F4;

font-size:11px;

font-weight:400;
">

<div style="
color:#344563;

white-space:nowrap;

overflow:hidden;

text-overflow:ellipsis;
">

<span style="
display:inline-block;

width:7px;

height:7px;

border-radius:50%;

background:{colores[i]};

margin-right:6px;
">
</span>

{categoria}

</div>

<div style="
text-align:right;

font-weight:400;

color:#172B4D;
">

{compacto(valor)}

</div>

<div style="
text-align:right;

font-weight:400;

color:#7A869A;
">

{pct:.1%}

</div>

</div>
""",

                        unsafe_allow_html=True
                    )


            # ------------------------------------------------
            # MAYOR CENTRO DE GASTO
            # ------------------------------------------------

            st.markdown(

                f"""
<div style="
background:#EAF3FF;

border:1px solid #C7DDF8;

border-radius:8px;

padding:8px 10px;

margin:3px 8px 0 8px;

font-family:
-apple-system,
BlinkMacSystemFont,
'Segoe UI',
sans-serif;

font-size:11px;

font-weight:400;

color:#344563;

line-height:1.35;
">

💡 Mayor centro de gasto:

<span style="font-weight:400;">

{html.escape(mayor_nombre)}

</span>

({compacto(mayor_valor)})

<span style="
color:#6B778C;
margin-left:4px;
">

{mayor_pct:.1%} del total

</span>

</div>
""",

                unsafe_allow_html=True
            )


    else:

        st.info(
            "No hay gastos para mostrar."
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


años_disponibles = sorted(

    df["Fecha"]
    .dt.year
    .dropna()
    .unique(),

    reverse=True
)


if años_disponibles:

    año_sistema = pd.Timestamp.now().year


    if año_sistema in años_disponibles:

        año_default = año_sistema

    else:

        año_default = años_disponibles[0]


    año_seleccionado = st.selectbox(

        "Año de análisis",

        años_disponibles,

        index=años_disponibles.index(
            año_default
        ),

        key="selector_año"
    )


    año_anterior = (

        año_seleccionado
        -
        1
    )


    # ========================================================
    # DATOS AÑO SELECCIONADO
    # ========================================================

    datos_año = df_base[

        df_base["Fecha"].dt.year
        ==
        año_seleccionado

    ].copy()


    # ========================================================
    # DATOS AÑO ANTERIOR
    # ========================================================

    datos_año_anterior = df_base[

        df_base["Fecha"].dt.year
        ==
        año_anterior

    ].copy()


    # ========================================================
    # MES DE CORTE
    # ========================================================

    if not datos_año.empty:

        mes_corte = (

            datos_año["Fecha"]
            .max()
            .month
        )

    else:

        mes_corte = 12


    # ========================================================
    # INGRESOS MENSUALES
    # ========================================================

    ingresos_actuales = (

        datos_año

        .groupby(
            datos_año["Fecha"].dt.month
        )["Ingreso"]

        .sum()
    )


    ingresos_anteriores = (

        datos_año_anterior

        .groupby(

            datos_año_anterior[
                "Fecha"
            ].dt.month

        )["Ingreso"]

        .sum()
    )


    meses_nombre = {

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


    comparacion = []


    for mes in range(

        1,

        mes_corte + 1

    ):

        comparacion.append({

            "Mes":
                meses_nombre[mes],

            str(año_seleccionado):

                float(
                    ingresos_actuales.get(
                        mes,
                        0
                    )
                ),

            str(año_anterior):

                float(
                    ingresos_anteriores.get(
                        mes,
                        0
                    )
                )

        })


    df_anual = pd.DataFrame(
        comparacion
    )


    # ========================================================
    # GRÁFICA ANUAL
    # ========================================================

    fig_anual = go.Figure()


    # AÑO ACTUAL / SELECCIONADO = BARRAS

    fig_anual.add_trace(

        go.Bar(

            x=df_anual["Mes"],

            y=df_anual[
                str(año_seleccionado)
            ],

            name=str(
                año_seleccionado
            ),

            marker_color="#00875A",

            opacity=0.88
        )
    )


    # AÑO ANTERIOR = LÍNEA

    fig_anual.add_trace(

        go.Scatter(

            x=df_anual["Mes"],

            y=df_anual[
                str(año_anterior)
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
            )
        )
    )


    fig_anual.update_layout(

        height=260,

        margin=dict(

            l=5,

            r=5,

            t=5,

            b=5
        ),

        template="plotly_white",

        hovermode="x unified",

        font=dict(

            family=
            "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",

            color="#172B4D"
        ),

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

            gridcolor="#E8ECF0"
        ),

        bargap=0.18
    )


    # ========================================================
    # PROMEDIO MENSUAL POR PROPIEDAD
    # ========================================================

    promedio = None

    fig_promedio = None


    if not datos_año.empty:

        promedio = (

            datos_año

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


        promedio["Meses"] = (

            (

                promedio[
                    "Fecha_Fin"
                ].dt.year

                -

                promedio[
                    "Fecha_Inicio"
                ].dt.year

            )

            *

            12

            +

            (

                promedio[
                    "Fecha_Fin"
                ].dt.month

                -

                promedio[
                    "Fecha_Inicio"
                ].dt.month

            )

            +

            1
        )


        promedio[
            "Promedio_Mensual"
        ] = (

            promedio["Ingreso"]

            /

            promedio["Meses"]
        )


        promedio = (

            promedio

            .sort_values(

                "Promedio_Mensual",

                ascending=False
            )
        )


        fig_promedio = go.Figure()


        fig_promedio.add_trace(

            go.Bar(

                x=promedio[
                    "Nombre_Propiedad"
                ],

                y=promedio[
                    "Promedio_Mensual"
                ],

                marker_color="#6554C0",

                opacity=0.88,

                text=[

                    compacto(x)

                    for x in promedio[
                        "Promedio_Mensual"
                    ]

                ],

                textposition="outside",

                textfont=dict(

                    size=9,

                    color="#172B4D",

                    family=
                    "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
                )

            )
        )


        fig_promedio.update_layout(

            height=260,

            margin=dict(

                l=5,

                r=5,

                t=15,

                b=5
            ),

            template="plotly_white",

            font=dict(

                family=
                "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",

                color="#172B4D"
            ),

            xaxis=dict(

                title=None,

                showgrid=False
            ),

            yaxis=dict(

                title=None,

                tickformat=",.0f",

                gridcolor="#E8ECF0"
            )
        )


    # ========================================================
    # GRÁFICAS ANUALES LADO A LADO
    # ========================================================

    anual1, anual2 = st.columns(

        2,

        gap="medium"
    )


    with anual1:

        st.markdown(

            f"""
<div class="section-title">

📊 Ingresos mensuales

</div>

<div class="section-subtitle">

Comparativo {año_seleccionado} vs {año_anterior}

</div>
""",

            unsafe_allow_html=True
        )


        st.plotly_chart(

            fig_anual,

            use_container_width=True,

            config={
                "displayModeBar": False
            },

            key="grafico_anual"
        )


    with anual2:

        st.markdown(

            f"""
<div class="section-title">

🏠 Promedio mensual por propiedad

</div>

<div class="section-subtitle">

Ingreso promedio mensual — {año_seleccionado}

</div>
""",

            unsafe_allow_html=True
        )


        if fig_promedio is not None:

            st.plotly_chart(

                fig_promedio,

                use_container_width=True,

                config={
                    "displayModeBar": False
                },

                key="grafico_promedio"
            )

        else:

            st.info(

                f"No hay datos para {año_seleccionado}."

            )


# ============================================================
# RESUMEN INFERIOR
# ============================================================

st.markdown("---")


p1, p2, p3, p4 = st.columns(4)


with p1:

    st.metric(

        "💵 Flujo del periodo",

        compacto(
            flujo_total
        )
    )


with p2:

    st.metric(

        "🏠 Propiedades",

        df_filtrado[
            "Nombre_Propiedad"
        ].nunique()
    )


with p3:

    st.metric(

        "👥 Socios",

        df_filtrado[
            "Nombre_Socio"
        ].nunique()
    )


with p4:

    st.markdown(

        """
<div style="
text-align:center;

padding:8px;

color:#52617A;

font-size:11px;

font-family:
-apple-system,
BlinkMacSystemFont,
'Segoe UI',
sans-serif;

font-weight:400;
">

📊

<br>

Más que propiedades,
mejores decisiones.

</div>
""",

        unsafe_allow_html=True
    )
