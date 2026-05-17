import dlt
import requests
from typing import Iterator

@dlt.resource(name="latest_rates", write_disposition="append")
def latest_rates(api_key: str, base_currency: str, currencies: str) -> Iterator[dict]:
    response = requests.get(
        "https://api.freecurrencyapi.com/v1/latest",
        params={"apikey": api_key, "base_currency": base_currency, "currencies": currencies},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json().get("data", {})

    # yield em vez de return — é um gerador
    # o dlt processa cada item conforme chegam, não espera tudo na memória
    for target_currency, rate in data.items():
        yield {
            "base_currency": base_currency,
            "target_currency": target_currency,
            "rate": rate,
        }