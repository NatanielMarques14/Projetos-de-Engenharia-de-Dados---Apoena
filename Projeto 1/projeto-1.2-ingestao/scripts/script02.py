from datetime import datetime, timezone
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
data = response.json().get("data", {})
extracted_at = datetime.now(timezone.utc).isoformat()

registros = []
for target_currency, rate in data.items():
    registros.append({
        "base_currency": "BRL",
        "target_currency": target_currency,
        "rate": rate,
        "extracted_at": extracted_at,
    })

for r in registros:
    print(r)