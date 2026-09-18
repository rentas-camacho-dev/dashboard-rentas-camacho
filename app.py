import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
from google.cloud import bigquery


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="FinQuery - Rentas Cortas Camacho",
    page_icon="🏠",
    layout="wide"
)


# ============================================================
# CONEXIÓN BIGQUERY
# ============================================================

@st.cache_resource
def get_bigquery_client():

    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    return bigquery.Client(
        credentials=credentials,
        project="rentascamacho"
    )


conn = get_bigquery_client()


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data(ttl=300)
def load_data():

    query = """
        SELECT
            ID_Movimiento,
            Fecha,
            Tipo,
            Nombre_Tipo,
            Nombre_Propiedad,
            Nombre_Socio,
            Nombre_Categoria,
            Nombre_Subcategoria,
            Nombre_Cuenta,
            Valor_Repartido,
            Ingreso,
            Gasto
        FROM `rentascamacho.rentas_cortas.Movimientos_Operativos_Reparto`
    """

    df = conn.query(query).to_dataframe()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    for col in ["Valor_Repartido", "Ingreso", "Gasto"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


try:
    df_base = load_data()

except Exception as e:

    st.error("❌ No fue posible cargar los datos desde BigQuery.")
    st.code(str(e))
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔎 Filtros")

socios = sorted(
    df_base["Nombre_Socio"].dropna().unique().tolist()
)

propiedades = sorted(
    df_base["Nombre_Propiedad"].dropna().unique().tolist()
)

categorias = sorted(
    df_base["Nombre_Categoria"].dropna().unique().tolist()
)


socios_sel = st.sidebar.multiselect(
    "Socio",
    socios,
    default=socios
)

propiedades_sel = st.sidebar.multiselect(
    "Propiedad",
    propiedades,
    default=propiedades
)

categorias_sel = st.sidebar.multiselect(
    "Categoría",
    categorias,
    default=categorias
)


# ============================================================
# FILTRO DE DATOS
# ============================================================

df = df_base.copy()

if socios_sel:
    df = df[df["Nombre_Socio"].isin(socios_sel)]

if propiedades_sel:
    df = df[df["Nombre_Propiedad"].isin(propiedades_sel)]

if categorias_sel:
    df = df[df["Nombre_Categoria"].isin(categorias_sel)]


# ============================================================
# ENCABEZADO
# ============================================================

st.title("🏠 Portafolio de Inversión Familiar - Camacho")

st.markdown(
    "Dashboard en vivo conectado a Google Cloud BigQuery "
    "(`rentascamacho.rentas_cortas`)"
)

st.divider()


# ============================================================
# KPIs
# ============================================================

total_ingresos = df["Ingreso"].sum()
total_gastos = df["Gasto"].sum()
flujo = total_ingresos - total_gastos

rentabilidad = (
    flujo / total_ingresos * 100
    if total_ingresos != 0
    else 0
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Ingreso Total",
        f"${total_ingresos:,.0f}"
    )


with col2:

    st.metric(
        "💸 Gasto",
        f"${total_gastos:,.0f}"
    )


with col3:

    st.metric(
        "📈 Flujo",
        f"${flujo:,.0f}"
    )


with col4:

    st.metric(
        "📊 Rentabilidad",
        f"{rentabilidad:.1f}%"
    )


st.divider()


# ============================================================
# RESUMEN POR PROPIEDAD
# ============================================================

st.subheader("🏠 Resumen por Propiedad")


df_prop = (
    df.groupby("Nombre_Propiedad", as_index=False)
    .agg(
        Ingreso=("Ingreso", "sum"),
        Gasto=("Gasto", "sum")
    )
)


df_prop["Flujo"] = (
    df_prop["Ingreso"] - df_prop["Gasto"]
)


df_prop["%"] = (
    df_prop["Flujo"]
    .div(df_prop["Ingreso"].replace(0, pd.NA))
    .mul(100)
    .fillna(0)
)


df_prop = df_prop.sort_values(
    "Ingreso",
    ascending=False
)


# Formato visual para la tabla

df_visual = df_prop.copy()

df_visual["Ingreso"] = df_visual["Ingreso"].apply(
    lambda x: f"${x:,.0f}"
)

df_visual["Gasto"] = df_visual["Gasto"].apply(
    lambda x: f"${x:,.0f}"
)

df_visual["Flujo"] = df_visual["Flujo"].apply(
    lambda x: f"${x:,.0f}"
)

df_visual["%"] = df_visual["%"].apply(
    lambda x: f"{x:.1f}%"
)


st.dataframe(
    df_visual,
    use_container_width=True,
    hide_index=True,
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
            "Rentabilidad"
        )
    }
)


st.divider()


# ============================================================
# GRÁFICOS
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# INGRESOS MENSUALES
# ------------------------------------------------------------

with col1:

    st.subheader("📊 Ingresos mensuales")

    df_mes = (
        df[df["Ingreso"] > 0]
        .assign(
            Mes=lambda x: x["Fecha"].dt.to_period("M").astype(str)
        )
        .groupby("Mes", as_index=False)["Ingreso"]
        .sum()
    )

    if not df_mes.empty:

        fig_mes = px.bar(
            df_mes,
            x="Mes",
            y="Ingreso",
            text_auto=".2s"
        )

        fig_mes.update_layout(
            xaxis_title="",
            yaxis_title="Ingresos",
            showlegend=False,
            height=400
        )

        st.plotly_chart(
            fig_mes,
            use_container_width=True
        )

    else:

        st.info("No hay ingresos para mostrar.")


# ------------------------------------------------------------
# GASTOS POR SUBCATEGORÍA
# ------------------------------------------------------------

with col2:

    st.subheader("🍩 Distribución de gastos")

    df_gastos = (
        df[df["Gasto"] > 0]
        .groupby(
            "Nombre_Subcategoria",
            as_index=False
        )["Gasto"]
        .sum()
        .sort_values(
            "Gasto",
            ascending=False
        )
    )

    if not df_gastos.empty:

        fig_gastos = px.pie(
            df_gastos,
            names="Nombre_Subcategoria",
            values="Gasto",
            hole=0.55
        )

        fig_gastos.update_layout(
            height=400,
            showlegend=True
        )

        st.plotly_chart(
            fig_gastos,
            use_container_width=True
        )

    else:

        st.info("No hay gastos para mostrar.")


# ============================================================
# FLUJO POR PROPIEDAD
# ============================================================

st.divider()

st.subheader("📈 Flujo por propiedad")


fig_prop = px.bar(
    df_prop.sort_values("Flujo"),
    x="Flujo",
    y="Nombre_Propiedad",
    orientation="h",
    text="Flujo"
)


fig_prop.update_traces(
    texttemplate="$%{x:,.0f}",
    textposition="outside"
)


fig_prop.update_layout(
    xaxis_title="Flujo",
    yaxis_title="",
    height=max(400, len(df_prop) * 55),
    showlegend=False
)


st.plotly_chart(
    fig_prop,
    use_container_width=True
)


# ============================================================
# ÚLTIMOS MOVIMIENTOS
# ============================================================

st.divider()

st.subheader("🧾 Últimos movimientos")


df_ultimos = (
    df.sort_values(
        "Fecha",
        ascending=False
    )
    .head(15)
    [
        [
            "Fecha",
            "Tipo",
            "Nombre_Propiedad",
            "Nombre_Socio",
            "Nombre_Categoria",
            "Nombre_Subcategoria",
            "Valor_Repartido"
        ]
    ]
    .copy()
)


df_ultimos["Fecha"] = df_ultimos["Fecha"].dt.strftime(
    "%d/%m/%Y"
)


df_ultimos["Valor_Repartido"] = (
    df_ultimos["Valor_Repartido"]
    .apply(lambda x: f"${x:,.0f}")
)


st.dataframe(
    df_ultimos,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PIE
# ============================================================

st.caption(
    "FinQuery • Datos consultados directamente desde BigQuery"
)
