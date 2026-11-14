# BioShield Analytics — Ciberseguridad UEBA y Validación Biomédica

Sistema integrado para la gestión de amenazas internas (Insider Threat) y evaluación de modelos fundacionales de IA médica desarrollado para **BioShield Health & Security**.

## Estructura del Repositorio
* `app.py`: Aplicación interactiva principal en Streamlit con 3 módulos visuales.
* `ueba_telemetry.csv`: Dataset simulado de telemetría de ciberseguridad (60 registros).
* `biomed_metrics.csv`: Dataset simulado de métricas clínicas y proteómicas (60 registros).
* `requirements.txt`: Dependencias de Python necesarias para la ejecución.

## Instrucciones de Ejecución en VS Code
1. Clona o abre este repositorio en Visual Studio Code.
2. Crea y activa un entorno virtual de Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicación de Streamlit:
   ```bash
   streamlit run app.py
   ```
