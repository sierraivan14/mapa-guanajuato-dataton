<div align="center">

# M.A.P.A. Guanajuato
### Modelo Analítico de Predicción y Asignación de Recursos para Personas con Discapacidad

*Proyecto desarrollado en el **Primer Datathon Guanajuato de Discapacidad***

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=leaflet&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

</div>

---

## 1. Resumen Ejecutivo

**M.A.P.A. Guanajuato** es una herramienta de apoyo a la decisión pública que transforma los datos de evaluación de personas con discapacidad en respuestas concretas a tres preguntas de gestión:

1. **¿Dónde está la necesidad más urgente?** Mapa georreferenciado y ranking de municipios en "foco rojo".
2. **¿Qué hay que adquirir y para quién?** Cuadro de adquisiciones por tipo de ayuda técnica y padrón nominal priorizado.
3. **¿Qué impacto tendría una inversión?** Simulador *what-if* que muestra, en tiempo real, el antes y el después de cada decisión presupuestal.

**Valor público.** Los recursos para transporte adaptado, ayudas técnicas y apoyo a cuidadores son limitados. M.A.P.A. permite asignarlos con evidencia: prioriza territorios con un índice objetivo, estima cuántas personas dejarían de enfrentar cada barrera según el nivel de cobertura elegido y ordena a la población por probabilidad de rezago crítico para planear brigadas de atención.

| Decisión de gobierno | Qué aporta M.A.P.A. |
|---|---|
| Priorizar municipios | Índice de Urgencia M.A.P.A. y Top 10 de focos rojos con filtro de confiabilidad (≥ 10 evaluados). |
| Justificar presupuesto | Comparativo base vs. simulado, con personas "rescatadas" por cada palanca de inversión. |
| Planear adquisiciones | Requerimientos y cantidades a comprar de cinco tipos de ayudas técnicas, por municipio. |
| Desplegar brigadas | Padrón nominal ordenado de mayor a menor probabilidad de déficit. |

> **Alcance.** M.A.P.A. **apoya** la toma de decisiones; no la sustituye. Las proyecciones del simulador son estimaciones basadas en supuestos explícitos (ver sección 3) y deben interpretarse junto con el criterio técnico de las áreas responsables.

---

## 2. Insignias Tecnológicas

Las insignias de la parte superior resumen el stack: **Python**, **Streamlit**, **HTML5**, **CSS3**, **Pandas**, **NumPy**, **Plotly**, **Folium** y **GitHub**.

---

## 3. Características Principales

### Simulador de impacto presupuestal (what-if)
La funcionalidad de mayor impacto de la herramienta. Desde el panel lateral, el usuario define el porcentaje de cobertura (0 a 100 %) de tres palancas de inversión:

| Palanca | Barrera que atiende | Peso en el índice |
|---|---|---|
| **P1.** Transporte adaptado y unidades móviles | Barrera de transporte | 0.40 |
| **P2.** Ayudas técnicas / ortopedia | Déficit de ayuda técnica | 0.35 |
| **P3.** Apoyo al cuidador y accesibilidad | Déficit de apoyo y entorno | 0.25 |

- **Índice de Urgencia** = `0.40 × tasa de barrera de transporte + 0.35 × tasa de déficit técnico + 0.25 × tasa de déficit de apoyo y entorno`.
- Cada palanca reduce proporcionalmente su tasa; la **tasa de exclusión laboral y educativa** se reduce con un factor de mitigación que usa los mismos pesos.
- Los indicadores (KPI) se recalculan al instante y muestran **base vs. simulado**, con el número de personas "rescatadas" y "reinsertadas".
- *Transparencia metodológica:* es un modelo lineal y explícito, pensado para **comparar escenarios**, no para predecir resultados exactos.

### Filtro territorial interactivo
- Selector de **Todo Guanajuato** o de un municipio específico: KPI, mapa, cuadro de compras y padrón se actualizan en conjunto.
- Casilla para limitar el ranking a municipios con **al menos 10 evaluados** ("Focos Rojos Oficiales"), evitando conclusiones sobre muestras pequeñas.

### Mapa GPS con perfiles de atención (clusters K-Means)
- Cada persona evaluada se ubica en un mapa interactivo (OpenStreetMap) y se colorea según su perfil de riesgo:
  - 🔴 **Cluster 0:** alta severidad clínica (ortopedia y apoyo al cuidador).
  - 🟠 **Cluster 2:** entorno rural crítico (unidades móviles).
  - 🟢 **Cluster 1:** urbano moderado (inclusión laboral y becas).
- Información emergente por punto: municipio, localidad, diagnóstico, porcentaje de discapacidad y probabilidad de déficit estimada por IA.
- Centrado y zoom automáticos según el territorio seleccionado.

### Análisis de barreras de accesibilidad y ranking de focos rojos
- Medición de tres barreras: **transporte**, **ayudas técnicas** y **apoyo y entorno**.
- **Top 10 de municipios** por Índice de Urgencia, con gráfica que superpone el índice base (sin intervención) y el posterior a la inversión simulada. Exportable a PNG.

### Cuadro de adquisiciones para licitación
- Requerimientos y unidades a comprar, según la cobertura elegida, de **sillas de ruedas, bastones, andadores, prótesis/órtesis y audífonos**.
- Desglose por municipio con índice de urgencia, tasa de exclusión y faltantes por tipo de ayuda.

### Padrón nominal priorizado (Random Forest)
- Lista de personas ordenada por **probabilidad de rezago crítico**, con municipio, localidad, ámbito, edad, sexo, diagnóstico, porcentaje de discapacidad, perfil de cluster y barreras identificadas, lista para planear el despliegue de brigadas.

### Experiencia y robustez
- Identidad institucional (paleta azul, encabezado y logotipo de la Secretaría de Derechos Humanos).
- Carga de datos en caché para una navegación fluida.
- Manejo de errores amigable si faltan los archivos CSV o el logotipo.

---

## 4. Stack Tecnológico e Instalación Local

### Stack tecnológico

| Tecnología | Uso en el proyecto |
|---|---|
| **Python** | Lenguaje principal y motor de cálculo del simulador. |
| **Streamlit** | Interfaz web: panel de control, pestañas, métricas y tablas. |
| **Pandas** y **NumPy** | Carga, filtrado y cálculo de indicadores. |
| **Plotly** | Gráfica comparativa del ranking de municipios. |
| **Folium** + **streamlit-folium** | Mapa interactivo con marcadores por cluster. |
| **HTML y CSS** | Encabezado, leyendas y estilo institucional incrustados con `st.markdown`. |
| **Pillow** y **qrcode** | Incluidas en las dependencias del proyecto (`requirements.txt`). |
| **GitHub** | Control de versiones y publicación del código. |

> Los clusters K-Means y las probabilidades del modelo Random Forest están **precalculados** en los archivos CSV (`PERFIL_CLUSTER`, `PROBABILIDAD_DEFICIT_IA`). La aplicación los consume y visualiza; no entrena modelos al ejecutarse, lo que la mantiene rápida y ligera.

### Instalación paso a paso

**Requisitos previos:** [Python 3.9+](https://www.python.org/downloads/) y [Git](https://git-scm.com/downloads).

**1. Clonar el repositorio**
```bash
git clone https://github.com/sierraivan14/mapa-guanajuato-dataton.git
cd mapa-guanajuato-dataton
```

**2. Crear y activar un entorno virtual (recomendado)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instalar las dependencias**

Todas las librerías necesarias están listas en `requirements.txt`:
```bash
pip install -r requirements.txt
```

**4. Ejecutar la aplicación**
```bash
streamlit run app.py
```

**5. Abrir en el navegador**

Streamlit abrirá la aplicación automáticamente; si no, visite [http://localhost:8501](http://localhost:8501).

> Ejecute los comandos desde la carpeta raíz del proyecto: `app.py` lee los CSV y el logotipo mediante rutas relativas a esa ubicación.

### Estructura del repositorio

```text
mapa-guanajuato-dataton/
├── .streamlit/                       # Configuración de Streamlit
├── app.py                            # Aplicación: interfaz, simulador, mapa y gráficas
├── requirements.txt                  # Dependencias de Python
├── MAPA_PACIENTES_ENRIQUECIDO.csv    # Padrón de pacientes: ubicación, diagnóstico, cluster y probabilidad IA
├── MAPA_MUNICIPIOS_RANKING.csv       # Indicadores agregados por municipio
└── logo_derechos_humanos.png         # Logotipo institucional
```

<!-- VERIFICAR antes de publicar: que los datos de pacientes estén anonimizados y cumplan la normativa de protección de datos personales aplicable. -->

---

## 5. Equipo Desarrollador

Proyecto creado en el **Primer Datathon Guanajuato de Discapacidad**.

1. **Cristhian Ivan Sierra Contreras**
2. **Cristobal Enrique Paz Dominguez**
3. **Juan Pablo Arredondo Escobar**
4. **Lezzra Jahir Rocha Sainez**

---

<div align="center">

**Gobierno del Estado de Guanajuato** · Secretaría de Derechos Humanos · M.A.P.A. 2024–2030

</div>
