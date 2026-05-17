import streamlit as st  # <-- Corregido aquí (debe ser 'st')
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
from coingecko_api import obtener_top_criptos


# 1. Configuración de la página web (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Crypto Dashboard UDP",
    page_icon="📊",
    layout="wide"
)

# 2. Título principal de la web
st.title("📊 Dashboard de Criptomonedas en Tiempo Real")
st.markdown("### Proyecto Universitario - Datos conectados a la API de CoinGecko")

# Botón para actualizar los datos manualmente
if st.button("🔄 Actualizar Datos"):
    st.rerun()

st.write("---") # Línea divisoria

# 3. Llamada al backend para obtener los datos
st.subheader("Top 10 Criptomonedas más importantes")

with st.spinner("Cargando datos desde CoinGecko..."):
    df = obtener_top_criptos()

if df is not None and not df.empty:
    # --- SECCIÓN DE MÉTRICAS RÁPIDAS ---
    col1, col2, col3 = st.columns(3)
    
    # Buscamos Bitcoin y Ethereum en el DataFrame para mostrar su precio destacado
    btc_rows = df[df['symbol'].str.lower() == 'btc']
    eth_rows = df[df['symbol'].str.lower() == 'eth']
    
    btc_price = btc_rows['current_price'].values[0] if not btc_rows.empty else "N/A"
    eth_price = eth_rows['current_price'].values[0] if not eth_rows.empty else "N/A"
    
    with col1:
        if isinstance(btc_price, (int, float)):
            st.metric(label="Líder del Mercado (Bitcoin)", value=f"${btc_price:,.2f}")
        else:
            st.metric(label="Líder del Mercado (Bitcoin)", value=str(btc_price))
    with col2:
        if isinstance(eth_price, (int, float)):
            st.metric(label="Segundo Líder (Ethereum)", value=f"${eth_price:,.2f}")
        else:
            st.metric(label="Segundo Líder (Ethereum)", value=str(eth_price))
    with col3:
        st.metric(label="Monedas Monitoreadas", value=len(df))

    st.write("---") # Línea divisoria

    # --- SECCIÓN DE TABLA Y GRÁFICO (Lado a Lado) ---
    col_tabla, col_grafico = st.columns([1, 1])

    with col_tabla:
        st.markdown("### 📋 Tabla de Precios")
        df_mostrar = df.copy()
        df_mostrar.columns = ['Nombre', 'Símbolo', 'Precio (USD)', 'Cap. de Mercado', 'Cambio 24h (%)', 'Logo URL']
        # Mostramos la tabla ocultando la columna de la URL de la imagen
        st.dataframe(df_mostrar.drop(columns=['Logo URL']), use_container_width=True)

    with col_grafico:
        st.markdown("### 📈 Rendimiento en las Últimas 24 Horas (%)")
        
        # Ordenamos el DataFrame por la variación para que el gráfico sea estético
        df_ordenado = df.sort_values(by='price_change_percentage_24h', ascending=False)
        
        # Gráfico basado en el porcentaje de cambio
        fig = px.bar(
            df_ordenado, 
            x='name', 
            y='price_change_percentage_24h',
            labels={'name': 'Criptomoneda', 'price_change_percentage_24h': 'Variación (%)'},
            title="Ganancias / Pérdidas del Día",
            color='price_change_percentage_24h',
            # Escala de color: Rojo para pérdidas, Verde para ganancias
            color_continuous_scale=px.colors.diverging.RdYlGn, 
            color_continuous_midpoint=0
        )
        st.plotly_chart(fig, use_container_width=True)
        # --- NUEVA SECCIÓN: RECOMENDACIONES DE INVERSIÓN ---
    st.write("---")
    st.markdown("## 🤖 Sistema de Recomendaciones Automatizado")
    st.markdown("Este módulo analiza las variaciones de precio de las últimas 24 horas para generar alertas de mercado.")

    # Filtro para que el usuario elija una cripto y vea su recomendación detallada
    opciones_cripto = df['name'].tolist()
    cripto_seleccionada = st.selectbox("Selecciona una criptomoneda para ver la recomendación:", opciones_cripto)

    # Extraer datos de la moneda seleccionada
    datos_cripto = df[df['name'] == cripto_seleccionada].iloc[0]
    variacion = datos_cripto['price_change_percentage_24h']
    precio_actual = datos_cripto['current_price']

    # Lógica algorítmica para la recomendación
    if variacion < -3.0:
        status_color = "🟢 Oportunidad de Compra (Buy)"
        detalles = f"El precio ha caído un {variacion:.2f}% en las últimas 24h. Podría estar en zona de sobreventa, ideal para acumular a precios más bajos."
        tipo_alerta = st.success
    elif variacion > 3.0:
        status_color = "🔴 Alerta de Toma de Ganancias (Sell / Overbought)"
        detalles = f"El precio ha subido un {variacion:.2f}% en las últimas 24h. Podría experimentar una corrección pronto; evalúa proteger tus ganancias."
        tipo_alerta = st.warning
    else:
        status_color = "🟡 Condición de Mercado Estable (Hold)"
        detalles = f"La variación es leve ({variacion:.2f}%). El mercado está en consolidación lateral. Se recomienda mantener posiciones existentes."
        tipo_alerta = st.info

    # Mostrar la recomendación de forma visual en la web
    col_rec1, col_rec2 = st.columns([1, 2])
    
    with col_rec1:
        st.metric(label=f"Estado de {cripto_seleccionada}", value=status_color)
    
    with col_rec2:
        tipo_alerta(f"**Análisis:** {detalles}")
        
    # --- NUEVA SECCIÓN: CONSULTORÍA INTEGRADA CON IA ---
    st.write("---")
    st.markdown("## 🧠 Consultor Financiero de IA en Tiempo Real")
    st.markdown("Al hacer clic en el botón, una Inteligencia Artificial analizará los datos actuales del mercado para generar un reporte ejecutivo instantáneo.")

    # Importamos la librería de Google e iniciamos el cliente usando la API Key del archivo .env

    # Inicializamos el cliente de IA leyendo la clave del entorno

    if st.button("🤖 Generar Reporte con IA"):
        # 1. Construimos el resumen de datos que le pasaremos a la IA
        resumen_mercado = ""
        for index, row in df.iterrows():
            resumen_mercado += f"- {row['name']} ({row['symbol'].upper()}): Precio ${row['current_price']:,}, Variación 24h: {row['price_change_percentage_24h']:.2f}%\n"

        # 2. Diseñamos el prompt interno que el usuario no ve, pero que guía a la IA
        prompt_interno = f"""
        Actúa como un Analista Financiero Senior experto en Criptoactivos. Requiero un informe ejecutivo basado en los siguientes datos del mercado en tiempo real extraídos de la API de CoinGecko:

        {resumen_mercado}

        Por favor, proporcióname un análisis detallado en español que incluya:
        1. Resumen del sentimiento del mercado general (¿Es alcista, bajista o neutral?).
        2. Identificación de las 2 monedas con mayor riesgo y las 2 con mayor oportunidad en el corto plazo según sus variaciones.
        3. Una recomendación estratégica breve para un perfil de inversión moderado.

        Usa formato Markdown con negritas y listas para que el reporte se vea muy ordenado y estético en la aplicación web.
        """

        # 3. Llamamos al modelo de IA mediante un spinner de carga
        with st.spinner("La IA está analizando los gráficos y datos de CoinGecko..."):
            try:
                # Usamos el modelo optimizado y rápido 'gemini-2.5-flash'
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_interno,
                )
                
                # 4. Desplegamos el resultado de la IA directamente en la web
                st.success("¡Reporte generado con éxito!")
                st.markdown("### 📋 Informe Ejecutivo de la IA")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Hubo un error al conectar con la IA: {e}")
        
else:
    st.error("No se pudieron cargar los datos de la API o el DataFrame está vacío. Verifica tu API Key o los límites de la demo en coingecko_api.py.")
    
    
