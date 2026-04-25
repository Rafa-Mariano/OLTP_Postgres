-- ============================================================
-- SCRIPT DE CRIAÇÃO DE ÍNDICES - SISTEMA OLTP DE VENDAS
-- ============================================================
-- Índices foram cuidadosamente selecionados para otimizar
-- as queries mais comuns e melhorar a performance
-- ============================================================

-- 1. ÍNDICES NA TABELA PEDIDOS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente 
    ON pedidos(cliente_id);
    
CREATE INDEX IF NOT EXISTS idx_pedidos_data 
    ON pedidos(data_pedido DESC);
    
CREATE INDEX IF NOT EXISTS idx_pedidos_status 
    ON pedidos(status);

-- 2. ÍNDICES NA TABELA ITENS_PEDIDO
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido 
    ON itens_pedido(pedido_id);
    
CREATE INDEX IF NOT EXISTS idx_itens_pedido_produto 
    ON itens_pedido(produto_id);

-- 3. ÍNDICES NA TABELA PAGAMENTOS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_pagamentos_cliente 
    ON pagamentos(cliente_id);
    
CREATE INDEX IF NOT EXISTS idx_pagamentos_pedido 
    ON pagamentos(pedido_id);
    
CREATE INDEX IF NOT EXISTS idx_pagamentos_data 
    ON pagamentos(data_pagamento DESC);
    
CREATE INDEX IF NOT EXISTS idx_pagamentos_status 
    ON pagamentos(status);

-- 4. ÍNDICES NA TABELA CLIENTES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_clientes_email 
    ON clientes(email);
    
CREATE INDEX IF NOT EXISTS idx_clientes_data_cadastro 
    ON clientes(data_cadastro DESC);

-- 5. ÍNDICES NA TABELA PRODUTOS
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_produtos_categoria 
    ON produtos(categoria);
    
CREATE INDEX IF NOT EXISTS idx_produtos_estoque 
    ON produtos(estoque);

-- 6. ÍNDICES COMPOSTOS (PARA QUERIES MAIS COMPLEXAS)
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_status 
    ON pedidos(cliente_id, status);
    
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_data 
    ON pedidos(cliente_id, data_pedido DESC);
    
CREATE INDEX IF NOT EXISTS idx_pagamentos_cliente_status 
    ON pagamentos(cliente_id, status);

-- ============================================================
-- ANÁLISE DE DESEMPENHO
-- ============================================================
-- Para analisar o desempenho das queries, use:
-- EXPLAIN ANALYZE <sua_query>;
-- 
-- Exemplos:
-- EXPLAIN ANALYZE SELECT * FROM pedidos WHERE cliente_id = 1;
-- EXPLAIN ANALYZE SELECT * FROM pagamentos WHERE data_pagamento > NOW() - INTERVAL '30 days';
-- ============================================================

-- ============================================================
-- DICAS PARA MANUTENÇÃO
-- ============================================================
-- Periodicamente, execute VACUUM e ANALYZE:
-- VACUUM ANALYZE;
-- 
-- Para visualizar estatísticas do índice:
-- SELECT * FROM pg_stat_user_indexes;
-- 
-- Para visualizar tamanho dos índices:
-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     pg_size_pretty(pg_relation_size(indexrelid)) as size
-- FROM pg_stat_user_indexes
-- ORDER BY pg_relation_size(indexrelid) DESC;
-- ============================================================
