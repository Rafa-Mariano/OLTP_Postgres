-- ============================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS - SISTEMA OLTP DE VENDAS
-- ============================================================
-- Este script cria toda a estrutura do banco de dados
-- com tabelas, relacionamentos e constraints
-- ============================================================

-- 1. TABELA CLIENTES
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    endereco TEXT NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT email_valid CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- 2. TABELA PRODUTOS
-- ============================================================
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    estoque INTEGER DEFAULT 0,
    categoria VARCHAR(50),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT preco_positivo CHECK (preco > 0),
    CONSTRAINT estoque_nao_negativo CHECK (estoque >= 0)
);

-- 3. TABELA PEDIDOS
-- ============================================================
CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN ('pendente', 'confirmado', 'enviado', 'entregue', 'cancelado')),
    total DECIMAL(10, 2) NOT NULL DEFAULT 0,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    CONSTRAINT total_positivo CHECK (total >= 0)
);

-- 4. TABELA ITENS_PEDIDO
-- ============================================================
CREATE TABLE IF NOT EXISTS itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
    CONSTRAINT quantidade_positiva CHECK (quantidade > 0),
    CONSTRAINT preco_unitario_positivo CHECK (preco_unitario > 0),
    CONSTRAINT subtotal_valido CHECK (subtotal = quantidade * preco_unitario)
);

-- 5. TABELA PAGAMENTOS
-- ============================================================
CREATE TABLE IF NOT EXISTS pagamentos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    pedido_id INTEGER NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo VARCHAR(30) CHECK (metodo IN ('credito', 'debito', 'boleto', 'pix', 'dinheiro')),
    status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN ('pendente', 'confirmado', 'cancelado', 'reembolso')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    CONSTRAINT valor_positivo CHECK (valor > 0)
);

-- ============================================================
-- SEQUENCES (para IDs)
-- ============================================================
CREATE SEQUENCE IF NOT EXISTS clientes_id_seq;
CREATE SEQUENCE IF NOT EXISTS produtos_id_seq;
CREATE SEQUENCE IF NOT EXISTS pedidos_id_seq;
CREATE SEQUENCE IF NOT EXISTS itens_pedido_id_seq;
CREATE SEQUENCE IF NOT EXISTS pagamentos_id_seq;

-- ============================================================
-- COMENTÁRIOS NAS TABELAS
-- ============================================================
COMMENT ON TABLE clientes IS 'Tabela de armazenamento de informações dos clientes';
COMMENT ON TABLE produtos IS 'Catálogo de produtos disponíveis para venda';
COMMENT ON TABLE pedidos IS 'Registro de todos os pedidos realizados';
COMMENT ON TABLE itens_pedido IS 'Itens individuais que compõem cada pedido';
COMMENT ON TABLE pagamentos IS 'Histórico de pagamentos dos clientes';

-- ============================================================
-- COMMIT
-- ============================================================
-- Todas as tabelas foram criadas com sucesso!
