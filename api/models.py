"""
Modelos SQLAlchemy para o banco de dados
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Cliente(Base):
    """Modelo de Cliente"""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefone = Column(String(20))
    endereco = Column(Text, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow, index=True)

    # Relacionamentos
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", back_populates="cliente", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('email', name='uq_cliente_email'),
    )


class Produto(Base):
    """Modelo de Produto"""
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric(10, 2), nullable=False)
    estoque = Column(Integer, default=0, index=True)
    categoria = Column(String(50), index=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    itens_pedido = relationship("ItemPedido", back_populates="produto")

    __table_args__ = (
        CheckConstraint('preco > 0', name='ck_produto_preco_positivo'),
        CheckConstraint('estoque >= 0', name='ck_produto_estoque_nao_negativo'),
    )


class Pedido(Base):
    """Modelo de Pedido"""
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True)
    data_pedido = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), default="pendente", index=True)
    total = Column(Numeric(10, 2), default=0, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="pedidos")
    itens_pedido = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", back_populates="pedido", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('pendente', 'confirmado', 'enviado', 'entregue', 'cancelado')", 
                       name='ck_pedido_status'),
        CheckConstraint('total >= 0', name='ck_pedido_total_positivo'),
    )


class ItemPedido(Base):
    """Modelo de Item do Pedido"""
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens_pedido")
    produto = relationship("Produto", back_populates="itens_pedido")

    __table_args__ = (
        CheckConstraint('quantidade > 0', name='ck_item_quantidade_positiva'),
        CheckConstraint('preco_unitario > 0', name='ck_item_preco_positivo'),
        CheckConstraint('subtotal > 0', name='ck_item_subtotal_positivo'),
    )


class Pagamento(Base):
    """Modelo de Pagamento"""
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False, index=True)
    valor = Column(Numeric(10, 2), nullable=False)
    data_pagamento = Column(DateTime, default=datetime.utcnow, index=True)
    metodo = Column(String(30), default="credito")
    status = Column(String(20), default="pendente", index=True)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="pagamentos")
    pedido = relationship("Pedido", back_populates="pagamentos")

    __table_args__ = (
        CheckConstraint("metodo IN ('credito', 'debito', 'boleto', 'pix', 'dinheiro')", 
                       name='ck_pagamento_metodo'),
        CheckConstraint("status IN ('pendente', 'confirmado', 'cancelado', 'reembolso')", 
                       name='ck_pagamento_status'),
        CheckConstraint('valor > 0', name='ck_pagamento_valor_positivo'),
    )
