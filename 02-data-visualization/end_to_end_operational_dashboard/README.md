# 🚀 End-to-End Operations & Business Intelligence Suite

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75.svg)](https://plotly.com/)

Un proyecto integrador de **Business Intelligence y Analytics Operativo** diseñado para simular y optimizar la cadena de valor completa en un entorno empresarial multi-sector / multi-tribu (ej. Telecomunicaciones, SaaS, Servicios Financieros).

---

## 📌 Contexto del Proyecto & Problema de Negocio

En operaciones complejas de alto volumen transaccional, los equipos suelen trabajar en silos: el área de captación mide **Altas**, operaciones mide **Tiempos de Activación y SLA**, y finanzas evalúa **Facturación y Cobranza**. La falta de una **visión transversal interrelacionada** genera cuellos de botella invisibles donde un retraso operacional se traduce directamente en fuga de ingresos (*revenue leakage*) y cancelaciones de clientes (*churn*).

Este proyecto resuelve este desafío mediante:
1. **Modelado del Embudo Transversal:** Integración de KPIs clave (Altas, Tiempos de Activación, SLAs, Suspensiones, Bajas, Facturación y Aportes).
2. **Tablero Interactivo End-to-End:** Visualización unificada que conecta la operación diaria con el impacto financiero.
3. **Identificación de Relaciones Causa-Efecto:** Demostración cuantitativa de cómo las demoras en la activación incrementan la tasa de suspensión y reducen la efectividad de cobro.

---

## 🏗️ Arquitectura del Proyecto

```text
end_to_end_operational_dashboard/
├── app.py                   # Aplicación principal del Dashboard interactivo (Streamlit + Plotly)
├── data_generator.py        # Generador de datos sintéticos transaccionales con lógica de negocio
├── kpi_engine.py            # Motor analítico para cálculo de métricas de conversión y finanzas
├── requirements.txt         # Lista de librerías y dependencias
└── data/
    └── operational_data.csv # Base transaccional generada
```

---

## 📊 Matriz de KPIs e Interrelación de la Cadena de Valor

| Etapa de la Cadena | KPI Métrico | Descripción / Fórmula | Impacto Transversal |
| :--- | :--- | :--- | :--- |
| **1. Captación** | **Altas** | Total de clientes incorporados | Volumen base para la proyección de facturación. |
| **2. Operación** | **Tiempo de Activación** | Días promedio para habilitar el servicio | Un aumento en días deteriora el SLA y dispara las suspensiones. |
| **3. Servicio** | **SLA Cumplimiento (%)** | % de órdenes completadas dentro del tiempo objetivo | Mide el nivel de servicio y la experiencia del cliente interno/externo. |
| **4. Control** | **Suspensiones** | Unidades temporalmente pausadas por fallas | Principal alerta temprana del Churn futuro. |
| **5. Retención** | **Bajas (Churn)** | Cancelaciones definitivas del servicio | Pérdida directa de la base recurrente. |
| **6. Finanzas** | **Facturación vs Aportes** | Conciliación de monto facturado vs. cobrado | Mide el gap de cobranza derivado de fricciones operativas. |

---

## 💻 Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/data_visualization.git
cd data_visualization/end_to_end_operational_dashboard
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generar dataset y ejecutar el Dashboard
```bash
python data_generator.py
streamlit run app.py
```

El tablero se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## 🎯 Hallazgos Clave Simulados

1. **Sensibilidad del Tiempo de Activación:** Por cada día adicional que se demora la activación del servicio en la *Tribu B2B*, la probabilidad de suspensión prematura se incrementa en un **15%**.
2. **Gap de Cobranza Operativo:** Sectores con un cumplimiento de SLA inferior al **85%** registraron un desvío promedio del **12%** entre la Facturación emitida y los Aportes efectivamente cobrados.

---

## 👨‍💻 Perfil Técnico Demostrado

* **Librerías Analytics & Vis:** Streamlit, Plotly Express, Plotly Graph Objects, Pandas, NumPy.
* **Competencias de Negocio:** Visión End-to-End, Modelado de KPIs, Análisis Causa-Raíz, Conciliación Financiera y Segmentación por Tribus.
