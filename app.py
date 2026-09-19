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
# ESTILOS STREAMLIT
# ============================================================

st.markdown("""
<style>

    .stApp {
        background-color: #F5F7FA;
    }

    .block-container {
        max-width: 100%;
        padding-top: 0.65rem;
        padding-bottom: 0.8rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .section-title {
        font-size: 19px;
        font-weight: 750;
        color: #172B4D;
        margin-top: 8px;
        margin-bottom: 3px;
    }

    .section-subtitle {
        font-size: 11px;
        color: #6B778C;
        margin-bottom: 6px;
    }

    label {
        font-size: 12px !important;
        color: #344563 !important;
    }

    div[data-baseweb="select"] {
        border-radius: 8px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 11px;
        overflow: hidden;
    }

    .stDownloadButton button {
        border-radius: 8px;
        border: 1px solid #D7DEE7;
        background: white;
        color: #172B4D;
        font-size: 11px;
        padding: 4px 10px;
    }

    hr {
        border-color: #E6E9EF;
        margin: 7px 0;
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


@st.cache_data(
    ttl=300,
    show_spinner=False
)
def cargar_datos():

    credentials = (
        service_account
        .Credentials
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

    return client.query(
        QUERY
    ).to_dataframe()


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
    valor = abs(valor)

    if valor >= 1_000_000_000:
        return f"{signo}$ {valor / 1_000_000_000:.1f} B"

    if valor >= 1_000_000:
        return f"{signo}$ {valor / 1_000_000:.1f} M"

    if valor >= 1_000:
        return f"{signo}$ {valor / 1_000:.0f} mil"

    return (
        f"{signo}${valor:,.0f}"
        .replace(",", ".")
    )


def porcentaje_cambio(
    actual,
    anterior
):

    if anterior == 0:
        return None

    return (
        (actual - anterior)
        / abs(anterior)
    )


def estado_porcentaje(
    porcentaje
):

    if porcentaje >= 0.80:
        return "🏆"

    if porcentaje >= 0.50:
        return "⚡"

    return "🚩"


# ============================================================
# ENCABEZADO
# ============================================================

header1, header2 = st.columns(
    [2.6, 1]
)

with header1:

    st.markdown(
        """
        <div style="
            font-size:30px;
            font-weight:750;
            color:#172B4D;
            line-height:1.05;">
            🏠 Rentas Cortas — Airbnb
        </div>

        <div style="
            font-size:13px;
            color:#6B778C;
            margin-top:3px;">
            Ingresos, gastos y rentabilidad de tus propiedades
        </div>
        """,
        unsafe_allow_html=True
    )


with header2:

    ultima_fecha = df["Fecha"].max()

    fecha_texto = (
        ultima_fecha.strftime("%d %b %Y")
        if not pd.isna(ultima_fecha)
        else "—"
    )

    st.markdown(
        f"""
        <div style="
            text-align:right;
            color:#6B778C;
            font-size:10px;">
            Último dato disponible
        </div>

        <div style="
            text-align:right;
            color:#172B4D;
            font-size:12px;
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

f1, f2, f3, f4 = st.columns(4)


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
        placeholder="Todas"
    )


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
        placeholder="Todas"
    )


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
        placeholder="Todos"
    )


with f4:

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
# APLICAR FILTROS
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
# FILTRO FECHA
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
        +
        pd.Timedelta(days=1)
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
# KPIs
# ============================================================

ingreso_total = df_filtrado[
    "Ingreso"
].sum()

gasto_total = df_filtrado[
    "Gasto"
].sum()

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
        inicio_periodo -
        pd.Timedelta(days=1)
    )

    inicio_anterior = (
        fin_anterior -
        pd.Timedelta(
            days=dias_periodo - 1
        )
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


    if not df_anterior.empty:

        ingreso_anterior = (
            df_anterior[
                "Ingreso"
            ].sum()
        )

        gasto_anterior = (
            df_anterior[
                "Gasto"
            ].sum()
        )

        flujo_anterior = (
            ingreso_anterior -
            gasto_anterior
        )

        rent_anterior = (
            flujo_anterior /
            ingreso_anterior
            if ingreso_anterior != 0
            else 0
        )

        delta_income = porcentaje_cambio(
            ingreso_total,
            ingreso_anterior
        )

        delta_expense = porcentaje_cambio(
            gasto_total,
            gasto_anterior
        )

        delta_flow = porcentaje_cambio(
            flujo_total,
            flujo_anterior
        )

        delta_profit = (
            rentabilidad -
            rent_anterior
        )


# ============================================================
# HTML KPI
# ============================================================

def html_kpi(
    titulo,
    valor,
    color,
    delta=None,
    porcentaje=False
):

    delta_html = ""

    if delta is not None:

        if porcentaje:

            delta_text = (
                f"{delta * 100:+.1f} pp"
            )

        else:

            delta_text = (
                f"{delta * 100:+.1f}%"
            )

        color_delta = (
            "#00875A"
            if delta >= 0
            else "#DE350B"
        )

        flecha = (
            "↑"
            if delta >= 0
            else "↓"
        )

        delta_html = f"""
        <div style="
            margin-top:6px;
            font-size:10px;
            color:{color_delta};">

            {flecha} {delta_text}

            <span style="
                color:#97A0AF;">
                vs periodo anterior
            </span>

        </div>
        """


    return f"""
    <!DOCTYPE html>

    <html>

    <head>

    <meta charset="utf-8">

    <style>

        * {{
            box-sizing:border-box;
        }}

        body {{
            margin:0;
            background:transparent;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;
        }}

        .card {{
            background:white;
            border:1px solid #E3E7EC;
            border-radius:14px;
            padding:14px 17px;
            height:94px;
            box-shadow:
                0 2px 7px rgba(0,0,0,.035);
        }}

        .title {{
            font-size:12px;
            color:#6B778C;
            margin-bottom:5px;
        }}

        .value {{
            font-size:26px;
            font-weight:750;
            line-height:1.1;
            color:{color};
        }}

    </style>

    </head>

    <body>

        <div class="card">

            <div class="title">
                {html.escape(titulo)}
            </div>

            <div class="value">
                {html.escape(valor)}
            </div>

            {delta_html}

        </div>

    </body>

    </html>
    """


# ============================================================
# KPI EN UNA FILA
# ============================================================

k1, k2, k3, k4 = st.columns(
    [1, 1, 1, 1],
    gap="medium"
)


with k1:

    components.html(
        html_kpi(
            "Ingreso Total",
            formato_moneda(
                ingreso_total
            ),
            "#00875A",
            delta_income
        ),
        height=101,
        scrolling=False
    )


with k2:

    components.html(
        html_kpi(
            "Gasto Total",
            formato_moneda(
                gasto_total
            ),
            "#DE350B",
            delta_expense
        ),
        height=101,
        scrolling=False
    )


with k3:

    components.html(
        html_kpi(
            "Flujo",
            formato_moneda(
                flujo_total
            ),
            "#0065FF",
            delta_flow
        ),
        height=101,
        scrolling=False
    )


with k4:

    components.html(
        html_kpi(
            "Rentabilidad",
            f"{rentabilidad:.1%}",
            "#6554C0",
            delta_profit,
            porcentaje=True
        ),
        height=101,
        scrolling=False
    )


# ============================================================
# RESUMEN + GASTOS
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.58, 1],
    gap="medium"
)


# ============================================================
# TABLA PROPIEDADES
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
                row["Flujo"]
                /
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


        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # HTML TABLA
        # ----------------------------------------------------

        filas = ""


        for _, row in (
            resumen_propiedad.iterrows()
        ):

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


            flujo_color = (
                "#00875A"
                if flujo >= 0
                else "#DE350B"
            )


            filas += f"""
            <tr>

                <td class="property">
                    {nombre}
                </td>

                <td class="number income">
                    {formato_compacto(ingreso)}
                </td>

                <td class="number expense">
                    {formato_compacto(gasto)}
                </td>

                <td
                    class="number"
                    style="color:{flujo_color};"
                >
                    {formato_compacto(flujo)}
                </td>

                <td>

                    <div class="pct-value">
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

                </td>

                <td class="status">
                    {estado}
                </td>

            </tr>
            """


        total_width = min(
            max(
                total_pct * 100,
                0
            ),
            100
        )


        html_tabla = f"""
        <!DOCTYPE html>

        <html>

        <head>

        <meta charset="utf-8">

        <style>

        * {{
            box-sizing:border-box;
        }}

        body {{
            margin:0;
            background:transparent;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;
        }}

        .card {{
            background:white;
            border:1px solid #E1E5EA;
            border-radius:13px;
            overflow:hidden;
        }}

        table {{
            width:100%;
            border-collapse:collapse;
            table-layout:fixed;
        }}

        th {{
            background:#008A7A;
            color:white;
            padding:10px 8px;
            font-size:11px;
            font-weight:700;
            text-align:left;
        }}

        th:nth-child(1) {{
            width:24%;
        }}

        th:nth-child(2) {{
            width:14%;
            text-align:right;
        }}

        th:nth-child(3) {{
            width:14%;
            text-align:right;
        }}

        th:nth-child(4) {{
            width:14%;
            text-align:right;
        }}

        th:nth-child(5) {{
            width:25%;
            text-align:right;
        }}

        th:nth-child(6) {{
            width:9%;
            text-align:center;
        }}

        td {{
            padding:8px;
            border-bottom:1px solid #EDF0F2;
            font-size:11px;
            color:#172B4D;
            vertical-align:middle;
        }}

        tr:last-child td {{
            border-bottom:none;
        }}

        .property {{
            font-weight:600;
        }}

        .number {{
            text-align:right;
            white-space:nowrap;
        }}

        .income {{
            color:#00875A;
            font-weight:600;
        }}

        .expense {{
            color:#DE350B;
            font-weight:600;
        }}

        .pct-value {{
            text-align:right;
            font-size:10px;
            font-weight:600;
            margin-bottom:3px;
        }}

        .bar-bg {{
            width:100%;
            height:6px;
            background:#EDF1F5;
            border-radius:4px;
            overflow:hidden;
        }}

        .bar-fill {{
            height:100%;
            background:#16B5D1;
            border-radius:4px;
        }}

        .status {{
            text-align:center;
            font-size:16px;
        }}

        .total td {{
            background:#F8FAFC;
            border-top:2px solid #DDE3EA;
            font-weight:700;
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

            <td>
                Total
            </td>

            <td class="number income">
                {formato_compacto(total_ingreso)}
            </td>

            <td class="number expense">
                {formato_compacto(total_gasto)}
            </td>

            <td class="number"
                style="color:#00875A;">
                {formato_compacto(total_flujo)}
            </td>

            <td>

                <div class="pct-value">
                    {total_pct:.1%}
                </div>

                <div class="bar-bg">

                    <div
                        class="bar-fill"
                        style="
                            width:{total_width}%;
                        ">
                    </div>

                </div>

            </td>

            <td class="status">
                {estado_porcentaje(total_pct)}
            </td>

        </tr>

        </tbody>

        </table>

        </div>

        </body>

        </html>
        """


        altura_tabla = (
            52
            +
            len(resumen_propiedad) * 42
            + 44
        )


        components.html(
            html_tabla,
            height=min(
                max(
                    altura_tabla,
                    180
                ),
                500
            ),
            scrolling=False
        )


        csv_propiedades = (
            resumen_propiedad
            .to_csv(
                index=False
            )
            .encode("utf-8-sig")
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
# UNA SOLA TARJETA DE GASTOS
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

        gasto_total = (
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

            top = (
                gastos_subcategoria
                .head(top_n)
                .copy()
            )

            otros_valor = (
                gastos_subcategoria
                .iloc[top_n:][
                    "Gasto"
                ]
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
                    top,
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

        mayor_categoria = (
            str(
                mayor[
                    "Nombre_Subcategoria"
                ]
            )
        )

        mayor_valor = float(
            mayor["Gasto"]
        )

        mayor_pct = (
            mayor_valor /
            gasto_total
            if gasto_total != 0
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
        # PIE
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
            text=(
                f"<b>{mayor_pct:.1%}</b>"
            ),
            showarrow=False,
            font=dict(
                size=18,
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
                size=9,
                color="#7A869A"
            )
        )


        fig_gastos.update_layout(
            height=245,

            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),

            showlegend=False,

            template="plotly_white"
        )


        # ====================================================
        # HTML LISTA
        # ====================================================

        filas_gastos = ""


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
                gasto_total
                if gasto_total != 0
                else 0
            )

            filas_gastos += f"""
            <div class="expense-row">

                <div class="expense-left">

                    <span
                        class="dot"
                        style="
                            background:
                            {colores[i]};
                        ">
                    </span>

                    <span class="expense-name">
                        {categoria}
                    </span>

                </div>

                <div class="expense-right">

                    <strong>
                        {formato_compacto(valor)}
                    </strong>

                    <span class="expense-pct">
                        {pct:.1%}
                    </span>

                </div>

            </div>
            """


        # ====================================================
        # ÚNICA TARJETA COMPLETA
        # ====================================================

        html_gastos = f"""
        <!DOCTYPE html>

        <html>

        <head>

        <meta charset="utf-8">

        <style>

        * {{
            box-sizing:border-box;
        }}

        body {{
            margin:0;
            background:transparent;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Arial,
                sans-serif;
        }}

        .card {{
            background:white;
            border:1px solid #E1E5EA;
            border-radius:13px;
            overflow:hidden;
            padding:14px;
        }}

        .header {{
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            margin-bottom:7px;
        }}

        .title {{
            font-size:16px;
            font-weight:700;
            color:#172B4D;
        }}

        .total {{
            font-size:16px;
            font-weight:700;
            color:#172B4D;
        }}

        .subtitle {{
            font-size:10px;
            color:#7A869A;
            margin-top:1px;
        }}

        .content {{
            display:grid;
            grid-template-columns:46% 54%;
            gap:8px;
            align-items:center;
        }}

        .chart {{
            display:flex;
            justify-content:center;
            align-items:center;
        }}

        .list {{
            padding-left:2px;
        }}

        .table-header {{
            display:grid;
            grid-template-columns:1fr auto auto;
            gap:8px;
            padding-bottom:5px;
            border-bottom:1px solid #E6E9EF;
            color:#6B778C;
            font-size:10px;
            font-weight:700;
        }}

        .expense-row {{
            display:grid;
            grid-template-columns:1fr auto;
            align-items:center;
            min-height:27px;
            padding:2px 4px;
            border-bottom:1px solid #F0F2F4;
        }}

        .expense-row:last-child {{
            border-bottom:none;
        }}

        .expense-left {{
            display:flex;
            align-items:center;
            gap:6px;
            min-width:0;
        }}

        .dot {{
            width:7px;
            height:7px;
            min-width:7px;
            border-radius:50%;
        }}

        .expense-name {{
            color:#344563;
            font-size:10px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }}

        .expense-right {{
            display:flex;
            align-items:center;
            gap:7px;
            color:#172B4D;
            font-size:10px;
            white-space:nowrap;
        }}

        .expense-pct {{
            color:#7A869A;
        }}

        .highlight {{
            background:#F5F9FF;
            border-radius:5px;
        }}

        </style>

        </head>

        <body>

        <div class="card">

            <div class="header">

                <div>
                    <div class="title">
                        Distribución de gastos
                    </div>

                    <div class="subtitle">
                        Desglose por subcategoría
                    </div>
                </div>

                <div class="total">
                    {formato_compacto(gasto_total)}
                </div>

            </div>


            <div class="content">

                <div class="chart">

                    <iframe
                        srcdoc="{html.escape(
                            fig_gastos.to_html(
                                include_plotlyjs='cdn',
                                full_html=False
                            )
                        )}"
                        style="
                            width:100%;
                            height:250px;
                            border:none;
                        ">
                    </iframe>

                </div>


                <div class="list">

                    <div class="table-header">

                        <span>
                            Subcategoría
                        </span>

                        <span>
                            Valor
                        </span>

                        <span>
                            %
                        </span>

                    </div>

                    {filas_gastos}

                </div>

            </div>

        </div>

        </body>

        </html>
        """


        # ====================================================
        # NOTA:
        # Plotly dentro de iframe puede ser pesado.
        # Por eso hacemos una versión más simple usando
        # el gráfico directamente debajo si hiciera falta.
        # ====================================================

        # Para máxima estabilidad visual:
        card_col1, card_col2 = st.columns(
            [0.92, 1.08],
            gap="small"
        )


        with card_col1:

            st.plotly_chart(
                fig_gastos,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


        with card_col2:

            html_lista = f"""
            <!DOCTYPE html>

            <html>

            <head>

            <style>

            * {{
                box-sizing:border-box;
            }}

            body {{
                margin:0;
                background:transparent;
                font-family:
                    -apple-system,
                    BlinkMacSystemFont,
                    "Segoe UI",
                    Arial,
                    sans-serif;
            }}

            .box {{
                background:white;
                border:1px solid #E1E5EA;
                border-radius:13px;
                padding:12px;
            }}

            .total {{
                color:#172B4D;
                font-size:16px;
                font-weight:700;
                margin-bottom:2px;
            }}

            .sub {{
                color:#7A869A;
                font-size:10px;
                margin-bottom:7px;
            }}

            .row {{
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:5px 3px;
                border-bottom:1px solid #F0F2F4;
                gap:6px;
            }}

            .row:last-child {{
                border-bottom:none;
            }}

            .left {{
                display:flex;
                align-items:center;
                gap:5px;
                min-width:0;
            }}

            .dot {{
                width:7px;
                height:7px;
                min-width:7px;
                border-radius:50%;
            }}

            .name {{
                font-size:10px;
                color:#344563;
                white-space:nowrap;
                overflow:hidden;
                text-overflow:ellipsis;
            }}

            .right {{
                font-size:10px;
                color:#172B4D;
                white-space:nowrap;
                font-weight:600;
            }}

            .pct {{
                color:#7A869A;
                margin-left:5px;
                font-weight:400;
            }}

            </style>

            </head>

            <body>

            <div class="box">

                <div class="total">
                    {formato_compacto(gasto_total)}
                </div>

                <div class="sub">
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
                    gasto_total
                )


                html_lista += f"""
                <div class="row">

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


            html_lista += """
            </div>

            </body>

            </html>
            """


            components.html(
                html_lista,
                height=285,
                scrolling=False
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
    .dropna()
    .dt.year
    .unique(),
    reverse=True
)


if años_disponibles:

    año_actual_sistema = (
        pd.Timestamp.now().year
    )


    año_default = (
        año_actual_sistema
        if año_actual_sistema
        in años_disponibles
        else años_disponibles[0]
    )


    año_seleccionado = st.selectbox(
        "Año de análisis",
        años_disponibles,
        index=años_disponibles.index(
            año_default
        )
    )


    año_anterior = (
        año_seleccionado -
        1
    )


    # ========================================================
    # DATOS
    # ========================================================

    datos_año = df_graficos[
        df_graficos[
            "Fecha"
        ].dt.year
        ==
        año_seleccionado
    ].copy()


    datos_año_anterior = df_graficos[
        df_graficos[
            "Fecha"
        ].dt.year
        ==
        año_anterior
    ].copy()


    if not datos_año.empty:

        mes_corte = (
            datos_año[
                "Fecha"
            ].max().month
        )

    else:

        mes_corte = 12


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


    meses = {
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


    datos_comparacion = []


    for mes in range(
        1,
        mes_corte + 1
    ):

        datos_comparacion.append(
            {
                "Mes":
                    meses[mes],

                str(
                    año_seleccionado
                ):
                    float(
                        ingresos_actual.get(
                            mes,
                            0
                        )
                    ),

                str(
                    año_anterior
                ):
                    float(
                        ingresos_anterior.get(
                            mes,
                            0
                        )
                    )
            }
        )


    df_comparacion = (
        pd.DataFrame(
            datos_comparacion
        )
    )


    # ========================================================
    # GRÁFICO ANUAL
    # ========================================================

    fig_mensual = go.Figure()


    fig_mensual.add_trace(
        go.Bar(
            x=df_comparacion[
                "Mes"
            ],

            y=df_comparacion[
                str(año_seleccionado)
            ],

            name=str(
                año_seleccionado
            ),

            marker_color="#00875A",

            opacity=0.88
        )
    )


    fig_mensual.add_trace(
        go.Scatter(
            x=df_comparacion[
                "Mes"
            ],

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
            )
        )
    )


    fig_mensual.update_layout(
        height=285,

        margin=dict(
            l=5,
            r=5,
            t=5,
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


        grafico_promedio = go.Figure()


        grafico_promedio.add_trace(
            go.Bar(
                x=promedio_propiedad[
                    "Nombre_Propiedad"
                ],

                y=promedio_propiedad[
                    "Promedio_Mensual"
                ],

                name="Promedio",

                marker_color="#6554C0",

                opacity=0.88
            )
        )


        grafico_promedio.update_layout(
            height=285,

            margin=dict(
                l=5,
                r=5,
                t=5,
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

    anual1, anual2 = st.columns(
        [1, 1],
        gap="medium"
    )


    with anual1:

        st.markdown(
            f"**Ingresos {año_seleccionado} vs {año_anterior}**"
        )

        st.caption(
            "Barras = año seleccionado · "
            "línea = año anterior"
        )

        st.plotly_chart(
            fig_mensual,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    with anual2:

        st.markdown(
            f"**Promedio mensual por propiedad — {año_seleccionado}**"
        )

        st.caption(
            "Ingreso promedio mensual"
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


    y1, y2, y3 = st.columns(3)


    with y1:

        st.metric(
            f"Ingresos {año_seleccionado}",
            formato_moneda(
                total_actual
            )
        )


    with y2:

        st.metric(
            f"Ingresos {año_anterior}",
            formato_moneda(
                total_anterior
            )
        )


    with y3:

        st.metric(
            "Diferencia",
            formato_moneda(
                diferencia
            )
        )


    # ========================================================
    # DETALLE PROMEDIO
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
            height=230
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
                f"detalle_promedio_"
                f"{año_seleccionado}.csv"
            ),
            mime="text/csv",
            key="download_promedio"
        )


# ============================================================
# PIE DEL DASHBOARD
# ============================================================

cantidad_propiedades = (
    df_filtrado[
        "Nombre_Propiedad"
    ].nunique()
)

cantidad_socios = (
    df_filtrado[
        "Nombre_Socio"
    ].nunique()
)


st.markdown("---")


p1, p2, p3, p4 = st.columns(4)


with p1:

    st.metric(
        "Flujo del periodo",
        formato_compacto(
            flujo_total
        )
    )


with p2:

    st.metric(
        "Propiedades analizadas",
        cantidad_propiedades
    )


with p3:

    st.metric(
        "Socios",
        cantidad_socios
    )


with p4:

    st.metric(
        "Rentabilidad",
        f"{rentabilidad:.1%}"
    )
