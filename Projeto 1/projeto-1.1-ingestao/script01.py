import requests
import os
from dotenv import load_dotenv


load_dotenv() #pede pro python ir no .env e colocar as variáveis na memória, elas só vão existir quando o programa está rodando, em servidores em produção não usamos o load_env pois o próprio SO já entrega as variáveis prontas.
response = requests.get(
    "https://api.freecurrencyapi.com/v1/latest",
    params={
        "apikey": os.getenv("API_KEY"),
        "base_currency": "BRL",
        "currencies": "EUR,USD,JPY",
    }
)

print(response.status_code)   # 200
print(response.json())