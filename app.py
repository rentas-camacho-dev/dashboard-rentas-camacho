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

    /* --------------------------------------------------------
       FONDO GENERAL
    -------------------------------------------------------- */

    .stApp {
        background-color: #F5F7FA;
    }


    /* --------------------------------------------------------
       TÍTULOS
    -------------------------------------------------------- */

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


    /* --------------------------------------------------------
       TARJETAS KPI
    -------------------------------------------------------- */

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


    /* --------------------------------------------------------
       TARJETA TABLA
    -------------------------------------------------------- */

    .property-card {
        background: white;
        border: 1px solid #E1E5EA;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }


    /* --------------------------------------------------------
       TABLA
    -------------------------------------------------------- */

    .property-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        background: white;
    }

    .property-table th {
        background: #008577;
        color: white;
        padding: 11px 12px;
        font-size: 13px;
        font-weight: 700;
        text-align: left;
        border-bottom: 1px solid #00776A;
    }

    .property-table th.num {
        text-align: right;
    }

    .property-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #EDF0F2;
        font-size: 13px;
        color: #172B4D;
        vertical-align: middle;
    }

    .property-table td.num {
        text-align: right;
        white-space: nowrap;
    }

    .property-table tr:last-child td {
        border-bottom: none;
    }

    .property-table .property-name {
        font-weight: 600;
        color: #172B4D;
    }

    .income-text {
        color: #00875A;
        font-weight: 600;
    }

    .expense-text {
        color: #DE350B;
        font-weight: 600;
    }

    .flow-positive {
        color: #00875A;
        font-weight: 700;
    }

    .flow-negative {
        color: #DE350B;
        font-weight: 700;
    }


    /* --------------------------------------------------------
       BARRA DE PORCENTAJE
    -------------------------------------------------------- */

    .percent-wrapper {
        min-width: 125px;
    }

    .percent-value {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
        font-size: 12px;
        font-weight: 600;
    }

    .percent-bar {
        width: 100%;
        height: 8px;
        background: #EEF1F5;
        border-radius: 4px;
        overflow: hidden;
    }

    .percent-fill {
        height: 100%;
        background: #16B5D1;
        border-radius: 4px;
    }


    /* --------------------------------------------------------
       ICONO ESTADO
    -------------------------------------------------------- */

    .status-icon {
        text-align: center;
        font-size: 18px;
        white-space: nowrap;
    }


    /* --------------------------------------------------------
       TOTAL
    -------------------------------------------------------- */

    .total-row td {
        background: #F8FAFC;
        font-weight: 700;
        border-top: 2px solid #DDE3EA;
        color: #172B4D;
    }


    /* --------------------------------------------------------
       TARJETA GASTOS
    -------------------------------------------------------- */

    .expense-card {
        background: white;
        border: 1px solid #E1E5EA;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        height: 100%;
    }

    .expense-subtitle {
        color: #5E6C84;
        font-size: 13px;
        margin-bottom: 5px;
    }

    .expense-total {
        font-size: 17px;
        font-weight: 700;
        color: #172B4D;
        margin-bottom: 5px;
    }

    .expense-list {
        margin-top: 3px;
    }

    .expense-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        border-bottom: 1px solid #F0F2F4;
        font-size: 12px;
    }

    .expense-item:last-child {
        border-bottom: none;
    }

    .expense-name {
        color: #344563;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .expense-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }

    .expense-value {
        color: #172B4D;
        font-weight: 600;
        white-space: nowrap;
    }

    .expense-percent {
        color: #7A869A;
        margin-left: 7px;
        min-width: 42px;
        text-align: right;
    }


    /* --------------------------------------------------------
       TABLAS NATIVAS STREAMLIT
    -------------------------------------------------------- */

    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 12px;
    }


    /* --------------------------------------------------------
       ESPACIADO
    -------------------------------------------------------- */

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
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
# FUNCIONES DE FORMATO
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

    elif valor_abs >= 1_000_000:

        return (
            f"{signo}$ {valor_abs / 1_000_000:.1f} M"
        )

    elif valor_abs >= 1_000:

        return (
            f"{signo}$ {valor_abs / 1_000:.0f} mil"
        )

    else:

        return (
            f"{signo}$ {valor_abs:,.0f}"
            .replace(",", ".")
        )


def estado_porcentaje(porcentaje):

    if porcentaje >= 80:
        return "🏆"

    elif porcentaje >= 50:
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
        df_graficos["Nombre_Propiedad"]
        .astype(str)
        .isin(
            propiedad_seleccionada
        )
    ]


if socio_seleccionado:

    df_graficos = df_graficos[
        df_graficos["Nombre_Socio"]
        .astype(str)
        .isin(
            socio_seleccionado
        )
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

if ingreso_total != 0:

    rentabilidad = (
        flujo_total /
        ingreso_total
    )

else:

    rentabilidad = 0


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
# FILA PRINCIPAL:
# TABLA PROPIEDADES + DISTRIBUCIÓN GASTOS
# ============================================================

col_tabla, col_gastos = st.columns(
    [1.55, 1],
    gap="medium"
)


# ============================================================
# TABLA DE PROPIEDADES
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

        resumen_propiedad["Flujo"] = (
            resumen_propiedad["Ingreso"]
            -
            resumen_propiedad["Gasto"]
        )

        resumen_propiedad["%"] = (
            resumen_propiedad.apply(
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

        html_tabla = """
        <div class="property-card">
        <table class="property-table">

        <thead>
            <tr>
                <th>Propiedad</th>
                <th class="num">Ingreso</th>
                <th class="num">Gasto</th>
                <th class="num">Flujo</th>
                <th class="num">%</th>
                <th></th>
            </tr>
        </thead>

        <tbody>
        """


        for _, row in resumen_propiedad.iterrows():

            pct = float(
                row["%"]
            )

            pct_width = min(
                max(
                    pct,
                    0
                ),
                100
            )

            if row["Flujo"] >= 0:

                flujo_clase = (
                    "flow-positive"
                )

            else:

                flujo_clase = (
                    "flow-negative"
                )

            icono = estado_porcentaje(
                pct
            )


            html_tabla += f"""
            <tr>

                <td class="property-name">
                    {row['Nombre_Propiedad']}
                </td>

                <td class="num income-text">
                    {formato_compacto(row['Ingreso'])}
                </td>

                <td class="num expense-text">
                    {formato_compacto(row['Gasto'])}
                </td>

                <td class="num {flujo_clase}">
                    {formato_compacto(row['Flujo'])}
                </td>

                <td class="num">

                    <div class="percent-wrapper">

                        <div class="percent-value">
                            <span>{pct:.1f}%</span>
                        </div>

                        <div class="percent-bar">
                            <div
                                class="percent-fill"
                                style="width:{pct_width}%;">
                            </div>
                        </div>

                    </div>

                </td>

                <td class="status-icon">
                    {icono}
                </td>

            </tr>
            """


        # ----------------------------------------------------
        # FILA TOTAL
        # ----------------------------------------------------

        total_pct_width = min(
            max(total_pct * 100, 0),
            100
        )

        total_icono = (
            estado_porcentaje(
                total_pct * 100
            )
        )

        html_tabla += f"""

        <tr class="total-row">

            <td>
                Total
            </td>

            <td class="num income-text">
                {formato_compacto(total_ingreso)}
            </td>

            <td class="num expense-text">
                {formato_compacto(total_gasto)}
            </td>

            <td class="num flow-positive">
                {formato_compacto(total_flujo)}
            </td>

            <td class="num">

                <div class="percent-wrapper">

                    <div class="percent-value">
                        <span>{total_pct:.1%}</span>
                    </div>

                    <div class="percent-bar">
                        <div
                            class="percent-fill"
                            style="width:{total_pct_width}%;">
                        </div>
                    </div>

                </div>

            </td>

            <td class="status-icon">
                {total_icono}
            </td>

        </tr>

        </tbody>
        </table>
        </div>
        """


        st.markdown(
            html_tabla,
            unsafe_allow_html=True
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
            gastos_subcategoria[
                "Gasto"
            ].sum()
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
                gastos_subcategoria
                .copy()
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
            mayor_gasto[
                "Gasto"
            ]
        )

        mayor_pct = (
            mayor_valor /
            gasto_total_grafico
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
        # GRÁFICO DONA
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
                    colors=colores[:len(gastos_pie)],
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
            text=(
                f"<b>{mayor_pct:.1%}</b>"
            ),
            showarrow=False,
            font=dict(
                size=19,
                color="#172B4D"
            )
        )

        fig_gastos.add_annotation(
            x=0.5,
            y=0.43,
            text=(
                f"{mayor_categoria}"
            ),
            showarrow=False,
            font=dict(
                size=11,
                color="#7A869A"
            )
        )


        fig_gastos.update_layout(
            height=300,
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
        # HTML LISTA
        # ----------------------------------------------------

        html_gastos = f"""
        <div class="expense-card">

            <div style="
                font-size:18px;
                font-weight:700;
                color:#172B4D;
                margin-bottom:3px;">
                Desglose por subcategoría de gasto
            </div>

            <div class="expense-subtitle">
                Distribución porcentual de los egresos operativos
            </div>

            <div class="expense-total">
                {formato_moneda(gasto_total_grafico)}
            </div>

        """


        for i, (_, row) in enumerate(
            gastos_pie.iterrows()
        ):

            categoria = (
                row[
                    "Nombre_Subcategoria"
                ]
            )

            valor = float(
                row["Gasto"]
            )

            porcentaje = (
                valor /
                gasto_total_grafico
            )


            html_gastos += f"""

            <div class="expense-item">

                <div class="expense-name">

                    <span
                        class="expense-dot"
                        style="
                        background:{colores[i]};
                        ">
                    </span>

                    <span>
                        {categoria}
                    </span>

                </div>

                <div>

                    <span class="expense-value">
                        {formato_compacto(valor)}
                    </span>

                    <span class="expense-percent">
                        {porcentaje:.1%}
                    </span>

                </div>

            </div>
            """


        html_gastos += "</div>"


        # ----------------------------------------------------
        # DONA + LISTA
        # ----------------------------------------------------

        dona_col, lista_col = st.columns(
            [0.95, 1.05],
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
                html_gastos,
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
        df_graficos["Fecha"].dt.year ==
        año_seleccionado
    ].copy()

    datos_año_anterior = df_graficos[
        df_graficos["Fecha"].dt.year ==
        año_anterior
    ].copy()


    # ========================================================
    # MES CORTE
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
    # COMPARACIÓN
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

                str(año_seleccionado):
                    ingreso_actual,

                str(año_anterior):
                    ingreso_anterior
            }
        )


    df_comparacion = (
        pd.DataFrame(
            comparacion_mensual
        )
    )


    # ========================================================
    # GRÁFICA INGRESOS
    # ========================================================

    fig_mensual = go.Figure()


    # AÑO SELECCIONADO = BARRAS
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
    # PROMEDIO MENSUAL PROPIEDAD
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


        # ----------------------------------------------------
        # MESES
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # PROMEDIO
        # ----------------------------------------------------

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
    # GRÁFICAS ANUALES LADO A LADO
    # ========================================================

    st.markdown(
        "#### 📊 Comparación anual y desempeño por propiedad"
    )


    grafico1, grafico2 = st.columns(
        [1, 1],
        gap="medium"
    )


    # --------------------------------------------------------
    # GRÁFICA INGRESOS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # GRÁFICA PROMEDIO
    # --------------------------------------------------------

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
                f"No hay datos para {año_seleccionado} con los filtros seleccionados."
            )


    # ========================================================
    # RESUMEN YTD
    # ========================================================

    total_actual = (
        df_comparacion[
            str(año_seleccionado)
        ].sum()
    )

    total_anterior = (
        df_comparacion[
            str(año_anterior)
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
    # TABLA PROMEDIO POR PROPIEDAD
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
