import streamlit as st
import pandas as pd
import plotly.express as px

from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="FinQuery - Rentas Cortas Airbnb",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #F7F9FC;
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E6EAF0;
}

.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #172B4D;
    margin-bottom: 2px;
}

.subtitle {
    font-size: 15px;
    color: #718096;
    margin-bottom: 20px;
}

.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 22px;
    min-height: 125px;
    border: 1px solid #E5EAF1;
    box-shadow: 0px 4px 14px rgba(20, 40, 70, 0.06);
}

.kpi-title {
    font-size: 14px;
    color: #667085;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #172B4D;
}

.kpi-sub {
    font-size: 12px;
    color: #98A2B3;
    margin-top: 7px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #172B4D;
}

.section-subtitle {
    font-size: 13px;
    color: #718096;
    margin-bottom: 12px;
}

.info-card {
    background: #FFFFFF;
    border: 1px solid #E5EAF1;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0px 4px 14px rgba(20, 40, 70, 0.05);
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #DCE3EC;
    background-color: white;
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
# CARGAR DATOS
# ============================================================

@st.cache_data(ttl=600)
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

        FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`

        WHERE LOWER(TRIM(Nombre_Tipo)) = 'airbnb'
    """

    df = client.query(query).to_dataframe()

    df["Fecha"] = pd.to_datetime(
        df["Fecha"],
        errors="coerce"
    )

    for columna in [
        "Porcentaje",
        "Valor",
        "Valor_Repartido",
        "Ingreso",
        "Gasto"
    ]:

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        ).fillna(0)

    return df


# ============================================================
# CARGA
# ============================================================

try:

    df = cargar_datos()

except Exception as e:

    st.error(
        "❌ No fue posible cargar los datos desde BigQuery."
    )

    st.code(str(e))

    st.stop()


if df.empty:

    st.warning(
        "No se encontraron movimientos de Airbnb."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:27px;
            font-weight:700;
            color:#172B4D;
            margin-top:5px;
        ">
            FinQuery
        </div>

        <div style="
            font-size:13px;
            color:#718096;
            margin-top:4px;
            margin-bottom:28px;
        ">
            Rentas Cortas - Camacho
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### 🏠 Airbnb"
    )

    st.caption(
        "Vista exclusiva de ingresos y gastos Airbnb"
    )

    st.divider()

    st.markdown(
        "**Datos conectados a BigQuery**"
    )

    st.caption(
        "Movimientos_Operativos_Reparto"
    )


# ============================================================
# ENCABEZADO
# ============================================================

titulo, boton = st.columns(
    [4, 1]
)


with titulo:

    st.markdown(
        '<div class="main-title">'
        'Rentas Cortas - Airbnb'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Resumen de ingresos y gastos operativos'
        '</div>',
        unsafe_allow_html=True
    )


with boton:

    if st.button(
        "🔄 Actualizar",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# ============================================================
# FILTROS
# ============================================================

f1, f2, f3, f4 = st.columns(
    [1, 1, 1, 1.35]
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

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades
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

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades
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

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios
    )


# ------------------------------------------------------------
# FECHA
# ------------------------------------------------------------

with f4:

    fecha_min = df["Fecha"].min().date()

    fecha_max = df["Fecha"].max().date()

    rango = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()


if ciudad != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Ciudad"].astype(str) == ciudad
    ]


if propiedad != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Nombre_Propiedad"].astype(str)
        == propiedad
    ]


if socio != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Nombre_Socio"].astype(str)
        == socio
    ]


if isinstance(rango, tuple) and len(rango) == 2:

    fecha_inicio = pd.Timestamp(
        rango[0]
    )

    fecha_fin = (
        pd.Timestamp(rango[1])
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= fecha_inicio)
        &
        (df_filtrado["Fecha"] <= fecha_fin)
    ]


# ============================================================
# INDICADORES
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()

gasto_total = df_filtrado["Gasto"].sum()

flujo_total = (
    ingreso_total
    - gasto_total
)

rentabilidad = (
    flujo_total / ingreso_total
    if ingreso_total != 0
    else 0
)


# ============================================================
# KPI
# ============================================================

k1, k2, k3, k4 = st.columns(4)


# ------------------------------------------------------------
# INGRESO
# ------------------------------------------------------------

with k1:

    st.markdown(
        f"""
        <div class="kpi-card"
             style="border-left:5px solid #20A464;">

            <div class="kpi-title">
                💰 Ingreso Total
            </div>

            <div class="kpi-value"
                 style="color:#168A52;">

                $ {ingreso_total:,.0f}

            </div>

            <div class="kpi-sub">
                Ingresos Airbnb
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# GASTO
# ------------------------------------------------------------

with k2:

    st.markdown(
        f"""
        <div class="kpi-card"
             style="border-left:5px solid #F04438;">

            <div class="kpi-title">
                💸 Gasto
            </div>

            <div class="kpi-value"
                 style="color:#E53935;">

                $ {gasto_total:,.0f}

            </div>

            <div class="kpi-sub">
                Gastos operativos Airbnb
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# FLUJO
# ------------------------------------------------------------

with k3:

    st.markdown(
        f"""
        <div class="kpi-card"
             style="border-left:5px solid #3B82F6;">

            <div class="kpi-title">
                📈 Flujo
            </div>

            <div class="kpi-value">

                $ {flujo_total:,.0f}

            </div>

            <div class="kpi-sub">
                Ingreso - Gasto
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# RENTABILIDAD
# ------------------------------------------------------------

with k4:

    st.markdown(
        f"""
        <div class="kpi-card"
             style="border-left:5px solid #8B5CF6;">

            <div class="kpi-title">
                📊 Rentabilidad
            </div>

            <div class="kpi-value"
                 style="color:#7C3AED;">

                {rentabilidad:.1%}

            </div>

            <div class="kpi-sub">
                Flujo / Ingreso
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# DESEMPEÑO POR PROPIEDAD
# ============================================================

col_tabla, col_dona = st.columns(
    [1.25, 0.75]
)


with col_tabla:

    st.markdown(
        '<div class="section-title">'
        '🏠 Desempeño por Propiedad'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Ingresos, gastos y flujo por propiedad Airbnb'
        '</div>',
        unsafe_allow_html=True
    )


    resumen = (
        df_filtrado
        .groupby(
            "Nombre_Propiedad",
            dropna=False
        )
        .agg(
            Ingreso=("Ingreso", "sum"),
            Gasto=("Gasto", "sum")
        )
        .reset_index()
    )


    resumen["Flujo"] = (
        resumen["Ingreso"]
        - resumen["Gasto"]
    )


    resumen["%"] = resumen.apply(
        lambda x:
            x["Flujo"] / x["Ingreso"]
            if x["Ingreso"] != 0
            else 0,
        axis=1
    )


    resumen = resumen.sort_values(
        "Ingreso",
        ascending=False
    )


    def formato_dinero(valor):

        if abs(valor) >= 1_000_000:

            return (
                f"$ {valor / 1_000_000:.1f} M"
            )

        elif abs(valor) >= 1_000:

            return (
                f"$ {valor / 1_000:.0f} mil"
            )

        else:

            return (
                f"$ {valor:,.0f}"
            )


    resumen_display = resumen.copy()


    resumen_display["Ingreso"] = (
        resumen_display["Ingreso"]
        .apply(formato_dinero)
    )


    resumen_display["Gasto"] = (
        resumen_display["Gasto"]
        .apply(formato_dinero)
    )


    resumen_display["Flujo"] = (
        resumen_display["Flujo"]
        .apply(formato_dinero)
    )


    resumen_display["%"] = (
        resumen_display["%"]
        .apply(
            lambda x: f"{x:.1%}"
        )
    )


    resumen_display = resumen_display.rename(
        columns={
            "Nombre_Propiedad": "Propiedad"
        }
    )


    st.dataframe(
        resumen_display[
            [
                "Propiedad",
                "Ingreso",
                "Gasto",
                "Flujo",
                "%"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=350
    )


    total_ingreso = resumen["Ingreso"].sum()

    total_gasto = resumen["Gasto"].sum()

    total_flujo = resumen["Flujo"].sum()


    total_rentabilidad = (
        total_flujo / total_ingreso
        if total_ingreso != 0
        else 0
    )


    st.markdown(
        f"""
        <div style="
            background:#F0F4F8;
            border-radius:10px;
            padding:12px 15px;
            display:flex;
            justify-content:space-between;
            color:#172B4D;
            font-weight:700;
            font-size:13px;
        ">

            <span>Total</span>

            <span>
                $ {total_ingreso / 1_000_000:.1f} M
            </span>

            <span>
                $ {total_gasto / 1_000_000:.1f} M
            </span>

            <span>
                $ {total_flujo / 1_000_000:.1f} M
            </span>

            <span>
                {total_rentabilidad:.1%}
            </span>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


# ============================================================
# GASTOS POR SUBCATEGORÍA
# ============================================================

with col_dona:

    st.markdown(
        '<div class="section-title">'
        '💸 Gastos por Subcategoría'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Distribución de los gastos operativos Airbnb'
        '</div>',
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

        fig_dona = px.pie(
            gastos,
            names="Nombre_Subcategoria",
            values="Gasto",
            hole=0.55
        )


        fig_dona.update_traces(
            textinfo="percent",
            textposition="inside",
            hovertemplate=
                "<b>%{label}</b><br>"
                "$ %{value:,.0f}"
                "<extra></extra>"
        )


        fig_dona.update_layout(
            height=390,
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),
            legend=dict(
                orientation="v",
                x=1,
                y=0.5
            ),
            showlegend=True
        )


        st.plotly_chart(
            fig_dona,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    else:

        st.info(
            "No hay gastos para los filtros seleccionados."
        )


# ============================================================
# INGRESOS MES YTD VS LYTD
# ============================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-title">'
    '📈 Ingresos mes YTD vs LYTD'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-subtitle">'
    'Comparación de ingresos del año en curso frente al mismo período del año anterior'
    '</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# FECHA DE CORTE
# ------------------------------------------------------------

fecha_corte = df_filtrado["Fecha"].max()

año_actual = fecha_corte.year

año_anterior = año_actual - 1

mes_corte = fecha_corte.month


# ------------------------------------------------------------
# CREAR COLUMNAS AÑO / MES
# ------------------------------------------------------------

df_ytd = df_filtrado.copy()

df_ytd["Año"] = (
    df_ytd["Fecha"].dt.year
)

df_ytd["Mes"] = (
    df_ytd["Fecha"].dt.month
)


# ------------------------------------------------------------
# AÑO ACTUAL
# ------------------------------------------------------------

df_actual = df_ytd[
    df_ytd["Año"] == año_actual
].copy()


# ------------------------------------------------------------
# AÑO ANTERIOR
# ------------------------------------------------------------

df_anterior = df_ytd[
    df_ytd["Año"] == año_anterior
].copy()


# ------------------------------------------------------------
# INGRESOS MENSUALES
# ------------------------------------------------------------

actual_mensual = (
    df_actual
    .groupby("Mes")["Ingreso"]
    .sum()
    .reset_index()
)


anterior_mensual = (
    df_anterior
    .groupby("Mes")["Ingreso"]
    .sum()
    .reset_index()
)


# ------------------------------------------------------------
# COMPLETAR LOS 12 MESES
# ------------------------------------------------------------

meses = pd.DataFrame({
    "Mes": range(1, 13)
})


actual_mensual = meses.merge(
    actual_mensual,
    on="Mes",
    how="left"
)


anterior_mensual = meses.merge(
    anterior_mensual,
    on="Mes",
    how="left"
)


actual_mensual["Ingreso"] = (
    actual_mensual["Ingreso"]
    .fillna(0)
)


anterior_mensual["Ingreso"] = (
    anterior_mensual["Ingreso"]
    .fillna(0)
)


# ------------------------------------------------------------
# HASTA EL MES DE CORTE
# ------------------------------------------------------------

actual_mensual = actual_mensual[
    actual_mensual["Mes"] <= mes_corte
]


anterior_mensual = anterior_mensual[
    anterior_mensual["Mes"] <= mes_corte
]


# ------------------------------------------------------------
# NOMBRES DE MESES
# ------------------------------------------------------------

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


actual_mensual["Mes_Nombre"] = (
    actual_mensual["Mes"]
    .map(nombres_meses)
)


anterior_mensual["Mes_Nombre"] = (
    anterior_mensual["Mes"]
    .map(nombres_meses)
)


# ------------------------------------------------------------
# TOTALES YTD
# ------------------------------------------------------------

total_ytd_actual = (
    actual_mensual["Ingreso"].sum()
)


total_ytd_anterior = (
    anterior_mensual["Ingreso"].sum()
)


# ------------------------------------------------------------
# VARIACIÓN
# ------------------------------------------------------------

variacion_ytd = (

    (
        total_ytd_actual
        / total_ytd_anterior
    ) - 1

    if total_ytd_anterior != 0

    else 0

)


# ------------------------------------------------------------
# TARJETAS YTD
# ------------------------------------------------------------

y1, y2, y3 = st.columns(3)


with y1:

    st.markdown(
        f"""
        <div class="info-card">

            <div style="
                font-size:13px;
                color:#718096;
            ">
                YTD {año_actual}
            </div>

            <div style="
                font-size:27px;
                font-weight:700;
                color:#172B4D;
                margin-top:5px;
            ">
                $ {total_ytd_actual / 1_000_000:.1f} M
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


with y2:

    st.markdown(
        f"""
        <div class="info-card">

            <div style="
                font-size:13px;
                color:#718096;
            ">
                LYTD {año_anterior}
            </div>

            <div style="
                font-size:27px;
                font-weight:700;
                color:#172B4D;
                margin-top:5px;
            ">
                $ {total_ytd_anterior / 1_000_000:.1f} M
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


with y3:

    st.markdown(
        f"""
        <div class="info-card">

            <div style="
                font-size:13px;
                color:#718096;
            ">
                Variación YTD
            </div>

            <div style="
                font-size:27px;
                font-weight:700;
                color:#168A52;
                margin-top:5px;
            ">
                {variacion_ytd:+.1%}
            </div>

        </div>
        """.replace("\n", ""),
        unsafe_allow_html=True
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# GRÁFICO YTD VS LYTD
# ------------------------------------------------------------

grafico_ytd = pd.DataFrame({

    "Mes": actual_mensual["Mes_Nombre"],

    str(año_actual):
        actual_mensual["Ingreso"].values,

    str(año_anterior):
        anterior_mensual["Ingreso"].values

})


fig_ytd = px.line(
    grafico_ytd,
    x="Mes",
    y=[
        str(año_actual),
        str(año_anterior)
    ],
    markers=True
)


fig_ytd.update_layout(

    height=360,

    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    ),

    xaxis_title="",

    yaxis_title="",

    hovermode="x unified",

    legend_title=""

)


fig_ytd.update_traces(

    hovertemplate=
        "<b>%{fullData.name}</b><br>"
        "$ %{y:,.0f}"
        "<extra></extra>"

)


st.plotly_chart(
    fig_ytd,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


# ============================================================
# INGRESO PROMEDIO MENSUAL POR PROPIEDAD
# ============================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-title">'
    '💰 Ingreso promedio mensual por propiedad'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="section-subtitle">'
    'Ingreso acumulado dividido por los meses corridos de operación de cada propiedad'
    '</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# FECHA FINAL
# ------------------------------------------------------------

fecha_final = df_filtrado["Fecha"].max()


# ------------------------------------------------------------
# INGRESO POR PROPIEDAD
# ------------------------------------------------------------

propiedad_ingresos = (

    df_filtrado

    .groupby("Nombre_Propiedad")

    .agg(

        Ingreso=("Ingreso", "sum"),

        Primera_Fecha=("Fecha", "min")

    )

    .reset_index()

)


# ------------------------------------------------------------
# MESES CORRIDOS
# ------------------------------------------------------------

def calcular_meses_corridos(
    fecha_inicio,
    fecha_fin
):

    if (
        pd.isna(fecha_inicio)
        or pd.isna(fecha_fin)
    ):

        return 1


    meses = (

        (
            fecha_fin.year
            - fecha_inicio.year
        )
        * 12

        +

        (
            fecha_fin.month
            - fecha_inicio.month
        )

        + 1

    )


    return max(
        meses,
        1
    )


propiedad_ingresos[
    "Meses_Corridos"
] = propiedad_ingresos.apply(

    lambda fila:

        calcular_meses_corridos(

            fila["Primera_Fecha"],

            fecha_final

        ),

    axis=1

)


# ------------------------------------------------------------
# PROMEDIO MENSUAL
# ------------------------------------------------------------

propiedad_ingresos[
    "Promedio_Mensual"
] = (

    propiedad_ingresos["Ingreso"]

    /

    propiedad_ingresos["Meses_Corridos"]

)


# ------------------------------------------------------------
# ORDENAR
# ------------------------------------------------------------

propiedad_ingresos = (
    propiedad_ingresos
    .sort_values(
        "Promedio_Mensual",
        ascending=False
    )
)


# ------------------------------------------------------------
# GRÁFICO
# ------------------------------------------------------------

fig_promedio = px.bar(

    propiedad_ingresos,

    x="Nombre_Propiedad",

    y="Promedio_Mensual"

)


fig_promedio.update_traces(

    hovertemplate=

        "<b>%{x}</b><br>"
        "Promedio mensual: $ %{y:,.0f}"
        "<extra></extra>"

)


fig_promedio.update_layout(

    height=360,

    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    ),

    xaxis_title="",

    yaxis_title="",

    showlegend=False

)


st.plotly_chart(

    fig_promedio,

    use_container_width=True,

    config={
        "displayModeBar": False
    }

)


# ============================================================
# TABLA PROMEDIO
# ============================================================

st.markdown(
    '<div class="section-subtitle">'
    'Detalle utilizado para calcular el promedio'
    '</div>',
    unsafe_allow_html=True
)


tabla_promedio = (
    propiedad_ingresos.copy()
)


tabla_promedio["Ingreso"] = (
    tabla_promedio["Ingreso"]
    .apply(formato_dinero)
)


tabla_promedio[
    "Promedio_Mensual"
] = (

    tabla_promedio[
        "Promedio_Mensual"
    ]

    .apply(formato_dinero)

)


tabla_promedio = (
    tabla_promedio
    .rename(

        columns={

            "Nombre_Propiedad":
                "Propiedad",

            "Ingreso":
                "Ingreso acumulado",

            "Meses_Corridos":
                "Meses corridos",

            "Promedio_Mensual":
                "Promedio mensual"

        }

    )
)


st.dataframe(

    tabla_promedio[

        [
            "Propiedad",
            "Ingreso acumulado",
            "Meses corridos",
            "Promedio mensual"
        ]

    ],

    use_container_width=True,

    hide_index=True

)


# ============================================================
# PIE
# ============================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


st.caption(

    f"🏠 Airbnb · "
    f"{len(df_filtrado):,} movimientos · "
    f"Período hasta "
    f"{fecha_final.strftime('%d/%m/%Y')} · "
    f"Fuente: Movimientos_Operativos_Reparto"

)
