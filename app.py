import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
 
# Carga global de variables de entorno
load_dotenv()
 
# Inicialización del cliente de IA
api_key_gemini = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key_gemini)
 
# Llamada del backend
from coingecko_api import obtener_top_criptos, obtener_historico_activo, obtener_noticias_mercado
# --- OPTIMIZACIÓN DE CACHÉ ---
# Esto evita consultar a CoinGecko cada vez que envías un mensaje en el chat
@st.cache_data(ttl=300) # Guarda los datos por 300 segundos (5 minutos)
def get_top_criptos_cached():
    return obtener_top_criptos()

@st.cache_data(ttl=600) # Las noticias cambian menos, las guardamos 10 minutos
def get_noticias_cached():
    return obtener_noticias_mercado()
 
# ── FUNCIÓN CENTRALIZADA PARA LLAMADAS A GEMINI ───────────────────────────────
def llamar_gemini(prompt: str, system_instruction: str = None) -> str | None:
    """
    Wrapper unificado para todas las llamadas a la API de Gemini.
    Retorna el texto de la respuesta o None si ocurre un error.
    """
    try:
        from google.genai import types
        config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
        kwargs = {"model": "gemini-2.5-flash", "contents": prompt}
        if config:
            kwargs["config"] = config
        response = ai_client.models.generate_content(**kwargs)
        return response.text
    except Exception as e:
        error_str = str(e)
        # Verificamos si es el error 429 de límite de cuota
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            st.warning("⏳ La IA está recibiendo muchas consultas (Límite de la capa gratuita). Por favor, espera 30 segundos y vuelve a intentar.")
        else:
            st.error(f"Error en la API de Inteligencia Artificial: {e}")
        return None
 
# ── ESTILOS CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* 1. BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #E5E7EB !important;
        box-shadow: 2px 0px 15px rgba(0,0,0,0.5) !important;
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: #1F2937 !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] hr { border-color: #D1D5DB !important; }
 
    /* 2. DISEÑO ANCHO */
    [data-testid="stMainBlockContainer"], .block-container {
        max-width: 95% !important;
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
 
    /* 3. INPUTS OSCUROS Y CHAT */
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] input {
        background-color: #1F2937 !important;
        color: #FFFFFF !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    } /* <--- ¡OJO! En tu código faltaba esta llave de cierre */
 
    /* Input de texto clásico */
    div[data-testid="stTextInput"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
    }

    /* NUEVO: Input del Chat Nativo (Para que la letra sea negra) */
    div[data-testid="stChatInput"] textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important; 
    }
    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
    }
 
    /* Resto de los iconos de los inputs */
    div[data-testid="stSelectbox"] svg, div[data-testid="stSelectbox"] span,
    div[data-testid="stSelectbox"] div, div[data-testid="stNumberInput"] button,
    div[data-testid="stNumberInput"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        background-color: transparent !important;
    }
 
    /* 4. TABS NARANJA */
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-size: 14px !important;
        transition: all 0.3s ease;
    }
    button[data-baseweb="tab"]:hover { color: #FF6B00 !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FF6B00 !important;
        border-bottom-color: #FF6B00 !important;
        font-weight: bold !important;
    }
 
    /* 5. METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: #1F2937 !important;
        border-left: 5px solid #FF6B00 !important;
        border-radius: 8px !important;
        padding: 15px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3) !important;
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-2px); }
    div[data-testid="stMetric"] label {
        color: #9CA3AF !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
 
    /* 6. BURBUJAS DE CHAT */
    .chat-user {
        background-color: #1e3a5f;
        color: white;
        padding: 10px 14px;
        border-radius: 12px 12px 2px 12px;
        margin: 6px 0;
        text-align: right;
    }
    .chat-ai {
        background-color: #1a2e1a;
        color: #d4f5d4;
        padding: 10px 14px;
        border-radius: 12px 12px 12px 2px;
        margin: 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
 
# ── INICIALIZACIÓN DE ESTADO DE SESIÓN ────────────────────────────────────────
if "reporte_institucional" not in st.session_state:
    st.session_state["reporte_institucional"] = None
if "saldo_cash" not in st.session_state:
    st.session_state["saldo_cash"] = 100000.0
if "billetera" not in st.session_state:
    st.session_state["billetera"] = {}
if "chat_historia" not in st.session_state:
    st.session_state["chat_historia"] = []
if "resumen_noticias_ia" not in st.session_state:
    st.session_state["resumen_noticias_ia"] = None
 
# ── PANEL LATERAL ─────────────────────────────────────────────────────────────
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
        st.cache_data.clear()
        st.rerun()
 
# ── CABECERA PRINCIPAL ────────────────────────────────────────────────────────
st.title("Sistema de Monitoreo y Análisis de Activos Digitales")
st.markdown("""
Esta plataforma de integración tecnológica procesa datos financieros en tiempo real mediante la interfaz de CoinGecko, 
acoplando modelos de lenguaje de última generación para la auditoría de carteras y el soporte en la toma de decisiones.
""")
st.write("---")
 
# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
with st.spinner("Estableciendo conexión con los servidores de datos..."):
    df = get_top_criptos_cached()
 
if df is not None and not df.empty:
 
    # KPIs SUPERIORES
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
 
    with st.spinner("Sincronizando flujo de prensa internacional..."):
        lista_noticias = get_noticias_cached()
 
    col_analitica, col_prensa = st.columns([0.7, 0.3])
 
    # ── PANEL IZQUIERDO ───────────────────────────────────────────────────────
    with col_analitica:
        tab_datos, tab_analisis, tab_tecnico, tab_ia, tab_chat, tab_comparador, tab_simulador = st.tabs([
            " Visualización de Datos",
            " Análisis de Volatilidad",
            " Análisis Técnico",
            " Consultoría IA",
            " Chat de Mercado",
            " Comparador",
            " Simulador de Portafolio"
        ])
 
        # ── TAB A: VISUALIZACIÓN DE DATOS ─────────────────────────────────────
        with tab_datos:
            st.subheader("Reporte Global y Local de Capitalización de Mercado")
            st.markdown("Variables cuantitativas indexadas en dólares americanos (USD) y convertidas a pesos chilenos (CLP).")
 
            df_final = df.copy()
            TASA_CAMBIO_CLP = 935.0
            df_final['Precio (CLP)']     = df_final['current_price'] * TASA_CAMBIO_CLP
            df_final['Market Cap (CLP)'] = df_final['market_cap']    * TASA_CAMBIO_CLP
            df_final = df_final[['name','symbol','current_price','Precio (CLP)','market_cap','Market Cap (CLP)','price_change_percentage_24h']]
            df_final.columns = ['Activo','Ticker','Precio (USD)','Precio (CLP)','Market Cap (USD)','Market Cap (CLP)','Variación 24h']
 
            st.dataframe(
                df_final, use_container_width=True, height=450, hide_index=True,
                column_config={
                    "Activo":           st.column_config.TextColumn("Activo",           help="Nombre oficial del activo digital"),
                    "Ticker":           st.column_config.TextColumn("Ticker",           help="Nomenclatura internacional"),
                    "Precio (USD)":     st.column_config.NumberColumn("Precio (USD)",     format="$%,.2f"),
                    "Precio (CLP)":     st.column_config.NumberColumn("Precio (CLP)",     format="$%,.0f"),
                    "Market Cap (USD)": st.column_config.NumberColumn("Market Cap (USD)", format="$%,.0f"),
                    "Market Cap (CLP)": st.column_config.NumberColumn("Market Cap (CLP)", format="$%,.0f"),
                    "Variación 24h":    st.column_config.NumberColumn("Variación 24h",    format="%.2f%%")
                }
            )
 
        # ── TAB B: ANÁLISIS DE VOLATILIDAD ────────────────────────────────────
        with tab_analisis:
            st.subheader("Análisis Comparativo y Distribución de Mercado")
            st.markdown("Evaluación de anomalías estadísticas y rendimientos extremos de los activos bajo observación.")
 
            criterio_busqueda = st.radio(
                "Seleccione el segmento de volatilidad a evaluar:",
                ["Top 15 Activos con Mayor Crecimiento", "Top 15 Activos con Mayor Contracción"],
                horizontal=True
            )
 
            if "Mayor Crecimiento" in criterio_busqueda:
                df_filtrado     = df.sort_values(by='price_change_percentage_24h', ascending=False).head(15)
                color_secuencia = ['#FF6B00'] * len(df_filtrado)
            else:
                df_filtrado     = df.sort_values(by='price_change_percentage_24h', ascending=True).head(15)
                color_secuencia = ['#EF4444'] * len(df_filtrado)
 
            fig_barras = px.bar(
                df_filtrado, x='price_change_percentage_24h', y='name', orientation='h',
                labels={'price_change_percentage_24h': 'Variación diaria (%)', 'name': 'Activo'},
                template="plotly_dark"
            )
            fig_barras.update_traces(marker_color=color_secuencia)
            fig_barras.update_layout(
                margin=dict(l=20, r=20, t=10, b=10),
                coloraxis_showscale=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_barras, use_container_width=True)
 
            st.write("---")
            st.subheader("Mapa de Calor del Mercado (Treemap Total)")
            try:
                fig_treemap = px.treemap(
                    df, path=['name'], values='market_cap',
                    color='price_change_percentage_24h',
                    color_continuous_scale='RdYlGn', color_continuous_midpoint=0,
                    template="plotly_dark"
                )
                fig_treemap.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_treemap, use_container_width=True)
            except Exception as e:
                st.error(f"Error estructural en la generación del mapa de calor: {e}")
 
            st.write("---")
            st.subheader("Análisis de Tendencia Histórica")
            diccionario_criptos = dict(zip(df['name'], df['id']))
            nombre_seleccionado = st.selectbox("Activo objeto de estudio histórico:", list(diccionario_criptos.keys()))
            id_seleccionado     = diccionario_criptos[nombre_seleccionado]
 
            with st.spinner("Descargando registros históricos del servidor..."):
                df_historico = obtener_historico_activo(coin_id=id_seleccionado, days=30)
 
            if df_historico is not None and not df_historico.empty:
                fig_linea = px.line(
                    df_historico, x='Fecha', y='Precio',
                    labels={'Fecha': 'Línea Temporal', 'Precio': 'Valor de Cierre (USD)'},
                    template="plotly_dark"
                )
                fig_linea.update_traces(line_color='#00FFCC', line_width=2)
                fig_linea.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
                st.plotly_chart(fig_linea, use_container_width=True)
 
        # ── TAB C (NUEVO): ANÁLISIS TÉCNICO ───────────────────────────────────
        with tab_tecnico:
            st.subheader(" Análisis Técnico Avanzado")
            st.markdown("Indicadores cuantitativos sobre series de tiempo: RSI, medias móviles y señales de entrada/salida.")
 
            diccionario_criptos_t = dict(zip(df['name'], df['id']))
            col_at1, col_at2 = st.columns(2)
            with col_at1:
                activo_tecnico = st.selectbox("Seleccione activo para análisis técnico:", list(diccionario_criptos_t.keys()), key="at_activo")
            with col_at2:
                ventana_dias = st.selectbox("Período de análisis (días):", [30, 60, 90], key="at_dias")
 
            with st.spinner("Calculando indicadores técnicos..."):
                df_hist_t = obtener_historico_activo(coin_id=diccionario_criptos_t[activo_tecnico], days=ventana_dias)
 
            if df_hist_t is not None and not df_hist_t.empty:
                df_hist_t['MA7']  = df_hist_t['Precio'].rolling(window=7).mean()
                df_hist_t['MA30'] = df_hist_t['Precio'].rolling(window=min(30, len(df_hist_t))).mean()
 
                delta    = df_hist_t['Precio'].diff()
                ganancia = delta.clip(lower=0).rolling(window=14).mean()
                perdida  = (-delta.clip(upper=0)).rolling(window=14).mean()
                rs       = ganancia / perdida.replace(0, 1e-9)
                df_hist_t['RSI'] = 100 - (100 / (1 + rs))
 
                fig_ma = go.Figure()
                fig_ma.add_trace(go.Scatter(x=df_hist_t['Fecha'], y=df_hist_t['Precio'], name='Precio',     line=dict(color='#00FFCC', width=2)))
                fig_ma.add_trace(go.Scatter(x=df_hist_t['Fecha'], y=df_hist_t['MA7'],    name='MA 7 días',  line=dict(color='#FFD700', width=1.5, dash='dot')))
                fig_ma.add_trace(go.Scatter(x=df_hist_t['Fecha'], y=df_hist_t['MA30'],   name='MA 30 días', line=dict(color='#FF6B6B', width=1.5, dash='dash')))
                fig_ma.update_layout(
                    title=f"Precio y Medias Móviles — {activo_tecnico}", template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig_ma, use_container_width=True)
 
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=df_hist_t['Fecha'], y=df_hist_t['RSI'], name='RSI',
                    line=dict(color='#A78BFA', width=2), fill='tozeroy', fillcolor='rgba(167,139,250,0.1)'
                ))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red",   annotation_text="Sobrecompra (70)")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Sobreventa (30)")
                fig_rsi.update_layout(
                    title="RSI — Índice de Fuerza Relativa (14 períodos)", yaxis=dict(range=[0, 100]),
                    template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    hovermode="x unified"
                )
                st.plotly_chart(fig_rsi, use_container_width=True)
 
                st.write("---")
                st.markdown("####  Panel de Señales Técnicas")
                rsi_actual      = df_hist_t['RSI'].dropna().iloc[-1]
                ma7_actual      = df_hist_t['MA7'].dropna().iloc[-1]
                ma30_dropna     = df_hist_t['MA30'].dropna()
                ma30_actual     = ma30_dropna.iloc[-1] if not ma30_dropna.empty else None
                precio_actual_t = df_hist_t['Precio'].iloc[-1]
 
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("RSI Actual", f"{rsi_actual:.1f}")
                    if rsi_actual >= 70:
                        st.error(" Zona de Sobrecompra — posible corrección")
                    elif rsi_actual <= 30:
                        st.success(" Zona de Sobreventa — posible rebote")
                    else:
                        st.info(" RSI en zona neutral")
                with col_s2:
                    st.metric("MA7 vs Precio", f"${ma7_actual:,.2f}")
                    if precio_actual_t > ma7_actual:
                        st.success(" Precio sobre MA7 — tendencia alcista corto plazo")
                    else:
                        st.error(" Precio bajo MA7 — presión bajista")
                with col_s3:
                    if ma30_actual:
                        st.metric("MA30 vs Precio", f"${ma30_actual:,.2f}")
                        if ma7_actual > ma30_actual:
                            st.success(" Cruce Dorado — MA7 > MA30 (señal alcista)")
                        else:
                            st.error(" Cruce de Muerte — MA7 < MA30 (señal bajista)")
                    else:
                        st.info("Datos insuficientes para MA30")
 
        # ── TAB D: CONSULTORÍA IA ─────────────────────────────────────────────
        with tab_ia:
            st.subheader("Módulo de Inteligencia Artificial para Soporte Estrecho")
            st.markdown("Computación y procesamiento lingüístico de variables cuantitativas para la emisión de reportes.")
 
            if st.button("Generar Informe de Auditoría Financiera", use_container_width=True):
                fecha_servidor             = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                activo_top_ganador         = df.loc[df['price_change_percentage_24h'].idxmax()]
                activo_top_perdedor        = df.loc[df['price_change_percentage_24h'].idxmin()]
                promedio_variacion_mercado = df['price_change_percentage_24h'].mean()
                contexto = "".join([
                    f"- {r['name']} ({r['symbol'].upper()}): ${r['current_price']:,} (Var 24h: {r['price_change_percentage_24h']:.2f}%)\n"
                    for _, r in df.iterrows()
                ])
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
                    resultado = llamar_gemini(
                        prompt=prompt_enriquecido,
                        system_instruction="Actúa como un Analista Financiero Senior virtual, desarrollado para la Escuela de Informática y Gestión de la Universidad Diego Portales. Emite informes de auditoría ejecutiva bajo un carácter estrictamente formal, corporativo y técnico, basándote de forma exclusiva en la analítica de datos provista."
                    )
                    if resultado:
                        st.session_state["reporte_institucional"] = resultado
                        st.success("Informe de Auditoría Ejecutado Correctamente")
 
            if st.session_state["reporte_institucional"]:
                st.write("---")
                st.markdown("### Reporte Ejecutivo de Gestión Institucional")
                st.info(st.session_state["reporte_institucional"])
 
        # ── TAB F (NUEVO): CHAT DE MERCADO ────────────────────────────────────
        with tab_chat:
            st.subheader("💬 Chat de Mercado — Consulta libre con IA")
            st.markdown(
                "Pregunta cualquier cosa sobre el mercado cripto. La IA tiene acceso a los "
                "precios actuales en tiempo real para fundamentar sus respuestas."
            )
            
            # Botón para limpiar el chat arriba (fuera del contenedor)
            if st.button("🗑️ Limpiar chat", key="btn_limpiar_chat"):
                st.session_state["chat_historia"] = []
                st.rerun()
                
            st.write("---")

            # Preparar el contexto oculto de datos
            contexto_chat = "Datos actuales de mercado (Top 50):\n" + "".join([
                f"- {r['name']} ({r['symbol'].upper()}): ${r['current_price']:,} | Var 24h: {r['price_change_percentage_24h']:.2f}% | Market Cap: ${r['market_cap']:,}\n"
                for _, r in df.head(50).iterrows()
            ])

            # 1. CONTENEDOR DEL HISTORIAL DE MENSAJES
            chat_container = st.container(height=450)
            with chat_container:
                # Mensaje de bienvenida
                if not st.session_state["chat_historia"]:
                    with st.chat_message("assistant"):
                        st.write("👋 Hola, soy tu asistente de mercado cripto. Pregúntame sobre precios, tendencias, comparaciones o cualquier duda sobre los activos digitales.")
                
                # Dibujar todos los mensajes guardados en el historial
                for msg in st.session_state["chat_historia"]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            # 2. BARRA DE ESCRITURA NATIVA (Funciona con Enter automáticamente)
            # st.chat_input siempre se coloca al final y maneja su propio estilo
            if pregunta_usuario := st.chat_input("Escribe tu consulta. Ej: ¿Cuál es la mejor cripto hoy?"):
                
                # Mostrar inmediatamente el mensaje del usuario en la pantalla
                with chat_container:
                    with st.chat_message("user"):
                        st.write(pregunta_usuario)
                        
                # Guardar el mensaje del usuario en la memoria
                st.session_state["chat_historia"].append({"role": "user", "content": pregunta_usuario})
                
                # Preparar todo el texto que le enviaremos a Gemini
                contenido_gemini = "\n".join([
                    f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                    for m in st.session_state["chat_historia"]
                ])
                
                # Llamar a la IA mostrando una animación de carga
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Procesando tu consulta..."):
                            respuesta_ia = llamar_gemini(
                                prompt=contenido_gemini,
                                system_instruction=(
                                    f"Eres un asistente experto en criptomonedas de la Universidad Diego Portales. "
                                    f"Responde siempre en español, de forma clara y directa. "
                                    f"Tienes acceso a los siguientes datos de mercado en tiempo real:\n\n{contexto_chat}"
                                )
                            )
                            # Si responde bien, lo mostramos y lo guardamos
                            if respuesta_ia:
                                st.write(respuesta_ia)
                                st.session_state["chat_historia"].append({"role": "assistant", "content": respuesta_ia})
 
        # ── TAB G (NUEVO): COMPARADOR ─────────────────────────────────────────
        with tab_comparador:
            st.subheader(" Comparador de Criptomonedas")
            st.markdown("Análisis comparativo entre dos activos digitales: métricas financieras y tendencia histórica.")
            st.write("---")
 
            lista_activos = df['name'].tolist()
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cripto_a = st.selectbox("Activo A:", lista_activos, index=0, key="comp_a")
            with col_c2:
                cripto_b = st.selectbox("Activo B:", lista_activos, index=1, key="comp_b")
 
            dias_comp = st.select_slider("Período de comparación (días):", options=[7, 14, 30, 60, 90], value=30)
 
            if st.button("Comparar Activos", use_container_width=True, key="btn_comparar"):
                id_dict = dict(zip(df['name'], df['id']))
                with st.spinner(f"Cargando datos de {cripto_a} y {cripto_b}..."):
                    df_a = obtener_historico_activo(coin_id=id_dict[cripto_a], days=dias_comp)
                    df_b = obtener_historico_activo(coin_id=id_dict[cripto_b], days=dias_comp)
 
                row_a = df[df['name'] == cripto_a].iloc[0]
                row_b = df[df['name'] == cripto_b].iloc[0]
 
                st.write("---")
                st.markdown("####  Métricas Comparativas en Tiempo Real")
                col_m0, col_m1, col_m2 = st.columns(3)
                with col_m0:
                    st.markdown("**Indicador**")
                    st.markdown("Precio Actual")
                    st.markdown("Variación 24h")
                    st.markdown("Market Cap")
                with col_m1:
                    st.markdown(f"**{cripto_a}**")
                    st.markdown(f"${row_a['current_price']:,.4f}")
                    delta_a = row_a['price_change_percentage_24h']
                    st.markdown(f"{'🟢' if delta_a >= 0 else '🔴'} {delta_a:.2f}%")
                    st.markdown(f"${row_a['market_cap']:,.0f}")
                with col_m2:
                    st.markdown(f"**{cripto_b}**")
                    st.markdown(f"${row_b['current_price']:,.4f}")
                    delta_b = row_b['price_change_percentage_24h']
                    st.markdown(f"{'🟢' if delta_b >= 0 else '🔴'} {delta_b:.2f}%")
                    st.markdown(f"${row_b['market_cap']:,.0f}")
 
                if df_a is not None and df_b is not None:
                    st.write("---")
                    st.markdown("####  Rendimiento Relativo Normalizado (Base 100)")
                    st.caption("Ambos activos parten de 100 para hacer la comparación de rendimiento justa.")
 
                    df_a['Normalizado'] = (df_a['Precio'] / df_a['Precio'].iloc[0]) * 100
                    df_b['Normalizado'] = (df_b['Precio'] / df_b['Precio'].iloc[0]) * 100
 
                    fig_comp = go.Figure()
                    fig_comp.add_trace(go.Scatter(x=df_a['Fecha'], y=df_a['Normalizado'], name=cripto_a, line=dict(color='#00FFCC', width=2)))
                    fig_comp.add_trace(go.Scatter(x=df_b['Fecha'], y=df_b['Normalizado'], name=cripto_b, line=dict(color='#FF6B6B', width=2)))
                    fig_comp.add_hline(y=100, line_dash="dot", line_color="gray", annotation_text="Base 100")
                    fig_comp.update_layout(
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02),
                        yaxis_title="Rendimiento Relativo (%)"
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
 
                    st.write("---")
                    st.markdown("####  Veredicto de IA")
                    rend_a = df_a['Normalizado'].iloc[-1] - 100
                    rend_b = df_b['Normalizado'].iloc[-1] - 100
                    prompt_comp = f"""
                    Compara estos dos activos cripto en base a sus datos actuales y su rendimiento en los últimos {dias_comp} días:
                    {cripto_a}: precio ${row_a['current_price']:,} | variación 24h: {row_a['price_change_percentage_24h']:.2f}% | market cap: ${row_a['market_cap']:,} | rendimiento período: {rend_a:.2f}%
                    {cripto_b}: precio ${row_b['current_price']:,} | variación 24h: {row_b['price_change_percentage_24h']:.2f}% | market cap: ${row_b['market_cap']:,} | rendimiento período: {rend_b:.2f}%
                    Emite un análisis comparativo breve (máximo 150 palabras) indicando cuál presenta mejor perspectiva de corto plazo y por qué.
                    Responde en español y de forma directa.
                    """
                    with st.spinner("Generando veredicto..."):
                        veredicto = llamar_gemini(prompt=prompt_comp)
                        if veredicto:
                            st.info(veredicto)
                else:
                    st.error("No se pudieron obtener datos históricos para uno o ambos activos.")
 
        # ── TAB H: SIMULADOR DE PORTAFOLIO ────────────────────────────────────
        with tab_simulador:
            st.subheader("Simulador de Inversiones y Retorno de Inversión (ROI)")
            st.markdown("Módulo operativo para la gestión de activos y diversificación patrimonial en tiempo real.")
            st.write("---")
 
            precios_dict  = dict(zip(df['name'], df['current_price']))
            simbolos_dict = dict(zip(df['name'], df['symbol']))
 
            st.markdown("#### Terminal de Negociación (Órdenes de Mercado)")
            col_tx1, col_tx2, col_tx3 = st.columns(3)
            with col_tx1:
                crypto_tx   = st.selectbox("Seleccione Activo Objeto de Transacción:", df['name'].tolist(), key="sb_crypto_tx")
            with col_tx2:
                accion_tx   = st.selectbox("Tipo de Operación Financiera:", ["Comprar", "Vender"], key="sb_accion_tx")
            with col_tx3:
                cantidad_tx = st.number_input("Cantidad de Unidades de Activo:", min_value=0.0, step=0.01, key="num_cant_tx")
 
            if st.button("Ejecutar Transacción en Portafolio", use_container_width=True):
                precio_unitario = precios_dict[crypto_tx]
                costo_total     = precio_unitario * cantidad_tx
                if accion_tx == "Comprar":
                    if costo_total > st.session_state["saldo_cash"]:
                        st.error("Transacción Rechazada: Fondos de Efectivo (Cash) Insuficientes.")
                    elif cantidad_tx <= 0:
                        st.error("Error: La cantidad transaccionada debe ser mayor a cero.")
                    else:
                        st.session_state["saldo_cash"] -= costo_total
                        st.session_state["billetera"][crypto_tx] = st.session_state["billetera"].get(crypto_tx, 0.0) + cantidad_tx
                        st.success(f"Orden Ejecutada: Compra de {cantidad_tx} {simbolos_dict[crypto_tx].upper()}.")
                        st.rerun()
                elif accion_tx == "Vender":
                    cantidad_poseida = st.session_state["billetera"].get(crypto_tx, 0.0)
                    if cantidad_tx > cantidad_poseida:
                        st.error("Transacción Rechazada: Cantidad de activos en cartera insuficiente.")
                    elif cantidad_tx <= 0:
                        st.error("Error: La cantidad transaccionada debe ser mayor a cero.")
                    else:
                        st.session_state["saldo_cash"] += costo_total
                        st.session_state["billetera"][crypto_tx] = cantidad_poseida - cantidad_tx
                        if st.session_state["billetera"][crypto_tx] <= 0:
                            del st.session_state["billetera"][crypto_tx]
                        st.success(f"Orden Ejecutada: Venta de {cantidad_tx} {simbolos_dict[crypto_tx].upper()}.")
                        st.rerun()
 
            valor_criptos_total = 0.0
            filas_portafolio    = []
            for crypto, cant in st.session_state["billetera"].items():
                if cant > 0:
                    p_actual   = precios_dict.get(crypto, 0.0)
                    v_posicion = cant * p_actual
                    valor_criptos_total += v_posicion
                    filas_portafolio.append({
                        "Activo": crypto, "Unidades": cant,
                        "Precio de Mercado (USD)": f"${p_actual:,.2f}",
                        "Valorización (USD)": v_posicion
                    })
 
            patrimonio_neto_total = st.session_state["saldo_cash"] + valor_criptos_total
            roi_acumulado         = ((patrimonio_neto_total - 100000.0) / 100000.0) * 100
 
            st.write("---")
            st.markdown("#### Estado de Situación Patrimonial")
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            with col_kpi1:
                st.metric(label="Capital Disponible (Efectivo)",       value=f"${st.session_state['saldo_cash']:,.2f} USD")
            with col_kpi2:
                st.metric(label="Valorización Total de Criptoactivos", value=f"${valor_criptos_total:,.2f} USD")
            with col_kpi3:
                st.metric(label="Patrimonio Neto Total", value=f"${patrimonio_neto_total:,.2f} USD", delta=f"{roi_acumulado:.2f}% ROI")
 
            if filas_portafolio:
                df_port = pd.DataFrame(filas_portafolio)
                col_tab, col_pie = st.columns([0.55, 0.45])
                with col_tab:
                    st.markdown("##### Desglose de Posiciones de Inversión Abiertas")
                    df_mostrar = df_port.copy()
                    df_mostrar["Valorización (USD)"] = df_mostrar["Valorización (USD)"].map(lambda x: f"${x:,.2f}")
                    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                with col_pie:
                    st.markdown("##### Matriz Distribución de Activos")
                    fila_cash = pd.DataFrame([{
                        "Activo": "Efectivo (Cash)", "Unidades": 1.0,
                        "Precio de Mercado (USD)": "N/A",
                        "Valorización (USD)": st.session_state["saldo_cash"]
                    }])
                    df_pie  = pd.concat([df_port, fila_cash], ignore_index=True)
                    fig_pie = px.pie(df_pie, values='Valorización (USD)', names='Activo', template="plotly_dark")
                    fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("La cartera de inversión se encuentra actualmente vacía. Utilice el panel superior para generar órdenes de compra.")
 
    # ── PANEL DERECHO: NOTICIAS + RESUMEN IA ─────────────────────────────────
    with col_prensa:
        st.subheader("Prensa y Tendencias Globales")
        st.markdown("Variables cualitativas en tiempo real para mitigar riesgos operacionales.")
        st.write("---")
 
        if lista_noticias:
            if st.button(" Resumir Noticias con IA (ES)", use_container_width=True, key="btn_resumen_noticias"):
                titulos_noticias = "\n".join([f"- {n.get('title', '')}" for n in lista_noticias[:10]])
                prompt_resumen = f"""
                Analiza los siguientes titulares de noticias del mercado cripto y redacta un resumen ejecutivo
                en español (máximo 120 palabras) que destaque las tendencias principales, los activos más
                mencionados y el sentimiento general del mercado (alcista/bajista/neutral):
                {titulos_noticias}
                """
                with st.spinner("Resumiendo noticias..."):
                    resumen = llamar_gemini(prompt=prompt_resumen)
                    if resumen:
                        st.session_state["resumen_noticias_ia"] = resumen
 
            if st.session_state["resumen_noticias_ia"]:
                st.markdown("**📋 Resumen IA:**")
                st.info(st.session_state["resumen_noticias_ia"])
                st.write("---")
 
            for noticia in lista_noticias[:5]:
                titulo     = noticia.get('title', 'Publicación sin título')
                fuente     = noticia.get('source_info', {}).get('name', 'Agencia Externa')
                url_enlace = noticia.get('url', '#')
                imagen_url = noticia.get('imageurl', '')
                with st.container():
                    if imagen_url:
                        st.markdown(
                            f'<div style="width:100%;max-width:280px;max-height:140px;overflow:hidden;border-radius:6px;margin:0 auto 8px auto;">'
                            f'<img src="{imagen_url}" style="width:100%;height:140px;object-fit:cover;"></div>',
                            unsafe_allow_html=True
                        )
                    st.markdown(f"**[{titulo}]({url_enlace})**")
                    st.caption(f"Fuente: {fuente} | Idioma: Inglés")
                    st.write("---")
        else:
            st.error("Servicio de distribución de prensa no disponible en este momento.")
 
else:
    st.error("Error crítico: No fue posible establecer comunicación estable con los endpoints de CoinGecko.")
