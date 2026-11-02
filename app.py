import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# Configuración general de la página
st.set_page_config(page_title="Crypto Dashboard", page_icon="₿", layout="wide")

# Carga global de variables de entorno
load_dotenv()

# Inicialización del cliente de IA
api_key_gemini = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=api_key_gemini)

# Llamada del backend
from coingecko_api import obtener_top_criptos, obtener_historico_activo

# --- OPTIMIZACIÓN DE CACHÉ ---
@st.cache_data(ttl=300)
def get_top_criptos_cached():
    return obtener_top_criptos()

# ── FUNCIÓN CENTRALIZADA PARA LLAMADAS A GEMINI ───────────────────────────────
def llamar_gemini(prompt: str, system_instruction: str = None) -> str | None:
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
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            st.warning("⏳ La IA está recibiendo muchas consultas (límite de la capa gratuita). Por favor, espera 30 segundos y vuelve a intentar.")
        else:
            st.error(f"Error en la API de Inteligencia Artificial: {e}")
        return None

# ── TEMA VISUAL Y AYUDAS PLOTLY ───────────────────────────────────────────────
PLOTLY_THEME = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, Arial, sans-serif", "color": "#E2E8F0"},
    "hoverlabel": {"bgcolor": "#0F172A", "font_size": 12, "font_family": "Inter, Arial, sans-serif"},
    "legend": {"bgcolor": "rgba(15, 23, 42, 0.55)", "bordercolor": "rgba(148,163,184,0.2)", "borderwidth": 1},
    "margin": dict(l=10, r=10, t=30, b=10),
}


def configure_plotly(fig):
    fig.update_layout(**PLOTLY_THEME)
    fig.update_xaxes(showgrid=False, linecolor="rgba(148,163,184,0.35)", tickfont={"color": "#CBD5E1"})
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", linecolor="rgba(148,163,184,0.35)", tickfont={"color": "#CBD5E1"})
    return fig

# ── ESTILOS CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --bg: #071421;
        --bg-alt: #0d1d2d;
        --panel: rgba(15, 23, 42, 0.85);
        --panel-soft: rgba(19, 33, 49, 0.9);
        --sidebar: #0b1725;
        --border: rgba(148, 163, 184, 0.18);
        --primary: #5eead4;
        --primary-2: #38bdf8;
        --accent: #fbbf24;
        --accent-2: #f97316;
        --text: #e5eefb;
        --muted: #9fb5d1;
        --green: #34d399;
        --red: #f87171;
        --shadow: 0 12px 32px rgba(2, 8, 23, 0.35);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #071421 0%, #0b1626 100%);
        color: var(--text);
    }

    .stApp {
        background: linear-gradient(180deg, #071421 0%, #0b1626 100%);
        color: var(--text);
    }

    .main .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 1.5rem !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071824 0%, #0b1725 100%) !important;
        border-right: 1px solid var(--border);
        box-shadow: inset -1px 0 0 rgba(255,255,255,0.02);
    }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: var(--text) !important;
    }

    .brand-card {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        background: linear-gradient(135deg, rgba(94,234,212,0.12), rgba(56,189,248,0.10));
        border: 1px solid rgba(94,234,212,0.2);
        border-radius: 18px;
        padding: 0.8rem 0.9rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(14, 116, 144, 0.18);
    }

    .brand-mark {
        width: 42px;
        height: 42px;
        min-width: 42px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #5eead4, #38bdf8);
        box-shadow: 0 8px 20px rgba(94,234,212,0.35);
    }

    .brand-name {
        font-size: 1.02rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #F8FAFC !important;
    }

    .brand-tag {
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted) !important;
    }

    .stMetric {
        background: linear-gradient(180deg, rgba(18, 31, 47, 0.95), rgba(12, 23, 35, 0.92));
        border: 1px solid var(--border);
        border-radius: 18px !important;
        padding: 1.1rem 1.1rem 0.9rem !important;
        box-shadow: var(--shadow);
        backdrop-filter: blur(8px);
    }

    .stMetric label {
        color: var(--muted) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    .stMetric [data-testid="stMetricDelta"] {
        color: var(--green) !important;
        font-weight: 600;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stDateInput"] > div {
        background: rgba(15, 23, 42, 0.9) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }

    div[data-testid="stSelectbox"] svg,
    div[data-testid="stSelectbox"] span,
    div[data-testid="stNumberInput"] button,
    div[data-testid="stNumberInput"] svg {
        color: var(--text) !important;
        fill: var(--text) !important;
    }

    button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%);
        color: #03161d !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 20px rgba(56, 189, 248, 0.25);
    }

    .stTabs [role="tablist"] {
        gap: 0.6rem;
        background: rgba(15, 23, 42, 0.35);
        border: 1px solid var(--border);
        padding: 0.45rem;
        border-radius: 18px;
        margin-bottom: 1rem;
    }

    button[data-baseweb="tab"] {
        color: var(--muted) !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease;
        padding: 0.75rem 1.05rem !important;
    }

    button[data-baseweb="tab"]:hover {
        color: var(--text) !important;
        border-color: rgba(94,234,212,0.18) !important;
        background: rgba(148,163,184,0.07) !important;
        transform: translateY(-1px);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #03161d !important;
        border-color: transparent !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%) !important;
        box-shadow: 0 10px 18px rgba(56, 189, 248, 0.22);
    }

    .block-container {
        max-width: 100% !important;
    }

    .glass-panel {
        background: linear-gradient(180deg, rgba(14, 22, 33, 0.96), rgba(13, 24, 35, 0.92));
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: var(--shadow);
    }

    .top-badge {
        display: inline-block;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        background: rgba(94, 234, 212, 0.08);
        border: 1px solid rgba(94, 234, 212, 0.32);
        color: var(--primary) !important;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 700;
    }

    .page-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
        color: var(--text) !important;
        margin-top: 0.55rem !important;
        margin-bottom: 0.3rem !important;
    }

    .page-subtitle {
        color: var(--muted) !important;
        font-size: 1rem;
        margin-bottom: 1.2rem !important;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(94,234,212,0.5), rgba(148,163,184,0.15));
        border: none;
        margin: 1rem 0;
    }

    .status-pill {
        display: inline-block;
        padding: 0.4rem 0.7rem;
        background: rgba(52, 211, 153, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.28);
        border-radius: 999px;
        color: var(--green) !important;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .hero-panel {
        background: linear-gradient(135deg, rgba(15, 118, 110, 0.15), rgba(14, 165, 233, 0.10));
        border: 1px solid rgba(94, 234, 212, 0.14);
        border-radius: 22px;
        padding: 1.1rem 1.2rem;
        box-shadow: var(--shadow);
    }

    .small-label {
        color: var(--muted) !important;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .chat-user {
        background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(94,234,212,0.12));
        color: var(--text);
        border: 1px solid rgba(56,189,248,0.18);
        padding: 10px 14px;
        border-radius: 14px 14px 2px 14px;
        margin: 8px 0;
    }

    .chat-ai {
        background: rgba(148, 163, 184, 0.08);
        color: var(--text);
        border: 1px solid rgba(148,163,184,0.18);
        padding: 10px 14px;
        border-radius: 14px 14px 14px 2px;
        margin: 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
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

# ── PANEL LATERAL ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="brand-card">
            <div class="brand-mark">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2.5C7.31 2.5 3.5 6.31 3.5 11C3.5 15.69 7.31 19.5 12 19.5C16.69 19.5 20.5 15.69 20.5 11C20.5 6.31 16.69 2.5 12 2.5ZM12 17.5C8.41 17.5 5.5 14.59 5.5 11C5.5 7.41 8.41 4.5 12 4.5C15.59 4.5 18.5 7.41 18.5 11C18.5 14.59 15.59 17.5 12 17.5Z" fill="#041A2A"/>
                    <path d="M13.1 7.1H10.9V10.15H8.02V12.25H10.9V15.8H13.1V12.25H15.98V10.15H13.1V7.1Z" fill="#041A2A"/>
                </svg>
            </div>
            <div>
                <div class="brand-name">NovaCrypto</div>
                <div class="brand-tag">Market Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    st.markdown('<div class="status-pill">Sistema activo</div>', unsafe_allow_html=True)
    st.write("")

    if st.button("Sincronizar Datos de Mercado", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── CABECERA PRINCIPAL ─────────────────────────────────────────────────────────
st.markdown('<div class="top-badge">Live market</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Crypto Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Monitoreo inteligente de activos digitales, análisis técnico y gestión de cartera.</div>', unsafe_allow_html=True)

hero = st.container()
with hero:
    st.markdown('<div class="hero-panel">', unsafe_allow_html=True)
    col_hero_1, col_hero_2 = st.columns([2, 1])
    with col_hero_1:
        st.markdown('<div class="small-label">Resumen del mercado</div>', unsafe_allow_html=True)
        st.markdown("Tendencias globales, análisis comparativo y soporte de IA para decisiones más rápidas y fundamentadas.")
    with col_hero_2:
        st.markdown('<div class="small-label">Estado</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-pill">Datos en vivo</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── CARGA DE DATOS ─────────────────────────────────────────────────────────────
with st.spinner("Estableciendo conexión con los servidores de datos..."):
    df = get_top_criptos_cached()

if df is not None and not df.empty:
    col1, col2, col3 = st.columns(3)
    btc_data = df[df['symbol'].str.lower() == 'btc']
    eth_data = df[df['symbol'].str.lower() == 'eth']

    with col1:
        val_btc = btc_data['current_price'].values[0] if not btc_data.empty else 0
        st.metric(label="Bitcoin", value=f"${val_btc:,.2f}")
    with col2:
        val_eth = eth_data['current_price'].values[0] if not eth_data.empty else 0
        st.metric(label="Ethereum", value=f"${val_eth:,.2f}")
    with col3:
        st.metric(label="Activos analizados", value=len(df))

    st.write("---")

    tab_datos, tab_analisis, tab_tecnico, tab_ia, tab_chat, tab_comparador, tab_simulador = st.tabs([
        "📈 Resumen",
        "📊 Volatilidad",
        "📉 Técnico",
        "🤖 IA",
        "💬 Chat",
        "⚖️ Comparador",
        "🧮 Portafolio"
    ])

    # ── TAB A: VISUALIZACIÓN DE DATOS ─────────────────────────────────────
    with tab_datos:
        st.subheader("Reporte global de capitalización")
        df_final = df.copy()
        TASA_CAMBIO_CLP = 935.0
        df_final['Precio (CLP)'] = df_final['current_price'] * TASA_CAMBIO_CLP
        df_final['Market Cap (CLP)'] = df_final['market_cap'] * TASA_CAMBIO_CLP
        df_final = df_final[['name', 'symbol', 'current_price', 'Precio (CLP)', 'market_cap', 'Market Cap (CLP)', 'price_change_percentage_24h']]
        df_final.columns = ['Activo', 'Ticker', 'Precio (USD)', 'Precio (CLP)', 'Market Cap (USD)', 'Market Cap (CLP)', 'Variación 24h']

        st.dataframe(
            df_final,
            use_container_width=True,
            height=450,
            hide_index=True,
            column_config={
                "Activo": st.column_config.TextColumn("Activo"),
                "Ticker": st.column_config.TextColumn("Ticker"),
                "Precio (USD)": st.column_config.NumberColumn("Precio (USD)", format="$%,.2f"),
                "Precio (CLP)": st.column_config.NumberColumn("Precio (CLP)", format="$%,.0f"),
                "Market Cap (USD)": st.column_config.NumberColumn("Market Cap (USD)", format="$%,.0f"),
                "Market Cap (CLP)": st.column_config.NumberColumn("Market Cap (CLP)", format="$%,.0f"),
                "Variación 24h": st.column_config.NumberColumn("Variación 24h", format="%.2f%%")
            }
        )

    # ── TAB B: ANÁLISIS DE VOLATILIDAD ────────────────────────────────────
    with tab_analisis:
        st.subheader("Análisis comparativo y distribución del mercado")

        criterio_busqueda = st.radio(
            "Seleccione el segmento a evaluar:",
            ["Top 15 activos con mayor crecimiento", "Top 15 activos con mayor contracción"],
            horizontal=True,
        )

        if "mayor crecimiento" in criterio_busqueda.lower():
            df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=False).head(15)
            color_secuencia = ['#5eead4'] * len(df_filtrado)
        else:
            df_filtrado = df.sort_values(by='price_change_percentage_24h', ascending=True).head(15)
            color_secuencia = ['#f87171'] * len(df_filtrado)

        fig_barras = px.bar(
            df_filtrado,
            x='price_change_percentage_24h',
            y='name',
            orientation='h',
            labels={'price_change_percentage_24h': 'Variación diaria (%)', 'name': 'Activo'},
            template='plotly_dark',
            color_discrete_sequence=['#5eead4'] * len(df_filtrado),
            text_auto='.2f'
        )
        fig_barras.update_traces(
            marker_line_color='rgba(255,255,255,0.15)',
            marker_line_width=1,
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Variación: %{x:.2f}%<extra></extra>'
        )
        fig_barras.update_layout(
            title='Rendimiento del mercado por activo',
            xaxis_title='Variación diaria (%)',
            yaxis_title='',
            bargap=0.35,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#E2E8F0'},
            margin=dict(l=15, r=15, t=40, b=15),
        )
        st.plotly_chart(fig_barras, use_container_width=True)

        st.write("---")
        st.subheader("Mapa de calor del mercado")
        try:
            fig_treemap = px.treemap(
                df,
                path=['name'],
                values='market_cap',
                color='price_change_percentage_24h',
                color_continuous_scale='Viridis',
                color_continuous_midpoint=0,
                template='plotly_dark'
            )
            fig_treemap.update_layout(
                title='Capitalización y variación diaria',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=35, b=10),
                font={'color': '#E2E8F0'},
            )
            fig_treemap.update_traces(textinfo='label+percent entry')
            st.plotly_chart(fig_treemap, use_container_width=True)
        except Exception as e:
            st.error(f"Error estructural en la generación del mapa: {e}")

        st.write("---")
        st.subheader("Tendencia histórica")
        diccionario_criptos = dict(zip(df['name'], df['id']))
        nombre_seleccionado = st.selectbox("Activo a analizar:", list(diccionario_criptos.keys()))
        id_seleccionado = diccionario_criptos[nombre_seleccionado]

        with st.spinner("Descargando registros históricos..."):
            df_historico = obtener_historico_activo(coin_id=id_seleccionado, days=30)

        if df_historico is not None and not df_historico.empty:
            fig_linea = go.Figure()
            fig_linea.add_trace(go.Scatter(
                x=df_historico['Fecha'],
                y=df_historico['Precio'],
                mode='lines',
                line=dict(color='#5eead4', width=3),
                hovertemplate='<b>%{x|%d %b}</b><br>Precio: $%{y:,.2f}<extra></extra>'
            ))
            fig_linea.add_area(
                x=df_historico['Fecha'],
                y=df_historico['Precio'],
                mode='lines',
                line=dict(color='#5eead4', width=0),
                fillcolor='rgba(94,234,212,0.15)',
            )
            fig_linea = configure_plotly(fig_linea)
            fig_linea.update_layout(
                title=f'{nombre_seleccionado} — Serie histórica',
                xaxis_title='Fecha',
                yaxis_title='Precio (USD)',
                hovermode='x unified',
            )
            st.plotly_chart(fig_linea, use_container_width=True)

    # ── TAB C: ANÁLISIS TÉCNICO ───────────────────────────────────
    with tab_tecnico:
        st.subheader("Análisis técnico avanzado")
        diccionario_criptos_t = dict(zip(df['name'], df['id']))
        col_at1, col_at2 = st.columns(2)
        with col_at1:
            activo_tecnico = st.selectbox("Seleccione activo:", list(diccionario_criptos_t.keys()), key="at_activo")
        with col_at2:
            ventana_dias = st.selectbox("Período:", [30, 60, 90], key="at_dias")

        with st.spinner("Calculando indicadores técnicos..."):
            df_hist_t = obtener_historico_activo(coin_id=diccionario_criptos_t[activo_tecnico], days=ventana_dias)

        if df_hist_t is not None and not df_hist_t.empty:
            df_hist_t['MA7'] = df_hist_t['Precio'].rolling(window=7).mean()
            df_hist_t['MA30'] = df_hist_t['Precio'].rolling(window=min(30, len(df_hist_t))).mean()

            delta = df_hist_t['Precio'].diff()
            ganancia = delta.clip(lower=0).rolling(window=14).mean()
            perdida = (-delta.clip(upper=0)).rolling(window=14).mean()
            rs = ganancia / perdida.replace(0, 1e-9)
            df_hist_t['RSI'] = 100 - (100 / (1 + rs))

            fig_ma = go.Figure()
            fig_ma.add_trace(go.Scatter(x=df_hist_t['Fecha'], y=df_hist_t['Precio'], name='Precio', line=dict(color='#5eead4', width=2.5), hovertemplate='%{x|%d %b}<br>Precio: $%{y:,.2f}<extra></extra>'))
            fig_ma.add_trace(go.Scatter(x=df_hist_t['Fecha'], y=df_hist_t['MA7'], name='MA 7 días', line=dict(color='#fbbf24', width=2), hovertemplate='%{x|%d %b}<br>MA7: $%{y:,.2f}<extra></extra>'))
            fig_ma.add_trace(go.Scatter(x=df_hist_t['Fecha'], y=df_hist_t['MA30'], name='MA 30 días', line=dict(color='#f87171', width=2), hovertemplate='%{x|%d %b}<br>MA30: $%{y:,.2f}<extra></extra>'))
            fig_ma = configure_plotly(fig_ma)
            fig_ma.update_layout(
                title=f"Precio y medias móviles — {activo_tecnico}",
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='left', x=0),
            )
            st.plotly_chart(fig_ma, use_container_width=True)

            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df_hist_t['Fecha'], y=df_hist_t['RSI'], name='RSI',
                line=dict(color='#38bdf8', width=2.5), fill='tozeroy', fillcolor='rgba(56,189,248,0.08)',
                hovertemplate='%{x|%d %b}<br>RSI: %{y:.1f}<extra></extra>'
            ))
            fig_rsi.add_hline(y=70, line_dash='dash', line_color='rgba(248,113,113,0.9)', annotation_text='Sobrecompra (70)')
            fig_rsi.add_hline(y=30, line_dash='dash', line_color='rgba(52,211,153,0.9)', annotation_text='Sobreventa (30)')
            fig_rsi = configure_plotly(fig_rsi)
            fig_rsi.update_layout(
                title='Índice de Fuerza Relativa (RSI)',
                yaxis=dict(range=[0, 100]),
                hovermode='x unified',
            )
            st.plotly_chart(fig_rsi, use_container_width=True)

            st.write("---")
            st.markdown("#### Panel de señales técnicas")
            rsi_actual = df_hist_t['RSI'].dropna().iloc[-1]
            ma7_actual = df_hist_t['MA7'].dropna().iloc[-1]
            ma30_actual = df_hist_t['MA30'].dropna().iloc[-1] if not df_hist_t['MA30'].dropna().empty else None
            precio_actual_t = df_hist_t['Precio'].iloc[-1]

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("RSI Actual", f"{rsi_actual:.1f}")
                if rsi_actual >= 70:
                    st.error("Zona de sobrecompra")
                elif rsi_actual <= 30:
                    st.success("Zona de sobreventa")
                else:
                    st.info("Neutral")
            with col_s2:
                st.metric("MA7 vs. Precio", f"${ma7_actual:,.2f}")
                if precio_actual_t > ma7_actual:
                    st.success("Tendencia alcista de corto plazo")
                else:
                    st.error("Presión bajista")
            with col_s3:
                if ma30_actual:
                    st.metric("MA30", f"${ma30_actual:,.2f}")
                    if ma7_actual > ma30_actual:
                        st.success("Cruce dorado")
                    else:
                        st.error("Cruce de muerte")
                else:
                    st.info("Datos insuficientes")

    # ── TAB D: CONSULTORÍA IA ─────────────────────────────────────────────
    with tab_ia:
        st.subheader("Módulo de inteligencia artificial")
        if st.button("Generar informe financiero", use_container_width=True):
            fecha_servidor = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
            activo_top_ganador = df.loc[df['price_change_percentage_24h'].idxmax()]
            activo_top_perdedor = df.loc[df['price_change_percentage_24h'].idxmin()]
            promedio_variacion_mercado = df['price_change_percentage_24h'].mean()
            contexto = "\n".join([
                f"- {r['name']} ({r['symbol'].upper()}): ${r['current_price']:,} (Var 24h: {r['price_change_percentage_24h']:.2f}%)"
                for _, r in df.iterrows()
            ])
            prompt_enriquecido = f"""
            Fecha y hora: {fecha_servidor}
            Mayor rendimiento diario: {activo_top_ganador['name']} ({activo_top_ganador['price_change_percentage_24h']:.2f}%)
            Mayor contracción diaria: {activo_top_perdedor['name']} ({activo_top_perdedor['price_change_percentage_24h']:.2f}%)
            Variación promedio del mercado: {promedio_variacion_mercado:.2f}%

            Activos analizados:
            {contexto}
            """
            with st.spinner("Procesando reporte..."):
                resultado = llamar_gemini(
                    prompt=prompt_enriquecido,
                    system_instruction="Actúa como un analista financiero senior. Responde en español, de forma clara y con foco en tendencias de mercado y riesgos."
                )
                if resultado:
                    st.session_state["reporte_institucional"] = resultado
                    st.success("Informe ejecutado correctamente")

        if st.session_state["reporte_institucional"]:
            st.write("---")
            st.markdown("### Reporte ejecutivo")
            st.info(st.session_state["reporte_institucional"])

    # ── TAB E: CHAT DE MERCADO ─────────────────────────────────────────────
    with tab_chat:
        st.subheader("Chat de mercado")
        if st.button("🗑️ Limpiar chat", key="btn_limpiar_chat"):
            st.session_state["chat_historia"] = []
            st.rerun()

        contexto_chat = "Datos actuales de mercado (Top 50):\n" + "".join([
            f"- {r['name']} ({r['symbol'].upper()}): ${r['current_price']:,} | Var 24h: {r['price_change_percentage_24h']:.2f}% | Market Cap: ${r['market_cap']:,}\n"
            for _, r in df.head(50).iterrows()
        ])

        chat_container = st.container(height=450)
        with chat_container:
            if not st.session_state["chat_historia"]:
                with st.chat_message("assistant"):
                    st.write("Hola, soy tu asistente de mercado. Pregúntame por precios, tendencias o comparaciones.")

            for msg in st.session_state["chat_historia"]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        if pregunta_usuario := st.chat_input("Escribe tu consulta sobre criptomonedas..."):
            with chat_container:
                with st.chat_message("user"):
                    st.write(pregunta_usuario)

            st.session_state["chat_historia"].append({"role": "user", "content": pregunta_usuario})
            contenido_gemini = "\n".join([
                f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                for m in st.session_state["chat_historia"]
            ])

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Procesando tu consulta..."):
                        respuesta_ia = llamar_gemini(
                            prompt=contenido_gemini,
                            system_instruction=(
                                "Eres un asistente experto en criptomonedas. Responde siempre en español y de forma clara. "
                                f"Tienes acceso a estos datos actuales:\n\n{contexto_chat}"
                            )
                        )
                        if respuesta_ia:
                            st.write(respuesta_ia)
                            st.session_state["chat_historia"].append({"role": "assistant", "content": respuesta_ia})

    # ── TAB F: COMPARADOR ───────────────────────────────────────────────
    with tab_comparador:
        st.subheader("Comparador de criptomonedas")
        st.write("---")

        lista_activos = df['name'].tolist()
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            cripto_a = st.selectbox("Activo A:", lista_activos, index=0, key="comp_a")
        with col_c2:
            cripto_b = st.selectbox("Activo B:", lista_activos, index=1, key="comp_b")

        dias_comp = st.select_slider("Período:", options=[7, 14, 30, 60, 90], value=30)

        if st.button("Comparar activos", use_container_width=True, key="btn_comparar"):
            id_dict = dict(zip(df['name'], df['id']))
            with st.spinner(f"Cargando datos de {cripto_a} y {cripto_b}..."):
                df_a = obtener_historico_activo(coin_id=id_dict[cripto_a], days=dias_comp)
                df_b = obtener_historico_activo(coin_id=id_dict[cripto_b], days=dias_comp)

            row_a = df[df['name'] == cripto_a].iloc[0]
            row_b = df[df['name'] == cripto_b].iloc[0]

            st.write("---")
            st.markdown("#### Métricas comparativas")
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
                st.markdown("#### Rendimiento relativo")
                df_a['Normalizado'] = (df_a['Precio'] / df_a['Precio'].iloc[0]) * 100
                df_b['Normalizado'] = (df_b['Precio'] / df_b['Precio'].iloc[0]) * 100

                fig_comp = go.Figure()
                fig_comp.add_trace(go.Scatter(x=df_a['Fecha'], y=df_a['Normalizado'], name=cripto_a, line=dict(color='#5eead4', width=2.5), hovertemplate='%{x|%d %b}<br>%{y:.2f}<extra></extra>'))
                fig_comp.add_trace(go.Scatter(x=df_b['Fecha'], y=df_b['Normalizado'], name=cripto_b, line=dict(color='#f97316', width=2.5), hovertemplate='%{x|%d %b}<br>%{y:.2f}<extra></extra>'))
                fig_comp.add_hline(y=100, line_dash='dot', line_color='rgba(148,163,184,0.8)', annotation_text='Base 100')
                fig_comp = configure_plotly(fig_comp)
                fig_comp.update_layout(
                    title='Comparación de rendimiento relativo',
                    hovermode='x unified',
                    yaxis_title='Rendimiento relativo (%)',
                    legend=dict(orientation='h', yanchor='bottom', y=1.12, xanchor='left', x=0),
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                st.write("---")
                st.markdown("#### Veredicto de IA")
                rend_a = df_a['Normalizado'].iloc[-1] - 100
                rend_b = df_b['Normalizado'].iloc[-1] - 100
                prompt_comp = f"""
                Compara estos dos activos cripto en base a sus datos actuales y rendimiento en los últimos {dias_comp} días:
                {cripto_a}: precio ${row_a['current_price']:,} | variación 24h: {row_a['price_change_percentage_24h']:.2f}% | market cap: ${row_a['market_cap']:,} | rendimiento período: {rend_a:.2f}%
                {cripto_b}: precio ${row_b['current_price']:,} | variación 24h: {row_b['price_change_percentage_24h']:.2f}% | market cap: ${row_b['market_cap']:,} | rendimiento período: {rend_b:.2f}%
                Emite un análisis breve (máximo 150 palabras) indicando cuál presenta mejor perspectiva de corto plazo y por qué.
                Responde en español y de forma directa.
                """
                with st.spinner("Generando veredicto..."):
                    veredicto = llamar_gemini(prompt=prompt_comp)
                    if veredicto:
                        st.info(veredicto)
            else:
                st.error("No se pudieron obtener datos históricos para uno o ambos activos.")

    # ── TAB G: SIMULADOR DE PORTAFOLIO ────────────────────────────────────
    with tab_simulador:
        st.subheader("Simulador de inversiones")
        st.write("---")

        precios_dict = dict(zip(df['name'], df['current_price']))
        simbolos_dict = dict(zip(df['name'], df['symbol']))

        st.markdown("#### Terminal de operaciones")
        col_tx1, col_tx2, col_tx3 = st.columns(3)
        with col_tx1:
            crypto_tx = st.selectbox("Seleccione activo:", df['name'].tolist(), key="sb_crypto_tx")
        with col_tx2:
            accion_tx = st.selectbox("Tipo de operación:", ["Comprar", "Vender"], key="sb_accion_tx")
        with col_tx3:
            cantidad_tx = st.number_input("Cantidad:", min_value=0.0, step=0.01, key="num_cant_tx")

        if st.button("Ejecutar transacción", use_container_width=True):
            precio_unitario = precios_dict[crypto_tx]
            costo_total = precio_unitario * cantidad_tx
            if accion_tx == "Comprar":
                if costo_total > st.session_state["saldo_cash"]:
                    st.error("Fondos insuficientes.")
                elif cantidad_tx <= 0:
                    st.error("La cantidad debe ser mayor a cero.")
                else:
                    st.session_state["saldo_cash"] -= costo_total
                    st.session_state["billetera"][crypto_tx] = st.session_state["billetera"].get(crypto_tx, 0.0) + cantidad_tx
                    st.success(f"Compra ejecutada: {cantidad_tx} {simbolos_dict[crypto_tx].upper()}.")
                    st.rerun()
            elif accion_tx == "Vender":
                cantidad_poseida = st.session_state["billetera"].get(crypto_tx, 0.0)
                if cantidad_tx > cantidad_poseida:
                    st.error("Cantidad insuficiente en cartera.")
                elif cantidad_tx <= 0:
                    st.error("La cantidad debe ser mayor a cero.")
                else:
                    st.session_state["saldo_cash"] += costo_total
                    st.session_state["billetera"][crypto_tx] = cantidad_poseida - cantidad_tx
                    if st.session_state["billetera"][crypto_tx] <= 0:
                        del st.session_state["billetera"][crypto_tx]
                    st.success(f"Venta ejecutada: {cantidad_tx} {simbolos_dict[crypto_tx].upper()}.")
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
                    "Precio de mercado (USD)": f"${p_actual:,.2f}",
                    "Valorización (USD)": v_posicion,
                })

        patrimonio_neto_total = st.session_state["saldo_cash"] + valor_criptos_total
        roi_acumulado = ((patrimonio_neto_total - 100000.0) / 100000.0) * 100

        st.write("---")
        st.markdown("#### Estado patrimonial")
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.metric(label="Capital disponible", value=f"${st.session_state['saldo_cash']:,.2f} USD")
        with col_kpi2:
            st.metric(label="Criptoactivos", value=f"${valor_criptos_total:,.2f} USD")
        with col_kpi3:
            st.metric(label="Patrimonio neto", value=f"${patrimonio_neto_total:,.2f} USD", delta=f"{roi_acumulado:.2f}% ROI")

        if filas_portafolio:
            df_port = pd.DataFrame(filas_portafolio)
            col_tab, col_pie = st.columns([0.55, 0.45])
            with col_tab:
                st.markdown("##### Desglose de posiciones")
                df_mostrar = df_port.copy()
                df_mostrar["Valorización (USD)"] = df_mostrar["Valorización (USD)"].map(lambda x: f"${x:,.2f}")
                st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            with col_pie:
                st.markdown("##### Distribución")
                fila_cash = pd.DataFrame([{
                    "Activo": "Efectivo (Cash)",
                    "Unidades": 1.0,
                    "Precio de mercado (USD)": "N/A",
                    "Valorización (USD)": st.session_state["saldo_cash"],
                }])
                df_pie = pd.concat([df_port, fila_cash], ignore_index=True)
                fig_pie = px.pie(df_pie, values='Valorización (USD)', names='Activo', template='plotly_dark')
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), font={'color': '#E2E8F0'})
                fig_pie.update_traces(textinfo='percent+label', pull=[0.02 if i == 0 else 0 for i in range(len(df_pie))], marker=dict(colors=['#5eead4', '#38bdf8', '#fbbf24', '#f97316', '#f87171']))
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("La cartera se encuentra vacía. Usa el panel superior para comprar activos.")

else:
    st.error("Error crítico: No fue posible establecer comunicación con CoinGecko.")
