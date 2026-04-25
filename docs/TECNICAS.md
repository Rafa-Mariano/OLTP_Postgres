# 📚 Documentação Técnica - Sistema OLTP de Vendas

## Índice
1. [O que é OLTP?](#o-que-é-oltp)
2. [Técnicas de Design](#técnicas-de-design)
3. [Normalização de Dados](#normalização-de-dados)
4. [Integridade de Dados](#integridade-de-dados)
5. [Otimização de Performance](#otimização-de-performance)
6. [Implementação da API](#implementação-da-api)
7. [Tratamento de Transações](#tratamento-de-transações)
8. [Segurança](#segurança)

---

## O que é OLTP?

**OLTP** significa **Online Transaction Processing** (Processamento de Transações Online).

### Características principais:

| Característica | Descrição |
|---|---|
| **Transações Rápidas** | Muitas operações pequenas e rápidas |
| **Alta Concorrência** | Vários usuários acessando simultaneamente |
| **Integridade de Dados** | Criticamente importante (ACID) |
| **Normalização** | Dados bem estruturados e sem redundância |
| **Índices** | Muitos índices para acelerar buscas |
| **Backups Frequentes** | Proteção de dados críticos |

### Diferenças OLTP vs OLAP

```
OLTP (Transacional)          OLAP (Analítico)
─────────────────────────────────────────────
Muitas operações pequenas     Poucas operações grandes
Leitura/Escrita equilibrada   Leitura intensiva
Dados normalizados            Dados desnormalizados
Índices múltiplos             Índices seletivos
Backup frequente              Backup menos frequente
Exemplo: Sistema de vendas    Exemplo: Data warehouse
```

---

## Técnicas de Design

### 1. **Diagrama Entidade-Relacionamento (ER)**

Antes de implementar o banco, devemos desenhar o diagrama ER para:
- Identificar entidades (tabelas)
- Definir relacionamentos
- Estabelecer multiplicidade (1:1, 1:N, M:N)

No nosso caso:
```
1 Cliente ──────── N Pedidos
1 Pedido ──────── N Itens_Pedido ──── 1 Produto
1 Cliente ──────── N Pagamentos
```

### 2. **Nomenclatura Padronizada**

```
Tabelas: snake_case no plural (pedidos, itens_pedido)
Colunas: snake_case no singular (cliente_id, data_pedido)
Primary Keys: id
Foreign Keys: tabela_singularizada_id (cliente_id)
Índices: idx_tabela_coluna
Constraints: constraint_descritivo
```

### 3. **Versionamento de Schema**

Use migrations para rastrear mudanças no banco:
```
V1__initial_schema.sql
V2__add_new_columns.sql
V3__create_indexes.sql
```

---

## Normalização de Dados

### O que é Normalização?

Normalização é o processo de organizar dados para **reduzir redundância** e **melhorar integridade**.

### Formas Normais

#### **1ª Forma Normal (1NF)**
- Todos os atributos contêm valores **atômicos** (não podem ser decompostos)
- Não há grupos repetidos

❌ Errado:
```
pedidos: id, cliente_id, produtos_id[1,2,3], quantidades[1,2,3]
```

✅ Correto:
```
pedidos: id, cliente_id
itens_pedido: id, pedido_id, produto_id, quantidade
```

#### **2ª Forma Normal (2NF)**
- Está em 1NF
- Atributos não-chave dependem **completamente** da chave primária

❌ Errado:
```
itens_pedido: id, pedido_id, produto_id, produto_nome, quantidade
(produto_nome depende de produto_id, não da chave completa)
```

✅ Correto:
```
itens_pedido: id, pedido_id, produto_id, quantidade
produtos: id, nome
```

#### **3ª Forma Normal (3NF)**
- Está em 2NF
- Atributos não-chave não dependem **transitivamente** de outros atributos não-chave

❌ Errado:
```
clientes: id, nome, endereco, cidade, estado, cep
(cidade e estado dependem de cep)
```

✅ Correto:
```
clientes: id, nome, endereco, cep_id
ceps: id, cep, cidade, estado
```

### Nossa Estrutura

Nosso banco está em **3ª Forma Normal (3NF)**:

```
clientes: id, nome, email, telefone, endereco, data_cadastro
produtos: id, nome, descricao, preco, estoque, categoria
pedidos: id, cliente_id, data_pedido, status, total
itens_pedido: id, pedido_id, produto_id, quantidade, preco_unitario, subtotal
pagamentos: id, cliente_id, pedido_id, valor, data_pagamento, metodo, status
```

**Benefícios:**
- ✅ Sem redundância de dados
- ✅ Fácil manutenção
- ✅ Integridade garantida

---

## Integridade de Dados

### 1. **Chaves Primárias (Primary Keys)**

```sql
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,  -- Identificador único
    ...
);
```

**Garantem:**
- Unicidade de registros
- Rápida identificação
- Referência de foreign keys

### 2. **Chaves Estrangeiras (Foreign Keys)**

```sql
ALTER TABLE pedidos
ADD CONSTRAINT fk_pedidos_cliente
FOREIGN KEY (cliente_id) 
REFERENCES clientes(id) 
ON DELETE CASCADE;
```

**Garantem:**
- Relacionamentos válidos
- Cascata de deletions (ON DELETE CASCADE)
- Integridade referencial

### 3. **Constraints (Restrições)**

#### CHECK Constraint
```sql
ALTER TABLE produtos
ADD CONSTRAINT preco_positivo CHECK (preco > 0);
```

#### UNIQUE Constraint
```sql
ALTER TABLE clientes
ADD CONSTRAINT email_unico UNIQUE (email);
```

#### NOT NULL
```sql
ALTER TABLE clientes
MODIFY nome VARCHAR(150) NOT NULL;
```

### 4. **Triggers (Gatilhos)**

Executam ações automaticamente quando eventos ocorrem:

```sql
CREATE TRIGGER atualizar_total_pedido
AFTER INSERT ON itens_pedido
FOR EACH ROW
EXECUTE FUNCTION calcular_total_pedido();
```

---

## Otimização de Performance

### 1. **Índices**

Um índice é uma **estrutura de dados** que acelera buscas (similar a índice de um livro).

#### Tipos de índices:

**a) Índice Simples**
```sql
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id);
-- Acelera: SELECT * FROM pedidos WHERE cliente_id = 5
```

**b) Índice Composto**
```sql
CREATE INDEX idx_pedidos_cliente_data 
ON pedidos(cliente_id, data_pedido DESC);
-- Acelera: SELECT * FROM pedidos WHERE cliente_id = 5 ORDER BY data_pedido
```

**c) Índice em Expressão**
```sql
CREATE INDEX idx_clientes_nome_upper 
ON clientes(UPPER(nome));
-- Acelera: SELECT * FROM clientes WHERE UPPER(nome) = 'JOÃO'
```

#### Quando criar índices:

✅ **SIM** - Colunas usadas frequentemente em:
- WHERE clauses
- JOIN conditions
- ORDER BY
- GROUP BY

❌ **NÃO** - Tabelas muito pequenas ou colunas com poucos valores distintos

### 2. **EXPLAIN e QUERY ANALYSIS**

Use EXPLAIN para entender como o PostgreSQL executa queries:

```sql
EXPLAIN ANALYZE
SELECT * FROM pedidos 
WHERE cliente_id = 5 AND data_pedido > '2024-01-01';
```

**Saída:**
```
Seq Scan on pedidos (cost=0.00..35.50 rows=10)
  Filter: ((cliente_id = 5) AND (data_pedido > '2024-01-01'))
```

**Dicas:**
- `cost=inicio..fim` - Custo estimado
- `rows=N` - Linhas retornadas
- Seq Scan = leitura sequencial (lento)
- Index Scan = leitura indexada (rápido)

### 3. **Particionamento**

Para tabelas muito grandes, dividir em partições:

```sql
CREATE TABLE pedidos_2024 PARTITION OF pedidos
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 4. **Normalização vs Performance**

**Trade-off**: Normalização = integridade, mas pode ser lenta (muitos JOINs)

**Solução**: Índices bem planejados mantêm performance com dados normalizados.

### 5. **Connection Pooling**

Em produção, use connection pooling (ex: PgBouncer):

```
Sem pooling: 1000 conexões = alta latência
Com pooling: 100 conexões gerenciadas = menor latência
```

---

## Implementação da API

### 1. **Arquitetura da API FastAPI**

```
main.py (aplicação principal)
    ├── models.py (SQLAlchemy ORM)
    ├── schemas.py (Pydantic validators)
    ├── database.py (conexão com BD)
    └── routes/
        ├── clientes.py
        ├── produtos.py
        ├── pedidos.py
        └── pagamentos.py
```

### 2. **Modelo SQLAlchemy vs Schema Pydantic**

**SQLAlchemy (models.py)** - Mapear tabelas do BD
```python
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(100), unique=True)
```

**Pydantic (schemas.py)** - Validar entrada/saída
```python
class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
```

### 3. **CRUD Operations**

```python
# CREATE
@app.post("/clientes")
def criar_cliente(cliente: ClienteCreate, db: Session):
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    return db_cliente

# READ
@app.get("/clientes/{id}")
def obter_cliente(id: int, db: Session):
    return db.query(Cliente).filter(Cliente.id == id).first()

# UPDATE
@app.put("/clientes/{id}")
def atualizar_cliente(id: int, cliente: ClienteUpdate, db: Session):
    db_cliente = db.query(Cliente).filter(Cliente.id == id).first()
    for key, value in cliente.dict().items():
        setattr(db_cliente, key, value)
    db.commit()
    return db_cliente

# DELETE
@app.delete("/clientes/{id}")
def deletar_cliente(id: int, db: Session):
    db.query(Cliente).filter(Cliente.id == id).delete()
    db.commit()
```

### 4. **Tratamento de Erros**

```python
from fastapi import HTTPException

@app.get("/clientes/{id}")
def obter_cliente(id: int, db: Session):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente
```

### 5. **Paginação**

```python
@app.get("/clientes")
def listar_clientes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Cliente).offset(skip).limit(limit).all()

# Uso: GET /clientes?skip=0&limit=10
```

---

## Tratamento de Transações

### 1. **O que são Transações?**

Conjunto de operações que devem ser executadas **tudo ou nada** (atomicidade).

### 2. **ACID Compliance**

```
A - Atomicidade: Tudo ou nada
C - Consistência: Dados válidos antes e depois
I - Isolamento: Transações não interferem
D - Durabilidade: Dados persistidos
```

### 3. **Exemplo: Criar Pedido com Itens**

```python
@app.post("/pedidos")
def criar_pedido(pedido: PedidoCreate, db: Session):
    try:
        # Iniciar transação
        db_pedido = Pedido(cliente_id=pedido.cliente_id)
        db.add(db_pedido)
        db.flush()  # Gerar ID
        
        # Adicionar itens
        total = 0
        for item in pedido.itens:
            db_item = ItemPedido(
                pedido_id=db_pedido.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario
            )
            db_item.subtotal = item.quantidade * item.preco_unitario
            total += db_item.subtotal
            db.add(db_item)
        
        db_pedido.total = total
        db.commit()  # Commit transação
        return db_pedido
        
    except Exception as e:
        db.rollback()  # Desfazer todas operações
        raise HTTPException(status_code=400, detail=str(e))
```

### 4. **Níveis de Isolamento**

```sql
-- Mais fraco (menos bloqueio, mais conflitos)
READ UNCOMMITTED
READ COMMITTED (padrão PostgreSQL)
REPEATABLE READ
SERIALIZABLE
-- Mais forte (mais bloqueio, menos conflitos)
```

---

## Segurança

### 1. **Autenticação e Autorização**

```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt

security = HTTPBearer()

@app.get("/clientes", dependencies=[Depends(security)])
def listar_clientes(credentials: HTTPAuthCredentials, db: Session):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401)
    return db.query(Cliente).all()
```

### 2. **SQL Injection Prevention**

❌ **NUNCA** usar concatenação:
```python
query = f"SELECT * FROM clientes WHERE id = {user_id}"
```

✅ **SEMPRE** usar parametrização:
```python
db.query(Cliente).filter(Cliente.id == user_id).first()
```

### 3. **Validação de Entrada**

```python
from pydantic import BaseModel, EmailStr, validator

class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    
    @validator('nome')
    def nome_nao_vazio(cls, v):
        if not v.strip():
            raise ValueError('Nome não pode ser vazio')
        return v
```

### 4. **CORS (Cross-Origin Resource Sharing)**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. **Rate Limiting**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/clientes", dependencies=[Depends(limiter.limit("10/minute"))])
def listar_clientes(db: Session):
    return db.query(Cliente).all()
```

### 6. **Criptografia de Dados Sensíveis**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)
```

### 7. **Audit Trail (Rastreamento)**

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    tabela VARCHAR(50),
    operacao VARCHAR(10),  -- INSERT, UPDATE, DELETE
    registro_id INTEGER,
    usuario VARCHAR(100),
    data TIMESTAMP DEFAULT NOW(),
    valores_anteriores JSONB,
    valores_novos JSONB
);
```

---

## Resumo das Melhores Práticas

| Prática | Por quê? |
|---------|---------|
| Normalização 3NF | Elimina redundância |
| Índices estratégicos | Acelera queries |
| Foreign Keys | Garante integridade |
| Constraints | Validação no banco |
| ACID Transactions | Dados consistentes |
| Connection Pooling | Melhor performance |
| Validação em 2 camadas | Segurança |
| EXPLAIN ANALYZE | Diagnosticar lentidão |
| Backup frequente | Recuperação de falhas |
| Monitoramento | Detectar problemas |

---

## Próximos Passos

1. ✅ Criar schema do banco
2. ✅ Criar índices
3. ✅ Popular com dados de teste
4. ✅ Criar API CRUD
5. ✅ Implementar autenticação
6. ✅ Adicionar logging
7. ✅ Fazer testes automatizados
8. ✅ Deploy em produção
