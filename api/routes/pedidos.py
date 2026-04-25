"""
Rotas para CRUD de Pedidos
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Pedido, ItemPedido, Produto, Cliente
from ..schemas import (
    PedidoCreate, PedidoUpdate, PedidoResponse, 
    ItemPedidoResponse, MessageResponse
)

router = APIRouter(prefix="/pedidos")


@router.post("", response_model=PedidoResponse, status_code=201)
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    """Criar um novo pedido com itens"""
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == pedido.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    try:
        # Criar pedido
        novo_pedido = Pedido(cliente_id=pedido.cliente_id)
        db.add(novo_pedido)
        db.flush()  # Gerar ID
        
        # Adicionar itens
        total = 0
        for item in pedido.itens:
            # Verificar se produto existe
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if not produto:
                raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
            
            # Verificar estoque
            if produto.estoque < item.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para {produto.nome}"
                )
            
            # Criar item
            item_pedido = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                subtotal=item.quantidade * item.preco_unitario
            )
            db.add(item_pedido)
            
            # Atualizar estoque
            produto.estoque -= item.quantidade
            
            total += item_pedido.subtotal
        
        novo_pedido.total = total
        db.commit()
        db.refresh(novo_pedido)
        return novo_pedido
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[PedidoResponse])
def listar_pedidos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = None,
    cliente_id: int = None,
    db: Session = Depends(get_db)
):
    """Listar pedidos com filtros e paginação"""
    query = db.query(Pedido)
    
    if status:
        query = query.filter(Pedido.status == status)
    
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    
    return query.order_by(Pedido.data_pedido.desc()).offset(skip).limit(limit).all()


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de um pedido"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.put("/{pedido_id}", response_model=PedidoResponse)
def atualizar_pedido(
    pedido_id: int,
    pedido_update: PedidoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar status de um pedido"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    for key, value in pedido_update.dict(exclude_unset=True).items():
        setattr(pedido, key, value)
    
    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{pedido_id}", response_model=MessageResponse)
def deletar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Deletar um pedido"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    db.delete(pedido)
    db.commit()
    return {"message": "Pedido deletado com sucesso"}


@router.get("/{pedido_id}/itens", response_model=List[ItemPedidoResponse])
def listar_itens_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Listar itens de um pedido"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return pedido.itens_pedido


@router.get("/relatorio/resumo", response_model=dict, tags=["Relatórios"])
def resumo_pedidos(db: Session = Depends(get_db)):
    """Resumo de pedidos por status"""
    resultado = db.query(
        Pedido.status,
        func.count(Pedido.id).label("quantidade"),
        func.sum(Pedido.total).label("total")
    ).group_by(Pedido.status).all()
    
    return {
        "resumo": [
            {
                "status": r[0],
                "quantidade": r[1],
                "total": float(r[2]) if r[2] else 0
            }
            for r in resultado
        ]
    }
