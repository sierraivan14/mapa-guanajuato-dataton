import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from pathlib import Path
import base64


AZUL_INST = "#0082FF"
AZUL_INST_ALT = "#0066FF"
AZUL_OSCURO = "#00408F"
AZUL_CLARO = "#E6F2FF"
GRIS_BASE = "#B0BEC5"

# Rutas de imagenes que estan dentro de la raiz
BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR  
LOGO_PRINCIPAL = ASSETS / "logo_derechos_humanos.png"

# Esto es en caso de que no exista una imagen, no se rompa el programa
def mostrar_imagen(ruta, **kwargs):
    if Path(ruta).exists():
        st.image(str(ruta), **kwargs)

#Convierte la imagen en html para que no se pueda ampliar la imagen
def logo_fijo(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        return ""
    datos = base64.b64encode(ruta.read_bytes()).decode()
    return (
        "<img src='data:image/png;base64," + datos + "' "
        "style='width:100%; pointer-events:none; user-select:none;' draggable='false'>"
    )


# CONFIGURACION DE LA PAGINA Y ESTILO EJECUTIVO
st.set_page_config(
    page_title="M.A.P.A. Guanajuato | Simulador IA",
    page_icon=str(LOGO_PRINCIPAL) if LOGO_PRINCIPAL.exists() else None,
    layout="wide",
    initial_sidebar_state="auto"
)

css_style = (
    "<style>"
    ".header-box { background: linear-gradient(90deg, " + AZUL_OSCURO + " 0%, " + AZUL_INST_ALT + " 55%, " + AZUL_INST + " 100%); color: white; padding: 22px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,102,255,0.30); }"
    "div[data-testid='stMetric'] { border-left: 5px solid " + AZUL_INST + "; padding: 12px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,130,255,0.18); }"
    ".legend-box { padding: 10px 14px; border-radius: 8px; background-color: rgba(0, 130, 255, 0.08); border: 1px solid rgba(0, 130, 255, 0.35); margin-bottom: 10px; font-size: 14px; }"
    "h2, h3, h4 { color: " + AZUL_INST_ALT + "; }"
    ".footer-box { text-align: center; padding: 14px; margin-top: 24px; border-top: 3px solid " + AZUL_INST + "; font-size: 13px; opacity: 0.85; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# CARGA DE DATOS
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

# BARRA LATERAL: FILTROS Y SIMULADOR WHAT-IF
with st.sidebar:
    st.markdown("## Panel de Control M.A.P.A.")
    st.caption("Modelo Analitico de Prediccion y Asignacion - Guanajuato")
    
    lista_municipios = ["Todo Guanajuato"] + sorted(df_mun["MUNICIPIO"].unique().tolist())
    mun_seleccionado = st.selectbox("Filtrar Territorio:", lista_municipios)
    
    min_evaluados = st.checkbox("Filtrar Ranking con >= 10 evaluados (Focos Rojos Oficiales)", value=True)
    
    st.caption("Seleccione el porcentaje de cobertura presupuestal para simular el impacto en tiempo real:")
    
    slider_transporte = st.number_input(
        "Palanca 1: Transporte Adaptado y U. Moviles (%)",
        min_value=0, max_value=100, value=0, step=1
    )
    slider_ortopedia = st.number_input(
        "Palanca 2: Entrega de Ayudas Tecnicas / Ortopedia (%)",
        min_value=0, max_value=100, value=0, step=1
    )
    slider_apoyo = st.number_input(
        "Palanca 3: Apoyo al Cuidador y Accesibilidad (%)",
        min_value=0, max_value=100, value=0, step=1
    )

# MOTOR MATEMATICO DEL SIMULADOR WHAT-IF
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

# ENCABEZADO (LOGO + BANNER) Y TARJETAS KPI
col_logo, col_header = st.columns([1, 4], vertical_alignment="center")

with col_logo:
    st.markdown(logo_fijo(LOGO_PRINCIPAL), unsafe_allow_html=True)

with col_header:
    header_html = (
        "<div class='header-box'>"
        "<h1 style='margin:0; font-size: 28px; color: white;'>Sistema M.A.P.A. - Estado de Guanajuato</h1>"
        "<p style='margin:5px 0 0 0; font-size: 16px; opacity: 0.95;'>"
        "Modelo Analitico de Prediccion y Asignacion de Recursos para Personas con Discapacidad | <b>Territorio: " + str(mun_seleccionado) + "</b>"
        "</p></div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)

st.subheader("Impacto Presupuestal Simulado: Antes vs. Despues de la Inversion")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Poblacion Evaluada", f"{total_eval:,}", "100% Cobertura SIDIS")
with c2:
    delta_ind = indice_urgencia_sim - indice_urgencia_base
    st.metric("Indice Urgencia M.A.P.A.", f"{indice_urgencia_sim:.2f} pts", f"{delta_ind:.2f} pts (Base: {indice_urgencia_base:.2f})", delta_color="inverse")
with c3:
    delta_exc = tasa_exc_sim - tasa_exc_base
    st.metric("Tasa de Exclusion", f"{tasa_exc_sim:.1f}%", f"{delta_exc:.1f}% ({excluidos_rescatados} reinsertados)", delta_color="inverse")

c4, c5, c6 = st.columns(3)
with c4:
    st.metric("Barrera Transporte (P1)", f"{tot_transporte - rescatados_transporte:,} pac.", f"-{rescatados_transporte} rescatados (Base: {tot_transporte})", delta_color="inverse")
with c5:
    st.metric("Deficit Ayuda Tecnica (P2)", f"{tot_tecnica - rescatados_ortopedia:,} pac.", f"-{rescatados_ortopedia} rescatados (Base: {tot_tecnica})", delta_color="inverse")
with c6:
    st.metric("Deficit Apoyo y Entorno (P3)", f"{tot_apoyo - rescatados_apoyo:,} pac.", f"-{rescatados_apoyo} rescatados (Base: {tot_apoyo})", delta_color="inverse")

st.markdown("---")

# PESTANAS DE NAVEGACION
tab1, tab2, tab3 = st.tabs([
    "Mapa GPS (Clusters IA) y Focos Rojos",
    "Licitacion Exacta de Ortopedia y Ayudas Tecnicas",
    "Explorador de Pacientes y Prediccion Random Forest"
])

with tab1:
    col_mapa, col_rank = st.columns([1.35, 1])
    
    with col_mapa:
        st.markdown("#### Georreferenciacion de Pacientes por Cluster K-Means")

        legend_html = (
            "<div class='legend-box'>"
            "<span style='color:#D90429; font-weight:bold;'>Cluster 0 (Rojo):</span> Alta Severidad Clinica (Ortopedia/Cuidador) | "
            "<span style='color:#F77F00; font-weight:bold;'>Cluster 2 (Naranja):</span> Rural Entorno Critico (U. Moviles) | "
            "<span style='color:#2B9348; font-weight:bold;'>Cluster 1 (Verde):</span> Urbano Moderado (Inclusion/Becas)"
            "</div>"
        )
        st.markdown(legend_html, unsafe_allow_html=True)
        
        colores_clusters = {
            "Cluster 0: Alta Severidad Clinica (Ortopedia/Cuidador)": "#D90429",
            "Cluster 2: Rural Entorno Critico (Unidades Moviles)": "#F77F00",
            "Cluster 1: Urbano Moderado (Inclusion Laboral/Becas)": "#2B9348"
        }
        
        if len(df_p_f) > 0:
            lat_centro = float(df_p_f["LAT_DECIMAL"].mean())
            lon_centro = float(df_p_f["LON_DECIMAL"].mean())
        else:
            lat_centro, lon_centro = 21.0190, -101.2574
            
        zoom_nivel = 8 if mun_seleccionado == "Todo Guanajuato" else 11
        
        m = folium.Map(
            location=[lat_centro, lon_centro],
            zoom_start=zoom_nivel,
            tiles="OpenStreetMap",
            control_scale=True
        )
        
        for _, row in df_p_f.iterrows():
            perfil = str(row["PERFIL_CLUSTER"])
            color_punto = colores_clusters.get(perfil, AZUL_INST_ALT)
            tooltip_txt = (
                "<b>Municipio:</b> " + str(row["MUNICIPIO"]) + "<br>"
                "<b>Localidad:</b> " + str(row["LOCALIDAD"]) + "<br>"
                "<b>Cluster:</b> " + perfil + "<br>"
                "<b>Diagnostico:</b> " + str(row["DIAGNOSTICO"]) + "<br>"
                "<b>Discapacidad:</b> " + str(row["PCT_DISCAPACIDAD"]) + "%<br>"
                "<b>Prob. Deficit IA:</b> " + f"{row['PROBABILIDAD_DEFICIT_IA']:.1f}%"
            )
            folium.CircleMarker(
                location=[float(row["LAT_DECIMAL"]), float(row["LON_DECIMAL"])],
                radius=5,
                color=color_punto,
                fill=True,
                fill_color=color_punto,
                fill_opacity=0.85,
                tooltip=folium.Tooltip(tooltip_txt)
            ).add_to(m)
            
        st_folium(m, use_container_width=True, height=480, returned_objects=[])
        
    with col_rank:
        st.markdown("#### Top 10 Municipios en Foco Rojo (Indice M.A.P.A.)")
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
            name="Indice Base (Sin Intervencion)",
            orientation="h",
            marker_color=GRIS_BASE
        ))
        fig_bar.add_trace(go.Bar(
            y=top10["MUNICIPIO"],
            x=top10["INDICE_SIMULADO"],
            name="Indice Post-Inversion (Simulado)",
            orientation="h",
            marker_color=AZUL_INST
        ))
        fig_bar.update_layout(
            barmode="overlay",
            height=520,
            xaxis_title="Indice de Urgencia M.A.P.A. (0 a 100)",
            yaxis_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin={"r": 10, "t": 30, "l": 10, "b": 10}
        )
        fig_bar.update_xaxes(fixedrange=True)
        fig_bar.update_yaxes(fixedrange=True)

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config={
                "displaylogo": False,
                "modeBarButtons": [["toImage"]],
                "toImageButtonOptions": {"format": "png", "filename": "ranking_mapa", "scale": 2},
            },
        )

with tab2:
    st.markdown("#### Cuadro de Adquisiciones Quirurgicas para Gobierno")
    
    sillas_tot = int(df_p_f["FALTA_SILLA_RUEDAS"].sum())
    bastones_tot = int(df_p_f["FALTA_BASTON"].sum())
    andadores_tot = int(df_p_f["FALTA_ANDADOR"].sum())
    protesis_tot = int(df_p_f["FALTA_PROTESIS"].sum())
    audifonos_tot = int(df_p_f["FALTA_AUDIFONO"].sum())
    
    factor_orto = slider_ortopedia / 100.0
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Sillas de Ruedas", f"{sillas_tot} req.", f"{int(round(sillas_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k2.metric("Bastones", f"{bastones_tot} req.", f"{int(round(bastones_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k3.metric("Andadores", f"{andadores_tot} req.", f"{int(round(andadores_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k4.metric("Protesis / Ortesis", f"{protesis_tot} req.", f"{int(round(protesis_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    k5.metric("Audifonos", f"{audifonos_tot} req.", f"{int(round(audifonos_tot * factor_orto))} a comprar ({slider_ortopedia}%)")
    
    st.markdown("##### Desglose Exacto de Compras por Municipio")
    cols_compras = [
        "MUNICIPIO", "TOTAL_EVALUADOS", "INDICE_URGENCIA_MAPA", "TASA_EXCLUSION_PCT",
        "TOTAL_SIN_AYUDA_TECNICA", "SILLAS_FALTANTES", "BASTONES_FALTANTES",
        "ANDADORES_FALTANTES", "PROTESIS_FALTANTES", "AUDIFONOS_FALTANTES"
    ]
    tabla_compras = df_m_f[cols_compras].sort_values("TOTAL_SIN_AYUDA_TECNICA", ascending=False)
    st.dataframe(tabla_compras, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### Padron Nominal Priorizado por Random Forest")
    st.caption("Ordenado desde el paciente con mayor probabilidad de rezago critico para despliegue inmediato de brigadas:")
    
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

# PIE DE PAGINA
st.markdown(
    "<div class='footer-box'><b>Gobierno del Estado de Guanajuato</b> | Secretaria de Derechos Humanos | M.A.P.A. 2024-2030</div>",
    unsafe_allow_html=True
)
