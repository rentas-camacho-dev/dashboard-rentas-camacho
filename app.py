import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="FinQuery - Resumen",
    page_icon="🏠",
    layout="wide"
)


# ============================================================
# BIGQUERY
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


# ============================================================
# TÍTULO
# ============================================================

st.title("🏠 Resumen por Apartamento")

st.markdown(
    "### Ingresos y Gastos"
)


# ============================================================
# FILTROS
# ============================================================

col_filtro1, col_filtro2 = st.columns([1, 1])


with col_filtro1:

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


with col_filtro2:

    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    rango_fecha = st.date_input(
        "Fecha",
        value=(fecha_min.date(), fecha_max.date()),
        min_value=fecha_min.date(),
        max_value=fecha_max.date()
    )


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()


# Ciudad
if ciudad != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Ciudad"].astype(str) == ciudad
    ]


# Fecha
if isinstance(rango_fecha, tuple) and len(rango_fecha) == 2:

    fecha_inicio = pd.Timestamp(rango_fecha[0])

    fecha_fin = (
        pd.Timestamp(rango_fecha[1])
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"] >= fecha_inicio)
        &
        (df_filtrado["Fecha"] <= fecha_fin)
    ]


# ============================================================
# KPIs
# ============================================================

ingreso_total = df_filtrado["Ingreso"].sum()

gasto_total = df_filtrado["Gasto"].sum()

flujo_total = ingreso_total - gasto_total

rentabilidad = (
    flujo_total / ingreso_total
    if ingreso_total != 0
    else 0
)


k1, k2, k3, k4 = st.columns(4)


with k1:

    st.metric(
        "Ingreso Total",
        f"$ {ingreso_total:,.0f}"
    )


with k2:

    st.metric(
        "Gasto",
        f"$ {gasto_total:,.0f}"
    )


with k3:

    st.metric(
        "Flujo",
        f"$ {flujo_total:,.0f}"
    )


with k4:

    st.metric(
        "Rentabilidad",
        f"{rentabilidad:.1%}"
    )


st.divider()


# ============================================================
# TABLA POR PROPIEDAD
# ============================================================

col_tabla, col_grafico = st.columns([1.25, 0.75])


with col_tabla:

    st.subheader("🏠 Propiedad")

    resumen = (
        df_filtrado
        .groupby("Nombre_Propiedad", dropna=False)
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

    # Fila TOTAL
    total = pd.DataFrame({
        "Nombre_Propiedad": ["Total"],
        "Ingreso": [resumen["Ingreso"].sum()],
        "Gasto": [resumen["Gasto"].sum()],
        "Flujo": [resumen["Flujo"].sum()],
        "%": [
            resumen["Flujo"].sum()
            / resumen["Ingreso"].sum()
            if resumen["Ingreso"].sum() != 0
            else 0
        ]
    })

    resumen_mostrar = pd.concat(
        [resumen, total],
        ignore_index=True
    )

    resumen_mostrar = resumen_mostrar.rename(
        columns={
            "Nombre_Propiedad": "Propiedad"
        }
    )

    resumen_mostrar["Ingreso"] = resumen_mostrar[
        "Ingreso"
    ].apply(
        lambda x: f"$ {x:,.0f}"
    )

    resumen_mostrar["Gasto"] = resumen_mostrar[
        "Gasto"
    ].apply(
        lambda x: f"$ {x:,.0f}"
    )

    resumen_mostrar["Flujo"] = resumen_mostrar[
        "Flujo"
    ].apply(
        lambda x: f"$ {x:,.0f}"
    )

    resumen_mostrar["%"] = resumen_mostrar[
        "%"
    ].apply(
        lambda x: f"{x:.1%}"
    )

    st.dataframe(
        resumen_mostrar[
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
        height=390
    )


# ============================================================
# GASTOS POR SUBCATEGORÍA
# ============================================================

with col_grafico:

    st.subheader("💸 Gastos por Subcategoría")

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

    if len(gastos) > 0:

        fig = px.pie(
            gastos,
            names="Nombre_Subcategoria",
            values="Gasto",
            hole=0.48
        )

        fig.update_traces(
            textinfo="percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "$ %{value:,.0f}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),
            legend_title=""
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No hay gastos para los filtros seleccionados."
        )


# ============================================================
# INFORMACIÓN
# ============================================================

st.caption(
    f"Movimientos incluidos: {len(df_filtrado):,}"
)
