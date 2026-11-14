import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="BioShield Analytics: Dashboard", layout="wide")

st.title("🛡️ BioShield Analytics: Ciberseguridad UEBA y Validación Biomédica")
st.markdown("Dashboard interactivo para la gestión de amenazas internas (Insider Threat) y evaluación de modelos de IA médica.")

# Carga de datos
@st.cache_data
def load_data():
    df_ueba = pd.read_csv('ueba_telemetry.csv')
    df_biomed = pd.read_csv('biomed_metrics.csv')
    return df_ueba, df_biomed

try:
    df_ueba, df_biomed = load_data()
except Exception as e:
    st.error(f"Error al cargar los datasets: {e}")
    st.stop()

# Sidebar de navegación y filtros
st.sidebar.header("Filtros Interactivos")
roles_disponibles = df_ueba['rol'].unique().tolist()
rol_seleccionado = st.sidebar.multiselect("Filtrar por Rol de Usuario", roles_disponibles, default=roles_disponibles)

horas_disponibles = sorted(df_ueba['hora_acceso'].unique().tolist())
rango_horas = st.sidebar.select_slider("Filtrar por Ventana Horaria", options=horas_disponibles, value=(horas_disponibles[0], horas_disponibles[-1]))

# Filtrado de datos UEBA
df_ueba_filtered = df_ueba[
    (df_ueba['rol'].isin(rol_seleccionado)) & 
    (df_ueba['hora_acceso'] >= rango_horas[0]) & 
    (df_ueba['hora_acceso'] <= rango_horas[1])
]

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["Módulo 1: Riesgo de Identidad (UEBA)", "Módulo 2: Desempeño Biomédico", "Módulo 3: Alertas y Explicabilidad (XAI)"])

with tab1:
    st.subheader("Monitoreo de Anomalías y Comportamiento (UEBA)")
    st.markdown("Gráfico de dispersión multivariado: Volumen de descarga vs. Índice de riesgo.")
    
    def get_color(score):
        if score < 50:
            return 'Verde (Normal)'
        elif score < 80:
            return 'Amarilla (Observación)'
        else:
            return 'Roja (Crítica)'
            
    df_ueba_filtered['severidad'] = df_ueba_filtered['risk_score'].apply(get_color)
    
    fig_ueba = px.scatter(
        df_ueba_filtered,
        x='volumen_descarga_mb',
        y='risk_score',
        color='severidad',
        color_discrete_map={'Verde (Normal)': '#2ca02c', 'Amarilla (Observación)': '#ff7f0e', 'Roja (Crítica)': '#d62728'},
        hover_data=['user_id', 'rol', 'hora_acceso', 'ubicacion_ip'],
        labels={'volumen_descarga_mb': 'Volumen de Descarga (MB)', 'risk_score': 'Índice de Riesgo (0-100)'},
        title="Dispersión Multivariado UEBA"
    )
    st.plotly_chart(fig_ueba, use_container_width=True)

with tab2:
    st.subheader("Evaluación de Modelos Biomédicos (U-Net vs MedSAM) y AlphaFold 3")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Comparativa DSC Promedio por Órgano**")
        df_melt = df_biomed.melt(id_vars=['tipo_organo'], value_vars=['dice_unet', 'dice_medsam'], var_name='Modelo', value_name='Dice Score')
        fig_bar = px.bar(
            df_melt, x='tipo_organo', y='Dice Score', color='Modelo', barmode='group',
            labels={'tipo_organo': 'Órgano / Tejido', 'Dice Score': 'Coeficiente Dice (DSC)'},
            color_discrete_map={'dice_unet': '#1f77b4', 'dice_medsam': '#2ca02c'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_b:
        st.markdown("**Distribución Puntajes pLDDT (AlphaFold 3)**")
        fig_hist = px.histogram(
            df_biomed, x='plddt_score', nbins=15,
            labels={'plddt_score': 'Puntaje pLDDT', 'count': 'Frecuencia'},
            color_discrete_sequence=['#9467bd']
        )
        fig_hist.add_vline(x=90, line_dash="dash", line_color="red", annotation_text="Umbral Alta Confianza (>90)")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    st.markdown("### Candidatos Farmacológicos de Alta Confianza (pLDDT > 90)")
    df_confianza = df_biomed[df_biomed['plddt_score'] > 90][['estudio_id', 'tipo_organo', 'complejo_proteina', 'plddt_score', 'tiempo_inferencia_seg']]
    st.dataframe(df_confianza, use_container_width=True)

with tab3:
    st.subheader("Panel de Alertas Tempranas y Explicabilidad (XAI)")
    st.markdown("Top de entidades con mayor riesgo de exfiltración y justificación automatizada.")
    
    df_top_riesgo = df_ueba.sort_values(by='risk_score', ascending=False).head(5).copy()
    
    def generar_xai(row):
        return f"Acceso atípico a las {row['hora_acceso']} hrs + Volumen de descarga de {row['volumen_descarga_mb']} MB (Z-score temporal: {row['z_score_temporal']})"
        
    df_top_riesgo['justificacion_xai'] = df_top_riesgo.apply(generar_xai, axis=1)
    
    st.dataframe(
        df_top_riesgo[['user_id', 'rol', 'hora_acceso', 'volumen_descarga_mb', 'risk_score', 'justificacion_xai']],
        use_container_width=True
    )
