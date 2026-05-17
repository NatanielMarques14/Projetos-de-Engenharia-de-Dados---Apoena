import requests
import os
from dotenv import load_dotenv

load_dotenv()

response = requests.get(
    "https://api.freecurrencyapi.com/v1/latest",
    params={
        "apikey": os.getenv("API_KEY"),
        "base_currency": "BRL",
        "currencies": "EUR,USD,JPY",
    }
)
# Sem tratamento — se der 401, o código trava com um KeyError no .json()
data = response.json()["data"]   # ERRO se a API retornou {"message": "Invalid API key"}

# Com tratamento correto
response = requests.get(url, params=params, timeout=30)
response.raise_for_status()   # lança HTTPError se status != 2xx

data = response.json().get("data", {})