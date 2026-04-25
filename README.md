# 📊 Sistema Completo de Vendas (OLTP)

## 🎯 Objetivo

Criar um banco de dados transacional (OLTP) completo com um sistema de gerenciamento de vendas, incluindo cliente, produtos, pedidos e pagamentos com API em Python/FastAPI.

---

## 🔧 Stack Tecnológico

- **Banco de Dados**: PostgreSQL 12+
- **Backend**: Python 3.9+ com FastAPI
- **ORM**: SQLAlchemy
- **Validação**: Pydantic
- **Testes**: Pytest

---

## 📦 Estrutura do Projeto

```
OLTP_Postgres/
├── database/
│   ├── schema.sql          # Scripts de criação das tabelas
│   ├── indexes.sql         # Scripts de índices
│   └── queries.sql         # Queries analíticas complexas
├── api/
│   ├── main.py             # Aplicação FastAPI
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Schemas Pydantic
│   ├── routes/
│   │   ├── clientes.py
│   │   ├── produtos.py
│   │   ├── pedidos.py
│   │   └── pagamentos.py
│   └── database.py         # Configuração do banco
├── tests/
│   ├── test_clientes.py
│   ├── test_produtos.py
│   ├── test_pedidos.py
│   └── test_pagamentos.py
├── docs/
│   ├── TECNICAS.md         # Documentação técnica detalhada
│   └── DIAGRAMA_ER.md      # Diagrama entidade-relacionamento
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

---

## 📌 Modelo de Dados (Diagrama Entidade-Relacionamento)

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│  CLIENTES   │◄─────►│   PEDIDOS    │◄─────►│   PRODUTOS   │
├─────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)     │       │ id (PK)      │       │ id (PK)      │
│ nome        │       │ cliente_id   │       │ nome         │
│ email       │       │ data_pedido  │       │ preco        │
│ telefone    │       │ status       │       │ estoque      │
│ endereco    │       │ total        │       │ categoria    │
│ data_cadastro       │ data_criacao │       │ descricao    │
└─────────────┘       └──────────────┘       └──────────────┘
       ▲                      ▲
       │                      │
       │                      │
       │              ┌──────────────────┐
       │              │  ITENS_PEDIDO    │
       │              ├──────────────────┤
       │              │ id (PK)          │
       │              │ pedido_id (FK)   │
       │              │ produto_id (FK)  │
       │              │ quantidade       │
       │              │ preco_unitario   │
       │              │ subtotal         │
       │              └──────────────────┘
       │
       │              ┌──────────────────┐
       └──────────────│  PAGAMENTOS      │
                      ├──────────────────┤
                      │ id (PK)          │
                      │ cliente_id (FK)  │
                      │ pedido_id (FK)   │
                      │ valor            │
                      │ data_pagamento   │
                      │ metodo           │
                      │ status           │
                      └──────────────────┘
```

---

## 💾 Tabelas do Banco de Dados

### 1. **CLIENTES**
Armazena informações dos clientes

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | SERIAL PRIMARY KEY | ID único do cliente |
| nome | VARCHAR(150) NOT NULL | Nome completo |
| email | VARCHAR(100) UNIQUE | Email |
| telefone | VARCHAR(20) | Telefone de contato |
| endereco | TEXT | Endereço completo |
| data_cadastro | TIMESTAMP DEFAULT NOW() | Data do cadastro |

### 2. **PRODUTOS**
Catálogo de produtos disponíveis

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | SERIAL PRIMARY KEY | ID único do produto |
| nome | VARCHAR(150) NOT NULL | Nome do produto |
| descricao | TEXT | Descrição detalhada |
| preco | DECIMAL(10,2) NOT NULL | Preço unitário |
| estoque | INTEGER DEFAULT 0 | Quantidade em estoque |
| categoria | VARCHAR(50) | Categoria do produto |
| data_criacao | TIMESTAMP DEFAULT NOW() | Data de criação |

### 3. **PEDIDOS**
Pedidos realizados pelos clientes

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | SERIAL PRIMARY KEY | ID único do pedido |
| cliente_id | INTEGER (FK) | Referência ao cliente |
| data_pedido | TIMESTAMP DEFAULT NOW() | Data do pedido |
| status | VARCHAR(20) DEFAULT 'pendente' | Status (pendente, confirmado, enviado, entregue, cancelado) |
| total | DECIMAL(10,2) | Valor total do pedido |
| data_criacao | TIMESTAMP DEFAULT NOW() | Data de criação |

### 4. **ITENS_PEDIDO**
Itens que compõem cada pedido

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | SERIAL PRIMARY KEY | ID único do item |
| pedido_id | INTEGER (FK) | Referência ao pedido |
| produto_id | INTEGER (FK) | Referência ao produto |
| quantidade | INTEGER NOT NULL | Quantidade de produtos |
| preco_unitario | DECIMAL(10,2) NOT NULL | Preço unitário no momento da compra |
| subtotal | DECIMAL(10,2) NOT NULL | Quantidade × Preço unitário |

### 5. **PAGAMENTOS**
Histórico de pagamentos

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | SERIAL PRIMARY KEY | ID único do pagamento |
| cliente_id | INTEGER (FK) | Referência ao cliente |
| pedido_id | INTEGER (FK) | Referência ao pedido |
| valor | DECIMAL(10,2) NOT NULL | Valor pago |
| data_pagamento | TIMESTAMP DEFAULT NOW() | Data do pagamento |
| metodo | VARCHAR(30) | Método (credito, debito, boleto, pix) |
| status | VARCHAR(20) DEFAULT 'pendente' | Status (pendente, confirmado, cancelado) |

---

## 🔍 Queries Analíticas Complexas

### 1. **Faturamento Mensal**
```sql
SELECT 
    DATE_TRUNC('month', p.data_pagamento) AS mes,
    SUM(p.valor) AS total_faturado,
    COUNT(DISTINCT p.pedido_id) AS total_pedidos
FROM pagamentos p
WHERE p.status = 'confirmado'
GROUP BY DATE_TRUNC('month', p.data_pagamento)
ORDER BY mes DESC;
```

### 2. **Cliente que Mais Compra**
```sql
SELECT 
    c.id,
    c.nome,
    COUNT(ped.id) AS total_pedidos,
    SUM(ped.total) AS total_gasto,
    AVG(ped.total) AS ticket_medio
FROM clientes c
LEFT JOIN pedidos ped ON c.id = ped.cliente_id
GROUP BY c.id, c.nome
ORDER BY total_gasto DESC
LIMIT 10;
```

### 3. **Ticket Médio por Cliente**
```sql
SELECT 
    c.nome,
    COUNT(ped.id) AS numero_pedidos,
    AVG(ped.total)::DECIMAL(10,2) AS ticket_medio,
    SUM(ped.total)::DECIMAL(10,2) AS total_gasto
FROM clientes c
JOIN pedidos ped ON c.id = ped.cliente_id
GROUP BY c.id, c.nome
HAVING COUNT(ped.id) > 0
ORDER BY ticket_medio DESC;
```

### 4. **Produtos Mais Vendidos**
```sql
SELECT 
    pr.id,
    pr.nome,
    SUM(ip.quantidade) AS total_vendido,
    SUM(ip.subtotal)::DECIMAL(10,2) AS receita_total
FROM produtos pr
LEFT JOIN itens_pedido ip ON pr.id = ip.produto_id
GROUP BY pr.id, pr.nome
ORDER BY total_vendido DESC
LIMIT 20;
```

### 5. **Status dos Pedidos**
```sql
SELECT 
    status,
    COUNT(*) AS quantidade,
    SUM(total)::DECIMAL(10,2) AS valor_total
FROM pedidos
GROUP BY status
ORDER BY quantidade DESC;
```

---

## 🔑 Relacionamentos e Restrições

### Foreign Keys (Chaves Estrangeiras)
- `pedidos.cliente_id` → `clientes.id`
- `itens_pedido.pedido_id` → `pedidos.id`
- `itens_pedido.produto_id` → `produtos.id`
- `pagamentos.cliente_id` → `clientes.id`
- `pagamentos.pedido_id` → `pedidos.id`

### Constraints (Restrições)
- ON DELETE CASCADE em tabelas dependentes
- CHECK constraints para valores válidos (preço > 0, estoque >= 0)
- UNIQUE constraints em email de clientes

---

## 📈 Índices para Performance

Os seguintes índices foram criados para otimizar consultas:

```sql
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX idx_pedidos_data ON pedidos(data_pedido);
CREATE INDEX idx_itens_pedido ON itens_pedido(pedido_id);
CREATE INDEX idx_itens_produto ON itens_pedido(produto_id);
CREATE INDEX idx_pagamentos_cliente ON pagamentos(cliente_id);
CREATE INDEX idx_pagamentos_pedido ON pagamentos(pedido_id);
CREATE INDEX idx_pagamentos_data ON pagamentos(data_pagamento);
CREATE INDEX idx_clientes_email ON clientes(email);
CREATE INDEX idx_produtos_categoria ON produtos(categoria);
```

---

## 🚀 Como Usar

### 1. Criar o Banco de Dados

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco
CREATE DATABASE vendas_oltp;
```

### 2. Executar Scripts SQL

```bash
# Aplicar schema
psql -U postgres -d vendas_oltp -f database/schema.sql

# Aplicar índices
psql -U postgres -d vendas_oltp -f database/indexes.sql
```

### 3. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Criar arquivo `.env`:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/vendas_oltp
```

### 5. Iniciar a API

```bash
cd api
uvicorn main:app --reload --port 8000
```

### 6. Acessar a Documentação

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## 📚 Técnicas OLTP Implementadas

1. **Normalização de Dados (3NF)**: Eliminação de redundâncias
2. **Integridade Referencial**: Foreign Keys e Constraints
3. **Índices Estratégicos**: Otimização de SELECT e JOIN
4. **ACID Compliance**: Transações ACID no PostgreSQL
5. **Particionamento Lógico**: Separação de responsabilidades
6. **API RESTful**: CRUD completo com FastAPI
7. **Validação em Múltiplas Camadas**: Banco + Aplicação
8. **Tratamento de Erros**: Exceções customizadas
9. **Paginação e Filtering**: Queries eficientes
10. **Auditoria**: Timestamps de criação/atualização

---

## 📖 Documentação Adicional

Veja em `docs/TECNICAS.md` uma documentação mais detalhada sobre técnicas OLTP.

---

## 👨‍💻 Autor

Sistema OLTP de Vendas

