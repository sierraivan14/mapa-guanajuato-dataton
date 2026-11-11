import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from pathlib import Path
import base64

AZUL_INST = "#1A73E8"
AZUL_INST_ALT = "#1967D2"
AZUL_OSCURO = "#0D47A1"
AZUL_CLARO = "#E8F0FE"
GRIS_BASE = "#D1D5DB"
GRIS_FONDO = "#F3F4F6"

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR
LOGO_PRINCIPAL = ASSETS / "logo_derechos_humanos.png"

def mostrar_imagen(ruta, **kwargs):
    if Path(ruta).exists():
        st.image(str(ruta), **kwargs)

def logo_fijo(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        return ""
    datos = base64.b64encode(ruta.read_bytes()).decode()
    return (
        "<img src='data:image/png;base64," + datos + "' "
        "style='width:100%; max-width: 180px; pointer-events:none; user-select:none;' draggable='false'>"
    )

st.set_page_config(
    page_title="M.A.P.A. Guanajuato | Simulador IA",
    page_icon=str(LOGO_PRINCIPAL) if LOGO_PRINCIPAL.exists() else None,
    layout="wide",
    initial_sidebar_state="auto"
)

css_style = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');"
    "html, body, [class*='css'] { font-family: 'Inter', sans-serif; }"
    ".stApp { background-color: " + GRIS_FONDO + "; }"
    "[data-testid='stSidebar'] { background-color: #ffffff; border-right: 1px solid #E5E7EB; }"
    ".header-box { "
    "   background: linear-gradient(135deg, " + AZUL_OSCURO + " 0%, " + AZUL_INST + " 100%); "
    "   color: white; "
    "   padding: 24px 30px; "
    "   border-radius: 12px; "
    "   margin-bottom: 24px; "
    "   box-shadow: 0 10px 15px -3px rgba(26, 115, 232, 0.2), 0 4px 6px -2px rgba(26, 115, 232, 0.1); "
    "}"
    ".header-box h1 { font-weight: 700; letter-spacing: -0.5px; }"
    "div[data-testid='metric-container'] { "
    "   background-color: #ffffff; "
    "   padding: 16px 20px; "
    "   border-radius: 10px; "
    "   border: 1px solid #E5E7EB; "
    "   border-left: 6px solid " + AZUL_INST + "; "
    "   box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); "
    "   transition: transform 0.2s ease, box-shadow 0.2s ease; "
    "}"
    "div[data-testid='metric-container']:hover { "
    "   transform: translateY(-2px); "
    "   box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); "
    "}"
    "div[data-testid='metric-container'] label { "
    "   color: #6B7280; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.02em; "
    "}"
    ".legend-box { "
    "   padding: 12px 16px; "
    "   border-radius: 8px; "
    "   background-color: #ffffff; "
    "   border: 1px solid #E5E7EB; "
    "   box-shadow: 0 1px 3px rgba(0,0,0,0.05); "
    "   margin-bottom: 15px; "
    "   font-size: 13px; "
    "   color: #374151; "
    "}"
    "h2, h3, h4 { color: #111827; font-weight: 600; }"
    "h3 { margin-bottom: 1rem; }"
    ".stTabs [data-baseweb='tab-list'] { gap: 8px; }"
    ".stTabs [data-baseweb='tab'] { "
    "   background-color: #ffffff; "
    "   border-radius: 8px 8px 0 0; "
    "   padding: 10px 16px; "
    "   border: 1px solid transparent; "
    "}"
    ".stTabs [aria-selected='true'] { "
    "   background-color: #ffffff; "
    "   border-color: #E5E7EB; "
    "   border-bottom-color: #ffffff; "
    "   color: " + AZUL_INST + "; font-weight: 600; "
    "}"
    "[data-testid='stDataFrame'], [data-testid='stPlotlyChart'] { "
    "   background-color: #ffffff; "
    "   padding: 10px; "
    "   border-radius: 10px; "
    "   box-shadow: 0 1px 3px rgba(0,0,0,0.05); "
    "   border: 1px solid #E5E7EB; "
    "}"
    ".footer-box { "
    "   text-align: center; "
    "   padding: 20px; "
    "   margin-top: 40px; "
    "   border-top: 1px solid #E5E7EB; "
    "   color: #6B7280; "
    "   font-size: 13px; "
    "}"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    df_pac = pd.read_csv("MAPA_PACIENTES_ENRIQUECIDO.csv")
    df_mun = pd.read_csv("MAPA_MUNICIPIOS_RANKING.csv")
    
    df_pac["LAT_DECIMAL"] = pd.to_numeric(df_pac["LAT_DECIMAL"], errors="coerce")
    df_pac["LON_DECIMAL"] = pd.to_numeric(df_pac["LON_DECIMAL"], errors="coerce")

    return df_pac, df_mun

try:
    df_pac, df_mun = cargar_datos()
except Exception as e:
    st.error("No se encontraron los archivos CSV en el repositorio.")
    st.stop()

with st.sidebar:
    st.markdown("## Panel de Control")
    st.caption("M.A.P.A. Guanajuato")
    st.divider()
    
    lista_municipios = ["Todo Guanajuato"] + sorted(df_mun["MUNICIPIO"].unique().tolist())
    mun_seleccionado = st.selectbox("Filtrar Territorio:", lista_municipios)
    
    min_evaluados = st.checkbox("Filtrar Ranking con >= 10 evaluados (Focos Rojos)", value=True)
    
    st.divider()
    st.markdown("#### Simulador de Presupuesto")
    st.caption("Seleccione el porcentaje de cobertura para simular el impacto:")
    
    slider_transporte = st.number_input(
        "Palanca 1: Transporte y U. Moviles (%)",
        min_value=0, max_value=100, value=0, step=1
    )
    slider_ortopedia = st.number_input(
        "Palanca 2: Ayudas Tecnicas/Ortopedia (%)",
        min_value=0, max_value=100, value=0, step=1
    )
    slider_apoyo = st.number_input(
        "Palanca 3: Apoyo a Cuidador (%)",
        min_value=0, max_value=100, value=0, step=1
    )

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

tasa_exc_base = (tot_excluidos / total_eval * 100.0) if total_eval > 0 else 0.0
tasa_trans_base = (tot_transporte / total_eval * 100.0) if total_eval > 0 else 0.0
tasa_tec_base = (tot_tecnica / total_eval * 100.0) if total_eval > 0 else 0.0
tasa_apo_base = (tot_apoyo / total_eval * 100.0) if total_eval > 0 else 0.0

indice_urgencia_base = (0.40 * tasa_trans_base) + (0.35 * tasa_tec_base) + (0.25 * tasa_apo_base)

rescatados_transporte = int(round(tot_transporte * (slider_transporte / 100.0)))
rescatados_ortopedia = int(round(tot_tecnica * (slider_ortopedia / 100.0)))
rescatados_apoyo = int(round(tot_apoyo * (slider_apoyo / 100.0)))

tasa_trans_post = tasa_trans_base * (1.0 - slider_transporte / 100.0)
tasa_tec_post = tasa_tec_base * (1.0 - slider_ortopedia / 100.0)
tasa_apo_post = tasa_apo_base * (1.0 - slider_apoyo / 100.0)

indice_urgencia_sim = (0.40 * tasa_trans_post) + (0.35 * tasa_tec_post) + (0.25 * tasa_apo_post)

factor_mitigacion_ia = (0.40 * (slider_transporte / 100.0)) + (0.35 * (slider_ortopedia / 100.0)) + (0.25 * (slider_apoyo / 100.0))
tasa_exc_sim = tasa_exc_base * (1.0 - factor_mitigacion_ia)
excluidos_rescatados = int(round(tot_excluidos * factor_mitigacion_ia))

col_logo, col_header = st.columns([1, 5], vertical_alignment="center")

with col_logo:
    st.markdown(logo_fijo(LOGO_PRINCIPAL), unsafe_allow_html=True)

with col_header:
    header_html = (
        "<div class='header-box'>"
        "<h1 style='margin:0; font-size: 32px; color: white;'>Sistema M.A.P.A.</h1>"
        "<p style='margin:8px 0 0 0; font-size: 15px; opacity: 0.90; font-weight: 300;'>"
        "Modelo Analítico de Predicción y Asignación de Recursos | <b>Territorio: " + str(mun_seleccionado) + "</b>"
        "</p></div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)

st.markdown("### Impacto Presupuestal Simulado")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Población Evaluada", f"{total_eval:,}", "100% Cobertura SIDIS")
with c2:
    delta_ind = indice_urgencia_sim - indice_urgencia_base
    st.metric("Índice Urgencia M.A.P.A.", f"{indice_urgencia_sim:.2f} pts", f"{delta_ind:.2f} pts (Base: {indice_urgencia_base:.2f})", delta_color="inverse")
with c3:
    delta_exc = tasa_exc_sim - tasa_exc_base
    st.metric("Tasa de Exclusión", f"{tasa_exc_sim:.1f}%", f"{delta_exc:.1f}% ({excluidos_rescatados} reinsertados)", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)
with c4:
    st.metric("Barrera Transporte (P1)", f"{tot_transporte - rescatados_transporte:,} pac.", f"-{rescatados_transporte} rescatados (Base: {tot_transporte})", delta_color="inverse")
with c5:
    st.metric("Déficit Ayuda Técnica (P2)", f"{tot_tecnica - rescatados_ortopedia:,} pac.", f"-{rescatados_ortopedia} rescatados (Base: {tot_tecnica})", delta_color="inverse")
with c6:
    st.metric("Déficit Apoyo y Entorno (P3)", f"{tot_apoyo - rescatados_apoyo:,} pac.", f"-{rescatados_apoyo} rescatados (Base: {tot_apoyo})", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📍 Mapa (Clústers IA)",
    "🛒 Adquisiciones Exactas",
    "📋 Explorador Random Forest"
])

with tab1:
    col_mapa, col_rank = st.columns([1.2, 1])
    
    with col_mapa:
        st.markdown("#### Distribución Espacial K-Means")

        legend_html = (
            "<div class='legend-box'>"
            "<strong>Leyenda de Severidad:</strong><br>"
            "<span style='color:#DC2626;'>●</span> Cluster 0 (Alta: Ortopedia/Cuidador) &nbsp;|&nbsp; "
            "<span style='color:#F59E0B;'>●</span> Cluster 2 (Media: Rural/Móviles) &nbsp;|&nbsp; "
            "<span style='color:#10B981;'>●</span> Cluster 1 (Baja: Urbano/Becas)"
            "</div>"
        )
        st.markdown(legend_html, unsafe_allow_html=True)
        
        colores_clusters = {
            "Cluster 0: Alta Severidad Clinica (Ortopedia/Cuidador)": "#DC2626",
            "Cluster 2: Rural Entorno Critico (Unidades Moviles)": "#F59E0B",
            "Cluster 1: Urbano Moderado (Inclusion Laboral/Becas)": "#10B981"
        }
        
        df_mapa_local = df_p_f.dropna(subset=["LAT_DECIMAL", "LON_DECIMAL"])
        
        if len(df_mapa_local) > 0:
            lat_centro = float(df_mapa_local["LAT_DECIMAL"].mean())
            lon_centro = float(df_mapa_local["LON_DECIMAL"].mean())
        else:
            lat_centro, lon_centro = 21.0190, -101.2574
            
        zoom_nivel = 8 if mun_seleccionado == "Todo Guanajuato" else 11
        
        m = folium.Map(
            location=[lat_centro, lon_centro],
            zoom_start=zoom_nivel,
            tiles="CartoDB positron",
            control_scale=True
        )
        
        for _, row in df_mapa_local.iterrows():
            perfil = str(row["PERFIL_CLUSTER"])
            color_punto = colores_clusters.get(perfil, AZUL_INST_ALT)
            tooltip_txt = (
                "<b>Municipio:</b> " + str(row["MUNICIPIO"]) + "<br>"
                "<b>Localidad:</b> " + str(row["LOCALIDAD"]) + "<br>"
                "<b>Cluster:</b> " + perfil + "<br>"
                "<b>Diagnóstico:</b> " + str(row["DIAGNOSTICO"]) + "<br>"
                "<b>Discapacidad:</b> " + str(row["PCT_DISCAPACIDAD"]) + "%<br>"
                "<b>Prob. Déficit IA:</b> " + f"{row['PROBABILIDAD_DEFICIT_IA']:.1f}%"
            )
            folium.CircleMarker(
                location=[float(row["LAT_DECIMAL"]), float(row["LON_DECIMAL"])],
                radius=4.5,
                color=color_punto,
                weight=1,
                fill=True,
                fill_color=color_punto,
                fill_opacity=0.75,
                tooltip=folium.Tooltip(tooltip_txt)
            ).add_to(m)
            
        st_folium(m, use_container_width=True, height=500, returned_objects=[])
        
    with col_rank:
        st.markdown("#### Top 10 Focos Rojos Municipales")
        df_rank = df_mun.copy()
        if min_evaluados:
            df_rank = df_rank[df_rank["TOTAL_EVALUADOS"] >= 10]

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
            name="Índice Base",
            orientation="h",
            marker_color=GRIS_BASE,
            marker_line_width=0
        ))
        fig_bar.add_trace(go.Bar(
            y=top10["MUNICIPIO"],
            x=top10["INDICE_SIMULADO"],
            name="Índice Simulado",
            orientation="h",
            marker_color=AZUL_INST,
            marker_line_width=0
        ))
        
        fig_bar.update_layout(
            barmode="overlay",
            height=500,
            xaxis_title="Índice de Urgencia (0 a 100)",
            yaxis_title=None,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h", 
                yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=12, color="#4B5563")
            ),
            margin={"r": 10, "t": 30, "l": 10, "b": 10},
            bargap=0.3
        )
        fig_bar.update_xaxes(fixedrange=True, showgrid=True, gridwidth=1, gridcolor='#E5E7EB')
        fig_bar.update_yaxes(fixedrange=True, showgrid=False)

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config={
                "displaylogo": False,
                "modeBarButtons": [["toImage"]],
            },
        )

with tab2:
    st.markdown("#### Cuadro de Adquisiciones Gubernamentales")
    st.caption("Cálculo exacto basado en pacientes nominales y porcentaje de inversión.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    sillas_tot = int(df_p_f["FALTA_SILLA_RUEDAS"].sum())
    bastones_tot = int(df_p_f["FALTA_BASTON"].sum())
    andadores_tot = int(df_p_f["FALTA_ANDADOR"].sum())
    protesis_tot = int(df_p_f["FALTA_PROTESIS"].sum())
    audifonos_tot = int(df_p_f["FALTA_AUDIFONO"].sum())
    
    factor_orto = slider_ortopedia / 100.0
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Sillas de Ruedas", f"{sillas_tot} req.", f"+{int(round(sillas_tot * factor_orto))} a comprar")
    k2.metric("Bastones", f"{bastones_tot} req.", f"+{int(round(bastones_tot * factor_orto))} a comprar")
    k3.metric("Andadores", f"{andadores_tot} req.", f"+{int(round(andadores_tot * factor_orto))} a comprar")
    k4.metric("Prótesis / Órtesis", f"{protesis_tot} req.", f"+{int(round(protesis_tot * factor_orto))} a comprar")
    k5.metric("Audífonos", f"{audifonos_tot} req.", f"+{int(round(audifonos_tot * factor_orto))} a comprar")
    
    st.markdown("<br>##### Desglose por Municipio", unsafe_allow_html=True)
    cols_compras = [
        "MUNICIPIO", "TOTAL_EVALUADOS", "INDICE_URGENCIA_MAPA", "TASA_EXCLUSION_PCT",
        "TOTAL_SIN_AYUDA_TECNICA", "SILLAS_FALTANTES", "BASTONES_FALTANTES",
        "ANDADORES_FALTANTES", "PROTESIS_FALTANTES", "AUDIFONOS_FALTANTES"
    ]
    tabla_compras = df_m_f[cols_compras].sort_values("TOTAL_SIN_AYUDA_TECNICA", ascending=False)
    st.dataframe(tabla_compras, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### Padrón Nominal Priorizado por Random Forest")
    st.caption("Ordenado desde el paciente con mayor probabilidad de rezago crítico.")
    
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

st.markdown(
    "<div class='footer-box'><b>Gobierno del Estado de Guanajuato</b> | Secretaría de Derechos Humanos | M.A.P.A. 2024-2030</div>",
    unsafe_allow_html=True
)
