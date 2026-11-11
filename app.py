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
