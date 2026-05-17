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

# Inicialización del estado de la sesión para el almacenamiento del reporte de IA
if "reporte_institucional" not in st.session_state:
    st.session_state["reporte_institucional"] = None

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

    # PESTAÑA 2: ANÁLISIS DE VOLATILIDAD AVANZADO (REESTRUCTURADO)
    with tab_analisis:
        st.subheader("Análisis Comparativo y Distribución de Mercado")
        st.markdown("""
        Herramientas analíticas avanzadas para la evaluación de anomalías y distribución de capital en el portafolio global.
        """)
        
        # Segmentación del gráfico de barras mediante un selector de control
        st.write("---")
        st.markdown("### Rendimiento Extremo del Mercado")
        
       # Corrección de la escala de color para compatibilidad nativa con Plotly
        if "Mayor Crecimiento" in criterio_busqueda:
            df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=False).head(15)
            color_escala = 'greens' # Escala compatible de tonalidades verdes
        else:
            df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=True).head(15)
            color_escala = 'Reds_r' # Escala compatible de tonalidades rojas invertidas
        
        
        # Procesamiento y ordenamiento de matrices con Pandas
        if "Mayor Crecimiento" in criterio_busqueda:
            df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=False).head(15)
            color_escala = 'Summer' # Tonalidades verdes
        else:
            df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=True).head(15)
            color_escala = 'Reds_r' # Tonalidades rojas
            
        # Gráfico de barras optimizado y legible (Máximo 15 elementos)
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
        
        # --- AMPLIACIÓN BI: MAPA DE CALOR DE CAPITALIZACIÓN GLOBAL ---
        st.write("---")
        st.subheader("Mapa de Calor del Mercado (Treemap Total)")
        st.markdown("""
        La siguiente visualización distribuye los 250 activos de la API. El tamaño del bloque representa 
        la dominancia por Capitalización de Mercado, mientras que el color mapea la variación porcentual de las últimas 24 horas.
        """)
        
        try:
            # Construcción del Treemap institucional para grandes volúmenes de datos
            fig_treemap = px.treemap(
                df,
                path=['name'],  # Define la jerarquía del bloque
                values='market_cap',  # Define el volumen/tamaño del cuadro
                color='price_change_percentage_24h',  # Define la regla de coloración
                color_continuous_scale='RdYlGn',  # Escala semafórica estándar (Rojo - Amarillo - Verde)
                color_continuous_midpoint=0,  # El punto neutral (0%) se asigna al color central
                template="plotly_dark"
            )
            
            fig_treemap.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
            
        except Exception as e:
            st.error(f"No se pudo inicializar la matriz del mapa de calor: {e}")

        # --- AMPLIACIÓN DE LA API: ANÁLISIS DE SERIES DE TIEMPO ---
        st.write("---")
        st.subheader("Análisis de Tendencia Histórica e Inteligencia de Negocios")
        st.markdown("""
        Seleccione un activo digital para proyectar la serie de tiempo correspondiente a los últimos 30 días. 
        Este módulo mitiga el sesgo de la volatilidad diaria mediante la visualización de tendencias macro.
        """)

        diccionario_criptos = dict(zip(df['name'], df['id']))
        nombre_seleccionado = st.selectbox("Activo objeto de estudio histórico:", list(diccionario_criptos.keys()))
        id_seleccionado = diccionario_criptos[nombre_seleccionado]

        with st.spinner("Extrayendo series temporales desde el servidor..."):
            from coingecko_api import obtener_historico_activo
            df_historico = obtener_historico_activo(coin_id=id_seleccionado, days=30)

        if df_historico is not None and not df_historico.empty:
            fig_linea = px.line(
                df_historico,
                x='Fecha',
                y='Precio',
                labels={'Fecha': 'Línea Temporal', 'Precio': 'Valor de Cierre (USD)'},
                title=f"Evolución de Cotización de {nombre_seleccionado} - Últimos 30 días",
                template="plotly_dark"
            )
            
            fig_linea.update_traces(line_color='#00FFCC', line_width=2)
            fig_linea.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode="x unified"
            )
            st.plotly_chart(fig_linea, use_container_width=True)
        else:
            st.error("No se pudo computar la serie temporal para el activo seleccionado.")

   # PESTAÑA 3: PROCESAMIENTO GENERATIVO DE AUDITORÍA (OPTIMIZADO)
    with tab_ia:
        st.subheader("Módulo de Inteligencia Artificial para Soporte Estrecho")
        st.markdown("Generación automatizada de reportes macroeconómicos computados a partir del estado actual de la API.")
        
        if st.button("Generar Informe de Financiero", use_container_width=True):
            from datetime import datetime
            
            # 1. Anclaje temporal dinámico
            fecha_servidor = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            
            # 2. Enriquecimiento estadístico del contexto (Mitigación de sesgo del modelo)
            activo_top_ganador = df.loc[df['price_change_percentage_24h'].idxmax()]
            activo_top_perdedor = df.loc[df['price_change_percentage_24h'].idxmin()]
            promedio_variacion_mercado = df['price_change_percentage_24h'].mean()
            
            # Consolidación estructurada de la matriz de datos
            contexto = "".join([f"- {r['name']} ({r['symbol'].upper()}): ${r['current_price']:,} (Var 24h: {r['price_change_percentage_24h']:.2f}%)\n" for i, r in df.iterrows()])
            
            # Construcción del Prompt de Datos con ingeniería de variables
            prompt_enriquecido = f"""
            Métricas de Control Temporal e Histórico:
            - Fecha y Hora de la Consulta: {fecha_servidor} (Considerar este marco como el estado actual del mercado de criptomonedas).
            - Máximo Rendimiento Diario Detectado: {activo_top_ganador['name']} ({activo_top_ganador['price_change_percentage_24h']:.2f}%)
            - Máxima Contracción Diaria Detectada: {activo_top_perdedor['name']} ({activo_top_perdedor['price_change_percentage_24h']:.2f}%)
            - Variación Promedio del Portafolio: {promedio_variacion_mercado:.2f}%
            
            Matriz Completa de Activos en Tiempo Real:
            {contexto}
            
            Instrucción Operativa:
            Desarrolle la auditoría basándose estrictamente en las métricas de control y la matriz provista. Estructure el informe con subtítulos claros y un desglose analítico profundo.
            """
            
            with st.spinner("Procesando modelos predictivos y estructurando reporte corporativo..."):
                try:
                    # Separación de responsabilidades: Configuración del Rol del Sistema
                    from google.genai import types
                    configuracion_ia = types.GenerateContentConfig(
                        system_instruction="Actúa como un Analista Financiero Senior y menciona que eres un modelo de inteligencia artificaail desarrollado por estudiantes de Informática y Gestión de la Universidad Diego Portales.Tu objetivo es emitir informes ejecutivos de carácter estrictamente formal, técnico y corporativo. Debes basar tu análisis rigurosamente en los datos temporales y estadísticos provistos en el prompt, eludiendo generalidades o especulaciones sin sustento matemático."
                    )
                    
                    # Llamada optimizada al modelo
                    response = ai_client.models.generate_content(
                        model='gemini-2.5-flash', 
                        contents=prompt_enriquecido,
                        config=configuracion_ia
                    )
                    
                    # Almacenamiento en el estado de la sesión para persistencia en UI
                    st.session_state["reporte_institucional"] = response.text
                    st.success("Informe de Auditoría Ejecutado Correctamente")
                    
                except Exception as e:
                    st.error(f"Error en la comunicación con el modelo generativo: {e}")
        
        # Despliegue condicional del reporte persistido
        if st.session_state["reporte_institucional"]:
            st.write("---")
            st.markdown("### Reporte Ejecutivo de Gestión Institucional")
            st.info(st.session_state["reporte_institucional"])
else:
    st.error("Error crítico: No fue posible establecer comunicación con los endpoints de CoinGecko.")
