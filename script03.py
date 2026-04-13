import os
import sys
from pathlib import Path

# Garante que a raiz do projeto onde está o pacote ingestion/ está no path, independente de ond eo script é executado

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dlt # o dlt sabe como buscar, processar e salvar dados, sem ele teríamos que fazer essas coisas manualmente
from datetime import datetime, timezone # precisamos de um carimbo de data nos dados, saber quando foi coletado é crítico
import requests # para fazer chamadas para APIs, sem ela não teríamos dados externos
from typing import Iterator # esteira dos dados
from dotenv import load_dotenv # carrega as variáveis do arquivo .env
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

# Esse bloco só roda se você executar o arquivo diretamente, tudo acima dele é o mesmo que tem no script02.py 
# (e não quando ele é importado em outro arquivo)
if __name__ == "__main__":

    # ==============================
    # 1. CARREGAR VARIÁVEIS DO .ENV
    # ==============================

    # Isso carrega variáveis de ambiente (tipo senha, endpoint, etc)
    # Analogia:
    # É como pegar um papel com configurações secretas guardadas
    load_dotenv()


    # ==============================
    # 2. DEFINIR O ENDPOINT DO MINIO
    # ==============================

    # Aqui ele tenta pegar o endpoint do MinIO do .env
    # Se não existir, usa "http://localhost:9000"
    endpoint_url = os.environ.get(
        "MINIO_ENDPOINT_URL",
        "http://localhost:9000"
    )

    # IMPORTANTE:
    # Se estiver rodando DENTRO do Docker, "localhost" não funciona
    # então ele troca "http://minio:" por "http://localhost:"
    endpoint_url = endpoint_url.replace(
        "http://minio:",
        "http://localhost:"
    )


    # ==============================
    # 3. DEFINIR O DESTINO (ONDE SALVAR OS DADOS)
    # ==============================

    destination = filesystem(
        # bucket_url é tipo o "caminho" do armazenamento
        # "s3://latest" → significa: usar padrão S3 (MinIO imita isso)
        bucket_url=os.environ.get("MINIO_BUCKET_URL", "s3://latest"),

        # credenciais para acessar o MinIO
        credentials={
            "aws_access_key_id": os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
            "aws_secret_access_key": os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
            "endpoint_url": endpoint_url,
        },
    )


    # ==============================
    # 4. CRIAR PIPELINE
    # ==============================

    pipeline = dlt.pipeline(
        pipeline_name="freecurrency_pipeline",  # nome da pipeline
        destination=destination,                # onde salvar os dados
        dataset_name="latest",                  # "pasta" dentro do bucket
    )


    # ==============================
    # 5. PEGAR API KEY
    # ==============================

    # Aqui pega a chave da API de moedas
    api_key = os.environ["API_KEY"]


    # ==============================
    # 6. RODAR PIPELINE
    # ==============================

    # freecurrency_source → função que busca dados da API
    load_info = pipeline.run(
        freecurrency_source(api_key=api_key), loader_file_format="parquet" # sem esse loader lá no minio aparece como formato jsonl, mas aí tem que instalar o dlt[parquet]
    )

    # imprime o resultado (quantos dados foram carregados, etc)
    print(load_info)

    # temos que dar um uv add dlt[s3] pra rodar isso, nisso instalamos o botocore e lá no http 127.0.0.1:9001 dentro do bucket que criamos com o nome de latest, vai aparecer uma pasta com o mesmo nome (pode ser diferente) e nela tera o loads, pipeline stat, version, init, latest_rates ao inves da pasta quea apareceu no vscode. Agora está dentro de um datalake no minio, e não solto num diretório na minha máquina local (o minio também é na máquina local mas ele é semelhante ao datalake de numa empresa onde todos conseguem acessar )
    # toda ver que der run ele cria um novo arquivo, seja json ou parquet no latest_rates no minio
    # temos que ler esse parquet, por isso criamos um arquiv a parte