import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import qrcode
from io import BytesIO

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO EJECUTIVO GOBIERNO GTO
# ==============================================================================
st.set_page_config(
    page_title="M.A.P.A. Guanajuato | Simulador IA",
    page_icon="📍",
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CARGA DE DATOS (CON CACHÉ PARA MÁXIMA VELOCIDAD)
# ==============================================================================
@st.cache_data
def cargar_datos():
    df_pac = pd.read_csv("MAPA_PACIENTES_ENRIQUECIDO.csv")
    df_mun = pd.read_csv("MAPA_MUNICIPIOS_RANKING.csv")
    return df_pac, df_mun

try:
    df_pac, df_mun = cargar_datos()
except Exception as e:
    st.error("⚠️ No se encontraron los archivos CSV. Asegúrate de que 'MAPA_PACIENTES_ENRIQUECIDO.csv' y 'MAPA_MUNICIPIOS_RANKING.csv' estén en la misma carpeta que 'app.py'.")
    st.stop()

# ==============================================================================
# 3. BARRA LATERAL: FILTROS, SIMULADOR WHAT-IF (3 PALANCAS) Y CÓDIGO QR
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Panel de Control M.A.P.A.")
    st.caption("Modelo Analítico de Predicción y Asignación - Guanajuato")
    
    lista_municipios = ["Todo Guanajuato"] + sorted(df_mun["MUNICIPIO"].unique().tolist())
    mun_seleccionado = st.selectbox("📍 Filtrar Territorio:", lista_municipios)
    
    min_evaluados = st.checkbox("Filtrar Ranking con >= 10 evaluados (Focos Rojos Oficiales)", value=True)
    
    st.markdown("---")
    st.markdown("### 🎛️ Simulador 'What-If' (Las 3 Palancas)")
    st.caption("Desliza el porcentaje de cobertura presupuestal para simular el impacto en tiempo real:")
    
    slider_transporte = st.slider(
        "🚌 Palanca 1: Transporte Adaptado y U. Móviles (%)",
        min_value=0, max_value=100, value=0, step=5
    )
    slider_ortopedia = st.slider(
        "🦽 Palanca 2: Entrega de Ayudas Técnicas / Ortopedia (%)",
        min_value=0, max_value=100, value=0, step=5
    )
    slider_apoyo = st.slider(
        "🤝 Palanca 3: Apoyo al Cuidador y Accesibilidad (%)",
        min_value=0, max_value=100, value=0, step=5
    )
    
    st.markdown("---")
    st.markdown("### 📱 Acceso QR para Jueces")
    url_app = st.text_input(
        "Pega aquí el link de tu App para generar el QR:",
        value="https://mapa-gto-dataton.streamlit.app"
    )
    if url_app:
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(url_app)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="#003366", back_color="white")
        buf = BytesIO()
        img_qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="Escanea con tu celular para interactuar en vivo", use_container_width=True)

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
    <h1 style="margin:0; font-size: 28px;">📍 Sistema M.A.P.A. — Estado de Guanajuato</h1>
    <p style="margin:5px 0 0 0; font-size: 16px; opacity: 0.92;">
        Modelo Analítico de Predicción y Asignación de Recursos para Personas con Discapacidad | <b>Territorio: {mun_seleccionado}</b>
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader("📊 Impacto Presupuestal Simulado: Antes vs. Después de la Inversión")

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric(
        "Población Evaluada",
        f"{total_eval:,}",
        "100% Cobertura SIDIS"
    )
with c2:
    delta_ind = indice_urgencia_sim - indice_urgencia_base
    st.metric(
        "Índice Urgencia M.A.P.A.",
        f"{indice_urgencia_sim:.2f} pts",
        f"{delta_ind:.2f} pts (Base: {indice_urgencia_base:.2f})",
        delta_color="inverse"
    )
with c3:
    delta_exc = tasa_exc_sim - tasa_exc_base
    st.metric(
        "Tasa de Exclusión",
        f"{tasa_exc_sim:.1f}%",
        f"{delta_exc:.1f}% ({excluidos_rescatados} reinsertados)",
        delta_color="inverse"
    )
with c4:
    st.metric(
        "Barrera Transporte (P1)",
        f"{tot_transporte - rescatados_transporte:,} pac.",
        f"-{rescatados_transporte} rescatados (Base: {tot_transporte})",
        delta_color="inverse"
    )
with c5:
    st.metric(
        "Déficit Ayuda Técnica (P2)",
        f"{tot_tecnica - rescatados_ortopedia:,} pac.",
        f"-{rescatados_ortopedia} rescatados (Base: {tot_tecnica})",
        delta_color="inverse"
    )
with c6:
    st.metric(
        "Déficit Apoyo y Entorno (P3)",
        f"{tot_apoyo - rescatados_apoyo:,} pac.",
        f"-{rescatados_apoyo} rescatados (Base: {tot_apoyo})",
        delta_color="inverse"
    )

st.markdown("---")

# ==============================================================================
# 6. PESTAÑAS DE NAVEGACIÓN EJECUTIVA
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "🗺️ Mapa GPS (Clusters IA) & Focos Rojos",
    "🛒 Licitación Exacta de Ortopedia y Ayudas Técnicas",
    "🤖 Explorador de Pacientes y Predicción Random Forest"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: MAPA GPS Y RANKING DE MUNICIPIOS
# ------------------------------------------------------------------------------
with tab1:
    col_mapa, col_rank = st.columns([1.35, 1])
    
    with col_mapa:
        st.markdown("#### 📍 Georreferenciación de Pacientes por Cluster K-Means")
        colores_clusters = {
            "Cluster 0: Alta Severidad Clinica (Ortopedia/Cuidador)": "#D90429",
            "Cluster 2: Rural Entorno Critico (Unidades Moviles)": "#F77F00",
            "Cluster 1: Urbano Moderado (Inclusion Laboral/Becas)": "#2B9348"
        }
        
        zoom_nivel = 7.3 if mun_seleccionado == "Todo Guanajuato" else 10.2
        
        # Compatible tanto con Plotly 6+ (scatter_map) como con Plotly 5 (scatter_mapbox)
        if hasattr(px, "scatter_map"):
            fig_mapa = px.scatter_map(
                df_p_f,
                lat="LAT_DECIMAL",
                lon="LON_DECIMAL",
                color="PERFIL_CLUSTER",
                color_discrete_map=colores_clusters,
                hover_name="MUNICIPIO",
                hover_data={
                    "LOCALIDAD": True,
                    "DIAGNOSTICO": True,
                    "PCT_DISCAPACIDAD": True,
                    "PROBABILIDAD_DEFICIT_IA": ":.1f",
                    "LAT_DECIMAL": False,
                    "LON_DECIMAL": False
                },
                zoom=zoom_nivel,
                height=520
            )
            fig_mapa.update_layout(
                map_style="carto-positron",
                margin={"r":0,"t":10,"l":0,"b":0},
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, title=None)
            )
        else:
            fig_mapa = px.scatter_mapbox(
                df_p_f,
                lat="LAT_DECIMAL",
                lon="LON_DECIMAL",
                color="PERFIL_CLUSTER",
                color_discrete_map=colores_clusters,
                hover_name="MUNICIPIO",
                hover_data={
                    "LOCALIDAD": True,
                    "DIAGNOSTICO": True,
                    "PCT_DISCAPACIDAD": True,
                    "PROBABILIDAD_DEFICIT_IA": ":.1f",
                    "LAT_DECIMAL": False,
                    "LON_DECIMAL": False
                },
                zoom=zoom_nivel,
                height=520
            )
            fig_mapa.update_layout(
                mapbox_style="carto-positron",
                margin={"r":0,"t":10,"l":0,"b":0},
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, title=None)
            )
            
        st.plotly_chart(fig_mapa, use_container_width=True)
        
    with col_rank:
        st.markdown("#### 🚨 Top 10 Municipios en Foco Rojo (Índice M.A.P.A.)")
        df_rank = df_mun.copy()
        if min_evaluados:
            df_rank = df_rank[df_rank["TOTAL_EVALUADOS"] >= 10]
            
        # Recalcular Índice Simulado para cada municipio según Sliders
        df_rank["INDICE_SIMULADO"] = (
            0.40 * (df_rank["TASA_BARRERA_TRANSPORTE_PCT"] * (1.0 - slider_transporte / 100.0)) +
            0.35 * (df_rank["TASA_DEFICIT_TECNICO_PCT"] * (1.0 - slider_ortopedia / 100.0)) +
            0.25 * (df_rank["TASA_DEFICIT_APOYO_PCT"] * (1.0 - slider_apoyo / 100.0))
        )
        
        top10 = df_rank.sort_values("INDICE_URGENCIA_MAPA", ascending=False).head(10).sort_values("INDICE_URGENCIA_MAPA", ascending=True)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=top10["MUNICIPIO"],
            x=top10["INDICE_URGENCIA_MAPA"],
            name="Índice Base (Sin Intervención)",
            orientation="h",
            marker_color="#B0BEC5"
        ))
        fig_bar.add_trace(go.Bar(
            y=top10["MUNICIPIO"],
            x=top10["INDICE_SIMULADO"],
            name="Índice Post-Inversión (Simulado)",
            orientation="h",
            marker_color="#D90429"
        ))
        fig_bar.update_layout(
            barmode="overlay",
            height=520,
            xaxis_title="Índice de Urgencia M.A.P.A. (0 a 100)",
            yaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin={"r":10,"t":30,"l":10,"b":10}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------------------------------------------
# PESTAÑA 2: TABLA DE COMPRAS EXACTAS DE APARATOS ORTOPÉDICOS
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("#### 🛒 Cuadro de Adquisiciones Quirúrgicas para Gobierno (Palanca 2)")
    
    sillas_tot = int(df_p_f["FALTA_SILLA_RUEDAS"].sum())
    bastones_tot = int(df_p_f["FALTA_BASTON"].sum())
    andadores_tot = int(df_p_f["FALTA_ANDADOR"].sum())
    protesis_tot = int(df_p_f["FALTA_PROTESIS"].sum())
    audifonos_tot = int(df_p_f["FALTA_AUDIFONO"].sum())
    
    factor_orto = slider_ortopedia / 100.0
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🦽 Sillas de Ruedas", f"{sillas_tot} req.", f"{int(round(sillas_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k2.metric("🦯 Bastones", f"{bastones_tot} req.", f"{int(round(bastones_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k3.metric("🚶 Andadores", f"{andadores_tot} req.", f"{int(round(andadores_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k4.metric("🦿 Prótesis / Órtesis", f"{protesis_tot} req.", f"{int(round(protesis_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k5.metric("🦻 Audífonos", f"{audifonos_tot} req.", f"{int(round(audifonos_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    
    st.markdown("##### 📋 Desglose Exacto de Compras por Municipio")
    cols_compras = [
        "MUNICIPIO", "TOTAL_EVALUADOS", "INDICE_URGENCIA_MAPA", "TASA_EXCLUSION_PCT",
        "TOTAL_SIN_AYUDA_TECNICA", "SILLAS_FALTANTES", "BASTONES_FALTANTES",
        "ANDADORES_FALTANTES", "PROTESIS_FALTANTES", "AUDIFONOS_FALTANTES"
    ]
    tabla_compras = df_m_f[cols_compras].sort_values("TOTAL_SIN_AYUDA_TECNICA", ascending=False)
    st.dataframe(tabla_compras, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# PESTAÑA 3: EXPLORADOR DE PACIENTES Y SCORE RANDOM FOREST
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("#### 🤖 Padrón Nominal Priorizado por Random Forest (`PROBABILIDAD_DEFICIT_IA`)")
    st.caption("Ordenado desde el paciente con mayor probabilidad de rezago crítico para despliegue inmediato de brigadas:")
    
    cols_pac = [
        "ID_REGISTRO", "MUNICIPIO", "LOCALIDAD", "AMBITO", "EDAD", "SEXO",
        "DIAGNOSTICO", "PCT_DISCAPACIDAD", "PERFIL_CLUSTER", "PROBABILIDAD_DEFICIT_IA",
        "EXCLUIDO_LABORAL_EDUCATIVO", "BARRERA_TRANSPORTE", "DEFICIT_AYUDA_TECNICA", "DEFICIT_APOYO_Y_ENTORNO"
    ]
    st.dataframe(
        df_p_f[cols_pac].sort_values("PROBABILIDAD_DEFICIT_IA", ascending=False),
        use_container_width=True,
        hide_index=True
    )
