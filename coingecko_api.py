import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Cargar la API Key desde el archivo .env
load_dotenv()
API_KEY = os.getenv("COINGECKO_API_KEY")

# URL base para la API Demo de CoinGecko
BASE_URL = "https://api.coingecko.com/api/v3"

# Configurar los headers obligatorios para la API Key Demo
HEADERS = {
    "accept": "application/json",
    "x-cg-demo-api-key": API_KEY
}

def obtener_top_criptos():
    # ... código anterior de la función ...
    
    url = f"{BASE_URL}/coins/markets"
    
    # Modificación del parámetro de paginación
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,  # <-- Cambie este valor (ej: 20, 50, 100) para ampliar la lista
        "page": 1,
        "sparkline": "false"
    }
    
    # ... resto del código que ejecuta el requests.get() ...
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            datos = response.json()
            # Convertimos la respuesta JSON en un DataFrame de Pandas para manejarlo fácil
            df = pd.DataFrame(datos)
            # Nos quedamos solo con las columnas que nos interesan para la web
           # Se agrega 'id' para habilitar las consultas en las series de tiempo
            columnas_interesantes = ['id', 'name', 'symbol', 'current_price', 'market_cap', 'price_change_percentage_24h', 'image']
            return df[columnas_interesantes]
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# Prueba rápida para verificar que tu llave funciona
if __name__ == "__main__":
    print("Probando conexión con CoinGecko...")
    df_prueba = obtener_top_criptos()
    if df_prueba is not None:
        print("\n¡Conexión exitosa! Aquí están las primeras 3 criptos:")
        print(df_prueba.head(3))

def obtener_historico_activo(coin_id="bitcoin", days=30):
    """
    Consume el endpoint de rango histórico de CoinGecko.
    Retorna un DataFrame estructurado con las variables Fecha y Precio.
    """
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            precios = response.json().get('prices', [])
            # Conversión de la lista de matrices a un DataFrame de Pandas
            df_hist = pd.DataFrame(precios, columns=['Fecha', 'Precio'])
            # Transformación del timestamp Unix (milisegundos) a formato DateTime estándar
            df_hist['Fecha'] = pd.to_datetime(df_hist['Fecha'], unit='ms')
            return df_hist
        else:
            print(f"Error en API Historica {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexion en modulo historico: {e}")
        return None

def obtener_noticias_mercado():
    """
    Consume el endpoint analítico de CryptoCompare para el feed de prensa.
    Requiere obligatoriamente autenticación por API Key mediante cabeceras HTTP
    para garantizar la tasa de transferencia en producción.
    """
    import requests
    import os
    import streamlit as st
    
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    
    # Extracción de la credencial desde el entorno seguro
    api_key_news = st.secrets.get("CRYPTOCOMPARE_API_KEY") or os.getenv("CRYPTOCOMPARE_API_KEY")
    
    if not api_key_news:
        print("Error: No se ha detectado la API Key de CryptoCompare en los Secrets.")
        return []
        
    # Configuración de cabeceras de seguridad y agente de usuario
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "authorization": f"Apikey {api_key_news}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json().get('Data', [])
            
        print(f"Error de API de noticias: Código {response.status_code}")
        return []
    except Exception as e:
        print(f"Excepción en el módulo de prensa: {e}")
        return []


# PESTAÑA D: SIMULADOR DE PORTAFOLIO CORPORATIVO
        with tab_simulador:
            st.subheader("Simulador de Inversiones y Retorno de Inversión (ROI)")
            st.markdown("Módulo operativo para la gestión de activos y diversificación patrimonial en tiempo real.")
            st.write("---")
            
            # Mapeos de diccionarios analíticos para consultas rápidas
            precios_dict = dict(zip(df['name'], df['current_price']))
            simbolos_dict = dict(zip(df['name'], df['symbol']))
            
            # 1. INTERFAZ DE TRANSACCIONES (Órdenes de Compra/Venta)
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
                        st.error("Error: La cantidad transaccionada debe ser estrictamente mayor a cero.")
                    else:
                        st.session_state["saldo_cash"] -= costo_total
                        st.session_state["billetera"][crypto_tx] = st.session_state["billetera"].get(crypto_tx, 0.0) + cantidad_tx
                        st.success(f"Orden Ejecutada: Compra de {cantidad_tx} {simbolos_dict[crypto_tx].upper()} por un valor de ${costo_total:,.2f} USD.")
                        st.rerun()
                        
                elif accion_tx == "Vender":
                    cantidad_poseida = st.session_state["billetera"].get(crypto_tx, 0.0)
                    if cantidad_tx > cantidad_poseida:
                        st.error("Transacción Rechazada: Cantidad de activos en cartera insuficiente para cubrir la orden.")
                    elif cantidad_tx <= 0:
                        st.error("Error: La cantidad transaccionada debe ser estrictamente mayor a cero.")
                    else:
                        st.session_state["saldo_cash"] += costo_total
                        st.session_state["billetera"][crypto_tx] = cantidad_poseida - cantidad_tx
                        if st.session_state["billetera"][crypto_tx] <= 0:
                            del st.session_state["billetera"][crypto_tx]
                        st.success(f"Orden Ejecutada: Venta de {cantidad_tx} {simbolos_dict[crypto_tx].upper()} por un valor de ${costo_total:,.2f} USD.")
                        st.rerun()

            # 2. VALORACIÓN COMPLEMENTARIA DE LA CARTERA
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
            
            # Despliegue de Indicadores de Control Patrimonial (KPIs Financieros)
            st.write("---")
            st.markdown("#### Estado de Situación Patrimonial")
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            
            with col_kpi1:
                st.metric(label="Capital Disponible (Efectivo)", value=f"${st.session_state['saldo_cash']:,.2f} USD")
            with col_kpi2:
                st.metric(label="Valorización Total de Criptoactivos", value=f"${valor_criptos_total:,.2f} USD")
            with col_kpi3:
                st.metric(label="Patrimonio Neto Total", value=f"${patrimonio_neto_total:,.2f} USD", delta=f"{roi_acumulado:.2f}% ROI")
                
            # 3. VISUALIZACIÓN MATRICIAL Y GRÁFICA DE RIESGO
            if filas_portafolio:
                df_port = pd.DataFrame(filas_portafolio)
                col_tab, col_pie = st.columns([0.55, 0.45])
                
                with col_tab:
                    st.markdown("##### Desglose de Posiciones de Inversión Abiertas")
                    # Formatear la visualización del valor en la tabla
                    df_mostrar = df_port.copy()
                    df_mostrar["Valorización (USD)"] = df_mostrar["Valorización (USD)"].map(lambda x: f"${x:,.2f}")
                    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                    
                with col_pie:
                    st.markdown("##### Matriz Distribución de Activos (Exposición al Riesgo)")
                    # Incorporación del Efectivo para cuadrar la torta total del capital
                    fila_cash = pd.DataFrame([{"Activo": "Efectivo (Cash)", "Unidades": 1.0, "Precio de Mercado (USD)": "N/A", "Valorización (USD)": st.session_state["saldo_cash"]}])
                    df_pie = pd.concat([df_port, fila_cash], ignore_index=True)
                    
                    fig_pie = px.pie(
                        df_pie, 
                        values='Valorización (USD)', 
                        names='Activo', 
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.sequential.YlGnBu_r
                    )
                    fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("La cartera de inversión se encuentra actualmente vacía. Utilice el panel superior para generar órdenes de compra.")
