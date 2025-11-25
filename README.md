# Kadupul - Sistema de Predição com Machine Learning

Sistema completo de classificação de flores Iris utilizando arquitetura de microserviços com Machine Learning, cache distribuído e persistência de dados.

<img src="./assets/ascii-art.png" alt="Banner" style="width: 100%; border-radius: 8px;"/>


## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Endpoints da API](#endpoints-da-api)
- [Testes](#testes)
- [Docker Compose](#docker-compose)

## 🌸 Sobre o Projeto

**Kadupul** é uma aplicação de Machine Learning que classifica flores do dataset Iris em três espécies: *Setosa*, *Versicolor* e *Virginica*. O sistema foi desenvolvido seguindo boas práticas de arquitetura de software, utilizando microserviços containerizados com Docker.

### Características Principais

- 🤖 **Machine Learning**: Modelo KNN (K-Nearest Neighbors) treinado com scikit-learn
- 🚀 **Microserviços**: Arquitetura distribuída com serviços independentes
- 💾 **Cache Inteligente**: Redis para otimização de consultas repetidas
- 📊 **Persistência**: MongoDB para armazenamento de predições e histórico
- 🐳 **Containerização**: Docker Compose para orquestração de serviços
- 🔄 **API RESTful**: Interface HTTP com endpoints documentados

## 🏗️ Arquitetura

O sistema é composto por **4 microserviços** principais que se comunicam através de uma rede Docker privada:

```
┌─────────────────────────────────────────────────────────────┐
│                         KADUPUL API                         │
│                    (Flask - Porta 8001)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Recebe requisições HTTP                           │   │
│  │  • Valida dados de entrada                           │   │
│  │  • Consulta cache (Redis)                            │   │
│  │  • Chama serviço ML                                  │   │
│  │  • Persiste resultados (MongoDB)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬──────────────┬──────────────┬──────────────────┘
             │              │              │
             ▼              ▼              ▼
    ┌────────────┐  ┌─────────────┐  ┌──────────────┐
    │   REDIS    │  │  MONGODB    │  │ ML SERVICE   │
    │  (Cache)   │  │ (Database)  │  │ (Inferência) │
    │ Porta 6379 │  │ Porta 27017 │  │ Porta 8002   │
    └────────────┘  └─────────────┘  └──────────────┘
```

### Fluxo de Predição

1. **Cliente** envia POST para `/api/predict` com features da flor
2. **API** verifica se já existe no **Redis** (cache)
3. Se **cache hit**: retorna resultado imediatamente
4. Se **cache miss**:
   - Envia features para o **ML Service**
   - Recebe predição do modelo KNN
   - Salva resultado no **Redis** (cache)
   - Persiste no **MongoDB** (histórico)
   - Retorna resultado ao cliente

### Serviços Detalhados

#### 1. **API Principal** (`kadupul_api`)
- **Função**: Gateway central, orquestra toda a lógica de negócio
- **Tecnologia**: Flask 3.0.0 + Python 3.11
- **Responsabilidades**:
  - Validação de entrada (4 features numéricas)
  - Gestão de cache (consulta/atualização Redis)
  - Comunicação HTTP com ML Service
  - Persistência de predições no MongoDB
  - Endpoints REST para clientes externos
  - Health checks de todos os serviços

#### 2. **ML Service** (`kadupul_ml_service`)
- **Função**: Inferência de Machine Learning isolada
- **Tecnologia**: Flask 3.0.0 + scikit-learn 1.3.2
- **Responsabilidades**:
  - Carregar modelo treinado (arquivo `.joblib`)
  - Receber features via POST `/predict`
  - Processar predição com modelo KNN
  - Retornar classe predita + probabilidades
  - Fornecer informações do modelo via `/model-info`

#### 3. **Redis** (`kadupul_redis`)
- **Função**: Cache de predições em memória
- **Tecnologia**: Redis 7 Alpine
- **Responsabilidades**:
  - Armazenar predições recentes (key-value)
  - Contador de predições por features
  - Redução de latência (evita reprocessamento)
  - Persistência em disco (`/data`)

#### 4. **MongoDB** (`kadupul_mongodb`)
- **Função**: Banco de dados de persistência
- **Tecnologia**: MongoDB 7
- **Responsabilidades**:
  - Armazenar histórico completo de predições
  - Collection `predictions` com índices em `timestamp` e `prediction_name`
  - Database `kadupul_db`
  - Suporte a agregações para estatísticas

## 📁 Estrutura de Pastas

```
Kadupul/
│
├── api/                              # Serviço principal da API
│   ├── src/
│   │   ├── routes/                   # Endpoints REST
│   │   │   ├── health_routes.py      # Health checks
│   │   │   └── predict_routes.py     # Predições e estatísticas
│   │   ├── services/                 # Camada de serviços
│   │   │   ├── mongo_service.py      # Conexão e operações MongoDB
│   │   │   ├── redis_service.py      # Conexão e operações Redis
│   │   │   └── ml_service.py         # Cliente HTTP para ML Service
│   │   ├── utils/                    # Utilitários
│   │   │   └── validators.py         # Validação de dados
│   │   └── app.py                    # Aplicação Flask principal
│   ├── Dockerfile                    # Container da API
│   ├── requirements.txt              # Dependências Python
│   └── .env                          # Variáveis de ambiente
│
├── model_service/                    # Serviço de Machine Learning
│   ├── src/
│   │   ├── app.py                    # API Flask de inferência
│   │   ├── main.py                   # Script de treinamento do modelo
│   │   ├── modelo_iris_knn.joblib    # Modelo serializado (KNN)
│   │   └── config.json               # Configurações do modelo
│   ├── Dockerfile                    # Container do ML Service
│   └── requirements.txt              # Dependências Python
│
├── data/                             # Dados de treinamento (Iris dataset)
│
├── docs/                             # Documentação do projeto
│
├── docsIA/                           # Instruções para desenvolvimento
│   └── instruções.md                 # Guia de implementação
│
├── assets/                           # Recursos visuais
│   └── ascii-art.png                 # Banner do README
│
├── docker-compose.yml                # Orquestração de todos os serviços
├── test_api.sh                       # Suite de testes automatizados
└── README.md                         # Este arquivo
```

### Descrição dos Componentes

- **`routes/`**: Define os endpoints HTTP e suas respostas
- **`services/`**: Lógica de negócio e integrações externas
- **`utils/`**: Funções auxiliares e validações
- **`modelo_iris_knn.joblib`**: Modelo KNN serializado com joblib
- **`docker-compose.yml`**: Arquivo de orquestração com 4 serviços

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11**: Linguagem principal
- **Flask 3.0.0**: Framework web para APIs REST
- **scikit-learn 1.3.2**: Biblioteca de Machine Learning
- **joblib 1.3.2**: Serialização do modelo

### Banco de Dados e Cache
- **MongoDB 7**: Database NoSQL para persistência
- **pymongo 4.6.0**: Driver Python para MongoDB
- **Redis 7 Alpine**: Cache em memória
- **redis-py 5.0.1**: Cliente Python para Redis

### DevOps
- **Docker**: Containerização de serviços
- **Docker Compose v3.8**: Orquestração multi-container
- **curl**: Testes de API
- **bash**: Automação de testes

## 📦 Pré-requisitos

Certifique-se de ter instalado:

- [Docker](https://docs.docker.com/get-docker/) (versão 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (versão 2.0+)
- Git (para clonar o repositório)

## 🚀 Instalação e Execução

### 1. Clone o Repositório

```bash
git clone https://github.com/samuka7abr/Kadupul.git
cd Kadupul
```

### 2. Inicie os Serviços com Docker Compose

```bash
docker compose up -d
```

Este comando irá:
- Construir as imagens Docker para `api` e `model_service`
- Baixar imagens oficiais do MongoDB e Redis
- Criar a rede `kadupul_network`
- Iniciar os 4 containers
- Configurar volumes persistentes para MongoDB e Redis

### 3. Verificar Status dos Containers

```bash
docker compose ps
```

Você deve ver 4 containers rodando:
- `kadupul_api` (porta 8001)
- `kadupul_ml_service` (porta 8002)
- `kadupul_mongodb` (porta 27017)
- `kadupul_redis` (porta 6379)

### 4. Testar a API

```bash
bash test_api.sh
```

## 📡 Endpoints da API

### Base URL
```
http://localhost:8001
```

### 1. **GET /** - Informações da API
Retorna informações sobre a API e lista de endpoints disponíveis.

**Response:**
```json
{
  "service": "Kadupul API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/api/predict",
    "predictions": "/api/predictions",
    "prediction_detail": "/api/predictions/<id>",
    "stats": "/api/stats"
  }
}
```

### 2. **GET /health** - Health Check
Verifica o status de todos os serviços.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "api": "healthy",
    "ml_service": "healthy",
    "mongodb": "connected",
    "redis": "connected"
  }
}
```

### 3. **POST /api/predict** - Fazer Predição
Classifica uma flor Iris com base nas features fornecidas.

**Request Body:**
```json
{
  "features": [5.1, 3.5, 1.4, 0.2]
}
```

**Features (em ordem):**
1. `sepal_length` - Comprimento da sépala (cm)
2. `sepal_width` - Largura da sépala (cm)
3. `petal_length` - Comprimento da pétala (cm)
4. `petal_width` - Largura da pétala (cm)

**Response:**
```json
{
  "prediction_id": "691fb575839425149bd6886c",
  "result": {
    "prediction_index": 0,
    "prediction_name": "setosa",
    "probabilities": {
      "setosa": 1.0,
      "versicolor": 0.0,
      "virginica": 0.0
    },
    "features": {
      "sepal length (cm)": 5.1,
      "sepal width (cm)": 3.5,
      "petal length (cm)": 1.4,
      "petal width (cm)": 0.2
    }
  },
  "source": "cache",
  "timestamp": "2025-11-21T00:42:29.212000"
}
```

### 4. **GET /api/predictions** - Listar Predições
Lista as últimas predições armazenadas no MongoDB.

**Query Parameters:**
- `limit` (opcional): Número de predições a retornar (padrão: 10)

**Response:**
```json
{
  "count": 3,
  "predictions": [
    {
      "_id": "691fb575839425149bd6886c",
      "prediction_name": "setosa",
      "prediction_index": 0,
      "features": [5.1, 3.5, 1.4, 0.2],
      "probabilities": {
        "setosa": 1.0,
        "versicolor": 0.0,
        "virginica": 0.0
      },
      "timestamp": "2025-11-21T00:42:29.212000"
    }
  ]
}
```

### 5. **GET /api/predictions/<id>** - Buscar Predição por ID
Retorna detalhes de uma predição específica.

**Response:**
```json
{
  "_id": "691fb575839425149bd6886c",
  "prediction_name": "setosa",
  "prediction_index": 0,
  "features": [5.1, 3.5, 1.4, 0.2],
  "probabilities": {
    "setosa": 1.0,
    "versicolor": 0.0,
    "virginica": 0.0
  },
  "timestamp": "2025-11-21T00:42:29.212000"
}
```

### 6. **GET /api/stats** - Estatísticas
Retorna estatísticas agregadas das predições.

**Response:**
```json
{
  "total_predictions": 3,
  "by_class": {
    "setosa": 1,
    "versicolor": 1,
    "virginica": 1
  }
}
```

## 🧪 Testes

O projeto inclui uma suite completa de testes automatizados:

```bash
bash test_api.sh
```

**Testes Incluídos:**
1. ✅ Endpoint raiz (informações da API)
2. ✅ Health check de todos os serviços
3. ✅ Predição - Iris Setosa
4. ✅ Predição - Iris Versicolor
5. ✅ Predição - Iris Virginica
6. ✅ Cache hit (predição repetida)
7. ✅ Listagem de predições
8. ✅ Estatísticas agregadas
9. ✅ Validação de erro (features inválidas)

## 🐳 Docker Compose

### Configuração dos Serviços

O arquivo `docker-compose.yml` define toda a infraestrutura:

```yaml
version: '3.8'

services:
  # API Principal
  api:
    build: ./api
    container_name: kadupul_api
    ports:
      - "8001:8001"
    environment:
      - MONGO_URI=mongodb://mongodb:27017/
      - MONGO_DB=kadupul_db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - ML_SERVICE_URL=http://model_service:8002
    depends_on:
      - mongodb
      - redis
      - model_service
    networks:
      - kadupul_network
    restart: unless-stopped

  # Serviço de Machine Learning
  model_service:
    build: ./model_service
    container_name: kadupul_ml_service
    ports:
      - "8002:8002"
    networks:
      - kadupul_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Redis (Cache)
  redis:
    image: redis:7-alpine
    container_name: kadupul_redis
    ports:
      - "6379:6379"
    networks:
      - kadupul_network
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # MongoDB (Database)
  mongodb:
    image: mongo:7
    container_name: kadupul_mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: kadupul_db
    networks:
      - kadupul_network
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

networks:
  kadupul_network:
    driver: bridge

volumes:
  redis_data:
  mongo_data:
```

### Comandos Docker Compose Úteis

```bash
# Iniciar todos os serviços
docker compose up -d

# Ver logs de todos os serviços
docker compose logs -f

# Ver logs de um serviço específico
docker compose logs -f api

# Parar todos os serviços
docker compose down

# Parar e remover volumes (ATENÇÃO: apaga dados!)
docker compose down -v

# Reconstruir imagens
docker compose build

# Reconstruir sem cache
docker compose build --no-cache

# Ver status dos containers
docker compose ps

# Reiniciar um serviço específico
docker compose restart api
```

### Portas Expostas

| Serviço | Porta Host | Porta Container | Descrição |
|---------|------------|-----------------|-----------|
| API | 8001 | 8001 | API REST principal |
| ML Service | 8002 | 8002 | Serviço de inferência ML |
| MongoDB | 27017 | 27017 | Banco de dados |
| Redis | 6379 | 6379 | Cache em memória |

### Volumes Persistentes

- **`mongo_data`**: Armazena os dados do MongoDB em `/data/db`
- **`redis_data`**: Armazena snapshots do Redis em `/data`

Estes volumes garantem que os dados não sejam perdidos ao reiniciar os containers.

### Rede Docker

Todos os serviços se comunicam através da rede privada `kadupul_network` (bridge driver), permitindo:
- Resolução de nomes via DNS (ex: `http://mongodb:27017`)
- Isolamento da rede host
- Comunicação eficiente entre containers

## 📝 Variáveis de Ambiente

O serviço API utiliza as seguintes variáveis (definidas no `docker-compose.yml`):

```bash
MONGO_URI=mongodb://mongodb:27017/
MONGO_DB=kadupul_db
REDIS_HOST=redis
REDIS_PORT=6379
ML_SERVICE_URL=http://model_service:8002
```

Para desenvolvimento local, você pode criar um arquivo `.env` na pasta `api/`.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais.

---

**Desenvolvido com ❤️ usando Python, Docker e Machine Learning**
