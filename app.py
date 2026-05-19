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

#llamada del backend
from coingecko_api import obtener_top_criptos, obtener_historico_activo, obtener_noticias_mercado

# --- CONTROL DE CONTRASTE, ANCHO E INPUTS DE LA INTERFAZ ---
# --- CONTROL DE CONTRASTE, ANCHO E INPUTS DE LA INTERFAZ ---
# --- ARQUITECTURA DE DISEÑO AVANZADO (UI/UX PREMIUM) ---
st.markdown(
    """
    <style>
    /* 1. BARRA LATERAL: Control de contraste institucional */
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
    [data-testid="stSidebar"] hr {
        border-color: #D1D5DB !important;
    }
    
    /* 2. DISEÑO ANCHO: Maximizar área analítica */
    [data-testid="stMainBlockContainer"], .block-container {
        max-width: 95% !important;
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    /* 3. CONTROLES DEL SIMULADOR: Unificación de inputs oscuros */
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] input {
        background-color: #1F2937 !important;
        color: #FFFFFF !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stSelectbox"] svg, div[data-testid="stSelectbox"] span,
    div[data-testid="stSelectbox"] div, div[data-testid="stNumberInput"] button,
    div[data-testid="stNumberInput"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        background-color: transparent !important;
    }

    /* 4. TABS/PESTAÑAS: Estilo Bloomberg con acento Naranja */
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-size: 15px !important;
        transition: all 0.3s ease;
    }
    button[data-baseweb="tab"]:hover {
        color: #FF6B00 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FF6B00 !important;
        border-bottom-color: #FF6B00 !important;
        font-weight: bold !important;
    }

    /* 5. METRIC CARDS: Transformación a Tarjetas Corporativas */
    div[data-testid="stMetric"] {
        background-color: #1F2937 !important;
        border-left: 5px solid #FF6B00 !important; /* Línea de acento naranja */
        border-radius: 8px !important;
        padding: 15px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px); /* Efecto flotante al pasar el mouse */
    }
    div[data-testid="stMetric"] label {
        color: #9CA3AF !important; /* Texto secundario gris claro */
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Inicialización del estado de la sesión para el almacenamiento del reporte de IA
if "reporte_institucional" not in st.session_state:
    st.session_state["reporte_institucional"] = None

# LO QUE AGREGAS AHORA:
if "saldo_cash" not in st.session_state:
    st.session_state["saldo_cash"] = 100000.0

if "billetera" not in st.session_state:
    st.session_state["billetera"] = {}

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
        # Modificar esta línea agregando "Simulador de Portafolio"
        tab_datos, tab_analisis, tab_ia, tab_simulador = st.tabs([
            "Visualización de Datos", 
            "Análisis de Volatilidad", 
            "Consultoría Predictiva IA",
            "Simulador de Portafolio"
        ])

        # PESTAÑA A: MATRIZ DE CAPITALIZACIÓN DE MERCADO
        # PESTAÑA A: MATRIZ DE CAPITALIZACIÓN DE MERCADO (MULTIDIVISA ENTERPRISE)
        with tab_datos:
            st.subheader("Reporte Global y Local de Capitalización de Mercado")
            st.markdown("Variables cuantitativas indexadas en dólares americanos (USD) y convertidas a pesos chilenos (CLP).")
            
            df_final = df.copy()
            
            # 1. Definición de la tasa de cambio de referencia para Chile
            TASA_CAMBIO_CLP = 935.0  # Paridad base: 1 USD = 935 CLP
            
            # 2. Computación de las nuevas capas de datos en el DataFrame
            df_final['Precio (CLP)'] = df_final['current_price'] * TASA_CAMBIO_CLP
            df_final['Market Cap (CLP)'] = df_final['market_cap'] * TASA_CAMBIO_CLP
            
            # 3. Selección y ordenamiento de columnas para la entrega formal (Excluyendo ID e Imagen)
            df_final = df_final[[
                'name', 'symbol', 
                'current_price', 'Precio (CLP)', 
                'market_cap', 'Market Cap (CLP)', 
                'price_change_percentage_24h'
            ]]
            
            # 4. Renombrado estructural de las columnas
            df_final.columns = [
                'Activo', 'Ticker', 
                'Precio (USD)', 'Precio (CLP)', 
                'Market Cap (USD)', 'Market Cap (CLP)', 
                'Variación 24h'
            ]
            
            # 5. Renderizado avanzado utilizando máscaras de configuración visual
            st.dataframe(
                df_final,
                use_container_width=True,
                height=450,
                hide_index=True,
                column_config={
                    "Activo": st.column_config.TextColumn("Activo", help="Nombre oficial del activo digital"),
                    "Ticker": st.column_config.TextColumn("Ticker", help="Nomenclatura internacional"),
                    "Precio (USD)": st.column_config.NumberColumn("Precio (USD)", format="$%,.2f"),
                    "Precio (CLP)": st.column_config.NumberColumn("Precio (CLP)", format="$%,.0f"),
                    "Market Cap (USD)": st.column_config.NumberColumn("Market Cap (USD)", format="$%,.0f"),
                    "Market Cap (CLP)": st.column_config.NumberColumn("Market Cap (CLP)", format="$%,.0f"),
                    "Variación 24h": st.column_config.NumberColumn("Variación 24h", format="%.2f%%")
                }
            )
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
                # Reemplaza la escala por un color sólido naranja corporativo
                color_secuencia = ['#FF6B00'] * len(df_filtrado)
            else:
                df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=True).head(15)
                color_secuencia = ['#EF4444'] * len(df_filtrado) # Rojo para pérdidas
                
            fig_barras = px.bar(
                df_filtrado, x='price_change_percentage_24h', y='name', orientation='h',
                labels={'price_change_percentage_24h': 'Variación diaria (%)', 'name': 'Activo'},
                template="plotly_dark"
            )
            # Forzar el color exacto en los tracks de las barras
            fig_linea = px.line(df_historico, x='Fecha', y='Precio', template="plotly_dark")
                # Cambiamos el color de la línea a Naranja Corporativo (#FF6B00)
            fig_linea.update_traces(line_color='#FF6B00', line_width=2.5)
            
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
    # PESTAÑA D: SIMULADOR DE PORTAFOLIO CORPORATIVO (PÉGALO AQUÍ)
        with tab_simulador:
            st.subheader("Simulador de Inversiones y Retorno de Inversión (ROI)")
            st.markdown("Módulo operativo para la gestión de activos y diversificación patrimonial en tiempo real.")
            st.write("---")
            
            precios_dict = dict(zip(df['name'], df['current_price']))
            simbolos_dict = dict(zip(df['name'], df['symbol']))
            
            st.markdown("#### Terminal de Negociación (Órdenes de Mercado)")
            col_tx1, col_tx2, col_tx3 = st.columns(3)
            
            with col_tx1:
                crypto_tx = st.selectbox("Seleccione Activo Objeto de Transacción:", df['name'].tolist(), key="sb_crypto_tx")
            with col_tx2:
                accion_tx = st.selectbox("Tipo de Operación Financiera:", ["Comprar", "Vender"], key="sb_accion_tx")
            with col_tx3:
                cantidad_tx = st.number_input("Cantidad de Unidades de Activo:", min_value=0.0, step=0.01, key="num_cant_tx")
                
            if st.button("Ejecutar Transacción en Portafolio", use_container_width=True):
                precio_unitario = precios_dict[crypto_tx]
                costo_total = precio_unitario * cantidad_tx
                
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
            filas_portafolio = []
            
            for crypto, cant in st.session_state["billetera"].items():
                if cant > 0:
                    p_actual = precios_dict.get(crypto, 0.0)
                    v_posicion = cant * p_actual
                    valor_criptos_total += v_posicion
                    filas_portafolio.append({
                        "Activo": crypto,
                        "Unidades": cant,
                        "Precio de Mercado (USD)": f"${p_actual:,.2f}",
                        "Valorización (USD)": v_posicion
                    })
                    
            patrimonio_neto_total = st.session_state["saldo_cash"] + valor_criptos_total
            roi_acumulado = ((patrimonio_neto_total - 100000.0) / 100000.0) * 100
            
            st.write("---")
            st.markdown("#### Estado de Situación Patrimonial")
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            
            with col_kpi1:
                st.metric(label="Capital Disponible (Efectivo)", value=f"${st.session_state['saldo_cash']:,.2f} USD")
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
                    fila_cash = pd.DataFrame([{"Activo": "Efectivo (Cash)", "Unidades": 1.0, "Precio de Mercado (USD)": "N/A", "Valorización (USD)": st.session_state["saldo_cash"]}])
                    df_pie = pd.concat([df_port, fila_cash], ignore_index=True)
                    
                    fig_pie = px.pie(df_pie, values='Valorización (USD)', names='Activo', template="plotly_dark")
                    fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("La cartera de inversión se encuentra actualmente vacía. Utilice el panel superior para generar órdenes de compra.")

    

    # --- PANEL DERECHO: CONTEXTO CUALITATIVO CONTINUO ---
    # --- PANEL DERECHO: CONTEXTO CUALITATIVO CONTINUO (CON LÍMITES ESTRICTOS) ---
    with col_prensa:
        st.subheader("Prensa y Tendencias Globales")
        st.markdown("Variables cualitativas en tiempo real para mitigar riesgos operacionales.")
        st.write("---")
        
        if lista_noticias:
            for noticia in lista_noticias[:5]:
                titulo = noticia.get('title', 'Publicación sin título')
                fuente = noticia.get('source_info', {}).get('name', 'Agencia Externa')
                url_enlace = noticia.get('url', '#')
                imagen_url = noticia.get('imageurl', '')
                
                with st.container():
                    if imagen_url:
                        # Forzado absoluto en píxeles para evitar el desborde en el navegador
                        st.markdown(
                            f"""
                            <div style="width: 100%; max-width: 280px; max-height: 140px; overflow: hidden; border-radius: 6px; margin: 0 auto 8px auto;">
                                <img src="{imagen_url}" style="width: 100%; height: 140px; object-fit: cover;">
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    st.markdown(f"**[{titulo}]({url_enlace})**")
                    st.caption(f"Fuente: {fuente} | Idioma: Inglés")
                    st.write("---")
        else:
            st.error("Servicio de distribución de prensa no disponible en este momento.")
else:
    st.error("Error crítico: No fue posible establecer comunicación estable con los endpoints de CoinGecko.")
