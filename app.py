import os
from datetime import datetime
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from google import genai

from coingecko_api import obtener_historico_activo, obtener_top_criptos

load_dotenv()
st.set_page_config(
    page_title="NovaCrypto | Market Intelligence",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palette
BG = "#071521"
PANEL = "#0D2131"
PANEL_ALT = "#102A3D"
TEXT = "#EAF4FB"
MUTED = "#93AFC2"
TEAL = "#55E6D0"
BLUE = "#56B8F5"
AMBER = "#FFBF69"
RED = "#FF7185"
GREEN = "#4DDBA5"

PLOTLY_THEME = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, Arial, sans-serif", "color": TEXT, "size": 13},
    "hoverlabel": {"bgcolor": PANEL, "font_size": 13, "font_family": "Inter, Arial, sans-serif"},
    "margin": {"l": 12, "r": 18, "t": 58, "b": 12},
    "legend": {"orientation": "h", "y": 1.12, "x": 0, "bgcolor": "rgba(0,0,0,0)"},
}


def style_chart(fig):
    fig.update_layout(**PLOTLY_THEME)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(147,175,194,.25)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(147,175,194,.10)", zeroline=False, linecolor="rgba(147,175,194,.25)")
    return fig


@st.cache_data(ttl=300, show_spinner=False)
def load_market_data():
    return obtener_top_criptos()


@st.cache_data(ttl=900, show_spinner=False)
def load_history(coin_id: str, days: int):
    return obtener_historico_activo(coin_id=coin_id, days=days)


def get_gemini_client() -> Optional[genai.Client]:
    try:
        key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        return genai.Client(api_key=key) if key else None
    except Exception:
        return None


def ask_gemini(prompt: str, instruction: Optional[str] = None) -> Optional[str]:
    client = get_gemini_client()
    if client is None:
        return "No encuentro GEMINI_API_KEY en Streamlit Secrets. Revisa la configuración de la app."
    try:
        from google.genai import types

        config = types.GenerateContentConfig(system_instruction=instruction) if instruction else None
        args = {"model": "gemini-2.5-flash", "contents": prompt}
        if config:
            args["config"] = config
        response = client.models.generate_content(**args)
        return getattr(response, "text", None) or "No recibí texto de respuesta. Inténtalo otra vez."
    except Exception as exc:
        if "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc):
            return "Alcancé el límite temporal de consultas. Espera un momento y vuelve a intentar."
        return "No pude completar la consulta. Comprueba los logs de Streamlit y vuelve a intentarlo."


# Visual styling, including a fixed, responsive chatbot launcher and panel.
st.markdown(
    f"""
    <style>
      :root {{ color-scheme: dark; }}
      html, body, [data-testid="stAppViewContainer"] {{
        background: radial-gradient(ellipse at 12% 0%, rgba(35,128,157,.18), transparent 34%),
                    radial-gradient(ellipse at 92% 8%, rgba(56,112,178,.15), transparent 30%), {BG};
        color: {TEXT};
      }}
      .stApp {{ background: transparent; }}
      .main .block-container {{ max-width: 1480px; padding: 1.5rem 2.2rem 5rem; }}
      [data-testid="stSidebar"] {{ background: linear-gradient(180deg,#091925,#0c2030) !important; border-right: 1px solid rgba(147,175,194,.14); }}
      [data-testid="stSidebar"] * {{ color: {TEXT}; }}
      h1,h2,h3 {{ letter-spacing: -.035em; }}
      h2 {{ margin-top: .55rem; }}
      [data-testid="stMetric"] {{ background: linear-gradient(145deg,rgba(16,42,61,.96),rgba(10,29,43,.96)); border: 1px solid rgba(147,175,194,.16); border-radius: 18px; padding: 1rem 1.15rem; box-shadow: 0 12px 30px rgba(0,0,0,.16); }}
      [data-testid="stMetricLabel"] {{ color: {MUTED} !important; font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; }}
      [data-testid="stMetricValue"] {{ color: {TEXT} !important; font-weight: 750; }}
      [data-testid="stSelectbox"] [data-baseweb="select"] {{ background: {PANEL_ALT} !important; border: 1px solid rgba(147,175,194,.22) !important; border-radius: 12px !important; }}
      [data-testid="stSelectbox"] * {{ color: {TEXT} !important; }}
      [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {{ background: #102A3D !important; color: {TEXT} !important; }}
      [role="option"]:hover, [role="option"][aria-selected="true"] {{ background: rgba(85,230,208,.16) !important; }}
      [data-testid="stTextInput"] input, [data-testid="stChatInput"] textarea, [data-testid="stNumberInput"] input {{ background: {PANEL_ALT} !important; color: {TEXT} !important; border-color: rgba(147,175,194,.22) !important; }}
      button[data-baseweb="tab"] {{ color: {MUTED} !important; font-weight: 650; }}
      button[data-baseweb="tab"][aria-selected="true"] {{ color: {TEAL} !important; }}
      [data-testid="stTabs"] [role="tablist"] {{ border-bottom: 1px solid rgba(147,175,194,.16); gap: .55rem; }}
      .brand {{ display:flex; align-items:center; gap:.85rem; padding:.9rem 1rem; border:1px solid rgba(85,230,208,.22); border-radius:18px; background:linear-gradient(135deg,rgba(85,230,208,.12),rgba(86,184,245,.08)); margin-bottom:1.2rem; }}
      .brand-icon {{ display:grid;place-items:center;width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,{TEAL},{BLUE});color:#071521;font-size:23px;font-weight:900; }}
      .brand-name {{ color:{TEXT};font-size:1.03rem;font-weight:800;letter-spacing:-.03em; }}
      .brand-caption {{ color:{MUTED};font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;margin-top:2px; }}
      .eyebrow {{ color:{TEAL};font-size:.72rem;font-weight:750;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.3rem; }}
      .hero-title {{ color:{TEXT};font-size:clamp(2rem,4vw,3.35rem);font-weight:850;letter-spacing:-.065em;line-height:1.05;margin:0; }}
      .hero-copy {{ color:{MUTED};font-size:1.02rem;line-height:1.6;margin-top:.75rem;max-width:740px; }}
      .hero {{ padding:1.45rem 1.6rem; border:1px solid rgba(147,175,194,.14); border-radius:24px; background:linear-gradient(135deg,rgba(16,42,61,.85),rgba(9,25,38,.78)); box-shadow:0 20px 50px rgba(0,0,0,.18); margin-bottom:1.2rem; }}
      .section-note {{ color:{MUTED}; font-size:.9rem; margin-top:-.25rem; margin-bottom:1rem; }}
      .stButton > button {{ border-radius:12px; border:1px solid rgba(85,230,208,.28); background:linear-gradient(135deg,rgba(85,230,208,.16),rgba(86,184,245,.12)); color:{TEXT}; font-weight:700; transition:all .18s ease; }}
      .stButton > button:hover {{ border-color:{TEAL}; color:{TEAL}; transform:translateY(-1px); }}

      /* Floating AI bot button: fixed to the viewport, with a gentle idle motion. */
      .st-key-ai_fab {{ position:fixed !important; right:26px !important; bottom:24px !important; z-index:10001 !important; width:74px !important; height:74px !important; }}
      .st-key-ai_fab [data-testid="stButton"] {{ width:74px !important; height:74px !important; }}
      .st-key-ai_fab button {{ width:68px !important; height:68px !important; min-height:68px !important; padding:0 !important; border-radius:50% !important; border:2px solid rgba(85,230,208,.9) !important; background:radial-gradient(circle at 30% 25%,#244e66,#102a3d 72%) !important; color:#eaffff !important; font-size:31px !important; box-shadow:0 0 0 6px rgba(85,230,208,.09),0 12px 35px rgba(0,0,0,.42),0 0 26px rgba(85,230,208,.24) !important; animation:bot-float 3.2s ease-in-out infinite; }}
      .st-key-ai_fab button:hover {{ transform:translateY(-4px) scale(1.04) !important; box-shadow:0 0 0 8px rgba(85,230,208,.12),0 16px 40px rgba(0,0,0,.46),0 0 34px rgba(85,230,208,.4) !important; }}
      .st-key-ai_fab button p {{ font-size:0 !important; }}
      .st-key-ai_fab button p:before {{ content:"🤖"; font-size:31px; }}
      .st-key-ai_fab button:after {{ content:""; position:absolute; width:10px;height:10px;border-radius:50%;right:3px;top:3px;background:#4DDBA5;border:2px solid #0D2131; }}
      @keyframes bot-float {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-5px); }} }}

      /* Chat panel floats above the bot and remains usable on smaller screens. */
      .st-key-ai_panel {{ position:fixed !important; right:27px !important; bottom:108px !important; z-index:10000 !important; width:min(390px,calc(100vw - 32px)) !important; max-width:390px !important; background:linear-gradient(155deg,#102a3d,#091b29) !important; border:1px solid rgba(85,230,208,.32) !important; border-radius:22px !important; padding:15px 16px 12px !important; box-shadow:0 24px 70px rgba(0,0,0,.56),0 0 32px rgba(85,230,208,.10) !important; }}
      .st-key-ai_panel [data-testid="stVerticalBlock"] {{ gap:.45rem; }}
      .st-key-ai_panel [data-testid="stChatMessage"] {{ background:rgba(255,255,255,.035); border:1px solid rgba(147,175,194,.10); border-radius:14px; padding:.55rem .7rem; }}
      .st-key-ai_panel [data-testid="stChatMessage"] p {{ font-size:.9rem; }}
      .st-key-ai_panel [data-testid="stTextInput"] input {{ border-radius:12px !important; }}
      .st-key-ai_panel [data-testid="stFormSubmitButton"] button {{ min-height:42px; }}
      .st-key-ai_panel [data-testid="stButton"] button {{ min-height:38px; }}
      @media(max-width:700px) {{
        .main .block-container {{ padding:1rem .8rem 6rem; }}
        .hero {{ padding:1.1rem; }}
        .st-key-ai_fab {{ right:16px !important; bottom:16px !important; }}
        .st-key-ai_panel {{ right:12px !important; bottom:94px !important; width:calc(100vw - 24px) !important; max-width:none !important; }}
      }}
      @media(prefers-reduced-motion:reduce) {{ .st-key-ai_fab button {{ animation:none !important; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar and page header
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-icon">₿</div><div><div class="brand-name">NOVA / CRYPTO</div><div class="brand-caption">Market intelligence</div></div></div>',
        unsafe_allow_html=True,
    )
    st.caption("CENTRO DE ANÁLISIS DIGITAL")
    st.markdown("Datos de mercado, análisis técnico y herramientas de comparación en un solo lugar.")
    st.divider()
    st.caption(f"Actualizado al cargar · {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    if st.button("↻  Actualizar mercado", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown('<div class="eyebrow">TERMINAL DE MERCADO · EN VIVO</div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1 class="hero-title">NovaCrypto<br>Market Intelligence</h1><p class="hero-copy">Una vista clara del mercado cripto: movimientos, tendencias e indicadores técnicos para explorar datos con más contexto.</p></div>', unsafe_allow_html=True)

with st.spinner("Conectando con CoinGecko..."):
    market = load_market_data()

if market is None or market.empty:
    st.error("No se pudieron cargar los datos de mercado. Verifica la conexión con CoinGecko e inténtalo de nuevo.")
    st.stop()

market = market.copy()
for col in ("current_price", "market_cap", "price_change_percentage_24h"):
    if col not in market:
        market[col] = pd.NA
    market[col] = pd.to_numeric(market[col], errors="coerce")
market["symbol"] = market["symbol"].fillna("").astype(str)
market["name"] = market["name"].fillna("Activo")
market = market.dropna(subset=["id", "current_price"])
if market.empty:
    st.error("CoinGecko respondió, pero no hay precios válidos para mostrar.")
    st.stop()

market["symbol_upper"] = market["symbol"].str.upper()
valid_change = market.dropna(subset=["price_change_percentage_24h"])

# Summary metrics
bitcoin_rows = market[market["symbol_upper"] == "BTC"]
ethereum_rows = market[market["symbol_upper"] == "ETH"]
col_btc, col_eth, col_change, col_cap = st.columns(4)
with col_btc:
    value = bitcoin_rows["current_price"].iloc[0] if not bitcoin_rows.empty else None
    st.metric("Bitcoin", f"${value:,.2f}" if pd.notna(value) else "—")
with col_eth:
    value = ethereum_rows["current_price"].iloc[0] if not ethereum_rows.empty else None
    st.metric("Ethereum", f"${value:,.2f}" if pd.notna(value) else "—")
with col_change:
    st.metric("Activos con datos", f"{len(market):,}")
with col_cap:
    cap = market["market_cap"].sum(min_count=1)
    st.metric("Capitalización (Top list)", f"${cap:,.0f}" if pd.notna(cap) else "—")

market_tab, technical_tab, compare_tab = st.tabs(["◈  Mercado", "⌁  Análisis técnico", "⇄  Comparador"])

with market_tab:
    st.subheader("Pulso del mercado")
    st.markdown('<div class="section-note">Activos destacados y variación porcentual de las últimas 24 horas.</div>', unsafe_allow_html=True)
    if not valid_change.empty:
        best = valid_change.loc[valid_change["price_change_percentage_24h"].idxmax()]
        worst = valid_change.loc[valid_change["price_change_percentage_24h"].idxmin()]
        avg_move = valid_change["price_change_percentage_24h"].mean()
        a, b, c = st.columns(3)
        a.metric("Mayor alza · 24 h", f"{best['name']}  {best['price_change_percentage_24h']:+.2f}%")
        b.metric("Mayor caída · 24 h", f"{worst['name']}  {worst['price_change_percentage_24h']:+.2f}%")
        c.metric("Variación media", f"{avg_move:+.2f}%")

    st.subheader("Mapa de rendimiento")
    st.markdown('<div class="section-note">El tamaño representa capitalización; el color representa variación en 24 h.</div>', unsafe_allow_html=True)
    treemap_df = market.dropna(subset=["market_cap", "price_change_percentage_24h"]).copy()
    treemap_df = treemap_df[treemap_df["market_cap"] > 0]
    if not treemap_df.empty:
        max_abs = max(float(treemap_df["price_change_percentage_24h"].abs().quantile(.95)), 1.0)
        fig_tree = px.treemap(
            treemap_df,
            path=[px.Constant("Mercado"), "name"],
            values="market_cap",
            color="price_change_percentage_24h",
            color_continuous_scale=[[0, "#E85D75"], [.5, "#243B53"], [1, "#45D6A4"]],
            range_color=[-max_abs, max_abs],
            custom_data=["symbol_upper", "current_price", "price_change_percentage_24h", "market_cap"],
            labels={"price_change_percentage_24h": "Variación 24 h", "market_cap": "Capitalización"},
        )
        fig_tree.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]} · %{customdata[2]:+.2f}%",
            hovertemplate="<b>%{label}</b> (%{customdata[0]})<br>Precio: $%{customdata[1]:,.4g}<br>Variación 24 h: %{customdata[2]:+.2f}%<br>Capitalización: $%{customdata[3]:,.0f}<extra></extra>",
            marker={"line": {"width": 1.2, "color": BG}}, root_color=PANEL_ALT,
        )
        fig_tree.update_coloraxes(colorbar={"title": {"text": "Variación 24 h (%)"}, "ticksuffix": "%", "len": .78})
        fig_tree.update_layout(**PLOTLY_THEME, height=610)
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.info("No hay suficientes datos de capitalización y variación para dibujar el mapa.")

    st.subheader("Listado de activos")
    display_df = market[["name", "symbol_upper", "current_price", "market_cap", "price_change_percentage_24h"]].copy()
    display_df.columns = ["Activo", "Ticker", "Precio USD", "Capitalización USD", "Variación 24 h (%)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True, column_config={
        "Precio USD": st.column_config.NumberColumn(format="$%.4f"),
        "Capitalización USD": st.column_config.NumberColumn(format="$%.0f"),
        "Variación 24 h (%)": st.column_config.NumberColumn(format="%.2f%%"),
    })

coin_map = dict(zip(market["name"], market["id"]))

with technical_tab:
    st.subheader("Análisis técnico")
    st.markdown('<div class="section-note">Precio, medias móviles y RSI calculados sobre el historial devuelto por CoinGecko.</div>', unsafe_allow_html=True)
    col_coin, col_days = st.columns([2, 1])
    with col_coin:
        selected_name = st.selectbox("Activo", list(coin_map), key="technical_coin")
    with col_days:
        days = st.selectbox("Ventana histórica", [30, 60, 90], key="technical_days")
    with st.spinner(f"Cargando historial de {selected_name}..."):
        history = load_history(coin_map[selected_name], days)

    if history is None or history.empty:
        st.warning("No hay datos históricos disponibles para este activo y período.")
    else:
        hist = history.copy().dropna(subset=["Fecha", "Precio"])
        hist["Fecha"] = pd.to_datetime(hist["Fecha"], errors="coerce")
        hist["Precio"] = pd.to_numeric(hist["Precio"], errors="coerce")
        hist = hist.dropna(subset=["Fecha", "Precio"]).sort_values("Fecha").reset_index(drop=True)
        if hist.empty:
            st.warning("El historial recibido no contiene precios válidos.")
        else:
            hist["MA7"] = hist["Precio"].rolling(7, min_periods=1).mean()
            hist["MA30"] = hist["Precio"].rolling(30, min_periods=1).mean()
            delta = hist["Precio"].diff()
            gains = delta.clip(lower=0).rolling(14, min_periods=14).mean()
            losses = (-delta.clip(upper=0)).rolling(14, min_periods=14).mean()
            hist["RSI"] = 100 - 100 / (1 + gains / losses.replace(0, float("nan")))
            last_price, first_price = hist["Precio"].iloc[-1], hist["Precio"].iloc[0]
            period_return = ((last_price / first_price) - 1) * 100 if first_price else float("nan")
            m1, m2, m3 = st.columns(3)
            m1.metric("Precio más reciente", f"${last_price:,.4f}")
            m2.metric(f"Rendimiento · {days} días", f"{period_return:+.2f}%" if pd.notna(period_return) else "—")
            valid_rsi = hist["RSI"].dropna()
            m3.metric("RSI", f"{valid_rsi.iloc[-1]:.1f}" if not valid_rsi.empty else "Calculando…")

            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(x=hist["Fecha"], y=hist["Precio"], name="Precio", mode="lines", line={"color": TEAL, "width": 3.2, "shape": "spline"}, fill="tozeroy", fillcolor="rgba(85,230,208,.075)", hovertemplate="<b>%{x|%d %b %Y}</b><br>Precio: $%{y:,.4f}<extra></extra>"))
            fig_price.add_trace(go.Scatter(x=hist["Fecha"], y=hist["MA7"], name="Media móvil · 7 períodos", mode="lines", line={"color": AMBER, "width": 2.2, "shape": "spline"}, hovertemplate="MA 7: $%{y:,.4f}<extra></extra>"))
            fig_price.add_trace(go.Scatter(x=hist["Fecha"], y=hist["MA30"], name="Media móvil · 30 períodos", mode="lines", line={"color": RED, "width": 2.2, "shape": "spline"}, hovertemplate="MA 30: $%{y:,.4f}<extra></extra>"))
            style_chart(fig_price)
            fig_price.update_layout(title={"text": f"{selected_name} <sup>· precio y tendencia</sup>", "x": .02, "xanchor": "left"}, yaxis_title="Precio (USD)", hovermode="x unified", height=500, legend={"orientation": "h", "y": 1.12, "x": .02})
            st.plotly_chart(fig_price, use_container_width=True)

            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=hist["Fecha"], y=hist["RSI"], name="RSI", mode="lines", line={"color": BLUE, "width": 2.5, "shape": "spline"}, fill="tozeroy", fillcolor="rgba(86,184,245,.08)", hovertemplate="<b>%{x|%d %b}</b><br>RSI: %{y:.1f}<extra></extra>"))
            fig_rsi.add_hrect(y0=30, y1=70, fillcolor="rgba(85,230,208,.045)", line_width=0, layer="below")
            fig_rsi.add_hline(y=70, line_dash="dash", line_color=RED, annotation_text="Sobrecompra · 70", annotation_position="top right")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color=GREEN, annotation_text="Sobreventa · 30", annotation_position="bottom right")
            style_chart(fig_rsi)
            fig_rsi.update_layout(title="Índice de fuerza relativa (RSI)", yaxis={"range": [0, 100], "title": "RSI"}, height=300, showlegend=False)
            st.plotly_chart(fig_rsi, use_container_width=True)
            st.caption("Las medias móviles del inicio del período usan los datos disponibles hasta completar su ventana.")

with compare_tab:
    st.subheader("Comparador de rendimiento")
    st.markdown('<div class="section-note">Compara el rendimiento porcentual desde una base común de 100.</div>', unsafe_allow_html=True)
    names = list(coin_map)
    c1, c2, c3 = st.columns([1, 1, .7])
    with c1:
        compare_a = st.selectbox("Activo A", names, index=0, key="compare_a")
    with c2:
        compare_b = st.selectbox("Activo B", names, index=min(1, len(names)-1), key="compare_b")
    with c3:
        compare_days = st.selectbox("Período", [7, 14, 30, 60, 90], index=2, key="compare_days")
    if st.button("Comparar activos", type="primary"):
        if compare_a == compare_b:
            st.info("Elige dos activos distintos para compararlos.")
        else:
            with st.spinner("Descargando ambos historiales..."):
                h_a = load_history(coin_map[compare_a], compare_days)
                h_b = load_history(coin_map[compare_b], compare_days)
            if h_a is None or h_b is None or h_a.empty or h_b.empty:
                st.warning("No se pudieron obtener ambos historiales para realizar la comparación.")
            else:
                traces = []
                for name, hist, color in [(compare_a, h_a, TEAL), (compare_b, h_b, AMBER)]:
                    hist = hist.dropna(subset=["Precio"]).copy()
                    hist["Precio"] = pd.to_numeric(hist["Precio"], errors="coerce")
                    hist = hist.dropna(subset=["Precio"])
                    if hist.empty or hist["Precio"].iloc[0] == 0:
                        continue
                    hist["Base 100"] = hist["Precio"] / hist["Precio"].iloc[0] * 100
                    traces.append((name, hist, color))
                if len(traces) < 2:
                    st.warning("No hay suficientes precios válidos para normalizar la comparación.")
                else:
                    fig = go.Figure()
                    for name, hist, color in traces:
                        fig.add_trace(go.Scatter(x=hist["Fecha"], y=hist["Base 100"], name=name, mode="lines", line={"color": color, "width": 3, "shape": "spline"}, hovertemplate="%{x|%d %b}<br>Base 100: %{y:.2f}<extra></extra>"))
                    fig.add_hline(y=100, line_dash="dot", line_color="rgba(147,175,194,.55)", annotation_text="Punto de partida")
                    style_chart(fig)
                    fig.update_layout(title=f"Rendimiento relativo · últimos {compare_days} días", yaxis_title="Índice (base 100)", hovermode="x unified", height=460)
                    st.plotly_chart(fig, use_container_width=True)

# Floating bot launcher. The compact round button stays on-screen while scrolling.
if "ai_panel_open" not in st.session_state:
    st.session_state.ai_panel_open = False
if "market_chat" not in st.session_state:
    st.session_state.market_chat = []

if st.session_state.ai_panel_open:
    with st.container(key="ai_panel"):
        title_col, close_col = st.columns([5, 1])
        with title_col:
            st.markdown("### 🤖 Nova · Asistente")
            st.caption("Consulta datos y tendencias del mercado")
        with close_col:
            if st.button("×", key="ai_panel_close", help="Cerrar asistente"):
                st.session_state.ai_panel_open = False
                st.rerun()

        messages_box = st.container(height=300, border=False)
        with messages_box:
            if not st.session_state.market_chat:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown("¡Hola! Soy Nova. Pregúntame por los movimientos recientes o por un activo del listado.")
            for message in st.session_state.market_chat[-12:]:
                with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "🧑"):
                    st.markdown(message["content"])

        with st.form("floating_ai_chat_form", clear_on_submit=True):
            prompt = st.text_input("Mensaje", placeholder="Ej.: ¿qué pasó con Bitcoin?", label_visibility="collapsed")
            send = st.form_submit_button("Enviar  ➤", use_container_width=True)

        if send and prompt.strip():
            st.session_state.market_chat.append({"role": "user", "content": prompt.strip()})
            top_context = market.head(35)
            context = "\n".join(
                f"{row['name']} ({row['symbol_upper']}): USD {row['current_price']}, variación 24h {row['price_change_percentage_24h']}%"
                for _, row in top_context.iterrows()
            )
            with st.spinner("Nova está pensando..."):
                answer = ask_gemini(
                    f"Datos recientes del mercado:\n{context}\n\nConsulta: {prompt.strip()}",
                    "Responde en español, de forma clara y prudente. Aclara que la información es una fotografía del mercado y no constituye asesoría financiera personalizada.",
                )
            if answer:
                st.session_state.market_chat.append({"role": "assistant", "content": answer})
            st.rerun()
else:
    with st.container(key="ai_fab"):
        if st.button("🤖", key="ai_fab_button", help="Abrir asistente de IA", use_container_width=True):
            st.session_state.ai_panel_open = True
            st.rerun()
