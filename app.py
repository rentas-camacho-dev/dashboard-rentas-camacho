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

    st.error("❌ No fue posible cargar los datos desde BigQuery.")
    st.code(str(e))
    st.stop()


if df.empty:

    st.warning("No se encontraron movimientos de Airbnb.")
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
        '<div class="main-title">Rentas Cortas - Airbnb</div>',
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
# KPI 1 - INGRESO
# ============================================================

k1, k2, k3, k4 = st.columns(4)


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


# ============================================================
# KPI 2 - GASTO
# ============================================================

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


# ============================================================
# KPI 3 - FLUJO
# ============================================================

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


# ============================================================
# KPI 4 - RENTABILIDAD
# ============================================================

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


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# TABLA + DONUT
# ============================================================

col_tabla, col_dona = st.columns(
    [1.25, 0.75]
)


# ============================================================
# DESEMPEÑO POR PROPIEDAD
# ============================================================

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


    # --------------------------------------------------------
    # FORMATO
    # --------------------------------------------------------

    resumen_display = resumen.copy()


    def formato_dinero(valor):

        if abs(valor) >= 1_000_000:

            return f"$ {valor / 1_000_000:.1f} M"

        elif abs(valor) >= 1_000:

            return f"$ {valor / 1_000:.0f} mil"

        else:

            return f"$ {valor:,.0f}"


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


    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

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
# DONUT GASTOS
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
# INGRESOS MENSUALES
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">'
    '📊 Ingresos Mensuales'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Evolución de ingresos Airbnb'
    '</div>',
    unsafe_allow_html=True
)


df_mensual = df_filtrado.copy()


df_mensual["Mes"] = (
    df_mensual["Fecha"]
    .dt.to_period("M")
    .dt.to_timestamp()
)


mensual = (
    df_mensual
    .groupby("Mes")["Ingreso"]
    .sum()
    .reset_index()
)


if not mensual.empty:

    fig_mensual = px.bar(
        mensual,
        x="Mes",
        y="Ingreso"
    )


    fig_mensual.update_traces(
        hovertemplate=
            "<b>%{x|%b %Y}</b><br>"
            "$ %{y:,.0f}"
            "<extra></extra>"
    )


    fig_mensual.update_layout(
        height=320,
        margin=dict(
            l=20,
            r=20,
            t=10,
            b=20
        ),
        xaxis_title="",
        yaxis_title="",
        hovermode="x unified"
    )


    fig_mensual.update_xaxes(
        dtick="M1",
        tickformat="%b"
    )


    st.plotly_chart(
        fig_mensual,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# INGRESOS YTD
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

col_ytd, col_ytd_info = st.columns(
    [3, 1]
)


with col_ytd:

    st.markdown(
        '<div class="section-title">'
        '📈 Ingresos YTD'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Ingresos acumulados durante el año'
        '</div>',
        unsafe_allow_html=True
    )


    ytd = df_filtrado.copy()

    ytd["Año"] = ytd["Fecha"].dt.year

    ytd["Mes"] = ytd["Fecha"].dt.month


    ytd_mensual = (
        ytd
        .groupby(
            ["Año", "Mes"]
        )["Ingreso"]
        .sum()
        .reset_index()
    )


    ytd_mensual = ytd_mensual.sort_values(
        ["Año", "Mes"]
    )


    ytd_mensual["Acumulado"] = (
        ytd_mensual
        .groupby("Año")["Ingreso"]
        .cumsum()
    )


    if not ytd_mensual.empty:

        fig_ytd = px.line(
            ytd_mensual,
            x="Mes",
            y="Acumulado",
            color="Año",
            markers=True
        )


        fig_ytd.update_layout(
            height=320,
            margin=dict(
                l=20,
                r=20,
                t=10,
                b=20
            ),
            xaxis_title="",
            yaxis_title="",
            hovermode="x unified"
        )


        fig_ytd.update_xaxes(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=[
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
        )


        fig_ytd.update_traces(
            hovertemplate=
                "<b>%{x}</b><br>"
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
# TARJETA YTD
# ============================================================

with col_ytd_info:

    if not ytd_mensual.empty:

        años = sorted(
            ytd_mensual["Año"].unique()
        )

        año_actual = años[-1]


        datos_año = ytd_mensual[
            ytd_mensual["Año"] == año_actual
        ]


        if not datos_año.empty:

            valor_ytd = datos_año[
                "Acumulado"
            ].iloc[-1]


            st.markdown(
                f"""
                <div class="info-card"
                     style="margin-top:35px;">

                    <div style="
                        color:#718096;
                        font-size:13px;
                    ">
                        YTD {año_actual}
                    </div>

                    <div style="
                        font-size:28px;
                        font-weight:700;
                        color:#172B4D;
                        margin-top:7px;
                    ">
                        $ {valor_ytd / 1_000_000:.1f} M
                    </div>

                    <div style="
                        color:#168A52;
                        font-size:13px;
                        margin-top:10px;
                    ">
                        Ingreso acumulado
                    </div>

                </div>
                """.replace("\n", ""),
                unsafe_allow_html=True
            )


# ============================================================
# PIE
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.caption(
    f"🏠 Airbnb · {len(df_filtrado):,} movimientos · "
    f"Fuente: Movimientos_Operativos_Reparto"
)
