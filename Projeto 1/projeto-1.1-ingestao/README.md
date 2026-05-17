# Projeto 1.1: Ingestão de Dados com dlt, MinIO e Parquet

Este primeiro projeto demonstra um pipeline completo de ingestão de dados utilizando:

- Python
- dlt (Data Load Tool)
- MinIO (Data Lake local compatível com S3)
- Docker Compose
- Parquet
- boto3
- PyArrow
- Pandas

O objetivo é extrair taxas de câmbio da API FreeCurrencyAPI, armazená-las em um Data Lake local e, posteriormente, ler os arquivos Parquet gerados.

---

# Visão Geral da Arquitetura

```text
FreeCurrencyAPI
      ↓
dlt Resource
      ↓
dlt Source
      ↓
dlt Pipeline
      ↓
MinIO (S3-compatible Data Lake)
      ↓
Arquivos Parquet
      ↓
read_parquet.py
      ↓
Pandas DataFrame
```

---

# Objetivo do Projeto

O projeto foi construído para demonstrar o fluxo completo de um pipeline de engenharia de dados:

1. Extrair dados de uma API REST.
2. Estruturar os dados com `dlt`.
3. Armazenar os dados em formato Parquet.
4. Utilizar um Data Lake local com MinIO.
5. Ler os arquivos gravados para análise.

---

# O que é o dlt?

dlt (Data Load Tool) é uma biblioteca Python da plataforma DLT Hub que automatiza a criação de pipelines de ingestão de dados.

Ele cuida de:

- Extração
- Normalização
- Escrita em diferentes destinos
- Gerenciamento de schema
- Controle de estado da pipeline

---

Podemos instalar ele com:

```bash
uv add dlt
```


# Três Conceitos Fundamentais do dlt

## Resource

Define como os dados são gerados.

Exemplo: uma API, banco de dados ou arquivo.

## Source

Agrupa um ou mais resources.

## Pipeline

Executa e salva os dados no destino escolhido.

---

# Analogia

| Conceito | Analogia |
|--------|--------|
| Resource | Máquina que produz dados |
| Source | Conjunto de máquinas |
| Pipeline | Sistema logístico que transporta e armazena |

---

# Estrutura do Projeto

```text
projeto-01-ingestao/
├── .venv/
├── data/
│   └── latest/
│       ├── _dlt_loads/
│       ├── _dlt_pipeline_state/
│       ├── _dlt_version/
│       ├── latest_rates/
│       └── init
├── minio/
├── .env
├── .gitignore
├── .python-version
├── docker-compose.yaml
├── pyproject.toml
├── README.md
├── read_parquet.py
├── script01.py
├── script02.py
├── script03.py
└── uv.lock
```

---

# Explicação das Pastas e Arquivos

## `.venv/`

Ambiente virtual Python com todas as dependências instaladas.

## `data/`

Diretório gerado pelo `script02.py`, quando o destino é o filesystem local.

## `data/latest/`

Dataset criado pelo dlt.

## `minio/`

Pasta para arquivos auxiliares relacionados ao MinIO.

## `.env`

Arquivo com variáveis de ambiente.

## `docker-compose.yaml`

Arquivo que define e sobe o MinIO via Docker.

## `pyproject.toml`

Configuração do projeto Python e dependências.

## `uv.lock`

Arquivo de lock das dependências.

## `script01.py`

Versão inicial do pipeline, apenas mostra as taxas de câmbio no terminal, sem salvar nada.

## `script02.py`

Salva os dados localmente em `data/`.

## `script03.py`

Salva os dados em um bucket no MinIO.

## `read_parquet.py`

Lê os arquivos Parquet gravados no MinIO.

---

# Estrutura Gerada pelo dlt

```text
data/latest/
├── _dlt_loads/
├── _dlt_pipeline_state/
├── _dlt_version/
├── latest_rates/
└── init
```

---

# `_dlt_loads/`

Armazena metadados de cada execução da pipeline.

Cada arquivo representa um load.

---

# `_dlt_pipeline_state/`

Guarda o estado interno da pipeline.

Usado para cargas incrementais e retomadas.

---

# `_dlt_version/`

Armazena o schema das tabelas.

Permite versionamento estrutural.

---

# `latest_rates/`

Tabela principal.

Contém os arquivos Parquet ou JSONL com os dados.

---

# `init`

Arquivo marcador criado pelo dlt ao inicializar o dataset.

---

# Script 02 — Salvando Localmente

```python
destination = filesystem(bucket_url="data")
```

Os arquivos são salvos no disco local.

---

# Script 03 — Salvando no MinIO

```python
destination = filesystem(
    bucket_url="s3://latest",
    credentials={...}
)
```

Os arquivos são enviados para o bucket `latest`.

---

# O que é MinIO?

MinIO é um servidor de object storage compatível com Amazon S3.

Ele permite criar um Data Lake local.

---

# Docker Compose

Para iniciar o MinIO:

```bash
docker compose up -d
```

Para acessar a interface:

```text
http://localhost:9001
```

---

# Relação entre `docker-compose.yaml` e `script03.py`

| Arquivo | Função |
|------|------|
| `docker-compose.yaml` | Cria e executa o servidor MinIO |
| `script03.py` | Envia os dados para o MinIO |

---

# Portas do MinIO

| Porta | Função |
|------:|------|
| 9000 | API S3 |
| 9001 | Interface Web |

---

# Resource: `latest_rates()`

Função responsável por consultar a API e produzir registros.

```python
@dlt.resource(name="latest_rates", write_disposition="append")
def latest_rates(...):
    ...
    yield {...}
```

---

# Por que `yield`?

`yield` devolve um registro por vez.

Isso permite:

- streaming
- menor consumo de memória
- processamento incremental

---

# Source: `freecurrency_source()`

Agrupa o resource.

```python
@dlt.source(name="freecurrency")
def freecurrency_source(...):
    return latest_rates(...)
```

---

# Por que usar `source`?

Mesmo com apenas um resource, o source:

- organiza o pipeline
- facilita expansão futura
- padroniza a arquitetura

---

# Pipeline

```python
pipeline = dlt.pipeline(
    pipeline_name="freecurrency_pipeline",
    destination=destination,
    dataset_name="latest",
)
```

Define:

- nome da pipeline
- destino
- dataset

---

# Execução da Pipeline

```python
load_info = pipeline.run(
    freecurrency_source(api_key=api_key),
    loader_file_format="parquet",
)
```

---

# `write_disposition="append"`

Sempre adiciona novos dados.

Outras opções:

- `replace`
- `merge`

---

# `loader_file_format="parquet"`

Força a escrita em Parquet.

---

# O que é Parquet?

Formato colunar altamente eficiente para analytics.

Vantagens:

- compacto
- rápido
- amplamente utilizado

---

# O que é boto3?

boto3 é o SDK da AWS para Python.

Como o MinIO é compatível com S3, o boto3 pode ser usado para:

- listar arquivos
- baixar objetos
- enviar objetos

---

# O que é PyArrow?

Biblioteca usada para manipular formatos como Parquet.

---

# O que é Pandas?

Biblioteca para análise de dados em DataFrames.

---

# `read_parquet.py`

Esse script:

1. Conecta ao MinIO.
2. Lista arquivos `.parquet`.
3. Baixa os arquivos.
4. Lê com PyArrow.
5. Concatena as tabelas.
6. Converte para Pandas.
7. Exibe os dados.

---

# Fluxo do `read_parquet.py`

```text
MinIO
  ↓
boto3
  ↓
BytesIO
  ↓
PyArrow
  ↓
Pandas
  ↓
print()
```

---

# Sequência de Execução do Projeto

## 1. Instalar dependências

```bash
uv sync
```

## 2. Subir o MinIO

```bash
docker compose up -d
```

## 3. Executar a pipeline

```bash
uv run python script03.py
```

## 4. Ler os dados

```bash
uv run python read_parquet.py
```


# Dependências Principais

```bash
uv add "dlt[s3,parquet]"
uv add boto3 pyarrow pandas python-dotenv requests
```


# Resumo

Este projeto implementa um pipeline moderno de engenharia de dados que:

1. Extrai dados de uma API.
2. Estrutura os dados com dlt.
3. Salva em formato Parquet.
4. Armazena em um Data Lake local com MinIO.
5. Lê os arquivos com boto3, PyArrow e Pandas.

Esse fluxo reproduz, em escala local, a arquitetura utilizada em projetos reais de engenharia de dados.

