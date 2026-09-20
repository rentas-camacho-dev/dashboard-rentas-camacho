import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    /* =========================
       GENERAL
       ========================= */

    html, body, [class*="css"] {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Arial,
            sans-serif;
    }

    .stApp {
        background: #F4F6F8;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    div[data-testid="column"] {
        padding-left: 5px;
        padding-right: 5px;
    }


    /* =========================
       HEADER
       ========================= */

    .dashboard-title {
        color: #172B4D;
        font-size: 30px;
        font-weight: 600;
        line-height: 1.25;
        margin-top: 0;
        margin-bottom: 8px;
    }

    .dashboard-subtitle {
        color: #6B778C;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.5;
        margin-bottom: 25px;
    }


    /* =========================
       SECCIONES
       ========================= */

    .section-title {
        color: #172B4D;
        font-size: 22px;
        font-weight: 600;
        line-height: 1.3;
        margin-top: 0;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #6B778C;
        font-size: 12px;
        font-weight: 400;
        line-height: 1.5;
        margin-top: 0;
        margin-bottom: 12px;
    }

    .filters-title {
        color: #172B4D;
        font-size: 22px;
        font-weight: 600;
        line-height: 1.3;
        margin-top: 5px;
        margin-bottom: 10px;
    }


    /* =========================
       FILTROS
       ========================= */

    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        color: #52617A !important;
        font-size: 13px !important;
        font-weight: 400 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #EEF1F5 !important;
        border: 1px solid #E0E5EA !important;
        border-radius: 9px !important;
        min-height: 44px !important;
    }


    /* =========================
       KPI
       ========================= */

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #DDE3E8;
        border-radius: 14px;
        padding: 16px 18px 15px 18px;
        min-height: 116px;
        box-shadow: 0 2px 8px rgba(23,43,77,0.04);
    }

    .kpi-title {
        color: #52617A;
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 7px;
    }

    .kpi-value {
        color: #172B4D;
        font-size: 27px;
        font-weight: 400;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .kpi-change {
        display: inline-block;
        border-radius: 14px;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 400;
    }

    .positive {
        color: #138A4B;
        background: #E7F7EE;
    }

    .negative {
        color: #D92D20;
        background: #FDE8E7;
    }

    .neutral {
        color: #52617A;
        background: #EEF1F5;
    }


    /* =========================
       TABLA
       ========================= */

    .property-table {
        width: 100%;
        height: 500px;
        border: 1px solid #D5DCE3;
        border-radius: 13px;
        overflow: hidden;
        background: #F1F3F5;
    }

    .property-table table {
        width: 100%;
        height: 100%;
        border-collapse: collapse;
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            Arial,
            sans-serif;
        font-size: 13px;
    }

    .property-table thead th {
        background: #008F83;
        color: white;
        font-size: 13px;
        font-weight: 400;
        padding: 11px 10px;
        text-align: center;
    }

    .property-table thead th:first-child {
        text-align: left;
    }

    .property-table tbody td {
        color: #344563;
        font-size: 13px;
        font-weight: 400;
        padding: 9px 10px;
        border-bottom: 1px solid #DDE3E8;
        background: #F7F8FA;
        vertical-align: middle;
    }

    .property-name {
        color: #172B4D;
        font-weight: 400;
    }

    .income-text {
        color: #00875A;
        text-align: center;
        white-space: nowrap;
    }

    .expense-text {
        color: #DE350B;
        text-align: center;
        white-space: nowrap;
    }

    .flow-positive {
        color: #00875A;
        text-align: center;
        white-space: nowrap;
    }

    .flow-negative {
        color: #DE350B;
        text-align: center;
        white-space: nowrap;
    }

    .percent-value {
        color: #344563;
        font-size: 12px;
        text-align: right;
        margin-bottom: 3px;
    }

    .progress-background {
        height: 6px;
        width: 100%;
        background: #E5E9ED;
        border-radius: 5px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: #16B4D1;
        border-radius: 5px;
    }

    .status-cell {
        text-align: center;
        font-size: 15px;
    }

    .total-row td {
        background: #EAF0F4 !important;
        border-top: 1px solid #CBD5DE;
    }


    /* =========================
       GASTOS
       ========================= */

    .expense-box {
        background: #F1F3F5;
        border: 1px solid #D5DCE3;
        border-radius: 13px;
        min-height: 500px;
        padding: 12px 14px;
        overflow: hidden;
    }

    .expense-total {
        color: #172B4D;
        font-size: 22px;
        font-weight: 400;
        margin-top: 5px;
        margin-bottom: 3px;
    }

    .expense-total-subtitle {
        color: #7A869A;
        font-size: 10px;
        font-weight: 400;
        margin-bottom: 8px;
    }

    .expense-header {
        display: grid;
        grid-template-columns: 1fr 75px 38px;
        color: #52617A;
        font-size: 10px;
        font-weight: 400;
        border-bottom: 1px solid #DDE3E8;
        padding-bottom: 5px;
    }

    .expense-row {
        display: grid;
        grid-template-columns: 1fr 75px 38px;
        min-height: 30px;
        align-items: center;
        border-bottom: 1px solid #E2E6EA;
        color: #344563;
        font-size: 11px;
        font-weight: 400;
    }

    .expense-name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .expense-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        margin-right: 6px;
    }

    .expense-value {
        text-align: right;
        color: #172B4D;
        font-weight: 400;
    }

    .expense-percent {
        text-align: right;
        color: #7A869A;
        font-weight: 400;
    }

    .expense-highlight {
        margin-top: 12px;
        padding: 8px 9px;
        background: #EAF3FF;
        border: 1px solid #C7DDF8;
        border-radius: 7px;
        color: #52617A;
        font-size: 9px;
        font-weight: 400;
        line-height: 1.4;
    }

    .expense-highlight strong {
        font-weight: 400;
        color: #344563;
    }


    /* =========================
       ANALISIS ANUAL
       ========================= */

    .annual-title {
        color: #172B4D;
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 4px;
    }

    .annual-subtitle {
        color: #6B778C;
        font-size: 12px;
        font-weight: 400;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CREDENCIALES
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
    absoluto = abs(valor)

    if absoluto >= 1_000_000_000:
        return f"$ {valor / 1_000_000_000:.1f} B"

    if absoluto >= 1_000_000:
        return f"$ {valor / 1_000_000:.1f} M"

    if absoluto >= 1_000:
        return f"$ {valor / 1_000:.0f} mil"

    return f"$ {valor:,.0f}".replace(",", ".")


def cambio_porcentual(actual, anterior):

    if anterior == 0:
        return None

    return (
        (actual - anterior)
        / abs(anterior)
    )


def mostrar_kpi(
    titulo,
    valor,
    cambio,
    icono,
    es_pp=False
):

    if cambio is None:

        texto = "—"
        clase = "neutral"

    elif es_pp:

        pp = cambio * 100

        if pp >= 0:
            texto = f"↑ {pp:.1f} pp"
            clase = "positive"
        else:
            texto = f"↓ {abs(pp):.1f} pp"
            clase = "negative"

    else:

        if cambio >= 0:
            texto = f"↑ {cambio:.1%}"
            clase = "positive"
        else:
            texto = f"↓ {abs(cambio):.1%}"
            clase = "negative"

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                {icono} {titulo}
            </div>

            <div class="kpi-value">
                {moneda(valor)}
            </div>

            <span class="kpi-change {clase}">
                {texto}
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CARGAR DATOS
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


@st.cache_data(ttl=300)
def cargar_datos():

    return client.query(query).to_dataframe()


df = cargar_datos()


# ============================================================
# LIMPIEZA
# ============================================================

df["Fecha"] = pd.to_datetime(
    df["Fecha"],
    errors="coerce"
)

for col in [
    "Ingreso",
    "Gasto",
    "Valor",
    "Valor_Repartido",
    "Porcentaje"
]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)


for col in [
    "Ciudad",
    "Nombre_Propiedad",
    "Nombre_Socio",
    "Nombre_Subcategoria"
]:

    df[col] = (
        df[col]
        .fillna("Sin información")
        .astype(str)
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        🏠 Rentas Cortas — Airbnb
    </div>

    <div class="dashboard-subtitle">
        Ingresos, gastos y rentabilidad de tus propiedades
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    '<div class="filters-title">🔎 Filtros</div>',
    unsafe_allow_html=True
)

f1, f2, f3, f4 = st.columns(4)


with f1:

    ciudades = sorted(
        df["Ciudad"].dropna().unique()
    )

    ciudad = st.selectbox(
        "Ciudad",
        ["Todas"] + ciudades
    )


with f2:

    propiedades = sorted(
        df["Nombre_Propiedad"]
        .dropna()
        .unique()
    )

    propiedad = st.selectbox(
        "Propiedad",
        ["Todas"] + propiedades
    )


with f3:

    socios = sorted(
        df["Nombre_Socio"]
        .dropna()
        .unique()
    )

    socio = st.selectbox(
        "Socio",
        ["Todos"] + socios
    )


with f4:

    fecha_min = (
        df["Fecha"]
        .dropna()
        .min()
        .date()
    )

    fecha_max = (
        df["Fecha"]
        .dropna()
        .max()
        .date()
    )

    rango_fecha = st.date_input(
        "Fecha",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )


if (
    isinstance(rango_fecha, tuple)
    and len(rango_fecha) == 2
):

    fecha_inicio = pd.Timestamp(
        rango_fecha[0]
    )

    fecha_fin = (
        pd.Timestamp(rango_fecha[1])
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

else:

    fecha_inicio = pd.Timestamp(
        fecha_min
    )

    fecha_fin = (
        pd.Timestamp(fecha_max)
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )


# ============================================================
# FILTROS SIN FECHA
# ============================================================

df_graficos = df.copy()

if ciudad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Ciudad"] == ciudad
    ]

if propiedad != "Todas":

    df_graficos = df_graficos[
        df_graficos["Nombre_Propiedad"]
        == propiedad
    ]

if socio != "Todos":

    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"]
        == socio
    ]


# ============================================================
# FILTRO CON FECHA
# ============================================================

df_filtrado = df_graficos[
    (df_graficos["Fecha"] >= fecha_inicio)
    &
    (df_graficos["Fecha"] <= fecha_fin)
].copy()


# ============================================================
# KPIs
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
# PERIODO ANTERIOR
# ============================================================

duracion = (
    fecha_fin - fecha_inicio
)

fecha_anterior_fin = (
    fecha_inicio
    - pd.Timedelta(seconds=1)
)

fecha_anterior_inicio = (
    fecha_anterior_fin
    - duracion
)


df_anterior = df_graficos[
    (df_graficos["Fecha"] >= fecha_anterior_inicio)
    &
    (df_graficos["Fecha"] <= fecha_anterior_fin)
]


ingreso_anterior = df_anterior["Ingreso"].sum()

gasto_anterior = df_anterior["Gasto"].sum()

flujo_anterior = (
    ingreso_anterior
    - gasto_anterior
)

rentabilidad_anterior = (
    flujo_anterior / ingreso_anterior
    if ingreso_anterior != 0
    else 0
)


cambio_ingreso = cambio_porcentual(
    ingreso_total,
    ingreso_anterior
)

cambio_gasto = cambio_porcentual(
    gasto_total,
    gasto_anterior
)

cambio_flujo = cambio_porcentual(
    flujo_total,
    flujo_anterior
)

cambio_rentabilidad = (
    rentabilidad
    - rentabilidad_anterior
)


# ============================================================
# KPI ROW
# ============================================================

k1, k2, k3, k4 = st.columns(4)


with k1:

    mostrar_kpi(
        "Ingreso Total",
        ingreso_total,
        cambio_ingreso,
        "💰"
    )


with k2:

    mostrar_kpi(
        "Gasto Total",
        gasto_total,
        cambio_gasto,
        "📄"
    )


with k3:

    mostrar_kpi(
        "Flujo",
        flujo_total,
        cambio_flujo,
        "💵"
    )


with k4:

    mostrar_kpi(
        "Rentabilidad",
        rentabilidad,
        cambio_rentabilidad,
        "🎯",
        es_pp=True
    )


st.markdown(
    "<div style='height:16px'></div>",
    unsafe_allow_html=True
)


# ============================================================
# RESUMEN POR PROPIEDAD
# ============================================================

resumen = (
    df_filtrado
    .groupby("Nombre_Propiedad")
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

resumen["Rentabilidad"] = 0.0

mask_ingreso = (
    resumen["Ingreso"] != 0
)

resumen.loc[
    mask_ingreso,
    "Rentabilidad"
] = (
    resumen.loc[
        mask_ingreso,
        "Flujo"
    ]
    /
    resumen.loc[
        mask_ingreso,
        "Ingreso"
    ]
    * 100
)

resumen = resumen.sort_values(
    "Ingreso",
    ascending=False
)


# ============================================================
# DOS TARJETAS
# MISMO ALTO
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.55, 1],
    gap="large"
)


# ============================================================
# TABLA
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

    filas = ""

    for _, row in resumen.iterrows():

        ingreso = row["Ingreso"]
        gasto = row["Gasto"]
        flujo = row["Flujo"]
        rent = row["Rentabilidad"]

        if ingreso == 0:

            rent_text = "-"

        else:

            rent_text = f"{rent:.1f}%"

        if rent > 0:

            barra = min(
                max(rent, 0),
                100
            )

        else:

            barra = 0

        if flujo >= 0:

            flujo_html = (
                f'<span class="flow-positive">'
                f'{compacto(flujo)}'
                f'</span>'
            )

        else:

            flujo_html = (
                f'<span class="flow-negative">'
                f'{compacto(flujo)}'
                f'</span>'
            )

        if rent >= 80:

            estado = "🏆"

        elif rent >= 50:

            estado = "⚡"

        else:

            estado = "🚩"

        filas += f"""
        <tr>

            <td>
                <span class="property-name">
                    {row["Nombre_Propiedad"]}
                </span>
            </td>

            <td>
                <div class="income-text">
                    {compacto(ingreso)}
                </div>
            </td>

            <td>
                <div class="expense-text">
                    {compacto(gasto)}
                </div>
            </td>

            <td>
                {flujo_html}
            </td>

            <td>

                <div class="percent-value">
                    {rent_text}
                </div>

                <div class="progress-background">

                    <div
                        class="progress-fill"
                        style="width:{barra}%"
                    ></div>

                </div>

            </td>

            <td class="status-cell">
                {estado}
            </td>

        </tr>
        """


    total_flujo = (
        ingreso_total
        - gasto_total
    )

    filas += f"""
    <tr class="total-row">

        <td>
            <span class="property-name">
                Total
            </span>
        </td>

        <td>
            <div class="income-text">
                {compacto(ingreso_total)}
            </div>
        </td>

        <td>
            <div class="expense-text">
                {compacto(gasto_total)}
            </div>
        </td>

        <td>
            <div class="flow-positive">
                {compacto(total_flujo)}
            </div>
        </td>

        <td>

            <div class="percent-value">
                {rentabilidad * 100:.1f}%
            </div>

            <div class="progress-background">

                <div
                    class="progress-fill"
                    style="width:{min(max(rentabilidad * 100, 0), 100)}%"
                ></div>

            </div>

        </td>

        <td class="status-cell">
            🚩
        </td>

    </tr>
    """


    tabla_html = f"""
    <div class="property-table">

        <table>

            <thead>

                <tr>

                    <th style="width:30%;">
                        Propiedad
                    </th>

                    <th style="width:15%;">
                        Ingreso
                    </th>

                    <th style="width:15%;">
                        Gasto
                    </th>

                    <th style="width:15%;">
                        Flujo
                    </th>

                    <th style="width:20%;">
                        %
                    </th>

                    <th style="width:7%;">
                        Estado
                    </th>

                </tr>

            </thead>

            <tbody>

                {filas}

            </tbody>

        </table>

    </div>
    """

    st.markdown(
        tabla_html,
        unsafe_allow_html=True
    )


# ============================================================
# GASTOS
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

    # -----------------------------------------
    # DATOS DE GASTOS
    # -----------------------------------------

    gastos = (
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

    gasto_distribucion = (
        gastos["Gasto"].sum()
    )

    if gasto_distribucion > 0:

        gastos["Porcentaje"] = (
            gastos["Gasto"]
            /
            gasto_distribucion
            * 100
        )

    else:

        gastos["Porcentaje"] = 0


    # -----------------------------------------
    # TOP CATEGORÍA
    # -----------------------------------------

    if len(gastos) > 0:

        top_categoria = gastos.iloc[0]

        top_nombre = (
            top_categoria[
                "Nombre_Subcategoria"
            ]
        )

        top_valor = (
            top_categoria["Gasto"]
        )

        top_porcentaje = (
            top_categoria["Porcentaje"]
        )

    else:

        top_nombre = "Sin información"
        top_valor = 0
        top_porcentaje = 0


    # -----------------------------------------
    # AGRUPAR OTROS
    # -----------------------------------------

    top_n = 8

    if len(gastos) > top_n:

        principales = gastos.iloc[
            :top_n
        ].copy()

        otros_valor = (
            gastos.iloc[top_n:]["Gasto"]
            .sum()
        )

        otros_pct = (
            otros_valor
            /
            gasto_distribucion
            * 100
            if gasto_distribucion > 0
            else 0
        )

        otros = pd.DataFrame({
            "Nombre_Subcategoria": [
                "Otros"
            ],
            "Gasto": [
                otros_valor
            ],
            "Porcentaje": [
                otros_pct
            ]
        })

        gastos_grafico = pd.concat(
            [principales, otros],
            ignore_index=True
        )

    else:

        gastos_grafico = gastos.copy()


    # -----------------------------------------
    # COLORES
    # -----------------------------------------

    colores = [
        "#D71920",
        "#ED1B24",
        "#EF4056",
        "#F15B6C",
        "#F37483",
        "#F58D9A",
        "#F7A6AF",
        "#F8BEC5",
        "#E8D6D9"
    ]


    # -----------------------------------------
    # PIE / DONUT
    # -----------------------------------------

    fig_gastos = go.Figure(
        data=[
            go.Pie(
                labels=gastos_grafico[
                    "Nombre_Subcategoria"
                ],
                values=gastos_grafico[
                    "Gasto"
                ],
                hole=0.55,
                sort=False,
                textinfo="none",
                marker=dict(
                    colors=colores[
                        :len(gastos_grafico)
                    ],
                    line=dict(
                        color="#F1F3F5",
                        width=2
                    )
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "$%{value:,.0f}"
                    "<br>%{percent}"
                    "<extra></extra>"
                )
            )
        ]
    )

    fig_gastos.update_layout(
        height=390,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),
        paper_bgcolor="#F1F3F5",
        plot_bgcolor="#F1F3F5",
        showlegend=False,
        font=dict(
            family=(
                "-apple-system, "
                "BlinkMacSystemFont, "
                "Segoe UI, Roboto, Arial"
            ),
            color="#172B4D"
        ),
        annotations=[
            dict(
                text=(
                    f"<b>{top_porcentaje:.1f}%</b>"
                    f"<br>"
                    f"<span style='font-size:10px'>"
                    f"{top_nombre}"
                    f"</span>"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(
                    size=20,
                    color="#172B4D"
                )
            )
        ]
    )


    # -----------------------------------------
    # TARJETA DE GASTOS
    # -----------------------------------------

    st.markdown(
        '<div class="expense-box">',
        unsafe_allow_html=True
    )

    ec1, ec2 = st.columns(
        [1.05, 0.95],
        gap="small"
    )


    # -----------------------------------------
    # GRÁFICO
    # -----------------------------------------

    with ec1:

        st.plotly_chart(
            fig_gastos,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
            key="grafico_gastos"
        )


    # -----------------------------------------
    # DETALLE
    # -----------------------------------------

    with ec2:

        st.markdown(
            f"""
            <div class="expense-total">
                {moneda(gasto_distribucion)}
            </div>

            <div class="expense-total-subtitle">
                Total de egresos operativos
            </div>

            <div class="expense-header">

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
            """,
            unsafe_allow_html=True
        )


        filas_gasto = ""

        for i, (_, row) in enumerate(
            gastos_grafico.iterrows()
        ):

            color = colores[
                i % len(colores)
            ]

            nombre = row[
                "Nombre_Subcategoria"
            ]

            valor = row["Gasto"]

            pct = row["Porcentaje"]

            filas_gasto += f"""
            <div class="expense-row">

                <div class="expense-name">

                    <span
                        class="expense-dot"
                        style="background:{color};"
                    ></span>

                    {nombre}

                </div>

                <div class="expense-value">
                    {compacto(valor)}
                </div>

                <div class="expense-percent">
                    {pct:.1f}%
                </div>

            </div>
            """


        st.markdown(
            filas_gasto,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="expense-highlight">

                💡 Mayor centro de gasto:
                <strong>
                    {top_nombre}
                </strong>
                ({compacto(top_valor)})

                <br>

                Representa el
                {top_porcentaje:.1f}%
                del total de egresos operativos.

            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# ANÁLISIS ANUAL
# ============================================================

st.markdown(
    """
    <div class="annual-title">
        📊 Análisis anual
    </div>

    <div class="annual-subtitle">
        Comparación mensual y desempeño promedio de las propiedades
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SELECTOR DE AÑO
# ============================================================

años_disponibles = sorted(
    df_graficos[
        "Fecha"
    ]
    .dropna()
    .dt.year
    .unique()
    .tolist(),
    reverse=True
)

if len(años_disponibles) == 0:

    st.info(
        "No hay información suficiente para el análisis anual."
    )

    st.stop()


año_actual_sistema = pd.Timestamp.now().year

if (
    año_actual_sistema
    in años_disponibles
):

    año_default = (
        años_disponibles.index(
            año_actual_sistema
        )
    )

else:

    año_default = 0


año_seleccionado = st.selectbox(
    "Año de análisis",
    años_disponibles,
    index=año_default
)


año_anterior = (
    año_seleccionado - 1
)


# ============================================================
# DATOS AÑOS
# ============================================================

datos_año = df_graficos[
    df_graficos["Fecha"].dt.year
    == año_seleccionado
].copy()

datos_año_anterior = df_graficos[
    df_graficos["Fecha"].dt.year
    == año_anterior
].copy()


# ============================================================
# FECHA CORTE
# ============================================================

if len(datos_año) > 0:

    fecha_corte = (
        datos_año["Fecha"]
        .dropna()
        .max()
    )

    mes_corte = (
        fecha_corte.month
    )

else:

    mes_corte = 12


# ============================================================
# INGRESOS MENSUALES
# ============================================================

datos_año["Mes"] = (
    datos_año["Fecha"].dt.month
)

datos_año_anterior["Mes"] = (
    datos_año_anterior["Fecha"].dt.month
)


mensual_actual = (
    datos_año
    .groupby("Mes")["Ingreso"]
    .sum()
)

mensual_anterior = (
    datos_año_anterior
    .groupby("Mes")["Ingreso"]
    .sum()
)


meses = list(
    range(
        1,
        mes_corte + 1
    )
)


valores_actual = [
    mensual_actual.get(
        mes,
        0
    )
    for mes in meses
]

valores_anterior = [
    mensual_anterior.get(
        mes,
        0
    )
    for mes in meses
]


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

nombres_mostrar = [
    nombres_meses[m - 1]
    for m in meses
]


# ============================================================
# GRÁFICO INGRESOS
# BARRAS AÑO SELECCIONADO
# LÍNEA AÑO ANTERIOR
# ============================================================

fig_anual = go.Figure()


fig_anual.add_trace(
    go.Bar(
        x=nombres_mostrar,
        y=valores_actual,
        name=str(año_seleccionado),
        marker_color="#18A57B",
        hovertemplate=(
            f"{año_seleccionado}"
            "<br>$%{y:,.0f}"
            "<extra></extra>"
        )
    )
)


fig_anual.add_trace(
    go.Scatter(
        x=nombres_mostrar,
        y=valores_anterior,
        name=str(año_anterior),
        mode="lines+markers",
        line=dict(
            color="#1769E0",
            width=3
        ),
        marker=dict(
            size=6
        ),
        hovertemplate=(
            f"{año_anterior}"
            "<br>$%{y:,.0f}"
            "<extra></extra>"
        )
    )
)


fig_anual.update_layout(
    height=370,
    margin=dict(
        l=10,
        r=10,
        t=45,
        b=10
    ),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family=(
            "-apple-system, "
            "BlinkMacSystemFont, "
            "Segoe UI, Roboto, Arial"
        ),
        color="#172B4D"
    ),
    legend=dict(
        orientation="h",
        y=1.08,
        x=0.5,
        xanchor="center"
    ),
    xaxis=dict(
        title=None,
        showgrid=False
    ),
    yaxis=dict(
        title=None,
        gridcolor="#E6E9ED",
        tickprefix="$ "
    ),
    bargap=0.25
)


# ============================================================
# PROMEDIO MENSUAL POR PROPIEDAD
# ============================================================

datos_promedio = datos_año.copy()

promedio_propiedad = (
    datos_promedio
    .groupby("Nombre_Propiedad")
    .agg(
        Ingreso=("Ingreso", "sum"),
        Fecha_Inicio=("Fecha", "min"),
        Fecha_Fin=("Fecha", "max")
    )
    .reset_index()
)


def meses_transcurridos(
    fecha_inicio,
    fecha_fin
):

    if pd.isna(fecha_inicio):
        return 1

    if pd.isna(fecha_fin):
        return 1

    meses = (
        (fecha_fin.year - fecha_inicio.year)
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


promedio_propiedad[
    "Meses"
] = promedio_propiedad.apply(
    lambda row: meses_transcurridos(
        row["Fecha_Inicio"],
        row["Fecha_Fin"]
    ),
    axis=1
)


promedio_propiedad[
    "Promedio_Mensual"
] = (
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


# ============================================================
# GRÁFICO PROMEDIO
# ============================================================

fig_promedio = go.Figure()


fig_promedio.add_trace(
    go.Bar(
        x=promedio_propiedad[
            "Nombre_Propiedad"
        ],
        y=promedio_propiedad[
            "Promedio_Mensual"
        ],
        marker_color="#7567D9",
        text=[
            compacto(v)
            for v in promedio_propiedad[
                "Promedio_Mensual"
            ]
        ],
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>$%{y:,.0f}"
            "<extra></extra>"
        )
    )
)


fig_promedio.update_layout(
    height=370,
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10
    ),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(
        family=(
            "-apple-system, "
            "BlinkMacSystemFont, "
            "Segoe UI, Roboto, Arial"
        ),
        color="#172B4D"
    ),
    xaxis=dict(
        title=None,
        showgrid=False
    ),
    yaxis=dict(
        title=None,
        gridcolor="#E6E9ED",
        tickprefix="$ "
    )
)


# ============================================================
# DOS GRÁFICOS LADO A LADO
# ============================================================

g1, g2 = st.columns(
    [1, 1],
    gap="large"
)


with g1:

    st.markdown(
        f"""
        <div class="section-title">
            📊 Ingresos mensuales
        </div>

        <div class="section-subtitle">
            Comparativo de ingresos del año {año_seleccionado}
            contra {año_anterior}
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


with g2:

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
        key="grafico_promedio"
    )


# ============================================================
# TABLA PEQUEÑA PROMEDIO
# ============================================================

if len(promedio_propiedad) > 0:

    tabla_promedio = promedio_propiedad[
        [
            "Nombre_Propiedad",
            "Ingreso",
            "Meses",
            "Promedio_Mensual"
        ]
    ].copy()

    tabla_promedio.columns = [
        "Propiedad",
        "Ingreso total",
        "Meses",
        "Promedio mensual"
    ]

    tabla_promedio[
        "Ingreso total"
    ] = tabla_promedio[
        "Ingreso total"
    ].apply(compacto)

    tabla_promedio[
        "Promedio mensual"
    ] = tabla_promedio[
        "Promedio mensual"
    ].apply(compacto)

    st.dataframe(
        tabla_promedio,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FIN
# ============================================================
