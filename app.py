import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from google import genai

# Carga global de variables de entorno
load_dotenv()

# Inicialización absoluta del cliente de IA para evitar errores de definición (NameError)
api_key_gemini = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key_gemini)

# Reemplazar la importación previa asi agregar nueva caracteristica del backend
from coingecko_api import obtener_top_criptos, obtener_historico_activo

# Configuración de la interfaz con enfoque analítico
st.set_page_config(
    page_title="Sistema de Análisis de Activos Digitales - UDP",
    layout="wide"
)

# --- PANEL LATERAL: IDENTIFICACIÓN INSTITUCIONAL ---
with st.sidebar:
    # Carga del logo local para garantizar disponibilidad permanente
    try:
        st.image("logo_udp.png", use_container_width=True)
    except Exception:
        # Alternativa de texto estructurado si el archivo local aún no se ha subido
        st.markdown("### Universidad Diego Portales")
    
    st.markdown("### Escuela de Informática y Gestión")
    st.markdown("""
    Facultad de Ingeniería y Ciencias  
    Ingenieria Informatica y Gestion
    """)
    
    st.write("---")
    if st.button("Sincronizar Datos de Mercado", use_container_width=True):
        st.rerun()

# --- CABECERA PRINCIPAL ---
st.title("Sistema de Monitoreo y Análisis de Activos Digitales")
st.markdown("""
Esta plataforma de integración tecnológica procesa datos financieros en tiempo real mediante la interfaz de CoinGecko, 
acoplando modelos de lenguaje de última generación para la auditoría de carteras y el soporte en la toma de decisiones.
""")

st.write("---")

# Obtención de datos desde el módulo analítico backend
with st.spinner("Estableciendo conexión con los servidores de datos..."):
    df = obtener_top_criptos()

if df is not None and not df.empty:
    
    # --- INDICADORES FINANCIEROS CLAVE ---
    col1, col2, col3 = st.columns(3)
    
    btc_data = df[df['symbol'].str.lower() == 'btc']
    eth_data = df[df['symbol'].str.lower() == 'eth']
    
    with col1:
        val_btc = btc_data['current_price'].values[0] if not btc_data.empty else 0
        st.metric(label="Valor de Mercado Bitcoin (USD)", value=f"${val_btc:,.2f}")
    with col2:
        val_eth = eth_data['current_price'].values[0] if not eth_data.empty else 0
        st.metric(label="Valor de Mercado Ethereum (USD)", value=f"${val_eth:,.2f}")
    with col3:
        st.metric(label="Activos Digitales bajo Análisis", value=len(df))

    st.write("---")

    # --- PESTAÑAS DE CONTROL Y CONTROL DE FLUJO ---
    tab_datos, tab_analisis, tab_ia = st.tabs([
        "Visualización de Datos", 
        "Análisis de Volatilidad", 
        "Consultoría Predictiva IA"
    ])
    # PESTAÑA 1: MATRIZ DE DATOS
    with tab_datos:
        st.subheader("Reporte de Capitalización de Mercado")
        df_final = df.copy()
        
        # Corrección: Lista de 7 elementos para incorporar la columna 'ID' proveniente del backend
        df_final.columns = ['ID', 'Activo', 'Ticker', 'Precio Actual', 'Market Cap', 'Variación 24h', 'Imagen']
        
        # Se excluyen las columnas 'ID' e 'Imagen' de la visualización para mantener el estándar institucional
        st.dataframe(df_final.drop(columns=['ID', 'Imagen']), use_container_width=True, height=450)

    # PESTAÑA 2: GRÁFICO CON PALETA DE TERMINAL DE TRADING
    with tab_analisis:
        st.subheader("Análisis Comparativo de Variación Porcentual")
        df_sorted = df.sort_values(by='price_change_percentage_24h', ascending=False)
        
        # Implementación de plantilla oscura para simular un entorno de criptoactivos
        fig = px.bar(
            df_sorted, 
            x='price_change_percentage_24h',
            y='name',
            orientation='h',
            labels={'price_change_percentage_24h': 'Variación diaria (%)', 'name': 'Activo evaluado'},
            color='price_change_percentage_24h',
            color_continuous_scale='RdYlGn',  # Verde para rendimientos positivos, rojo para negativos
            template="plotly_dark"            # Estética de terminal financiera
        )
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            coloraxis_showscale=False,
            paper_bgcolor='rgba(0,0,0,0)',    # Transparencia integrada para acoplar al contenedor
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        # --- AMPLIACIÓN DE LA API: ANÁLISIS DE SERIES DE TIEMPO ---
        st.write("---")
        st.subheader("Análisis de Tendencia Histórica e Inteligencia de Negocios")
        st.markdown("""
        Seleccione un activo digital para proyectar la serie de tiempo correspondiente a los últimos 30 días. 
        Este módulo mitiga el sesgo de la volatilidad diaria mediante la visualización de tendencias macro.
        """)

        # Generación de selectores mapeando el ID técnico de la API
        diccionario_criptos = dict(zip(df['name'], df['id']))
        nombre_seleccionado = st.selectbox("Activo objeto de estudio historico:", list(diccionario_criptos.keys()))
        id_seleccionado = diccionario_criptos[nombre_seleccionado]

        # Consulta al backend enriquecido
        with st.spinner("Extrayendo series temporales desde el servidor..."):
            df_historico = obtener_historico_activo(coin_id=id_seleccionado, days=30)

        if df_historico is not None and not df_historico.empty:
            # Construcción de gráfico de líneas con la paleta financiera oscura
            fig_linea = px.line(
                df_historico,
                x='Fecha',
                y='Precio',
                labels={'Fecha': 'Línea Temporal', 'Precio': 'Valor de Cierre (USD)'},
                title=f"Evolución de Cotización de {nombre_seleccionado} - Últimos 30 días",
                template="plotly_dark"
            )
            
            # Optimización estética del gráfico lineal corporativo
            fig_linea.update_traces(line_color='#00FFCC', line_width=2)
            fig_linea.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_linea, use_container_width=True)
        else:
            st.error("No se pudo computar la serie temporal para el activo seleccionado.")

    # PESTAÑA 3: PROCESAMIENTO GENERATIVO DE AUDITORÍA
    with tab_ia:
        st.subheader("Módulo de Inteligencia Artificial para Soporte Estrecho")
        st.markdown("Generación automatizada de reportes macroeconómicos computados a partir del estado actual de la API.")
        
        if st.button("Generar Informe de Auditoría Financiera", use_container_width=True):
            # Consolidación estructurada del string de datos para el modelo
            contexto = "".join([f"- {r['name']}: ${r['current_price']:,} (Var: {r['price_change_percentage_24h']:.2f}%)\n" for i, r in df.iterrows()])
            
            prompt_academico = f"""
            Como analista experto en gestión financiera e informática de la Universidad Diego Portales, analice la siguiente estructura de datos:
            {contexto}
            
            Entregue un reporte técnico que incluya de forma estricta:
            1. Diagnóstico macro del estado de liquidez y comportamiento de los activos.
            2. Evaluación cuantitativa del riesgo asociada a la volatilidad detectada.
            3. Plan estratégico de diversificación orientado a un perfil de gestión institucional.
            
            Redacte el documento bajo un estándar estrictamente formal, técnico y corporativo, omitiendo cualquier elemento informal.
            """
            
            with st.spinner("Procesando modelos predictivos y estructurando reporte..."):
                try:
                    response = ai_client.models.generate_content(
                        model='gemini-2.5-flash', 
                        contents=prompt_academico
                    )
                    st.success("Informe de Auditoría Ejecutado Correctamente")
                    st.markdown("### Reporte Ejecutivo de Gestión Institucional")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error(f"Error en la comunicación con el modelo generativo: {e}")
else:
    st.error("Error crítico: No fue posible establecer comunicación con los endpoints de CoinGecko.")
