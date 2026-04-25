-- ============================================================
-- QUERIES ANALÍTICAS COMPLEXAS - SISTEMA OLTP DE VENDAS
-- ============================================================
-- Queries úteis para análise de dados e business intelligence
-- ============================================================

-- 1. FATURAMENTO MENSAL
-- ============================================================
-- Calcula o total de faturamento agrupado por mês
SELECT 
    DATE_TRUNC('month', p.data_pagamento)::DATE AS mes,
    COUNT(DISTINCT p.pedido_id) AS total_pedidos,
    COUNT(DISTINCT p.cliente_id) AS total_clientes,
    SUM(p.valor)::DECIMAL(10,2) AS total_faturado,
    AVG(p.valor)::DECIMAL(10,2) AS valor_medio_pagamento
FROM pagamentos p
WHERE p.status = 'confirmado'
GROUP BY DATE_TRUNC('month', p.data_pagamento)
ORDER BY mes DESC;

-- 2. TOP 10 CLIENTES QUE MAIS COMPRAM
-- ============================================================
-- Clientes com maior volume de compras (quantidade e valor)
SELECT 
    c.id,
    c.nome,
    c.email,
    COUNT(DISTINCT ped.id) AS total_pedidos,
    SUM(ped.total)::DECIMAL(10,2) AS total_gasto,
    AVG(ped.total)::DECIMAL(10,2) AS ticket_medio,
    MAX(ped.data_pedido) AS ultima_compra
FROM clientes c
LEFT JOIN pedidos ped ON c.id = ped.cliente_id
GROUP BY c.id, c.nome, c.email
HAVING COUNT(ped.id) > 0
ORDER BY total_gasto DESC
LIMIT 10;

-- 3. TICKET MÉDIO POR CLIENTE
-- ============================================================
-- Análise do comportamento de gasto dos clientes
SELECT 
    c.nome,
    COUNT(ped.id) AS numero_pedidos,
    SUM(ped.total)::DECIMAL(10,2) AS total_gasto,
    AVG(ped.total)::DECIMAL(10,2) AS ticket_medio,
    MIN(ped.total)::DECIMAL(10,2) AS menor_pedido,
    MAX(ped.total)::DECIMAL(10,2) AS maior_pedido,
    STDDEV(ped.total)::DECIMAL(10,2) AS desvio_padrao
FROM clientes c
JOIN pedidos ped ON c.id = ped.cliente_id
GROUP BY c.id, c.nome
ORDER BY ticket_medio DESC;

-- 4. PRODUTOS MAIS VENDIDOS
-- ============================================================
-- Ranking de produtos por quantidade vendida e receita
SELECT 
    pr.id,
    pr.nome,
    pr.categoria,
    SUM(ip.quantidade) AS quantidade_vendida,
    COUNT(DISTINCT ip.pedido_id) AS numero_vendas,
    SUM(ip.subtotal)::DECIMAL(10,2) AS receita_total,
    AVG(ip.quantidade)::DECIMAL(5,2) AS media_quantidade_por_venda,
    pr.estoque AS estoque_atual
FROM produtos pr
LEFT JOIN itens_pedido ip ON pr.id = ip.produto_id
GROUP BY pr.id, pr.nome, pr.categoria, pr.estoque
ORDER BY quantidade_vendida DESC
LIMIT 20;

-- 5. STATUS DOS PEDIDOS
-- ============================================================
-- Distribuição de pedidos por status
SELECT 
    status,
    COUNT(*) AS quantidade,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentual,
    SUM(total)::DECIMAL(10,2) AS valor_total,
    AVG(total)::DECIMAL(10,2) AS valor_medio
FROM pedidos
GROUP BY status
ORDER BY quantidade DESC;

-- 6. ANÁLISE DE PAGAMENTOS
-- ============================================================
-- Distribuição de pagamentos por método e status
SELECT 
    metodo,
    status,
    COUNT(*) AS quantidade,
    SUM(valor)::DECIMAL(10,2) AS total_valor,
    AVG(valor)::DECIMAL(10,2) AS valor_medio,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY metodo), 2) AS percentual_por_metodo
FROM pagamentos
GROUP BY metodo, status
ORDER BY metodo, quantidade DESC;

-- 7. PRODUTOS POR CATEGORIA
-- ============================================================
-- Análise de vendas por categoria de produto
SELECT 
    pr.categoria,
    COUNT(DISTINCT pr.id) AS total_produtos,
    SUM(ip.quantidade) AS quantidade_vendida,
    SUM(ip.subtotal)::DECIMAL(10,2) AS receita,
    AVG(pr.preco)::DECIMAL(10,2) AS preco_medio,
    SUM(pr.estoque) AS estoque_total
FROM produtos pr
LEFT JOIN itens_pedido ip ON pr.id = ip.produto_id
GROUP BY pr.categoria
ORDER BY receita DESC NULLS LAST;

-- 8. CLIENTES INATIVOS
-- ============================================================
-- Clientes que não compraram nos últimos 30 dias
SELECT 
    c.id,
    c.nome,
    c.email,
    MAX(ped.data_pedido) AS ultima_compra,
    NOW() - MAX(ped.data_pedido) AS dias_inativo,
    COUNT(ped.id) AS total_pedidos,
    SUM(ped.total)::DECIMAL(10,2) AS total_gasto
FROM clientes c
LEFT JOIN pedidos ped ON c.id = ped.cliente_id
GROUP BY c.id, c.nome, c.email
HAVING MAX(ped.data_pedido) IS NULL OR MAX(ped.data_pedido) < NOW() - INTERVAL '30 days'
ORDER BY ultima_compra ASC NULLS FIRST;

-- 9. ANÁLISE DE CRESCIMENTO DIÁRIO
-- ============================================================
-- Crescimento de vendas dia a dia
SELECT 
    DATE(ped.data_pedido) AS data,
    COUNT(*) AS numero_pedidos,
    SUM(ped.total)::DECIMAL(10,2) AS faturamento_dia,
    COUNT(DISTINCT ped.cliente_id) AS clientes_unicos,
    SUM(SUM(ped.total)) OVER (ORDER BY DATE(ped.data_pedido)) AS faturamento_acumulado
FROM pedidos ped
WHERE ped.status IN ('confirmado', 'enviado', 'entregue')
GROUP BY DATE(ped.data_pedido)
ORDER BY data DESC;

-- 10. ANÁLISE DE CHURN (PERDA DE CLIENTES)
-- ============================================================
-- Clientes que fizeram apenas uma compra
SELECT 
    c.id,
    c.nome,
    c.email,
    ped.data_pedido AS data_primeira_compra,
    ped.total AS valor_compra,
    CURRENT_DATE - ped.data_pedido::DATE AS dias_desde_compra
FROM clientes c
JOIN pedidos ped ON c.id = ped.cliente_id
WHERE c.id NOT IN (
    SELECT cliente_id FROM pedidos GROUP BY cliente_id HAVING COUNT(*) > 1
)
ORDER BY dias_desde_compra DESC;

-- 11. CORRELAÇÃO ENTRE QUANTIDADE DE PRODUTOS E VALOR TOTAL
-- ============================================================
-- Análise de vendas cruzadas
SELECT 
    COUNT(DISTINCT ip.pedido_id) AS numero_pedidos,
    COUNT(DISTINCT ip.produto_id) AS quantidade_itens_diferentes,
    SUM(ip.quantidade) AS total_itens_pedidos,
    AVG(ped.total)::DECIMAL(10,2) AS ticket_medio,
    ROUND(SUM(ped.total)::DECIMAL(10,2) / COUNT(DISTINCT ip.pedido_id), 2) AS valor_medio_por_item
FROM itens_pedido ip
JOIN pedidos ped ON ip.pedido_id = ped.id;

-- 12. PRODUTOS COM BAIXO ESTOQUE
-- ============================================================
-- Alertas para reposição de estoque
SELECT 
    id,
    nome,
    categoria,
    estoque,
    preco,
    CASE 
        WHEN estoque = 0 THEN 'CRÍTICO'
        WHEN estoque < 10 THEN 'BAIXO'
        WHEN estoque < 50 THEN 'MÉDIO'
        ELSE 'OK'
    END AS status_estoque
FROM produtos
WHERE estoque < 50
ORDER BY estoque ASC;

-- 13. RECEITA POR CLIENTE POR MÊS
-- ============================================================
-- Análise temporal de receita por cliente (útil para RFM)
SELECT 
    c.nome,
    DATE_TRUNC('month', ped.data_pedido)::DATE AS mes,
    COUNT(ped.id) AS numero_pedidos,
    SUM(ped.total)::DECIMAL(10,2) AS receita_mes
FROM clientes c
JOIN pedidos ped ON c.id = ped.cliente_id
GROUP BY c.id, c.nome, DATE_TRUNC('month', ped.data_pedido)
ORDER BY c.nome, mes DESC;

-- 14. ANÁLISE RFM (Recência, Frequência, Monetária)
-- ============================================================
-- Segmentação de clientes para marketing
SELECT 
    c.id,
    c.nome,
    (CURRENT_DATE - MAX(ped.data_pedido)::DATE) AS recencia_dias,
    COUNT(ped.id) AS frequencia_compras,
    SUM(ped.total)::DECIMAL(10,2) AS valor_monetario,
    CASE 
        WHEN (CURRENT_DATE - MAX(ped.data_pedido)::DATE) <= 30 THEN 'Recente'
        WHEN (CURRENT_DATE - MAX(ped.data_pedido)::DATE) <= 90 THEN 'Médio'
        ELSE 'Antigo'
    END AS faixa_recencia,
    CASE 
        WHEN COUNT(ped.id) >= 10 THEN 'Frequente'
        WHEN COUNT(ped.id) >= 5 THEN 'Moderado'
        ELSE 'Ocasional'
    END AS faixa_frequencia,
    CASE 
        WHEN SUM(ped.total) >= 5000 THEN 'Alto Valor'
        WHEN SUM(ped.total) >= 1000 THEN 'Médio Valor'
        ELSE 'Baixo Valor'
    END AS faixa_monetaria
FROM clientes c
LEFT JOIN pedidos ped ON c.id = ped.cliente_id
WHERE ped.id IS NOT NULL
GROUP BY c.id, c.nome
ORDER BY valor_monetario DESC;
