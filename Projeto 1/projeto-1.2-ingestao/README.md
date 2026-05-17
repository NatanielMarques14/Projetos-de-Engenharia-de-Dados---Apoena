# Projeto 1.2: Ingestão de Dados com Apache Airflow, dlt e MinIO

## Visão Geral

Este projeto implementa uma pipeline de ingestão de dados que:

1. Consulta a API da FreeCurrency API.
2. Extrai cotações de moedas em relação ao BRL.
3. Salva os dados em formato Parquet no MinIO.
4. Agenda a execução automaticamente com Apache Airflow.

### Fluxo Geral

```text
FreeCurrency API
       ↓
ingestion/source.py
       ↓
ingestion/pipeline.py
       ↓
MinIO (bucket currency-raw)
       ↓
dags/currency_ingestion_dag.py
       ↓
Apache Airflow Scheduler
```

---

# Tecnologias Utilizadas

- Python 3.11
- dlt
- Apache Airflow
- MinIO
- PostgreSQL
- Docker Compose
- Docker
- uv
- pyarrow
- boto3
- requests
- python-dotenv

---

# Conceitos Fundamentais

## Resource (dlt)

Um `resource` representa uma fonte individual de dados.

Exemplo:

- endpoint `/latest` da FreeCurrency API.

## Source (dlt)

Um `source` agrupa um ou mais resources.

## Pipeline (dlt)

Executa o source e grava os dados no destino.

## Destination (dlt)

Define para onde os dados serão gravados.

Neste projeto:

- MinIO (compatível com S3).

## DAG (Airflow)

Define:

- quando executar;
- quais tarefas executar;
- políticas de retry;
- dependências.

## Task (Airflow)

Uma etapa individual dentro da DAG.

---

# Estrutura do Projeto

```text
projeto-02-airflow/
├── dags/
│   └── currency_ingestion_dag.py
│
├── ingestion/
│   ├── __init__.py
│   ├── source.py
│   └── pipeline.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env
└── README.md
```

---

# source.py

Responsável por extrair os dados da API.

## freecurrency_source()

Define um source dlt chamado `freecurrency`.

## latest_rates()

Resource que:

1. Faz requisição HTTP para a API.
2. Obtém o JSON.
3. Cria um registro por moeda.
4. Usa `yield` para entregar os dados ao dlt.

### Exemplo de registro produzido

```python
{
    "base_currency": "BRL",
    "target_currency": "USD",
    "rate": 0.18,
    "extracted_at": "2026-05-16T23:00:00+00:00"
}
```

---

# pipeline.py

Responsável por configurar e executar a pipeline.

## build_pipeline()

1. Lê variáveis de ambiente.
2. Cria o destination `filesystem`.
3. Configura o MinIO.
4. Cria e retorna o objeto `dlt.pipeline`.

## run_pipeline()

1. Chama `build_pipeline()`.
2. Cria o source.
3. Executa `pipeline.run()`.
4. Retorna métricas.

### Exemplo de retorno

```python
{
    "pipeline_name": "freecurrency_pipeline",
    "load_id": "1775949383.3064804",
    "rows_loaded": 7
}
```

---

# DAG do Airflow

Arquivo:

```text
dags/currency_ingestion_dag.py
```

## Propósito

Agendar a execução automática da pipeline.

## Schedule

```python
schedule="0 * * * *"
```

Executa:

- toda hora;
- no minuto 0.

## Task principal

```python
run_dlt_pipeline()
```

Ela executa:

```python
from ingestion.pipeline import run_pipeline
result = run_pipeline()
```

---

# DAG x Pipeline

## Pipeline

Contém a lógica de ingestão.

## DAG

Define quando e como a pipeline será executada.

---

# Dockerfile

Define a imagem customizada usada pelos containers do Airflow.

## Etapas

1. Usa a imagem oficial do Airflow.
2. Instala o `uv`.
3. Copia `pyproject.toml` e `uv.lock`.
4. Instala dependências.

---

# O que é uma Imagem Docker?

Uma imagem Docker é como um "snapshot" de um ambiente pronto.

Ela contém:

- sistema operacional;
- Python;
- Airflow;
- bibliotecas;
- configurações.

---

# docker-compose.yml

Orquestra todos os containers do projeto.

---

# Containers do Projeto

## postgres

Banco de metadados do Airflow.

Armazena:

- DAG Runs;
- Task Instances;
- logs;
- usuários;
- configurações.

## minio

Object storage compatível com S3.

Armazena:

- arquivos Parquet gerados pelo dlt.

## minio-init

Executa uma única vez para criar o bucket:

- `currency-raw`.

## airflow-init

Executa uma única vez para:

1. Inicializar o banco do Airflow.
2. Criar o usuário `admin/admin`.

## airflow-scheduler

Monitora as DAGs e cria execuções automaticamente.

## airflow-webserver

Interface gráfica do Airflow.

Acesso:

- http://localhost:8080

---

# MinIO

Object storage local compatível com S3.

## URLs

- API S3: http://localhost:9000
- Console Web: http://localhost:9001

---

# S3, MinIO e boto3

## S3

Protocolo/API de armazenamento de objetos criado pela Amazon.

## MinIO

Servidor local que implementa a API S3.

## boto3

Biblioteca Python que conversa com qualquer servidor S3-compatible.

---

# Destination do dlt

```python
destination = filesystem(
    bucket_url="s3://currency-raw",
    credentials={
        "aws_access_key_id": "...",
        "aws_secret_access_key": "...",
        "endpoint_url": "http://minio:9000",
    },
)
```

- `bucket_url`: onde salvar.
- `credentials`: como autenticar.
- `endpoint_url`: em qual servidor S3 conectar.

---

# Como Rodar o Projeto

## 1. Build da imagem

```bash
docker compose build
```

## 2. Subir containers

```bash
docker compose up -d
```

## 3. Verificar status

```bash
docker compose ps
```

## 4. Acessar Airflow

URL:

```text
http://localhost:8080
```

## 5. Acessar MinIO

URL:

```text
http://localhost:9001
```

---

# Interface do Airflow

## Toggle ON/OFF

- ON: scheduler cria execuções automáticas.
- OFF: scheduler para de criar novas execuções.

## Trigger DAG

Cria uma execução manual.

## Runs

Quantidade total de execuções da DAG.

## Last Run

Última execução criada.

## Next Run

Próxima execução automática prevista.

## Recent Tasks

Histórico das tasks.

---

# Significado das Bolinhas

- Cinza: sem execução.
- Azul: queued ou running.
- Verde: success.
- Vermelho: failed.

---

# Scheduled vs Manual

## scheduled

Criado automaticamente pelo scheduler.

## manual

Criado ao clicar em Trigger DAG.

---

# Auto Refresh

Atualiza a interface automaticamente.

Se estiver desligado, a página não reflete novas execuções até que você atualize manualmente.

---

# Catchup

```python
catchup=False
```

Não executa horários passados.

---

# Retry

```python
DEFAULT_ARGS = {
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}
```

Se falhar:

- tenta novamente até 3 vezes;
- espera 5 minutos entre tentativas.

---

# Lixeira

Remove o histórico da DAG no Airflow.

Não remove os arquivos Parquet do MinIO.

---

# Fluxo Completo de Execução

```text
1. Scheduler identifica que chegou o horário.
2. Cria um DAG Run.
3. Executa a task run_dlt_pipeline.
4. Task chama ingestion.pipeline.run_pipeline().
5. run_pipeline() cria o pipeline dlt.
6. source.py consulta a FreeCurrency API.
7. dlt grava arquivos Parquet no MinIO.
8. Task finaliza.
9. Airflow registra status e logs no PostgreSQL.
```

---

# Scripts 1 a 5 do Projeto 1.2

Esses scripts são didáticos.

## Script 1

Teste inicial.

## Script 2

Transforma resposta em registros.

## Script 3

Tratamento de erros HTTP.

## Script 4

Primeiro `@dlt.resource`.

## Script 5

Source + Pipeline local.

### Observação

Eles servem para aprendizado e não são usados no projeto final.

---

# Arquivos Usados em Produção

- `ingestion/source.py`
- `ingestion/pipeline.py`
- `dags/currency_ingestion_dag.py`
- `Dockerfile`
- `docker-compose.yml`
- `.env`

---

# Comandos Úteis

## Ver logs

```bash
docker compose logs -f airflow-scheduler
```

## Parar containers

```bash
docker compose stop
```

## Derrubar containers

```bash
docker compose down
```

## Derrubar e apagar volumes

```bash
docker compose down -v
```

---

# Resumo

Imagine uma fábrica automatizada:

- `source.py` → funcionário que coleta os dados.
- `pipeline.py` → linha de produção.
- MinIO → armazém.
- `currency_ingestion_dag.py` → gerente.
- Scheduler → relógio automático.
- Webserver → painel de controle.
- PostgreSQL → livro de registros.
- Docker Compose → condomínio onde tudo funciona.