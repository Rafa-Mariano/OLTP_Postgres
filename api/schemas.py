"""
Schemas Pydantic para validação de dados
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal


# ==================== CLIENTE ====================

class ClienteBase(BaseModel):
    """Base para schemas de Cliente"""
    nome: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: str = Field(..., min_length=1)

    @validator('nome')
    def nome_nao_vazio(cls, v):
        if not v.strip():
            raise ValueError('Nome não pode ser vazio')
        return v.strip()


class ClienteCreate(ClienteBase):
    """Schema para criação de Cliente"""
    pass


class ClienteUpdate(BaseModel):
    """Schema para atualização de Cliente"""
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None


class ClienteResponse(ClienteBase):
    """Schema de resposta para Cliente"""
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True


# ==================== PRODUTO ====================

class ProdutoBase(BaseModel):
    """Base para schemas de Produto"""
    nome: str = Field(..., min_length=1, max_length=150)
    descricao: Optional[str] = None
    preco: Decimal = Field(..., gt=0, decimal_places=2)
    estoque: int = Field(default=0, ge=0)
    categoria: Optional[str] = Field(None, max_length=50)

    @validator('preco')
    def preco_valido(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v


class ProdutoCreate(ProdutoBase):
    """Schema para criação de Produto"""
    pass


class ProdutoUpdate(BaseModel):
    """Schema para atualização de Produto"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[Decimal] = None
    estoque: Optional[int] = None
    categoria: Optional[str] = None


class ProdutoResponse(ProdutoBase):
    """Schema de resposta para Produto"""
    id: int
    data_criacao: datetime

    class Config:
        from_attributes = True


# ==================== ITEM PEDIDO ====================

class ItemPedidoBase(BaseModel):
    """Base para schemas de ItemPedido"""
    produto_id: int
    quantidade: int = Field(..., gt=0)
    preco_unitario: Decimal = Field(..., gt=0, decimal_places=2)


class ItemPedidoCreate(ItemPedidoBase):
    """Schema para criação de ItemPedido"""
    pass


class ItemPedidoResponse(ItemPedidoBase):
    """Schema de resposta para ItemPedido"""
    id: int
    pedido_id: int
    subtotal: Decimal
    produto: Optional[ProdutoResponse] = None

    class Config:
        from_attributes = True


# ==================== PEDIDO ====================

class PedidoBase(BaseModel):
    """Base para schemas de Pedido"""
    cliente_id: int
    status: str = Field(default="pendente")


class PedidoCreate(PedidoBase):
    """Schema para criação de Pedido"""
    itens: List[ItemPedidoCreate] = Field(..., min_items=1)


class PedidoUpdate(BaseModel):
    """Schema para atualização de Pedido"""
    status: Optional[str] = None


class PedidoResponse(PedidoBase):
    """Schema de resposta para Pedido"""
    id: int
    data_pedido: datetime
    total: Decimal
    data_criacao: datetime
    cliente: Optional[ClienteResponse] = None
    itens_pedido: List[ItemPedidoResponse] = []

    class Config:
        from_attributes = True


# ==================== PAGAMENTO ====================

class PagamentoBase(BaseModel):
    """Base para schemas de Pagamento"""
    cliente_id: int
    pedido_id: int
    valor: Decimal = Field(..., gt=0, decimal_places=2)
    metodo: str = Field(default="credito")
    status: str = Field(default="pendente")


class PagamentoCreate(PagamentoBase):
    """Schema para criação de Pagamento"""
    pass


class PagamentoUpdate(BaseModel):
    """Schema para atualização de Pagamento"""
    status: Optional[str] = None
    metodo: Optional[str] = None


class PagamentoResponse(PagamentoBase):
    """Schema de resposta para Pagamento"""
    id: int
    data_pagamento: datetime
    cliente: Optional[ClienteResponse] = None
    pedido: Optional[PedidoResponse] = None

    class Config:
        from_attributes = True


# ==================== RESPONSES ====================

class MessageResponse(BaseModel):
    """Response genérico com mensagem"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response de erro"""
    error: str
    detail: Optional[str] = None
    status_code: int
