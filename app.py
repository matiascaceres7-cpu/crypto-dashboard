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
# --- OBTENCIÓN DE DATOS DE PRENSA (PREVIO AL RENDERIZADO) ---
with st.spinner("Sincronizando flujo de prensa internacional..."):
        lista_noticias = obtener_noticias_mercado()

    # --- DISEÑO DE TERMINAL: DISTRIBUCIÓN DE COLUMNAS GLOBALES ---
    # Se divide el espacio: 70% para analítica (pestañas) y 30% para el panel fijo de noticias
    col_analitica, col_prensa = st.columns([0.7, 0.3])

    # --- PANEL IZQUIERDO: CONTENEDOR DE MÓDULOS DE ESTUDIO ---
    with col_analitica:
        tab_datos, tab_analisis, tab_ia = st.tabs([
            "Visualización de Datos", 
            "Análisis de Volatilidad", 
            "Consultoría Predictiva IA"
        ])

        # DESPLIEGUE: PESTAÑA 1 (MATRIZ DE DATOS)
        with tab_datos:
            st.subheader("Reporte de Capitalización de Mercado")
            df_final = df.copy()
            df_final.columns = ['ID', 'Activo', 'Ticker', 'Precio Actual', 'Market Cap', 'Variación 24h', 'Imagen']
            st.dataframe(df_final.drop(columns=['ID', 'Imagen']), use_container_width=True, height=450)

        # DESPLIEGUE: PESTAÑA 2 (VOLATILIDAD Y SERIES DE TIEMPO)
        with tab_analisis:
            st.subheader("Análisis Comparativo y Distribución de Mercado")
            st.markdown("Herramientas analíticas avanzadas para la evaluación de anomalías.")
            
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
            
            # Mapa de Calor (Treemap)
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
                st.error(f"Error en matriz de mapa de calor: {e}")

            # Análisis de Serie de Tiempo (30 días)
            st.write("---")
            st.subheader("Análisis de Tendencia Histórica")
            diccionario_criptos = dict(zip(df['name'], df['id']))
            nombre_seleccionado = st.selectbox("Activo objeto de estudio histórico:", list(diccionario_criptos.keys()))
            id_seleccionado = diccionario_criptos[nombre_seleccionado]

            with st.spinner("Extrayendo series temporales..."):
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
                fig_linea.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
                st.plotly_chart(fig_linea, use_container_width=True)

        # DESPLIEGUE: PESTAÑA 3 (AUDITORÍA DE INTELIGENCIA ARTIFICIAL)
        with tab_ia:
            st.subheader("Módulo de Inteligencia Artificial para Soporte Estrecho")
            
            if st.button("Generar Informe de Auditoría Financiera", use_container_width=True):
                from datetime import datetime
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
                
                with st.spinner("Procesando reporte corporativo..."):
                    try:
                        from google.genai import types
                        configuracion_ia = types.GenerateContentConfig(
                            system_instruction="Actúa como un Analista Financiero virtual (IA) creado por estudiantes de la Universidad Diego Portales. Emite informes ejecutivos de carácter formal, técnico y corporativo basados estrictamente en los datos estadísticos provistos."
                        )
                        response = ai_client.models.generate_content(
                            model='gemini-2.5-flash', 
                            contents=prompt_enriquecido,
                            config=configuracion_ia
                        )
                        st.session_state["reporte_institucional"] = response.text
                        st.success("Informe de Auditoría Ejecutado Correctamente")
                    except Exception as e:
                        st.error(f"Error con el modelo generativo: {e}")
            
            if st.session_state["reporte_institucional"]:
                st.write("---")
                st.markdown("### Reporte Ejecutivo de Gestión Institucional")
                st.info(st.session_state["reporte_institucional"])

    # --- PANEL DERECHO: COMPONENTE FIJO DE PRENSA (SIEMPRE VISIBLE) ---
    with col_prensa:
        st.subheader("Prensa y Tendencias Globales")
        st.markdown("""
        Variables cualitativas en tiempo real para contextualizar anomalías de volatilidad y mitigar riesgos operacionales.
        """)
        st.write("---")
        
        if lista_noticias:
            # Despliegue optimizado de los 5 artículos más recientes
            for noticia in lista_noticias[:5]:
                titulo = noticia.get('title', 'Publicación sin título')
                fuente = noticia.get('source_info', {}).get('name', 'Agencia Externa')
                url_enlace = noticia.get('url', '#')
                
                with st.container():
                    # Formato hipervínculo en negrita para el título corporativo
                    st.markdown(f"**[{titulo}]({url_enlace})**")
                    st.caption(f"Fuente: {fuente} | Idioma: Inglés")
                    st.write("---")
        else:
            st.error("Servicio de distribución de prensa no disponible en este momento.")
else:
    st.error("Error crítico: No fue posible establecer comunicación con los endpoints de CoinGecko.")

    
