import dlt # o dlt sabe como buscar, processar e salvar dados, sem ele teríamos que fazer essas coisas manualmente
from datetime import datetime, timezone # precisamos de um carimbo de data nos dados, saber quando foi coletado é crítico
import requests # para fazer chamadas para APIs, sem ela não teríamos dados externos
from typing import Iterator # esteira dos dados
from dotenv import load_dotenv # carrega as variáveis do arquivo .env
import os # acessa as coisas guardadas no sistema operacional
from dlt.sources import DltResource # é um tipo especial de dado que o dlt entende, é um recurso de dados
from dlt.destinations import filesystem # para salvar dados em arquivos e escolher onde guardar

BASE_URL = "https://api.freecurrencyapi.com/v1"
DEFAULT_CURRENCIES = "EUR,GBP,JPY,USD"
# no DLThub temos 3 importantes coisas, o RESOURCE (cada API, BD, Arquivos minha representa um resource ), SOURCE (conjunto de resources, a source é como um cardapio e a resources é como os itens nesse cardapio) e PIPELINE (quando especifico a origem e destino)

#resource é a máquina que produz os dados, source é o conjunto dessas máquinas, pipeline é o sistema que pega e armazena

# esse decorador turbina a função abaixo dele mudando o nome visto dela no pipeline pelo parâmetro name= e fazendo com que a disposição dos dados seja em append, fazendo com que ela seja uma função do tipo resource, em projetos pequenos a gente não precisa mudar o nome visto na pipeline
@dlt.resource(name="latest_rates", write_disposition="append") #sempre adiciona novos dados mas não apaga os antigos, poderiamos ainda ter replace e merge ao inves do append
def latest_rates(api_key: str, base_currency: str, currencies: str) -> Iterator[dict]: # recebe essas 3 coisas e retorna um dicionário iterado (um de cada vez, ao inves de uma lista que entregaria tudo), basicamente essa função vai na API pega os dados e devolve dados
    response = requests.get( # quem, o que, quantos
        f"{BASE_URL}/latest",
        params={"apikey": api_key, "base_currency": base_currency, "currencies": currencies},
        timeout=30, # demorou mais de 30 s, cancela
    )
    response.raise_for_status() # se der erro, exiba ele logo aqui

    data = response.json().get("data", {}) # transforma a resposta em dicionário e pega a parte "data", se não existir, usa um dicionário vazio {}
    extracted_at = datetime.now(timezone.utc).isoformat() # marca o horário da coleta

    # yield em vez de return — é um gerador
    # o dlt processa cada item conforme chegam, não espera tudo na memória
    for target_currency, rate in data.items(): # para cada moeda, entrega um registro de dados, target e rate são criadas para identificar as colunas do data, que tem o nome da moeda e a taxa 
        yield {
            "base_currency": base_currency,
            "target_currency": target_currency,
            "rate": rate,
        }

# source pode ter mais parametros, mas pra gente, name= já basta
@dlt.source(name="freecurrency") # isso é um conjunto de dados chamados freecurrency
def freecurrency_source(
    api_key: str = dlt.secrets.value,   # ← lê de SOURCES__FREECURRENCY__API_KEY, pega a API key de forma segura, lê de variaveis do ambiente e configs do dlt
    base_currency: str = "BRL",
    currencies: str = DEFAULT_CURRENCIES,
) -> DltResource:
    return latest_rates(api_key=api_key, base_currency=base_currency, currencies=currencies) # ele encaminha o resource

if __name__ == "__main__": # só roda se esse arquivo for executado diretamente
    load_dotenv()
    api_key = os.environ["API_KEY"] # pega a variável 
    destination = filesystem(bucket_url="data") # salva os dados numa pasta chamda data

    pipeline_local = dlt.pipeline( # cria a pipeline
        pipeline_name="freecurrency_pipeline",
        destination=destination,
        dataset_name="latest", # nome do conjunto de dados
    )
    load_info = pipeline_local.run(freecurrency_source(api_key=api_key))
    print(load_info)

    #RESOURCE : define como os dados são gerados e salvos (append, replace, merge) e uma tabela de dados
    #SOURCE: define o agrupamento, a organização e um grupo de tabelas
    #PIPELINE: executa e salva tudo 