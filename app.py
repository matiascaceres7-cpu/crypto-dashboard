import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from google import genai

# Carga de variables de entorno
load_dotenv()

# Configuración de credenciales de API
api_key_gemini = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key_gemini)

from coingecko_api import obtener_top_criptos

# Configuración de la interfaz
st.set_page_config(
    page_title="Sistema de Análisis de Activos Digitales - UDP",
    layout="wide"
)

# --- PANEL LATERAL: IDENTIFICACIÓN ACADÉMICA ---
with st.sidebar:
    # Logo oficial Universidad Diego Portales
    st.image("https://i.ibb.co/3pYf9yB/logo-udp.png", width=200)
    
    st.title("Información del Proyecto")
    st.markdown("""
    **Escuela de Informática y Gestión**  
    Facultad de Ingeniería y Ciencias  
    Universidad Diego Portales
    """)
    
    st.write("---")
    st.write("**Asignatura:** Proyecto de Integración Tecnológica")
    st.write("**Integrantes:** [Tus Nombres]")
    st.write("**Docente:** [Nombre del Profesor]")
    
    st.write("---")
    if st.button("Sincronizar Datos de Mercado", use_container_width=True):
        st.rerun()

# --- CABECERA PRINCIPAL ---
st.title("Sistema de Monitoreo y Análisis de Activos Digitales")
st.markdown("""
Esta plataforma integra datos financieros en tiempo real mediante la API de CoinGecko y modelos de procesamiento 
de lenguaje natural para el análisis de tendencias y apoyo a la gestión de inversiones.
""")

st.write("---")

# Obtención de datos desde el módulo backend
with st.spinner("Estableciendo conexión con los servidores de datos..."):
    df = obtener_top_criptos()

if df is not None and not df.empty:
    
    # --- MÉTRICAS ESTRATÉGICAS ---
    col1, col2, col3 = st.columns(3)
    
    # Extracción de valores específicos para indicadores clave
    btc_data = df[df['symbol'].str.lower() == 'btc']
    eth_data = df[df['symbol'].str.lower() == 'eth']
    
    with col1:
        val = btc_data['current_price'].values[0] if not btc_data.empty else 0
        st.metric(label="Valor Mercado Bitcoin (USD)", value=f"${val:,.2f}")
    with col2:
        val = eth_data['current_price'].values[0] if not eth_data.empty else 0
        st.metric(label="Valor Mercado Ethereum (USD)", value=f"${val:,.2f}")
    with col3:
        st.metric(label="Activos en Observación", value=len(df))

    st.write("---")

    # --- ESTRUCTURACIÓN DE PESTAÑAS TÉCNICAS ---
    tab_datos, tab_analisis, tab_ia = st.tabs([
        "Visualización de Datos", 
        "Análisis de Volatilidad", 
        "Consultoría Predictiva IA"
    ])

    # PESTAÑA 1: VISUALIZACIÓN DE DATOS (TABLA)
    with tab_datos:
        st.subheader("Reporte de Capitalización de Mercado")
        df_final = df.copy()
        df_final.columns = ['Activo', 'Ticker', 'Precio Actual', 'Market Cap', 'Variación 24h', 'Imagen']
        # Se excluye la columna de imagen para mantener la estética académica
        st.dataframe(df_final.drop(columns=['Imagen']), use_container_width=True, height=450)

    # PESTAÑA 2: ANÁLISIS DE VOLATILIDAD (GRÁFICO)
    with tab_analisis:
        st.subheader("Análisis Comparativo de Variación Porcentual")
        df_sorted = df.sort_values(by='price_change_percentage_24h', ascending=False)
        
        fig = px.bar(
            df_sorted, 
            x='price_change_percentage_24h',
            y='name',
            orientation='h',
            labels={'price_change_percentage_24h': 'Variación (%)', 'name': 'Activo Digital'},
            color='price_change_percentage_24h',
            color_continuous_scale='RdYlGn',
            template="simple_white"
        )
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # PESTAÑA 3: CONSULTORÍA PREDICTIVA (IA)
    with tab_ia:
        st.subheader("Módulo de Inteligencia Artificial para Apoyo a la Decisión")
        st.write("Generación de informes ejecutivos basados en el sentimiento del mercado y variaciones estadísticas.")
        
        if st.button("Generar Informe de Auditoría Financiera", use_container_width=True):
            # Construcción de contexto para la IA
            contexto = "".join([f"- {r['name']}: ${r['current_price']:,} (Var: {r['price_change_percentage_24h']:.2f}%)\n" for i, r in df.iterrows()])
            
            prompt_academico = f"""
            Como analista experto en gestión financiera e informática, analice los siguientes datos de mercado:
            {contexto}
            
            Entregue un reporte técnico que incluya:
            1. Diagnóstico del estado actual de la liquidez y sentimiento de mercado.
            2. Evaluación de riesgo basada en la volatilidad observada.
            3. Propuesta de diversificación para un perfil de gestión institucional.
            
            Redacte el informe en un lenguaje formal, técnico y estructurado.
            """
            
            with st.spinner("Procesando modelos de lenguaje y análisis de datos..."):
                try:
                    response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt_academico)
                    st.success("Informe de Auditoría Generado")
                    
                    st.markdown("### Reporte Ejecutivo de Gestión")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error(f"Error en la comunicación con el modelo generativo: {e}")
else:
    st.error("Error crítico: No fue posible establecer la conexión con la API de CoinGecko.")
