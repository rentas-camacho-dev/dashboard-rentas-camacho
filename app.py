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

st.markdown("""
<style>

.stApp {
    background:#F5F7FA;
}

.block-container {
    max-width:100%;
    padding-top:0.5rem;
    padding-bottom:0.5rem;
    padding-left:1rem;
    padding-right:1rem;
}

/* TITULOS */

.dashboard-title {
    font-size:30px;
    font-weight:800;
    color:#172B4D;
    line-height:1.05;
}

.dashboard-subtitle {
    font-size:13px;
    color:#6B778C;
    margin-top:3px;
}

.section-title {
    font-size:19px;
    font-weight:750;
    color:#172B4D;
    margin-top:6px;
    margin-bottom:2px;
}

.section-subtitle {
    font-size:11px;
    color:#6B778C;
    margin-bottom:5px;
}

/* SELECTORES */

label {
    font-size:12px !important;
    color:#344563 !important;
}

div[data-baseweb="select"] {
    border-radius:8px;
}

/* BOTONES */

.stDownloadButton button {
    border-radius:8px;
    border:1px solid #D7DEE7;
    background:white;
    color:#172B4D;
    font-size:11px;
    padding:4px 10px;
}

/* METRICS */

div[data-testid="stMetric"] {
    background:white;
    border:1px solid #E2E7EC;
    border-radius:13px;
    padding:10px 14px;
    box-shadow:0 2px 7px rgba(0,0,0,.035);
}

div[data-testid="stMetricLabel"] {
    font-size:11px;
}

div[data-testid="stMetricValue"] {
    font-size:24px;
}

/* DATAFRAME */

div[data-testid="stDataFrame"] {
    border-radius:11px;
    overflow:hidden;
}

hr {
    border-color:#E5E9EF;
    margin:6px 0;
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

    return client.query(
        QUERY
    ).to_dataframe()


with st.spinner("Cargando información..."):

    df = cargar_datos()


# ============================================================
# PREPARACIÓN
# ============================================================

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
            f"{signo}$ "
            f"{valor / 1_000_000_000:.1f} B"
        )

    if valor >= 1_000_000:

        return (
            f"{signo}$ "
            f"{valor / 1_000_000:.1f} M"
        )

    if valor >= 1_000:

        return (
            f"{signo}$ "
            f"{valor / 1_000:.0f} mil"
        )

    return (
        f"{signo}${valor:,.0f}"
        .replace(",", ".")
    )


def cambio(actual, anterior):

    if anterior == 0:
        return None

    return (
        (actual - anterior)
        / abs(anterior)
    )


def bandera(pct):

    if pct >= 0.80:
        return "🏆"

    if pct >= 0.50:
        return "⚡"

    return "🚩"


# ============================================================
# ENCABEZADO
# ============================================================

h1, h2 = st.columns(
    [2.5, 1]
)

with h1:

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


with h2:

    ultima = df["Fecha"].max()

    st.markdown(
        f"""
        <div style="
            text-align:right;
            color:#6B778C;
            font-size:10px;">
            Última actualización
        </div>

        <div style="
            text-align:right;
            color:#172B4D;
            font-size:12px;
            font-weight:600;">
            📅 {ultima.strftime("%d %b %Y")}
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

    ciudad = st.multiselect(
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

    propiedad = st.multiselect(
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

    socio = st.multiselect(
        "Socio",
        socios,
        placeholder="Todos"
    )


with f4:

    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()

    fechas = st.date_input(
        "Fecha",
        value=(
            fecha_min,
            fecha_max
        ),
        min_value=fecha_min,
        max_value=fecha_max
    )


# ============================================================
# FILTROS GENERALES
# ============================================================

df_base = df.copy()


if ciudad:

    df_base = df_base[
        df_base["Ciudad"]
        .astype(str)
        .isin(ciudad)
    ]


if propiedad:

    df_base = df_base[
        df_base["Nombre_Propiedad"]
        .astype(str)
        .isin(propiedad)
    ]


if socio:

    df_base = df_base[
        df_base["Nombre_Socio"]
        .astype(str)
        .isin(socio)
    ]


# ============================================================
# FECHA
# ============================================================

df_filtrado = df_base.copy()


if (
    isinstance(fechas, tuple)
    and len(fechas) == 2
):

    inicio = pd.Timestamp(
        fechas[0]
    )

    fin = (
        pd.Timestamp(
            fechas[1]
        )
        + pd.Timedelta(days=1)
    )

    df_filtrado = df_filtrado[
        (
            df_filtrado["Fecha"]
            >= inicio
        )
        &
        (
            df_filtrado["Fecha"]
            < fin
        )
    ]


# ============================================================
# KPIs
# ============================================================

ingreso = df_filtrado[
    "Ingreso"
].sum()

gasto = df_filtrado[
    "Gasto"
].sum()

flujo = (
    ingreso -
    gasto
)

rentabilidad = (
    flujo / ingreso
    if ingreso != 0
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
    isinstance(fechas, tuple)
    and len(fechas) == 2
):

    inicio_actual = pd.Timestamp(
        fechas[0]
    )

    fin_actual = pd.Timestamp(
        fechas[1]
    )

    dias = (
        fin_actual -
        inicio_actual
    ).days + 1

    fin_ant = (
        inicio_actual -
        pd.Timedelta(days=1)
    )

    inicio_ant = (
        fin_ant -
        pd.Timedelta(days=dias - 1)
    )

    df_ant = df_base[
        (
            df_base["Fecha"]
            >= inicio_ant
        )
        &
        (
            df_base["Fecha"]
            <= fin_ant
        )
    ]

    if not df_ant.empty:

        ingreso_ant = df_ant[
            "Ingreso"
        ].sum()

        gasto_ant = df_ant[
            "Gasto"
        ].sum()

        flujo_ant = (
            ingreso_ant -
            gasto_ant
        )

        rent_ant = (
            flujo_ant /
            ingreso_ant
            if ingreso_ant != 0
            else 0
        )

        delta_ingreso = cambio(
            ingreso,
            ingreso_ant
        )

        delta_gasto = cambio(
            gasto,
            gasto_ant
        )

        delta_flujo = cambio(
            flujo,
            flujo_ant
        )

        delta_rentabilidad = (
            rentabilidad -
            rent_ant
        )


# ============================================================
# KPIs
# ============================================================

k1, k2, k3, k4 = st.columns(4)


with k1:

    st.metric(
        "💰 Ingreso Total",
        moneda(ingreso),
        (
            f"{delta_ingreso:+.1%}"
            if delta_ingreso is not None
            else None
        )
    )


with k2:

    st.metric(
        "🧾 Gasto Total",
        moneda(gasto),
        (
            f"{delta_gasto:+.1%}"
            if delta_gasto is not None
            else None
        )
    )


with k3:

    st.metric(
        "💵 Flujo",
        moneda(flujo),
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
# RESUMEN POR PROPIEDAD
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.58, 1],
    gap="medium"
)


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


        # ----------------------------------------------------
        # CONSTRUIR FILAS
        # ----------------------------------------------------

        filas = ""


        for _, row in resumen.iterrows():

            nombre = html.escape(
                str(
                    row[
                        "Nombre_Propiedad"
                    ]
                )
            )

            ing = float(
                row["Ingreso"]
            )

            gas = float(
                row["Gasto"]
            )

            flu = float(
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
                if flu >= 0
                else "#DE350B"
            )

            filas += f"""
            <tr>

                <td class="propiedad">
                    {nombre}
                </td>

                <td class="num ingreso">
                    {compacto(ing)}
                </td>

                <td class="num gasto">
                    {compacto(gas)}
                </td>

                <td
                    class="num"
                    style="color:{color_flujo};">
                    {compacto(flu)}
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


        total_ingreso = resumen[
            "Ingreso"
        ].sum()

        total_gasto = resumen[
            "Gasto"
        ].sum()

        total_flujo = resumen[
            "Flujo"
        ].sum()

        total_pct = (
            total_flujo /
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

        .tabla-card {{
            background:white;
            border:1px solid #E1E5EA;
            border-radius:12px;
            overflow:hidden;
        }}

        .tabla-card table {{
            width:100%;
            border-collapse:collapse;
            table-layout:fixed;
        }}

        .tabla-card th {{
            background:#008A7A;
            color:white;
            padding:9px 8px;
            font-size:11px;
            font-weight:700;
            text-align:left;
        }}

        .tabla-card th:nth-child(1) {{
            width:23%;
        }}

        .tabla-card th:nth-child(2) {{
            width:14%;
            text-align:right;
        }}

        .tabla-card th:nth-child(3) {{
            width:14%;
            text-align:right;
        }}

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
            padding:7px 8px;
            border-bottom:1px solid #EDF0F2;
            font-size:10.5px;
            color:#172B4D;
            vertical-align:middle;
        }}

        .tabla-card tr:last-child td {{
            border-bottom:none;
        }}

        .propiedad {{
            font-weight:600;
        }}

        .num {{
            text-align:right;
            white-space:nowrap;
        }}

        .ingreso {{
            color:#00875A;
            font-weight:600;
        }}

        .gasto {{
            color:#DE350B;
            font-weight:600;
        }}

        .pct {{
            text-align:right;
            font-size:10px;
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
            font-size:15px;
        }}

        .total-row td {{
            background:#F8FAFC;
            border-top:2px solid #DCE3EA;
            font-weight:700;
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

            <td>Total</td>

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
                        style="
                            width:{total_ancho}%;
                        ">
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
            height=(
                48
                +
                len(resumen) * 40
                +
                43
            ),
            scrolling=False
        )


# ============================================================
# GASTOS
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

        total_gastos = gastos[
            "Gasto"
        ].sum()


        # ----------------------------------------------------
        # TOP 7 + OTROS
        # ----------------------------------------------------

        if len(gastos) > 7:

            top = gastos.head(7).copy()

            otros_valor = gastos.iloc[7:][
                "Gasto"
            ].sum()

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

            gastos_pie = gastos.copy()


        # ----------------------------------------------------
        # DONA
        # ----------------------------------------------------

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


        mayor_valor = float(
            gastos_pie.iloc[0]["Gasto"]
        )

        mayor_nombre = str(
            gastos_pie.iloc[0][
                "Nombre_Subcategoria"
            ]
        )

        mayor_pct = (
            mayor_valor /
            total_gastos
        )


        fig = go.Figure()


        fig.add_trace(
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


        fig.add_annotation(
            x=0.5,
            y=0.54,
            text=f"<b>{mayor_pct:.1%}</b>",
            showarrow=False,
            font=dict(
                size=18,
                color="#172B4D"
            )
        )


        fig.add_annotation(
            x=0.5,
            y=0.43,
            text=html.escape(
                mayor_nombre
            ),
            showarrow=False,
            font=dict(
                size=9,
                color="#7A869A"
            )
        )


        fig.update_layout(
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


        # ----------------------------------------------------
        # UNA SOLA TARJETA VISUAL
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                background:white;
                border:1px solid #E1E5EA;
                border-radius:13px;
                padding:10px;
                margin:0;
                height:290px;
            ">
            """,
            unsafe_allow_html=True
        )


        gc1, gc2 = st.columns(
            [0.95, 1.05],
            gap="small"
        )


        # ----------------------------------------------------
        # DONA
        # ----------------------------------------------------

        with gc1:

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar":False
                },
                key="grafico_gastos"
            )


        # ----------------------------------------------------
        # DETALLE
        # ----------------------------------------------------

        with gc2:

            filas_detalle = ""


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
                    total_gastos
                )


                filas_detalle += f"""
                <div style="
                    display:grid;
                    grid-template-columns:
                        1fr auto auto;
                    gap:6px;
                    align-items:center;
                    padding:5px 2px;
                    border-bottom:
                        1px solid #EEF1F4;
                    font-size:10px;
                ">

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:5px;
                        min-width:0;
                        color:#344563;
                    ">

                        <span style="
                            width:7px;
                            height:7px;
                            min-width:7px;
                            border-radius:50%;
                            background:
                            {colores[i]};
                        "></span>

                        <span style="
                            white-space:nowrap;
                            overflow:hidden;
                            text-overflow:ellipsis;
                        ">
                            {categoria}
                        </span>

                    </div>

                    <strong style="
                        color:#172B4D;
                        white-space:nowrap;
                    ">
                        {compacto(valor)}
                    </strong>

                    <span style="
                        color:#7A869A;
                        white-space:nowrap;
                    ">
                        {pct:.1%}
                    </span>

                </div>
                """


            detalle_html = f"""
            <div style="
                padding:4px 4px 0 0;
                font-family:
                    -apple-system,
                    BlinkMacSystemFont,
                    'Segoe UI',
                    Arial,
                    sans-serif;
            ">

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#172B4D;
                    margin-bottom:1px;
                ">
                    {moneda(total_gastos)}
                </div>

                <div style="
                    font-size:9px;
                    color:#7A869A;
                    margin-bottom:5px;
                ">
                    Total de egresos operativos
                </div>

                <div style="
                    display:grid;
                    grid-template-columns:
                        1fr auto auto;
                    gap:6px;
                    padding:3px 2px;
                    border-bottom:
                        1px solid #DDE3EA;
                    color:#52617A;
                    font-size:9px;
                    font-weight:700;
                ">

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

                {filas_detalle}

            </div>
            """


            components.html(
                detalle_html,
                height=265,
                scrolling=False
            )


        # Cerrar tarjeta
        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # MENSAJE MAYOR GASTO
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                background:#EAF3FF;
                border:1px solid #C7DDF8;
                border-radius:9px;
                padding:7px 10px;
                margin-top:5px;
                font-size:10px;
                color:#344563;
            ">

                💡 Mayor centro de gasto:
                <strong>{html.escape(mayor_nombre)}</strong>
                ({compacto(mayor_valor)})

                <br>

                <span style="color:#6B778C;">
                    Representa el {mayor_pct:.1%}
                    del total de egresos operativos.
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


años = sorted(
    df["Fecha"]
    .dt.year
    .dropna()
    .unique(),
    reverse=True
)


if años:

    año_sistema = pd.Timestamp.now().year

    año_default = (
        año_sistema
        if año_sistema in años
        else años[0]
    )


    año = st.selectbox(
        "Año de análisis",
        años,
        index=años.index(
            año_default
        )
    )


    año_anterior = año - 1


    # ========================================================
    # DATOS ANUALES
    # ========================================================

    actual = df_base[
        df_base["Fecha"].dt.year == año
    ].copy()


    anterior = df_base[
        df_base["Fecha"].dt.year == año_anterior
    ].copy()


    if not actual.empty:

        mes_corte = (
            actual["Fecha"]
            .max()
            .month
        )

    else:

        mes_corte = 12


    ingresos_actuales = (
        actual
        .groupby(
            actual["Fecha"].dt.month
        )["Ingreso"]
        .sum()
    )


    ingresos_anteriores = (
        anterior
        .groupby(
            anterior["Fecha"].dt.month
        )["Ingreso"]
        .sum()
    )


    nombres_meses = {
        1:"Ene",
        2:"Feb",
        3:"Mar",
        4:"Abr",
        5:"May",
        6:"Jun",
        7:"Jul",
        8:"Ago",
        9:"Sep",
        10:"Oct",
        11:"Nov",
        12:"Dic"
    }


    comparacion = []


    for mes in range(
        1,
        mes_corte + 1
    ):

        comparacion.append(
            {
                "Mes":
                    nombres_meses[mes],

                str(año):
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
            }
        )


    df_anual = pd.DataFrame(
        comparacion
    )


    # ========================================================
    # GRÁFICA INGRESOS
    # ========================================================

    fig_anual = go.Figure()


    fig_anual.add_trace(
        go.Bar(
            x=df_anual["Mes"],
            y=df_anual[
                str(año)
            ],
            name=str(año),
            marker_color="#00875A",
            opacity=0.88
        )
    )


    fig_anual.add_trace(
        go.Scatter(
            x=df_anual["Mes"],
            y=df_anual[
                str(año_anterior)
            ],
            name=str(año_anterior),
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
        height=270,

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
            showgrid=False
        ),

        yaxis=dict(
            tickformat=",.0f",
            gridcolor="#E8ECF0"
        ),

        bargap=0.18
    )


    # ========================================================
    # PROMEDIO PROPIEDAD
    # ========================================================

    promedio = None
    fig_promedio = None


    if not actual.empty:

        promedio = (
            actual
            .groupby(
                "Nombre_Propiedad"
            )
            .agg(
                Ingreso=(
                    "Ingreso",
                    "sum"
                ),
                Inicio=(
                    "Fecha",
                    "min"
                ),
                Fin=(
                    "Fecha",
                    "max"
                )
            )
            .reset_index()
        )


        promedio["Meses"] = (

            (
                promedio["Fin"].dt.year
                -
                promedio["Inicio"].dt.year
            )
            * 12

            +

            (
                promedio["Fin"].dt.month
                -
                promedio["Inicio"].dt.month
            )

            + 1
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
                    color="#172B4D"
                )
            )
        )


        fig_promedio.update_layout(
            height=270,

            margin=dict(
                l=5,
                r=5,
                t=12,
                b=5
            ),

            template="plotly_white",

            xaxis=dict(
                showgrid=False
            ),

            yaxis=dict(
                tickformat=",.0f",
                gridcolor="#E8ECF0"
            )
        )


    # ========================================================
    # GRÁFICAS LADO A LADO
    # ========================================================

    a1, a2 = st.columns(
        [1, 1],
        gap="medium"
    )


    with a1:

        st.markdown(
            f"**Ingresos mensuales — {año} vs {año_anterior}**"
        )

        st.caption(
            "Barras = año seleccionado · línea = año anterior"
        )

        st.plotly_chart(
            fig_anual,
            use_container_width=True,
            config={
                "displayModeBar":False
            },
            key="grafico_anual"
        )


    with a2:

        st.markdown(
            f"**Promedio mensual por propiedad — {año}**"
        )

        st.caption(
            "Ingreso promedio mensual"
        )


        if fig_promedio is not None:

            st.plotly_chart(
                fig_promedio,
                use_container_width=True,
                config={
                    "displayModeBar":False
                },
                key="grafico_promedio"
            )

        else:

            st.info(
                f"No hay datos para {año}."
            )


    # ========================================================
    # YTD
    # ========================================================

    total_actual = df_anual[
        str(año)
    ].sum()

    total_anterior = df_anual[
        str(año_anterior)
    ].sum()

    diferencia = (
        total_actual -
        total_anterior
    )


    y1, y2, y3 = st.columns(3)


    with y1:

        st.metric(
            f"Ingresos {año}",
            moneda(total_actual)
        )


    with y2:

        st.metric(
            f"Ingresos {año_anterior}",
            moneda(total_anterior)
        )


    with y3:

        st.metric(
            "Diferencia",
            moneda(diferencia)
        )


# ============================================================
# FOOTER EJECUTIVO
# ============================================================

st.markdown("---")


p1, p2, p3, p4 = st.columns(4)


with p1:

    st.metric(
        "💵 Flujo del periodo",
        compacto(flujo)
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
            padding:10px;
            text-align:center;
            color:#52617A;
            font-size:12px;">
            📊<br>
            <strong>
                Más que propiedades,
                mejores decisiones.
            </strong>
        </div>
        """,
        unsafe_allow_html=True
    )
