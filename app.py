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
# ESTILOS
# ============================================================

st.markdown("""
<style>

    .stApp {
        background-color: #F5F7FA;
    }

    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #172B4D;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 15px;
        color: #6B778C;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #172B4D;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .kpi-card {
        background-color: white;
        padding: 20px 22px;
        border-radius: 14px;
        border: 1px solid #E6E9EF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        min-height: 120px;
    }

    .kpi-title {
        font-size: 14px;
        color: #6B778C;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #172B4D;
    }

    .kpi-green {
        color: #2E7D32;
    }

    .kpi-red {
        color: #C62828;
    }

    .kpi-blue {
        color: #1565C0;
    }

    .kpi-purple {
        color: #6A1B9A;
    }

    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 12px;
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
# CONSULTA
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


# Eliminar fechas inválidas
df = df.dropna(subset=["Fecha"])


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Filtros</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


# CIUDAD
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


# PROPIEDAD
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


# SOCIO
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


# FECHA
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
        df_graficos["Ciudad"].astype(str).isin(
            ciudad_seleccionada
        )
    ]


if propiedad_seleccionada:
    df_graficos = df_graficos[
        df_graficos["Nombre_Propiedad"].astype(str).isin(
            propiedad_seleccionada
        )
    ]


if socio_seleccionado:
    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"].astype(str).isin(
            socio_seleccionado
        )
    ]


# ============================================================
# FILTRO DE FECHA
# ============================================================

df_filtrado = df_graficos.copy()

if isinstance(rango_fecha, tuple) and len(rango_fecha) == 2:

    fecha_inicio = pd.Timestamp(rango_fecha[0])
    fecha_fin = pd.Timestamp(rango_fecha[1]) + pd.Timedelta(days=1)

    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= fecha_inicio) &
        (df_filtrado["Fecha"] < fecha_fin)
    ]


# ============================================================
# KPIs
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()
gasto_total = df_filtrado["Gasto"].sum()
flujo_total = ingreso_total - gasto_total

if ingreso_total != 0:
    rentabilidad = flujo_total / ingreso_total
else:
    rentabilidad = 0


def formato_moneda(valor):

    return f"${valor:,.0f}".replace(",", ".")


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
# RESUMEN POR PROPIEDAD
# ============================================================

st.markdown(
    '<div class="section-title">🏢 Resumen por propiedad</div>',
    unsafe_allow_html=True
)

if not df_filtrado.empty:

    resumen_propiedad = (
        df_filtrado
        .groupby("Nombre_Propiedad", dropna=False)
        .agg(
            Ingreso=("Ingreso", "sum"),
            Gasto=("Gasto", "sum")
        )
        .reset_index()
    )

    resumen_propiedad["Flujo"] = (
        resumen_propiedad["Ingreso"] -
        resumen_propiedad["Gasto"]
    )

    resumen_propiedad["%"] = resumen_propiedad.apply(
        lambda row:
            row["Flujo"] / row["Ingreso"]
            if row["Ingreso"] != 0
            else 0,
        axis=1
    )

    resumen_propiedad = resumen_propiedad.sort_values(
        "Ingreso",
        ascending=False
    )

    resumen_mostrar = resumen_propiedad.copy()

    resumen_mostrar["Ingreso"] = resumen_mostrar["Ingreso"].apply(
        formato_moneda
    )

    resumen_mostrar["Gasto"] = resumen_mostrar["Gasto"].apply(
        formato_moneda
    )

    resumen_mostrar["Flujo"] = resumen_mostrar["Flujo"].apply(
        formato_moneda
    )

    resumen_mostrar["%"] = resumen_mostrar["%"].apply(
        lambda x: f"{x:.1%}"
    )

    st.dataframe(
        resumen_mostrar,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No hay datos para los filtros seleccionados.")


# ============================================================
# GASTOS POR SUBCATEGORÍA
# ============================================================

st.markdown(
    '<div class="section-title">💸 Distribución de gastos</div>',
    unsafe_allow_html=True
)

if not df_filtrado.empty:

    gastos_subcategoria = (
        df_filtrado[
            df_filtrado["Gasto"] > 0
        ]
        .groupby("Nombre_Subcategoria")["Gasto"]
        .sum()
        .reset_index()
        .sort_values(
            "Gasto",
            ascending=False
        )
    )

    if not gastos_subcategoria.empty:

        fig_gastos = go.Figure(
            data=[
                go.Pie(
                    labels=gastos_subcategoria[
                        "Nombre_Subcategoria"
                    ],
                    values=gastos_subcategoria[
                        "Gasto"
                    ],
                    hole=0.58,
                    textinfo="percent",
                    hovertemplate=
                    "<b>%{label}</b><br>"
                    "$%{value:,.0f}<br>"
                    "%{percent}"
                    "<extra></extra>"
                )
            ]
        )

        fig_gastos.update_layout(
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation="v"
            )
        )

        st.plotly_chart(
            fig_gastos,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    else:

        st.info("No hay gastos para mostrar.")


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

    st.warning("No hay años disponibles para analizar.")

else:

    año_actual_sistema = pd.Timestamp.now().year

    if año_actual_sistema in años_disponibles:
        año_default = año_actual_sistema
    else:
        año_default = años_disponibles[0]

    indice_default = años_disponibles.index(
        año_default
    )

    año_seleccionado = st.selectbox(
        "Año de análisis",
        años_disponibles,
        index=indice_default
    )

    año_anterior = año_seleccionado - 1


    # ========================================================
    # DATOS POR AÑO
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
    # YTD VS LYTD
    # ========================================================

    st.markdown(
        f"#### Ingresos YTD — {año_seleccionado} vs {año_anterior}"
    )


    if not datos_año.empty:

        fecha_corte_anual = datos_año["Fecha"].max()

        mes_corte_anual = fecha_corte_anual.month
        dia_corte_anual = fecha_corte_anual.day

    else:

        mes_corte_anual = 12
        dia_corte_anual = 31


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
            datos_año_anterior["Fecha"].dt.month
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
    # TABLA DE COMPARACIÓN
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
                "Mes": meses_nombres[mes],
                str(año_seleccionado):
                    ingreso_actual,
                str(año_anterior):
                    ingreso_anterior
            }
        )


    df_comparacion = pd.DataFrame(
        comparacion_mensual
    )


    # ========================================================
    # GRÁFICO COMBINADO
    # ========================================================

    fig_mensual = go.Figure()


    # AÑO SELECCIONADO → BARRAS
    fig_mensual.add_trace(
        go.Bar(
            x=df_comparacion["Mes"],
            y=df_comparacion[
                str(año_seleccionado)
            ],
            name=str(año_seleccionado),
            marker_color="#2E7D32",
            opacity=0.85
        )
    )


    # AÑO ANTERIOR → LÍNEA
    fig_mensual.add_trace(
        go.Scatter(
            x=df_comparacion["Mes"],
            y=df_comparacion[
                str(año_anterior)
            ],
            name=str(año_anterior),
            mode="lines+markers",
            line=dict(
                color="#1565C0",
                width=3
            ),
            marker=dict(
                size=7
            )
        )
    )


    fig_mensual.update_layout(
        height=430,
        margin=dict(
            l=10,
            r=10,
            t=25,
            b=10
        ),
        template="plotly_white",
        hovermode="x unified",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        xaxis=dict(
            title="Mes",
            showgrid=False
        ),

        yaxis=dict(
            title="Ingresos",
            tickformat=",.0f",
            gridcolor="#EAEAEA"
        ),

        bargap=0.25
    )


    st.plotly_chart(
        fig_mensual,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


    # ========================================================
    # TABLA YTD
    # ========================================================

    total_actual = df_comparacion[
        str(año_seleccionado)
    ].sum()

    total_anterior = df_comparacion[
        str(año_anterior)
    ].sum()

    col_ytd1, col_ytd2, col_ytd3 = st.columns(3)


    with col_ytd1:

        st.metric(
            f"Ingresos {año_seleccionado}",
            formato_moneda(total_actual)
        )


    with col_ytd2:

        st.metric(
            f"Ingresos {año_anterior}",
            formato_moneda(total_anterior)
        )


    with col_ytd3:

        diferencia = (
            total_actual -
            total_anterior
        )

        st.metric(
            "Diferencia",
            formato_moneda(diferencia)
        )


    # ========================================================
    # PROMEDIO MENSUAL POR PROPIEDAD
    # ========================================================

    st.markdown(
        f"#### Promedio mensual de ingresos por propiedad — {año_seleccionado}"
    )


    datos_promedio = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_seleccionado
    ].copy()


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


        # ====================================================
        # MESES TRANSCURRIDOS
        # ====================================================

        promedio_propiedad["Meses"] = (
            (
                promedio_propiedad["Fecha_Fin"].dt.year
                -
                promedio_propiedad["Fecha_Inicio"].dt.year
            ) * 12
            +
            (
                promedio_propiedad["Fecha_Fin"].dt.month
                -
                promedio_propiedad["Fecha_Inicio"].dt.month
            )
            + 1
        )


        promedio_propiedad["Promedio_Mensual"] = (
            promedio_propiedad["Ingreso"]
            /
            promedio_propiedad["Meses"]
        )


        promedio_propiedad = (
            promedio_propiedad
            .sort_values(
                "Promedio_Mensual",
                ascending=False
            )
        )


        # ====================================================
        # GRÁFICO PROMEDIO
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
                marker_color="#6A1B9A",
                opacity=0.85,

                hovertemplate=
                "<b>%{x}</b><br>"
                "Promedio mensual: "
                "$%{y:,.0f}"
                "<extra></extra>"
            )
        )


        grafico_promedio.update_layout(
            height=430,
            margin=dict(
                l=10,
                r=10,
                t=25,
                b=10
            ),
            template="plotly_white",

            xaxis=dict(
                title="Propiedad",
                showgrid=False
            ),

            yaxis=dict(
                title="Ingreso promedio mensual",
                tickformat=",.0f",
                gridcolor="#EAEAEA"
            )
        )


        st.plotly_chart(
            grafico_promedio,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


        # ====================================================
        # TABLA PROMEDIO
        # ====================================================

        tabla_promedio = promedio_propiedad[
            [
                "Nombre_Propiedad",
                "Ingreso",
                "Meses",
                "Promedio_Mensual"
            ]
        ].copy()


        tabla_promedio = tabla_promedio.rename(
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


        tabla_promedio[
            "Ingreso Total"
        ] = tabla_promedio[
            "Ingreso Total"
        ].apply(
            formato_moneda
        )


        tabla_promedio[
            "Promedio Mensual"
        ] = tabla_promedio[
            "Promedio Mensual"
        ].apply(
            formato_moneda
        )


        st.dataframe(
            tabla_promedio,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            f"No hay datos para {año_seleccionado} con los filtros seleccionados."
        )
