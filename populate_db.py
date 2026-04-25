"""
Script para popular o banco com dados de teste
"""
import os
os.environ['PGCLIENTENCODING'] = 'UTF8'

from sqlalchemy.orm import Session
from api.database import SessionLocal, engine
from api.models import Base, Cliente, Produto, Pedido, ItemPedido, Pagamento
from datetime import datetime, timedelta
from decimal import Decimal

# Criar tabelas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Limpar dados existentes
    db.query(Pagamento).delete()
    db.query(ItemPedido).delete()
    db.query(Pedido).delete()
    db.query(Produto).delete()
    db.query(Cliente).delete()
    
    # Criar clientes
    clientes = [
        Cliente(
            nome="João Silva",
            email="joao@example.com",
            telefone="11999999999",
            endereco="Rua A, 123 - São Paulo"
        ),
        Cliente(
            nome="Maria Santos",
            email="maria@example.com",
            telefone="11988888888",
            endereco="Rua B, 456 - Rio de Janeiro"
        ),
        Cliente(
            nome="Pedro Oliveira",
            email="pedro@example.com",
            telefone="11977777777",
            endereco="Rua C, 789 - Belo Horizonte"
        ),
        Cliente(
            nome="Ana Costa",
            email="ana@example.com",
            telefone="11966666666",
            endereco="Rua D, 321 - Brasília"
        ),
        Cliente(
            nome="Carlos Ferreira",
            email="carlos@example.com",
            telefone="11955555555",
            endereco="Rua E, 654 - Salvador"
        ),
    ]
    db.add_all(clientes)
    db.commit()
    print(f"✅ {len(clientes)} clientes criados")
    
    # Criar produtos
    produtos = [
        Produto(
            nome="Notebook Dell",
            descricao="Notebook com processador Intel i7",
            preco=Decimal("3000.00"),
            estoque=15,
            categoria="Eletrônicos"
        ),
        Produto(
            nome="Mouse Logitech",
            descricao="Mouse sem fio",
            preco=Decimal("150.00"),
            estoque=50,
            categoria="Periféricos"
        ),
        Produto(
            nome="Teclado Mecânico",
            descricao="Teclado RGB com switches Cherry MX",
            preco=Decimal("450.00"),
            estoque=25,
            categoria="Periféricos"
        ),
        Produto(
            nome="Monitor LG 27\"",
            descricao="Monitor 4K UltraWide",
            preco=Decimal("1500.00"),
            estoque=10,
            categoria="Monitores"
        ),
        Produto(
            nome="Webcam Logitech",
            descricao="Webcam 1080p com microfone",
            preco=Decimal("350.00"),
            estoque=30,
            categoria="Periféricos"
        ),
        Produto(
            nome="Fone Headset",
            descricao="Fone gamer com som surround",
            preco=Decimal("250.00"),
            estoque=40,
            categoria="Áudio"
        ),
    ]
    db.add_all(produtos)
    db.commit()
    print(f"✅ {len(produtos)} produtos criados")
    
    # Criar pedidos e itens
    data_atual = datetime.now()
    for i in range(10):
        cliente = clientes[i % len(clientes)]
        produto1 = produtos[i % len(produtos)]
        produto2 = produtos[(i + 1) % len(produtos)]
        
        pedido = Pedido(
            cliente_id=cliente.id,
            data_pedido=data_atual - timedelta(days=i),
            status="entregue" if i % 3 == 0 else "confirmado",
            total=Decimal("0")
        )
        db.add(pedido)
        db.flush()
        
        # Item 1
        item1 = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto1.id,
            quantidade=1 if i % 2 == 0 else 2,
            preco_unitario=produto1.preco,
            subtotal=Decimal(str(1 if i % 2 == 0 else 2)) * produto1.preco
        )
        db.add(item1)
        
        # Item 2
        item2 = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto2.id,
            quantidade=1,
            preco_unitario=produto2.preco,
            subtotal=produto2.preco
        )
        db.add(item2)
        
        # Atualizar total
        pedido.total = item1.subtotal + item2.subtotal
    
    db.commit()
    print(f"✅ 10 pedidos criados com itens")
    
    # Criar pagamentos
    for pedido in db.query(Pedido).all():
        pagamento = Pagamento(
            cliente_id=pedido.cliente_id,
            pedido_id=pedido.id,
            valor=pedido.total,
            data_pagamento=pedido.data_pedido + timedelta(hours=2),
            metodo="credito" if pedido.id % 2 == 0 else "pix",
            status="confirmado"
        )
        db.add(pagamento)
    
    db.commit()
    print(f"✅ Pagamentos criados")
    
    print("\n✨ Dados de teste população com sucesso!")
    
except Exception as e:
    db.rollback()
    print(f"❌ Erro: {e}")
finally:
    db.close()
