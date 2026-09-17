
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from data_generator import generate_operational_data
from kpi_engine import calculate_funnel_summary, calculate_financial_summary, get_tribe_benchmark

st.set_page_config(
    page_title="End-to-End Operations & BI Suite",
    page_icon="📊",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .header-title {
        color: #1e293b;
        font-weight: 700;
    }
</style>
""", unsafe_allow_text=True)

@st.cache_data
def load_data():
    data_path = 'data/operational_data.csv'
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        df = generate_operational_data()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

df_raw = load_data()

# Sidebar Filters
st.sidebar.title("🎛️ Filtros Operativos")
tribes_selected = st.sidebar.multiselect(
    "Seleccionar Tribu / Sector:",
    options=df_raw['Tribu'].unique(),
    default=df_raw['Tribu'].unique()
)

date_range = st.sidebar.date_input(
    "Rango de Fechas:",
    value=[df_raw['Fecha'].min(), df_raw['Fecha'].max()],
    min_value=df_raw['Fecha'].min(),
    max_value=df_raw['Fecha'].max()
)

# Filter Data
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df_raw[
        (df_raw['Tribu'].isin(tribes_selected)) & 
        (df_raw['Fecha'] >= start_date) & 
        (df_raw['Fecha'] <= end_date)
    ]
else:
    df_filtered = df_raw[df_raw['Tribu'].isin(tribes_selected)]

# Header
st.title("🚀 End-to-End Operations & Business Intelligence Suite")
st.caption("Visión transversal por sector/tribu e interrelación de KPIs en la Cadena de Valor Operativa")

# Top KPI Summary Cards
funnel_summary = calculate_funnel_summary(df_filtered)
fin_summary = calculate_financial_summary(df_filtered)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Altas Totales", f"{funnel_summary['Total_Altas']:,}")
c2.metric("Suspensiones", f"{funnel_summary['Total_Suspensiones']:,}", f"{funnel_summary['Tasa_Suspension_Pct']}% Tasa", delta_color="inverse")
c3.metric("Bajas (Churn)", f"{funnel_summary['Total_Bajas']:,}", f"{funnel_summary['Tasa_Churn_Pct']}% Tasa", delta_color="inverse")
c4.metric("Facturación", f"${fin_summary['Facturacion_Total_USD']:,.0f}")
c5.metric("Efectividad Cobro", f"{fin_summary['Pct_Recuperacion']}%", f"-${fin_summary['Gap_Cobranza_USD']:,.0f} Gap", delta_color="inverse")

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["🔄 Cadena de Valor & Funnel", "📈 Interrelación de KPIs & Finanzas", "📊 Benchmark por Tribu"])

with tab1:
    st.subheader("Visualización de la Cadena de Valor Transversal")
    
    col_f1, col_f2 = st.columns([1, 1])
    
    with col_f1:
        # Funnel Chart
        funnel_data = dict(
            number=[funnel_summary['Total_Altas'], 
                    int(funnel_summary['Total_Altas'] - funnel_summary['Total_Suspensiones']), 
                    int(funnel_summary['Total_Altas'] - funnel_summary['Total_Suspensiones'] - funnel_summary['Total_Bajas'])],
            stage=["1. Captación (Altas)", "2. Operación Activa", "3. Retención Neta"]
        )
        fig_funnel = px.funnel(funnel_data, x='number', y='stage', title="Funnel Operativo de Conversión y Retención")
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col_f2:
        # Daily Volume Trend
        df_daily = df_filtered.groupby('Fecha')[['Altas', 'Suspensiones', 'Bajas']].sum().reset_index()
        fig_trend = px.line(df_daily, x='Fecha', y=['Altas', 'Suspensiones', 'Bajas'], 
                            title="Evolución Temporal de Altas, Suspensiones y Bajas",
                            color_discrete_map={'Altas': '#2b5c8f', 'Suspensiones': '#e07a5f', 'Bajas': '#d62828'})
        st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("Análisis de Causa-Efecto e Impacto en la Facturación")
    
    col_i1, col_i2 = st.columns([1, 1])
    
    with col_i1:
        # Scatter: Activation Lead Time vs Suspension Rate
        fig_scatter = px.scatter(
            df_filtered, 
            x="Tiempo_Activacion_Dias", 
            y="SLA_Cumplimiento_Pct", 
            color="Tribu",
            size="Suspensiones",
            hover_data=['Altas', 'Facturacion_USD'],
            title="Impacto del Tiempo de Activación en el Cumplimiento de SLA y Suspensiones",
            labels={'Tiempo_Activacion_Dias': 'Días de Activación', 'SLA_Cumplimiento_Pct': 'SLA Cumplido (%)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_i2:
        # Dual-Axis / Gap Chart: Billing vs Collections
        df_monthly = df_filtered.copy()
        df_monthly['Mes'] = df_monthly['Fecha'].dt.to_period('M').astype(str)
        df_fin_m = df_monthly.groupby('Mes')[['Facturacion_USD', 'Aportes_USD']].sum().reset_index()
        
        fig_fin = go.Figure()
        fig_fin.add_trace(go.Bar(x=df_fin_m['Mes'], y=df_fin_m['Facturacion_USD'], name='Facturación (USD)', marker_color='#1d3557'))
        fig_fin.add_trace(go.Bar(x=df_fin_m['Mes'], y=df_fin_m['Aportes_USD'], name='Aportes / Cobranza (USD)', marker_color='#2a9d8f'))
        fig_fin.update_layout(barmode='group', title="Conciliación Mensual: Facturación vs. Aportes Recaudados")
        st.plotly_chart(fig_fin, use_container_width=True)

with tab3:
    st.subheader("Benchmark Transversal por Tribu / Sector")
    
    df_benchmark = get_tribe_benchmark(df_filtered)
    st.dataframe(df_benchmark, use_container_width=True, hide_index=True)
    
    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        fig_bar_sla = px.bar(df_benchmark, x='Tribu', y='SLA_Cumplimiento_Pct', 
                             color='Tribu', title="Promedio de Cumplimiento de SLA (%) por Sector",
                             text_auto=True)
        st.plotly_chart(fig_bar_sla, use_container_width=True)
        
    with col_b2:
        fig_bar_eff = px.bar(df_benchmark, x='Tribu', y='Efectividad_Cobro_%', 
                             color='Tribu', title="Efectividad de Cobro (%) por Sector",
                             text_auto=True)
        st.plotly_chart(fig_bar_eff, use_container_width=True)

st.caption("⚡ Proyecto desarrollado para portafolio laboral | Demostración de Visión Operativa End-to-End")
