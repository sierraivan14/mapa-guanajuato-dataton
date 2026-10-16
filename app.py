import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# 1. CONFIGURACION DE LA PAGINA Y ESTILO EJECUTIVO
st.set_page_config(
    page_title="M.A.P.A. Guanajuato | Simulador IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_style = (
    "<style>"
    ".header-box { background: linear-gradient(90deg, #003366 0%, #0055A5 100%); color: white; padding: 22px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.18); }"
    "div[data-testid='stMetric'] { border-left: 5px solid #0055A5; padding: 12px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }"
    ".legend-box { padding: 10px 14px; border-radius: 8px; background-color: rgba(255, 255, 255, 0.08); border: 1px solid rgba(128, 128, 128, 0.25); margin-bottom: 10px; font-size: 14px; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    df_pac = pd.read_csv("MAPA_PACIENTES_ENRIQUECIDO.csv")
    df_mun = pd.read_csv("MAPA_MUNICIPIOS_RANKING.csv")
    df_pac["LAT_DECIMAL"] = pd.to_numeric(df_pac["LAT_DECIMAL"], errors="coerce")
    df_pac["LON_DECIMAL"] = pd.to_numeric(df_pac["LON_DECIMAL"], errors="coerce")
    df_pac = df_pac.dropna(subset=["LAT_DECIMAL", "LON_DECIMAL"])
    return df_pac, df_mun

try:
    df_pac, df_mun = cargar_datos()
except Exception as e:
    st.error("No se encontraron los archivos CSV en el repositorio.")
    st.stop()

# 3. BARRA LATERAL: FILTROS Y SIMULADOR WHAT-IF
with st.sidebar:
    st.markdown("## Panel de Control M.A.P.A.")
    st.caption("Modelo Analitico de Prediccion y Asignacion - Guanajuato")
    
    lista_municipios = ["Todo Guanajuato"] + sorted(df_mun["MUNICIPIO"].unique().tolist())
