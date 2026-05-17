import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# Carga global de variables de entorno
load_dotenv()

# Inicialización absoluta del cliente de IA para evitar errores de definición
api_key_gemini = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key_gemini)

# CORRECCIÓN: Se añade 'obtener_noticias_mercado' a las funciones importadas del backend
from coingecko_api import obtener_top_criptos, obtener_historico_activo, obtener_noticias_mercado

# Configuración de la interfaz con enfoque analítico
st.set_page_config(
    page_title="Sistema de Análisis de Activos Digitales - UDP",
    layout="wide"
)

# Inicialización del estado de la sesión para el almacenamiento del reporte de IA
if "reporte_institucional" not in st.session_state:
    st.session_state["reporte_institucional"] = None

# --- PANEL LATERAL: IDENTIFICACIÓN INSTITUCIONAL ---
with st.sidebar:
    try:
        st.image("logo_udp.png", use_container_width=True)
    except Exception:
        st.markdown("### Universidad Diego Portales")
    
    st.markdown("### Escuela de Informática y Gestión")
    st.markdown("""
    Facultad de Ingeniería y Ciencias  
    Ingeniería Informática y Gestión
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

# --- FLUJO PRINCIPAL DE RENDERIZADO (CONTROL DE EXCEPCIONES EN RED) ---
with st.spinner("Estableciendo conexión con los servidores de datos..."):
    df = obtener_top_criptos()

if df is not None and not df.empty:
    
    # 1. INDICADORES FINANCIEROS CLAVE (KPIs SUPERIORES)
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

    # 2. SINCRONIZACIÓN ASÍNCRONA DE PRENSA (COMPONENTE CUALITATIVO)
    with st.spinner("Sincronizando flujo de prensa internacional..."):
        lista_noticias = obtener_noticias_mercado()

    # 3. DISTRIBUCIÓN PARALELA DE LA TERMINAL (Estilo Bloomberg: 70% Analítica, 30% Noticias)
    col_analitica, col_prensa = st.columns([0.7, 0.3])

    # --- PANEL IZQUIERDO: CONTENEDOR MULTI-MÓDULO ---
    with col_analitica:
        tab_datos, tab_analisis, tab_ia = st.tabs([
            "Visualización de Datos", 
            "Análisis de Volatilidad", 
            "Consultoría Predictiva IA"
        ])

        # PESTAÑA A: MATRIZ DE CAPITALIZACIÓN DE MERCADO
        with tab_datos:
            st.subheader("Reporte de Capitalización de Mercado")
            df_final = df.copy()
            df_final.columns = ['ID', 'Activo', 'Ticker', 'Precio Actual', 'Market Cap', 'Variación 24h', 'Imagen']
            st.dataframe(df_final.drop(columns=['ID', 'Imagen']), use_container_width=True, height=450)

        # PESTAÑA B: MODELADO GRÁFICO AVANZADO
        with tab_analisis:
            st.subheader("Análisis Comparativo y Distribución de Mercado")
            st.markdown("Evaluación de anomalías estadísticas y rendimientos extremos de los activos bajo observación.")
            
            criterio_busqueda = st.radio(
                "Seleccione el segmento de volatilidad a evaluar:",
                ["Top 15 Activos con Mayor Crecimiento", "Top 15 Activos con Mayor Contracción"],
                horizontal=True
            )
            
            if "Mayor Crecimiento" in criterio_busqueda:
                df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=False).head(15)
                color_escala = 'greens' 
            else:
                df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=True).head(15)
                color_escala = 'reds' 
                
            fig_barras = px.bar(
                df_filtrado, 
                x='price_change_percentage_24h',
                y='name',
                orientation='h',
                labels={'price_change_percentage_24h': 'Variación diaria (%)', 'name': 'Activo'},
                color='price_change_percentage_24h',
                color_continuous_scale=color_escala,
                template="plotly_dark"
            )
            fig_barras.update_layout(
                margin=dict(l=20, r=20, t=10, b=10),
                coloraxis_showscale=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_barras, use_container_width=True)
            
            # Sub-módulo: Mapa de Calor Global (Treemap)
            st.write("---")
            st.subheader("Mapa de Calor del Mercado (Treemap Total)")
            try:
                fig_treemap = px.treemap(
                    df,
                    path=['name'],
                    values='market_cap',
                    color='price_change_percentage_24h',
                    color_continuous_scale='RdYlGn',
                    color_continuous_midpoint=0,
                    template="plotly_dark"
                )
                fig_treemap.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_treemap, use_container_width=True)
            except Exception as e:
                st.error(f"Error estructural en la generación del mapa de calor: {e}")

            # Sub-módulo: Series de Tiempo Históricas (30 Días)
            st.write("---")
            st.subheader("Análisis de Tendencia Histórica")
            diccionario_criptos = dict(zip(df['name'], df['id']))
            nombre_seleccionado = st.selectbox("Activo objeto de estudio histórico:", list(diccionario_criptos.keys()))
            id_seleccionado = diccionario_criptos[nombre_seleccionado]

            with st.spinner("Descargando registros históricos del servidor..."):
                df_historico = obtener_historico_activo(coin_id=id_seleccionado, days=30)

            if df_historico is not None and not df_historico.empty:
                fig_linea = px.line(
                    df_historico,
                    x='Fecha',
                    y='Precio',
                    labels={'Fecha': 'Línea Temporal', 'Precio': 'Valor de Cierre (USD)'},
                    template="plotly_dark"
                )
                fig_linea.update_traces(line_color='#00FFCC', line_width=2)
                fig_linea.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    hovermode="x unified"
                )
                st.plotly_chart(fig_linea, use_container_width=True)

        # PESTAÑA C: INGENIERÍA DE PROMPTS E IA COGNITIVA
        with tab_ia:
            st.subheader("Módulo de Inteligencia Artificial para Soporte Estrecho")
            st.markdown("Computación y procesamiento lingüístico de variables cuantitativas para la emisión de reportes.")
            
            if st.button("Generar Informe de Auditoría Financiera", use_container_width=True):
                fecha_servidor = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                
                activo_top_ganador = df.loc[df['price_change_percentage_24h'].idxmax()]
                activo_top_perdedor = df.loc[df['price_change_percentage_24h'].idxmin()]
                promedio_variacion_mercado = df['price_change_percentage_24h'].mean()
                
                contexto = "".join([f"- {r['name']} ({r['symbol'].upper()}): ${r['current_price']:,} (Var 24h: {r['price_change_percentage_24h']:.2f}%)\n" for i, r in df.iterrows()])
                
                prompt_enriquecido = f"""
                Métricas de Control Temporal:
                - Fecha y Hora de la Consulta: {fecha_servidor}
                - Máximo Rendimiento Diario: {activo_top_ganador['name']} ({activo_top_ganador['price_change_percentage_24h']:.2f}%)
                - Máxima Contracción Diaria: {activo_top_perdedor['name']} ({activo_top_perdedor['price_change_percentage_24h']:.2f}%)
                - Variación Promedio del Portafolio: {promedio_variacion_mercado:.2f}%
                
                Matriz de Activos:
                {contexto}
                """
                
                with st.spinner("Procesando reporte corporativo en la nube de Google..."):
                    try:
                        from google.genai import types
                        configuracion_ia = types.GenerateContentConfig(
                            system_instruction="Actúa como un Analista Financiero Senior virtual, desarrollado para la Escuela de Informática y Gestión de la Universidad Diego Portales. Emite informes de auditoría ejecutiva bajo un carácter estrictamente formal, corporativo y técnico, basándote de forma exclusiva en la analítica de datos provista."
                        )
                        response = ai_client.models.generate_content(
                            model='gemini-2.5-flash', 
                            contents=prompt_enriquecido,
                            config=configuracion_ia
                        )
                        st.session_state["reporte_institucional"] = response.text
                        st.success("Informe de Auditoría Ejecutado Correctamente")
                    except Exception as e:
                        st.error(f"Error de comunicación en la API de Inteligencia Artificial: {e}")
            
            if st.session_state["reporte_institucional"]:
                st.write("---")
                st.markdown("### Reporte Ejecutivo de Gestión Institucional")
                st.info(st.session_state["reporte_institucional"])

    # --- PANEL DERECHO: CONTEXTO CUALITATIVO CONTINUO ---
    with col_prensa:
        st.subheader("Prensa y Tendencias Globales")
        st.markdown("""
        Variables cualitativas en tiempo real para contextualizar la volatilidad algorítmica y mitigar riesgos.
        """)
        st.write("---")
        
        if lista_noticias:
            for noticia in lista_noticias[:5]:
                titulo = noticia.get('title', 'Publicación sin título')
                fuente = noticia.get('source_info', {}).get('name', 'Agencia Externa')
                url_enlace = noticia.get('url', '#')
                
                with st.container():
                    st.markdown(f"**[{titulo}]({url_enlace})**")
                    st.caption(f"Fuente: {fuente} | Restricción: Idioma Inglés")
                    st.write("---")
        else:
            st.error("Servicio de distribución de prensa no disponible en este momento.")
else:
    st.error("Error crítico: No fue posible establecer comunicación estable con los endpoints de CoinGecko.")

    
