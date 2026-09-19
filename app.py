import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Rentas Cortas - Airbnb",
    page_icon="🏠",
    layout="wide"
)


# ============================================================
# ESTILOS GENERALES
# ============================================================

st.markdown("""
<style>

    .stApp {
        background-color: #F5F7FA;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    .main-title {
        font-size: 31px;
        font-weight: 700;
        color: #172B4D;
        margin-bottom: 2px;
    }

    .subtitle {
        font-size: 14px;
        color: #6B778C;
        margin-bottom: 15px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #172B4D;
        margin-top: 14px;
        margin-bottom: 8px;
    }

    .mini-title {
        font-size: 17px;
        font-weight: 700;
        color: #172B4D;
        margin-bottom: 5px;
    }

    .mini-subtitle {
        font-size: 12px;
        color: #6B778C;
        margin-bottom: 8px;
    }

    /* ========================================================
       KPIs
    ======================================================== */

    .kpi-card {
        background-color: white;
        padding: 16px 20px;
        border-radius: 13px;
        border: 1px solid #E6E9EF;
        box-shadow: 0 2px 7px rgba(0,0,0,0.04);
        min-height: 102px;
    }

    .kpi-title {
        font-size: 13px;
        color: #6B778C;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 26px;
        font-weight: 700;
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
       TABLA
    ======================================================== */

    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 12px;
    }

    /* ========================================================
       SELECTBOX
    ======================================================== */

    div[data-baseweb="select"] {
        border-radius: 8px;
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
# TÍTULO
# ============================================================

st.markdown(
    '<div class="main-title">🏠 Rentas Cortas — Airbnb</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Análisis de ingresos, gastos y rentabilidad de las propiedades Airbnb</div>',
    unsafe_allow_html=True
)


# ============================================================
# CONSULTA BIGQUERY
# ============================================================

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


# ============================================================
# PREPARACIÓN DE DATOS
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
        return f"{signo}$ {valor_abs / 1_000_000_000:.1f} B"

    elif valor_abs >= 1_000_000:
        return f"{signo}$ {valor_abs / 1_000_000:.1f} M"

    elif valor_abs >= 1_000:
        return f"{signo}$ {valor_abs / 1_000:.0f} mil"

    else:
        return (
            f"{signo}$ {valor_abs:,.0f}"
            .replace(",", ".")
        )


def estado_porcentaje(porcentaje):

    if porcentaje >= 0.80:
        return "🏆"

    elif porcentaje >= 0.50:
        return "⚡"

    else:
        return "🚩"


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Filtros</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


# ------------------------------------------------------------
# CIUDAD
# ------------------------------------------------------------

with col1:

    ciudades = sorted(
        df["Ciudad"]
        .dropna()
        .astype(str)
        .unique()
    )

    ciudad_seleccionada = st.multiselect(
        "Ciudad",
        ciudades
    )


# ------------------------------------------------------------
# PROPIEDAD
# ------------------------------------------------------------

with col2:

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .astype(str)
        .unique()
    )

    propiedad_seleccionada = st.multiselect(
        "Propiedad",
        propiedades
    )


# ------------------------------------------------------------
# SOCIO
# ------------------------------------------------------------

with col3:

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .astype(str)
        .unique()
    )

    socio_seleccionado = st.multiselect(
        "Socio",
        socios
    )


# ------------------------------------------------------------
# FECHA
# ------------------------------------------------------------

with col4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    rango_fecha = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
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
        .isin(ciudad_seleccionada)
    ]


if propiedad_seleccionada:

    df_graficos = df_graficos[
        df_graficos["Nombre_Propiedad"]
        .astype(str)
        .isin(propiedad_seleccionada)
    ]


if socio_seleccionado:

    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"]
        .astype(str)
        .isin(socio_seleccionado)
    ]


# ============================================================
# FILTRO DE FECHA
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
        (df_filtrado["Fecha"] >= fecha_inicio)
        &
        (df_filtrado["Fecha"] < fecha_fin)
    ]


# ============================================================
# KPIs
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()
gasto_total = df_filtrado["Gasto"].sum()

flujo_total = (
    ingreso_total -
    gasto_total
)

rentabilidad = (
    flujo_total / ingreso_total
    if ingreso_total != 0
    else 0
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Ingreso Total</div>
            <div class="kpi-value kpi-green">
                {formato_moneda(ingreso_total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Gasto</div>
            <div class="kpi-value kpi-red">
                {formato_moneda(gasto_total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with k3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Flujo</div>
            <div class="kpi-value kpi-blue">
                {formato_moneda(flujo_total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with k4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Rentabilidad</div>
            <div class="kpi-value kpi-purple">
                {rentabilidad:.1%}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TABLA + DISTRIBUCIÓN DE GASTOS
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.55, 1],
    gap="medium"
)


# ============================================================
# TABLA POR PROPIEDAD
# ============================================================

with col_tabla:

    st.markdown(
        '<div class="section-title">🏢 Resumen por propiedad</div>',
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
                Ingreso=("Ingreso", "sum"),
                Gasto=("Gasto", "sum")
            )
            .reset_index()
        )

        resumen_propiedad["Flujo"] = (
            resumen_propiedad["Ingreso"]
            -
            resumen_propiedad["Gasto"]
        )

        resumen_propiedad["%"] = (
            resumen_propiedad.apply(
                lambda row:
                (
                    row["Flujo"] /
                    row["Ingreso"]
                )
                if row["Ingreso"] != 0
                else 0,
                axis=1
            )
        )

        resumen_propiedad["Estado"] = (
            resumen_propiedad["%"]
            .apply(estado_porcentaje)
        )

        resumen_propiedad = (
            resumen_propiedad
            .sort_values(
                "Ingreso",
                ascending=False
            )
        )


        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        total_ingreso = (
            resumen_propiedad["Ingreso"].sum()
        )

        total_gasto = (
            resumen_propiedad["Gasto"].sum()
        )

        total_flujo = (
            resumen_propiedad["Flujo"].sum()
        )

        total_pct = (
            total_flujo / total_ingreso
            if total_ingreso != 0
            else 0
        )


        fila_total = pd.DataFrame(
            [{
                "Nombre_Propiedad": "Total",
                "Ingreso": total_ingreso,
                "Gasto": total_gasto,
                "Flujo": total_flujo,
                "%": total_pct,
                "Estado": estado_porcentaje(
                    total_pct
                )
            }]
        )


        tabla_propiedades = pd.concat(
            [
                resumen_propiedad[
                    [
                        "Nombre_Propiedad",
                        "Ingreso",
                        "Gasto",
                        "Flujo",
                        "%",
                        "Estado"
                    ]
                ],
                fila_total
            ],
            ignore_index=True
        )


        # ----------------------------------------------------
        # ESTILOS
        # ----------------------------------------------------

        def colorear_ingresos(valor):

            return "color: #00875A; font-weight: 600"


        def colorear_gastos(valor):

            return "color: #DE350B; font-weight: 600"


        def colorear_flujo(valor):

            if valor < 0:
                return (
                    "color: #DE350B; "
                    "font-weight: 700"
                )

            return (
                "color: #00875A; "
                "font-weight: 700"
            )


        def colorear_porcentaje(valor):

            if valor < 0:
                return (
                    "color: #DE350B; "
                    "font-weight: 600"
                )

            return (
                "color: #172B4D; "
                "font-weight: 600"
            )


        tabla_styled = (
            tabla_propiedades
            .style

            .format(
                {
                    "Ingreso": formato_compacto,
                    "Gasto": formato_compacto,
                    "Flujo": formato_compacto,
                    "%": "{:.1%}"
                }
            )

            .map(
                colorear_ingresos,
                subset=["Ingreso"]
            )

            .map(
                colorear_gastos,
                subset=["Gasto"]
            )

            .map(
                colorear_flujo,
                subset=["Flujo"]
            )

            .map(
                colorear_porcentaje,
                subset=["%"]
            )

            .bar(
                subset=["%"],
                align="zero",
                vmin=0,
                vmax=1,
                color="#16B5D1"
            )

            .set_properties(
                **{
                    "font-size": "13px",
                    "padding": "9px 10px"
                }
            )

            .set_table_styles(
                [
                    {
                        "selector": "th",
                        "props": [
                            (
                                "background-color",
                                "#008577"
                            ),
                            (
                                "color",
                                "white"
                            ),
                            (
                                "font-weight",
                                "700"
                            ),
                            (
                                "font-size",
                                "13px"
                            )
                        ]
                    },
                    {
                        "selector": "tbody tr:last-child",
                        "props": [
                            (
                                "font-weight",
                                "700"
                            ),
                            (
                                "background-color",
                                "#F8FAFC"
                            ),
                            (
                                "border-top",
                                "2px solid #DDE3EA"
                            )
                        ]
                    }
                ]
            )
        )


        st.dataframe(
            tabla_styled,
            use_container_width=True,
            hide_index=True,
            height=420,
            column_config={
                "Nombre_Propiedad": st.column_config.TextColumn(
                    "Propiedad"
                ),
                "Ingreso": st.column_config.TextColumn(
                    "Ingreso"
                ),
                "Gasto": st.column_config.TextColumn(
                    "Gasto"
                ),
                "Flujo": st.column_config.TextColumn(
                    "Flujo"
                ),
                "%": st.column_config.TextColumn(
                    "%"
                ),
                "Estado": st.column_config.TextColumn(
                    "",
                    width="small"
                )
            }
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
            gastos_subcategoria["Gasto"].sum()
        )


        # ----------------------------------------------------
        # TOP 7 + OTROS
        # ----------------------------------------------------

        top_n = 7

        if len(gastos_subcategoria) > top_n:

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
                gastos_subcategoria.copy()
            )


        # ----------------------------------------------------
        # MAYOR GASTO
        # ----------------------------------------------------

        mayor_gasto = (
            gastos_pie.iloc[0]
        )

        mayor_categoria = (
            mayor_gasto[
                "Nombre_Subcategoria"
            ]
        )

        mayor_valor = float(
            mayor_gasto["Gasto"]
        )

        mayor_pct = (
            mayor_valor /
            gasto_total_grafico
            if gasto_total_grafico != 0
            else 0
        )


        # ----------------------------------------------------
        # COLORES
        # ----------------------------------------------------

        colores = [
            "#D9232E",
            "#ED1C24",
            "#E83B5A",
            "#F05A66",
            "#F57A87",
            "#F99BA5",
            "#F7BDC3",
            "#F4D7DA"
        ]


        # ----------------------------------------------------
        # DONA
        # ----------------------------------------------------

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
            y=0.54,
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
            text=str(
                mayor_categoria
            ),
            showarrow=False,
            font=dict(
                size=10,
                color="#7A869A"
            )
        )


        fig_gastos.update_layout(
            height=310,
            margin=dict(
                l=0,
                r=0,
                t=5,
                b=5
            ),
            showlegend=False,
            template="plotly_white"
        )


        # ----------------------------------------------------
        # TABLA DESGLOSE
        # ----------------------------------------------------

        desglose_gastos = (
            gastos_pie[
                [
                    "Nombre_Subcategoria",
                    "Gasto"
                ]
            ]
            .copy()
        )

        desglose_gastos["%"] = (
            desglose_gastos["Gasto"]
            /
            gasto_total_grafico
        )


        desglose_gastos = (
            desglose_gastos
            .rename(
                columns={
                    "Nombre_Subcategoria":
                        "Categoría",
                    "Gasto":
                        "Valor"
                }
            )
        )


        desglose_styled = (
            desglose_gastos
            .style
            .format(
                {
                    "Valor": formato_compacto,
                    "%": "{:.1%}"
                }
            )
            .set_properties(
                **{
                    "font-size": "12px",
                    "padding": "5px 5px"
                }
            )
        )


        # ----------------------------------------------------
        # DONA + TABLA
        # ----------------------------------------------------

        dona_col, lista_col = st.columns(
            [1, 1.15],
            gap="small"
        )


        with dona_col:

            st.plotly_chart(
                fig_gastos,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


        with lista_col:

            st.markdown(
                f"**Desglose por subcategoría**"
            )

            st.caption(
                f"Total gastos: {formato_moneda(gasto_total_grafico)}"
            )

            st.dataframe(
                desglose_styled,
                use_container_width=True,
                hide_index=True,
                height=315,
                column_config={
                    "Categoría":
                        st.column_config.TextColumn(
                            "Categoría"
                        ),
                    "Valor":
                        st.column_config.TextColumn(
                            "Valor"
                        ),
                    "%":
                        st.column_config.TextColumn(
                            "%"
                        )
                }
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


# ============================================================
# AÑOS DISPONIBLES
# ============================================================

años_disponibles = sorted(
    df["Fecha"]
    .dropna()
    .dt.year
    .unique(),
    reverse=True
)


if not años_disponibles:

    st.warning(
        "No hay años disponibles para analizar."
    )

else:

    año_actual_sistema = pd.Timestamp.now().year


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
    # DATOS AÑOS
    # ========================================================

    datos_año = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_seleccionado
    ].copy()


    datos_año_anterior = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_anterior
    ].copy()


    # ========================================================
    # CORTE
    # ========================================================

    if not datos_año.empty:

        fecha_corte_anual = (
            datos_año["Fecha"].max()
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
            datos_año["Fecha"].dt.month
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


    # ========================================================
    # COMPARACIÓN MENSUAL
    # ========================================================

    comparacion_mensual = []


    for mes in range(
        1,
        mes_corte_anual + 1
    ):

        ingreso_actual = float(
            ingresos_actual.get(
                mes,
                0
            )
        )

        ingreso_anterior = float(
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
                    ingreso_actual,

                str(
                    año_anterior
                ):
                    ingreso_anterior
            }
        )


    df_comparacion = pd.DataFrame(
        comparacion_mensual
    )


    # ========================================================
    # GRÁFICA INGRESOS
    # ========================================================

    fig_mensual = go.Figure()


    # AÑO SELECCIONADO = BARRAS

    fig_mensual.add_trace(
        go.Bar(
            x=df_comparacion["Mes"],

            y=df_comparacion[
                str(año_seleccionado)
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


    # AÑO ANTERIOR = LÍNEA

    fig_mensual.add_trace(
        go.Scatter(
            x=df_comparacion["Mes"],

            y=df_comparacion[
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
    # PROMEDIO MENSUAL POR PROPIEDAD
    # ========================================================

    datos_promedio = df_graficos[
        df_graficos["Fecha"].dt.year ==
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


        promedio_propiedad["Meses"] = (

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


        # ----------------------------------------------------
        # GRÁFICA
        # ----------------------------------------------------

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

    st.markdown(
        "#### 📊 Comparación anual y desempeño por propiedad"
    )


    grafico1, grafico2 = st.columns(
        [1, 1],
        gap="medium"
    )


    with grafico1:

        st.markdown(
            f"**Ingresos {año_seleccionado} vs {año_anterior}**"
        )

        st.plotly_chart(
            fig_mensual,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    with grafico2:

        st.markdown(
            f"**Promedio mensual por propiedad — {año_seleccionado}**"
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


    col_ytd1, col_ytd2, col_ytd3 = (
        st.columns(3)
    )


    with col_ytd1:

        st.metric(
            f"Ingresos {año_seleccionado}",
            formato_moneda(
                total_actual
            )
        )


    with col_ytd2:

        st.metric(
            f"Ingresos {año_anterior}",
            formato_moneda(
                total_anterior
            )
        )


    with col_ytd3:

        st.metric(
            "Diferencia",
            formato_moneda(
                diferencia
            )
        )


    # ========================================================
    # TABLA PROMEDIO
    # ========================================================

    if promedio_propiedad is not None:

        st.markdown(
            f"#### 🏠 Detalle promedio mensual por propiedad — {año_seleccionado}"
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
            hide_index=True
        )
