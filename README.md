# Projetos 1.1 e 1.2: Ingestão de Dados com dlt, MinIO e Apache Airflow

## Visão Geral

Este primeiro projeto reúne dois subprojetos complementares de Engenharia de Dados.

* **Projeto 1.1**: implementação manual de uma pipeline de ingestão com `dlt` e `MinIO`.
* **Projeto 1.2**: evolução do Projeto 1.1 com orquestração automática usando `Apache Airflow`.

Ambos os projetos consomem dados da **FreeCurrency API**, que fornece cotações de moedas, e armazenam os resultados em formato **Parquet** em um bucket no **MinIO**.

---

## Objetivo 

Os dois projetos foram construídos para demonstrar a evolução natural de uma pipeline de dados:

1. Fazer requisições para uma API.
2. Transformar a resposta em registros estruturados.
3. Salvar os dados em um Data Lake.
4. Automatizar execuções periódicas.
5. Monitorar logs, status e métricas.

---

# Projeto 1.1: Pipeline com dlt e MinIO

## Objetivo

Criar uma pipeline funcional de ingestão usando apenas Python e `dlt`, gravando os dados em um bucket MinIO.

## Fluxo

```text
FreeCurrency API
      ↓
source/resource (dlt)
      ↓
pipeline.run()
      ↓
MinIO (Parquet)
```

## Principais Componentes

### `script01.py`

Fazemos um requisição HTTP e recebemos um json do resultado que é impresso no terminal, maneira mais simples de receber os dados.

### `script02.py`

Implementa um pipeline de dados usando a biblioteca dlt.

Define:

* `@dlt.resource`: função que extrai os dados da API.
* `@dlt.source`: agrupamento do resource.
* Salvamento local em uma pasta chamada data.

### `script03.py`

Implementa um pipeline de dados usando a biblioteca dlt e boto3.

Define:

* `@dlt.resource`: função que extrai os dados da API.
* `@dlt.source`: agrupamento do resource.
* Salvamento em um bucket no MinIO.

### Pipeline

Configura:

* `pipeline_name`
* `destination`
* `dataset_name`

### MinIO

Armazena os arquivos Parquet gerados.

### `read_parquet.py`

Script auxiliar que usa `boto3` e `pyarrow` para ler os arquivos gravados no MinIO.

---

## Estrutura Conceitual do dlt

### Resource

Representa uma tabela de dados.

Exemplo:

* `latest_rates`

### Source

Agrupa um ou mais resources.

Exemplo:

* `freecurrency_source`

### Pipeline

Executa o source e grava os dados no destino.

---

## Saída no MinIO

```text
currency-raw/
└── latest/
    ├── _dlt_loads/
    ├── _dlt_pipeline_state/
    ├── _dlt_version/
    └── latest_rates/
        └── *.parquet
```

### Pastas internas

* `_dlt_loads`: histórico de execuções.
* `_dlt_pipeline_state`: estado interno do pipeline.
* `_dlt_version`: schema e versões.
* `latest_rates`: dados reais.

---

## Aprendizados do Projeto 1.1

* Uso de APIs com `requests`.
* Uso de variáveis de ambiente.
* Criação de resources e sources no dlt.
* Escrita de arquivos Parquet.
* Uso do MinIO como Data Lake local.
* Leitura de Parquet com `boto3`.

---

# Projeto 1.2: Pipeline Orquestrada com Apache Airflow

## Objetivo

Automatizar a pipeline do Projeto 1 utilizando Apache Airflow.

## Fluxo

```text
Airflow Scheduler
      ↓
DAG
      ↓
Task
      ↓
run_pipeline()
      ↓
FreeCurrency API
      ↓
MinIO (Parquet)
```

---

## Principais Componentes

### `ingestion/source.py`

Responsável por extrair os dados da API.

### `ingestion/pipeline.py`

Constrói e executa a pipeline dlt.

### `dags/currency_ingestion_dag.py`

Define:

* cron schedule;
* retries;
* task principal;
* logs.

### `Dockerfile`

Cria uma imagem customizada do Airflow com todas as dependências.

### `docker-compose.yml`

Sobe todos os serviços necessários.

---

## Serviços do Docker Compose

### PostgreSQL

Banco de metadados do Airflow.

### MinIO

Armazenamento de objetos.

### MinIO Init

Cria automaticamente o bucket `currency-raw`.

### Airflow Init

Inicializa o banco e cria o usuário `admin/admin`.

### Airflow Scheduler

Dispara as DAGs nos horários programados.

### Airflow Webserver

Interface gráfica do Airflow.

---

## DAG

A DAG define que a pipeline deve executar:

* a cada hora;
* no minuto 0;
* com até 3 tentativas em caso de falha.

### Schedule

```python
schedule = "0 * * * *"
```

---

## Interface do Airflow

Na UI é possível:

* ativar/desativar DAGs;
* disparar execuções manuais;
* acompanhar logs;
* verificar status;
* visualizar métricas.

### Estados das Tasks

* Verde: sucesso.
* Vermelho: falha.
* Azul: executando.
* Cinza: sem execução.

---

## Aprendizados do Projeto 1.2

* Conceito de DAG.
* Conceito de Task.
* Agendamento automático.
* Retries.
* Monitoramento via UI.
* Orquestração de pipelines.
* Docker Compose com múltiplos serviços.

---

# Diferença entre Projeto 1.1 e Projeto 1.2

| Aspecto       | Projeto 1.1     | Projeto 1.2   |
| ------------- | --------------- | ------------- |
| Execução      | Manual          | Automática    |
| Orquestração  | Não             | Sim (Airflow) |
| Monitoramento | Terminal        | Interface Web |
| Retry         | Manual          | Automático    |
| Scheduler     | Não             | Sim           |
| PostgreSQL    | Não             | Sim           |
| Dockerfile    | Não obrigatório | Sim           |

---

# Tecnologias Utilizadas

* Python
* requests
* dlt
* MinIO
* boto3
* pyarrow
* Apache Airflow
* PostgreSQL
* Docker
* Docker Compose
* uv

---

# S3, MinIO e boto3

## S3

Protocolo/API de armazenamento de objetos.

## MinIO

Servidor local compatível com S3.

## boto3

SDK Python para acessar servidores S3.

---

# Fluxo Evolutivo do Aprendizado

```text
requests → dlt resource → dlt source → pipeline → MinIO → boto3 → Docker → Airflow → DAGs
```

---

# Conclusão

Os dois projetos representam uma jornada rica de aprendizados em Engenharia de Dados.

* O **Projeto 1.1** ensina a construir uma pipeline de ingestão e armazenamento.
* O **Projeto 1.2** ensina a automatizar, monitorar e operacionalizar essa pipeline.

Ao final, compreendemos desde a coleta de dados via API até a execução automática e monitorada em um ambiente semelhante ao utilizado em produção por empresas.

