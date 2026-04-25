# 📊 Diagrama Entidade-Relacionamento (ER)

## Visão Geral

```
                    ┌─────────────────────────────────────┐
                    │          CLIENTES                   │
                    ├─────────────────────────────────────┤
                    │ PK  id                              │
                    │     nome (VARCHAR)                  │
                    │ UQ  email                           │
                    │     telefone                        │
                    │     endereco                        │
                    │     data_cadastro (TIMESTAMP)       │
                    └─────────────────────────────────────┘
                              ▲                  ▲
                              │                  │
                    ┌─────────┴──────┐      ┌────┴─────────┐
                    │ 1:N            │      │ 1:N          │
                    │                │      │              │
                    ▼                │      ▼              │
          ┌──────────────────────┐   │  ┌────────────────┐ │
          │    PEDIDOS           │   │  │   PAGAMENTOS   │ │
          ├──────────────────────┤   │  ├────────────────┤ │
          │ PK  id               │   │  │ PK  id         │ │
          │ FK  cliente_id ──────┼───┘  │ FK  cliente_id ├─┘
          │     data_pedido      │      │ FK  pedido_id ─┼─────┐
          │     status (ENUM)    │      │     valor      │     │
          │     total (DECIMAL)  │      │     data_paga  │     │
          │     data_criacao     │      │     metodo     │     │
          └──────────────────────┘      │     status     │     │
                    │                   └────────────────┘     │
                    │                                          │
                    │ 1:N                                      │
                    │                                          │
                    ▼                                          │
          ┌──────────────────────┐                            │
          │  ITENS_PEDIDO        │                            │
          ├──────────────────────┤                            │
          │ PK  id               │                            │
          │ FK  pedido_id ───────┤ (N:1)                      │
          │ FK  produto_id ──────┼──┐                         │
          │     quantidade       │  │                         │
          │     preco_unitario   │  │                         │
          │     subtotal         │  │                         │
          └──────────────────────┘  │                         │
                                    │                         │
                                    ▼                         │
                    ┌───────────────────────────────┐         │
                    │       PRODUTOS                │         │
                    ├───────────────────────────────┤         │
                    │ PK  id                        │         │
                    │     nome (VARCHAR)            │         │
                    │     descricao                 │         │
                    │     preco (DECIMAL)           │◄────────┘
                    │     estoque (INTEGER)         │
                    │     categoria                 │
                    │     data_criacao (TIMESTAMP)  │
                    └───────────────────────────────┘
```

## Legendas

- **PK**: Primary Key (Chave Primária)
- **FK**: Foreign Key (Chave Estrangeira)
- **UQ**: Unique (Único)
- **1:N**: Um para Muitos
- **N:1**: Muitos para Um

---

## Relacionamentos Detalhados

### 1. CLIENTES → PEDIDOS (1:N)
- Um cliente pode ter **muitos pedidos**
- Foreign Key: `pedidos.cliente_id` referencia `clientes.id`
- Cascata: ON DELETE CASCADE

### 2. CLIENTES → PAGAMENTOS (1:N)
- Um cliente pode fazer **muitos pagamentos**
- Foreign Key: `pagamentos.cliente_id` referencia `clientes.id`
- Cascata: ON DELETE CASCADE

### 3. PEDIDOS → ITENS_PEDIDO (1:N)
- Um pedido pode ter **muitos itens**
- Foreign Key: `itens_pedido.pedido_id` referencia `pedidos.id`
- Cascata: ON DELETE CASCADE

### 4. PRODUTOS → ITENS_PEDIDO (1:N)
- Um produto pode aparecer em **muitos itens de pedidos**
- Foreign Key: `itens_pedido.produto_id` referencia `produtos.id`
- Cascata: ON DELETE CASCADE

### 5. PEDIDOS → PAGAMENTOS (1:N)
- Um pedido pode ter **múltiplos pagamentos**
- Foreign Key: `pagamentos.pedido_id` referencia `pedidos.id`
- Cascata: ON DELETE CASCADE

---

## Fluxo de Dados (Exemplo)

```
1. Cliente JOÃO é criado
   └─> clientes.id = 1

2. Produto NOTEBOOK é criado
   └─> produtos.id = 1

3. João faz um PEDIDO
   └─> pedidos.id = 1
   └─> pedidos.cliente_id = 1

4. Adicionar NOTEBOOK ao pedido
   └─> itens_pedido.id = 1
   └─> itens_pedido.pedido_id = 1
   └─> itens_pedido.produto_id = 1
   └─> itens_pedido.quantidade = 2
   └─> itens_pedido.subtotal = 6000.00

5. João realiza PAGAMENTO
   └─> pagamentos.id = 1
   └─> pagamentos.cliente_id = 1
   └─> pagamentos.pedido_id = 1
   └─> pagamentos.valor = 6000.00
   └─> pagamentos.status = 'confirmado'
```

---

## Integridade Referencial

### Constraints de Integridade

```sql
-- PRIMARY KEYS
clientes.id PRIMARY KEY
produtos.id PRIMARY KEY
pedidos.id PRIMARY KEY
itens_pedido.id PRIMARY KEY
pagamentos.id PRIMARY KEY

-- FOREIGN KEYS com cascata
pedidos.cliente_id → clientes.id (ON DELETE CASCADE)
itens_pedido.pedido_id → pedidos.id (ON DELETE CASCADE)
itens_pedido.produto_id → produtos.id (ON DELETE CASCADE)
pagamentos.cliente_id → clientes.id (ON DELETE CASCADE)
pagamentos.pedido_id → pedidos.id (ON DELETE CASCADE)

-- UNIQUE CONSTRAINTS
clientes.email UNIQUE

-- CHECK CONSTRAINTS
produtos.preco > 0
produtos.estoque >= 0
pedidos.total >= 0
itens_pedido.quantidade > 0
itens_pedido.preco_unitario > 0
pagamentos.valor > 0
```

---

## Exemplo de Consulta JOIN Complexa

```sql
-- Listar pedidos com detalhes do cliente, itens e produtos
SELECT 
    c.nome AS cliente,
    p.id AS pedido_id,
    p.data_pedido,
    p.status,
    pr.nome AS produto,
    ip.quantidade,
    ip.preco_unitario,
    ip.subtotal
FROM clientes c
INNER JOIN pedidos p ON c.id = p.cliente_id
INNER JOIN itens_pedido ip ON p.id = ip.pedido_id
INNER JOIN produtos pr ON ip.produto_id = pr.id
ORDER BY c.nome, p.data_pedido DESC;
```

---

## Índices para Otimização

```sql
-- Índices simples
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX idx_itens_pedido_pedido ON itens_pedido(pedido_id);
CREATE INDEX idx_itens_pedido_produto ON itens_pedido(produto_id);
CREATE INDEX idx_pagamentos_cliente ON pagamentos(cliente_id);
CREATE INDEX idx_pagamentos_pedido ON pagamentos(pedido_id);

-- Índices compostos
CREATE INDEX idx_pedidos_cliente_data ON pedidos(cliente_id, data_pedido DESC);
CREATE INDEX idx_pagamentos_cliente_status ON pagamentos(cliente_id, status);
```
