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
    Inyecta un User-Agent corporativo para evitar bloqueos de seguridad (Cloudflare/WAF)
    cuando el script se ejecuta desde la infraestructura de Streamlit Cloud.
    """
    import requests
    import os
    
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    
    # SOLUCIÓN: Simular una petición desde un navegador web real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        import streamlit as st
        api_key_news = st.secrets.get("CRYPTOCOMPARE_API_KEY") or os.getenv("CRYPTOCOMPARE_API_KEY")
        if api_key_news:
            headers["authorization"] = f"Apikey {api_key_news}"
    except Exception:
        pass

    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json().get('Data', [])
            
        # Si devuelve otra cosa (401, 403), lo metemos como una noticia falsa para leer el código de error
        return
