import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO EJECUTIVO GOBIERNO GTO
# ==============================================================================
st.set_page_config(
    page_title="M.A.P.A. Guanajuato | Simulador IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .header-box {
        background: linear-gradient(90deg, #003366 0%, #0055A5 100%);
        color: white;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    }
    div[data-testid="stMetric"] {
        border-left: 5px solid #0055A5;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .legend-box {
        padding: 10px 14px;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 10px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CARGA DE DATOS (CON CACHÉ PARA MÁXIMA VELOCIDAD)
# ==============================================================================
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
    st.error("No se encontraron los archivos CSV. Asegúrate de que 'MAPA_PACIENTES_ENRIQUECIDO.csv' y 'MAPA_MUNICIPIOS_RANKING.csv' estén en la misma carpeta que 'app.py'.")
    st.stop()

# ==============================================================================
# 3. BARRA LATERAL: FILTROS Y SIMULADOR WHAT-IF (3 PALANCAS)
# ==============================================================================
with st.sidebar:
    st.markdown("## Panel de Control M.A.P.A.")
    st.caption("Modelo Analítico de Predicción y Asignación - Guanajuato")
    
    lista_municipios = ["Todo Guanajuato"] + sorted(df_mun["MUNICIPIO"].unique().tolist())
    mun_seleccionado = st.selectbox("Filtrar Territorio:", lista_municipios)
    
    min_evaluados = st.checkbox("Filtrar Ranking con >= 10 evaluados (Focos Rojos Oficiales)", value=True)
    
    st.markdown("---")
    st.markdown("### Simulador 'What-If' (Las 3 Palancas)")
    st.caption("Desliza el porcentaje de cobertura presupuestal para simular el impacto en tiempo real:")
    
    slider_transporte = st.slider(
        "Palanca 1: Transporte Adaptado y U. Móviles (%)",
        min_value=0, max_value=100, value=0, step=5
    )
    slider_ortopedia = st.slider(
        "Palanca 2: Entrega de Ayudas Técnicas / Ortopedia (%)",
        min_value=0, max_value=100, value=0, step=5
    )
    slider_apoyo = st.slider(
        "Palanca 3: Apoyo al Cuidador y Accesibilidad (%)",
        min_value=0, max_value=100, value=0, step=5
    )

# ==============================================================================
# 4. MOTOR MATEMÁTICO DEL SIMULADOR WHAT-IF
# ==============================================================================
if mun_seleccionado == "Todo Guanajuato":
    df_p_f = df_pac.copy()
    df_m_f = df_mun.copy()
else:
    df_p_f = df_pac[df_pac["MUNICIPIO"] == mun_seleccionado].copy()
    df_m_f = df_mun[df_mun["MUNICIPIO"] == mun_seleccionado].copy()

total_eval = len(df_p_f)
tot_excluidos = int(df_p_f["EXCLUIDO_LABORAL_EDUCATIVO"].sum())
tot_transporte = int(df_p_f["BARRERA_TRANSPORTE"].sum())
tot_tecnica = int(df_p_f["DEFICIT_AYUDA_TECNICA"].sum())
tot_apoyo = int(df_p_f["DEFICIT_APOYO_Y_ENTORNO"].sum())

# Tasas Base (Antes de la inversión)
tasa_exc_base = (tot_excluidos / total_eval * 100) if total_eval > 0 else 0.0
tasa_trans_base = (tot_transporte / total_eval * 100) if total_eval > 0 else 0.0
tasa_tec_base = (tot_tecnica / total_eval * 100) if total_eval > 0 else 0.0
tasa_apo_base = (tot_apoyo / total_eval * 100) if total_eval > 0 else 0.0

indice_urgencia_base = (0.40 * tasa_trans_base) + (0.35 * tasa_tec_base) + (0.25 * tasa_apo_base)

# Pacientes Rescatados por Palanca
rescatados_transporte = int(round(tot_transporte * (slider_transporte / 100.0)))
rescatados_ortopedia = int(round(tot_tecnica * (slider_ortopedia / 100.0)))
rescatados_apoyo = int(round(tot_apoyo * (slider_apoyo / 100.0)))

# Tasas Post-Intervención (Después de la inversión)
tasa_trans_post = tasa_trans_base * (1.0 - slider_transporte / 100.0)
tasa_tec_post = tasa_tec_base * (1.0 - slider_ortopedia / 100.0)
tasa_apo_post = tasa_apo_base * (1.0 - slider_apoyo / 100.0)

indice_urgencia_sim = (0.40 * tasa_trans_post) + (0.35 * tasa_tec_post) + (0.25 * tasa_apo_post)

# Reducción ponderada de la Exclusión Laboral/Educativa (40% Transp, 35% Ortopedia, 25% Apoyo)
factor_mitigacion_ia = (0.40 * (slider_transporte / 100.0)) + (0.35 * (slider_ortopedia / 100.0)) + (0.25 * (slider_apoyo / 100.0))
tasa_exc_sim = tasa_exc_base * (1.0 - factor_mitigacion_ia)
excluidos_rescatados = int(round(tot_excluidos * factor_mitigacion_ia))

# ==============================================================================
# 5. ENCABEZADO Y TARJETAS KPI (ANTES VS. DESPUÉS DE LA INVERSIÓN)
# ==============================================================================
st.markdown(f"""
<div class="header-box">
