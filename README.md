# 🤖 WhatsApp AI Bot

Bot inteligente para WhatsApp com sistema de conhecimento baseado em PostgreSQL e busca semântica avançada usando pgvector.

## 🚀 Características

- **🧠 IA Conversacional**: Powered by OpenAI GPT com memória de contexto
- **🔍 Busca Inteligente**: Sistema híbrido (textual + semântica) usando PostgreSQL + pgvector
- **📚 Base de Conhecimento**: Gerenciamento completo via API REST
- **⚡ Performance**: Busca vetorial otimizada e debounce de mensagens
- **🐳 Docker Ready**: Configuração completa com Docker Compose
- **🔧 API Completa**: Interface REST para gerenciar conhecimento

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 15+ com extensão pgvector
- Redis (para cache e filas)
- Conta OpenAI API
- Instância Evolution API para WhatsApp

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd whatsapp_ai_bot
```

### 2. Instale dependências
```bash
pip install -r requirements.txt
# ou usando Poetry
poetry install
```

### 3. Configure variáveis de ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui

# PostgreSQL
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=whatsapp_bot
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha

# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_INSTANCE_NAME=seu_instance
AUTHENTICATION_API_KEY=sua_chave_auth

# Redis
CACHE_REDIS_URI=redis://localhost:6379/6
```

### 4. Inicie serviços com Docker
```bash
docker-compose up -d postgres redis evolution-api
```

### 5. Configure banco de dados
```bash
python scripts/setup_database.py
```

### 6. (Opcional) Migre dados existentes
Se você já tem arquivos RAG (txt/pdf):
```bash
python scripts/migrate_to_postgres.py
```

### 7. Inicie a aplicação
```bash
python main.py
```

A API estará disponível em: http://localhost:8000

## 📚 Documentação da API

### Endpoints Principais

#### Base de Conhecimento
- `GET /admin/knowledge` - Lista entradas
- `POST /admin/knowledge` - Cria nova entrada
- `GET /admin/knowledge/{id}` - Busca por ID
- `PUT /admin/knowledge/{id}` - Atualiza entrada
- `DELETE /admin/knowledge/{id}` - Remove entrada

#### Busca
- `POST /admin/knowledge/search` - Busca inteligente

Exemplo de busca:
```json
{
  "query": "como fazer login",
  "search_type": "hybrid",
  "category": "ajuda",
  "limit": 5
}
```

#### Estatísticas
- `GET /admin/stats` - Estatísticas da base de conhecimento
- `GET /admin/categories` - Lista categorias

#### Utilitários  
- `POST /admin/init-db` - Inicializa banco
- `POST /admin/knowledge/bulk-import` - Importação em lote

### Webhook
- `POST /webhook` - Recebe mensagens do WhatsApp

## 🏗️ Estrutura do Projeto

```
whatsapp_ai_bot/
├── src/                          # Código fonte principal
│   ├── api/                      # Endpoints REST
│   │   ├── admin_routes.py       # Rotas de administração
│   │   ├── webhook_routes.py     # Webhook WhatsApp
│   │   └── schemas.py            # Schemas Pydantic
│   ├── core/                     # Configurações centrais
│   │   ├── config.py             # Configurações
│   │   ├── chains.py             # Chains LangChain
│   │   ├── prompts.py            # Templates de prompts
│   │   ├── memory.py             # Gerenciamento de memória
│   │   ├── message_buffer.py     # Buffer de mensagens
│   │   └── evolution_api.py      # Integração Evolution API
│   ├── database/                 # Configurações de banco
│   │   ├── connection.py         # Conexões SQLAlchemy
│   │   └── initialization.py     # Inicialização
│   ├── models/                   # Modelos ORM
│   │   └── knowledge.py          # Modelo base de conhecimento
│   └── services/                 # Lógica de negócio
│       ├── knowledge_service.py  # Serviço de conhecimento
│       └── vectorstore_service.py # Vector store PostgreSQL
├── scripts/                      # Scripts utilitários
│   ├── migrate_to_postgres.py    # Migração de dados
│   └── setup_database.py         # Setup inicial
├── migrations/                   # Migrações Alembic
├── tests/                        # Testes automatizados
├── docs/                         # Documentação
├── docker-compose.yml            # Orquestração Docker
├── requirements.txt              # Dependências Python
├── pyproject.toml               # Configuração Poetry
└── main.py                      # Aplicação principal
```

## 🔧 Desenvolvimento

### Executar testes
```bash
pytest
```

### Formatação de código
```bash
black src/
isort src/
```

### Linting
```bash
flake8 src/
mypy src/
```

### Migrações de banco
```bash
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```

## 🔍 Como Funciona

### Sistema de Busca

1. **Busca Textual**: Usa PostgreSQL Full-Text Search com idioma português
2. **Busca Semântica**: Embeddings OpenAI + pgvector para similaridade cosseno
3. **Busca Híbrida**: Combina ambos métodos com scoring inteligente

### Fluxo de Mensagens

1. WhatsApp → Evolution API → Webhook `/webhook`
2. Mensagem vai para buffer Redis com debounce
3. Após debounce, processa com chain RAG
4. Busca conhecimento relevante no PostgreSQL
5. Gera resposta com OpenAI + contexto
6. Envia resposta via Evolution API

### Gerenciamento de Conhecimento

- **Interface API**: CRUD completo via REST
- **Categorização**: Organiza por categorias e tags
- **Metadados**: Campos flexíveis em JSONB
- **Versionamento**: Timestamps de criação/atualização
- **Embeddings**: Geração automática para busca semântica

## 🚀 Produção

### Variáveis de Ambiente Importantes
```env
# Produção
DEBUG=false
ENVIRONMENT=production

# Banco
DATABASE_CONNECTION_POOL_SIZE=20
DATABASE_CONNECTION_OVERFLOW=30

# Redis
REDIS_CONNECTION_POOL_SIZE=50

# OpenAI
OPENAI_RATE_LIMIT_REQUESTS=50
OPENAI_RATE_LIMIT_TOKENS=40000
```

### Docker Compose Produção
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoramento
- Health check: `GET /health`
- Métricas: `GET /admin/stats`
- Logs estruturados via uvicorn

## 🤝 Contribuição

1. Fork o projeto
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja arquivo `LICENSE` para detalhes.

## 🆘 Suporte

### Problemas Comuns

**Erro de conexão PostgreSQL:**
```bash
# Verifique se PostgreSQL está rodando
docker-compose ps postgres

# Verifique logs
docker-compose logs postgres
```

**Erro pgvector não encontrado:**
```bash
# Use imagem correta no docker-compose.yml
image: pgvector/pgvector:pg15
```

**Erro OpenAI API:**
- Verifique se `OPENAI_API_KEY` está configurada
- Confirme se tem saldo suficiente na conta
- Verifique rate limits

### Contato

- 📧 Email: seu.email@exemplo.com
- 💬 Issues: [GitHub Issues](link-para-issues)
- 📖 Docs: [Documentação](link-para-docs)

---

**Desenvolvido com ❤️ usando FastAPI, LangChain, PostgreSQL e pgvector**