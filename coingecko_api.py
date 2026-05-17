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

def obtener_top_criptos(vs_currency="usd", per_page=10):
    """
    Obtiene las principales criptomonedas por capitalización de mercado
    y las devuelve en un DataFrame de Pandas.
    """
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false"
    }
    
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
