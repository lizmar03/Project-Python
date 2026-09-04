import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Ventas de PC", layout="wide")

# Estilos CSS personalizados
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #4f46e5;
    }
    .stMetric label {
        color: #a0aec0 !important;
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("Fuente de datos")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["fecha"] = pd.to_datetime(df["fecha"])
else:
    st.info("Por favor, sube un archivo CSV en el panel izquierdo para comenzar.")
    st.stop()

st.sidebar.title("Filtros")

# Filtro de Fechas
fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()

fecha_inicio = st.sidebar.date_input("Fecha de inicio", fecha_min)
fecha_fin = st.sidebar.date_input("Fecha de fin", fecha_max)

# Filtro Categorías
categorias = ["Todos"] + list(df["categoria"].unique())
cat_selected = st.sidebar.selectbox("Seleccione las clasificaciones de producto", categorias)

# Filtro Rama
ramas = ["Todos"] + list(df["rama"].unique())
rama_selected = st.sidebar.selectbox("Seleccione la rama de venta", ramas)

# Filtro Ciudades
ciudades_opt = list(df["ciudad"].unique())
ciudad_selected = st.sidebar.multiselect("Seleccione las ciudades de venta", ciudades_opt, default=ciudades_opt)

# Filtros adicionales si existen columnas de hardware (RTX Serie 50 / Ryzen 9000)
gpu_selected = "Todos"
if "tarjeta_grafica" in df.columns:
    gpus = ["Todos"] + list(df["tarjeta_grafica"].unique())
    gpu_selected = st.sidebar.selectbox("Tarjeta Gráfica (GPU)", gpus)

cpu_selected = "Todos"
if "procesador" in df.columns:
    cpus = ["Todos"] + list(df["procesador"].unique())
    cpu_selected = st.sidebar.selectbox("Procesador (CPU)", cpus)

# Aplicar Filtros al DataFrame
df_filtered = df[
    (df["fecha"].dt.date >= fecha_inicio) & 
    (df["fecha"].dt.date <= fecha_fin) &
    (df["ciudad"].isin(ciudad_selected))
]

if cat_selected != "Todos":
    df_filtered = df_filtered[df_filtered["categoria"] == cat_selected]

if rama_selected != "Todos":
    df_filtered = df_filtered[df_filtered["rama"] == rama_selected]

if gpu_selected != "Todos" and "tarjeta_grafica" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["tarjeta_grafica"] == gpu_selected]

if cpu_selected != "Todos" and "procesador" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["procesador"] == cpu_selected]

# --- CUERPO PRINCIPAL ---
st.title("Ventas de Hardware / PCs")

# Búsqueda por ID
st.subheader("Búsqueda")
search_id = st.text_input("Ingrese el ID de la venta que desea buscar:")
if search_id:
    df_filtered = df_filtered[df_filtered["id_venta"].astype(str).str.contains(search_id, case=False, na=False)]

st.markdown("---")

# Métricas principales (KPIs)
st.subheader("Resumen General")

ingresos_totales = df_filtered["ingreso_total"].sum()
costo_total = df_filtered["costo"].sum()
ganancia_neta = ingresos_totales - costo_total
margen_ganancia = (ganancia_neta / ingresos_totales * 100) if ingresos_totales > 0 else 0
ticket_promedio = df_filtered["ingreso_total"].mean() if len(df_filtered) > 0 else 0
unidades_vendidas = df_filtered["unidades"].sum()
unidades_por_ticket = df_filtered["unidades"].mean() if len(df_filtered) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos Totales", f"$ {ingresos_totales:,.2f}")
col2.metric("Ganancia Neta Total", f"$ {ganancia_neta:,.2f}")
col3.metric("Margen de Ganancia Neto (%)", f"{margen_ganancia:.2f}%")
col4.metric("Costo Total de Ventas (COGS)", f"$ {costo_total:,.2f}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Ticket Promedio", f"$ {ticket_promedio:,.2f}")
col6.metric("Unidades Vendidas", f"{unidades_vendidas:,}")
col7.metric("Unidades por Ticket", f"{unidades_por_ticket:.2f}")

st.markdown("---")

# Visualización de Gráficos Principales
st.subheader("Análisis Visual")

col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.write("**Ventas por ciudad**")
    fig_ciudad = px.pie(
        df_filtered, 
        names="ciudad", 
        values="ingreso_total", 
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_ciudad.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_ciudad, use_container_width=True)

with col_graph2:
    st.write("**Ventas por método de pago**")
    fig_pago = px.pie(
        df_filtered, 
        names="metodo_pago", 
        values="ingreso_total", 
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_pago.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_pago, use_container_width=True)

# Gráficos adicionales para componentes de hardware
if "tarjeta_grafica" in df_filtered.columns and "procesador" in df_filtered.columns:
    st.markdown("---")
    st.subheader("Análisis por Componentes Hardware (RTX Serie 50 & Ryzen 9000)")
    
    col_hw1, col_hw2 = st.columns(2)
    
    with col_hw1:
        st.write("**Ventas por Tarjeta Gráfica (GPU)**")
        df_gpu = df_filtered.groupby("tarjeta_grafica")["ingreso_total"].sum().reset_index()
        fig_gpu = px.bar(
            df_gpu, 
            x="ingreso_total", 
            y="tarjeta_grafica", 
            orientation="h",
            color="ingreso_total",
            labels={"ingreso_total": "Ingresos ($)", "tarjeta_grafica": "GPU"},
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_gpu, use_container_width=True)
        
    with col_hw2:
        st.write("**Ventas por Procesador (CPU)**")
        df_cpu = df_filtered.groupby("procesador")["ingreso_total"].sum().reset_index()
        fig_cpu = px.bar(
            df_cpu, 
            x="procesador", 
            y="ingreso_total", 
            color="ingreso_total",
            labels={"ingreso_total": "Ingresos ($)", "procesador": "CPU"},
            color_continuous_scale="Plasma"
        )
        st.plotly_chart(fig_cpu, use_container_width=True)