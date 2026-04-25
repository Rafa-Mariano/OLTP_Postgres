"""
Rotas para CRUD de Pagamentos
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Pagamento, Pedido, Cliente
from ..schemas import PagamentoCreate, PagamentoUpdate, PagamentoResponse, MessageResponse

router = APIRouter(prefix="/pagamentos")


@router.post("", response_model=PagamentoResponse, status_code=201)
def criar_pagamento(pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    """Criar um novo pagamento"""
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == pagamento.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar se pedido existe
    pedido = db.query(Pedido).filter(Pedido.id == pagamento.pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Verificar se pedido pertence ao cliente
    if pedido.cliente_id != pagamento.cliente_id:
        raise HTTPException(status_code=400, detail="Pedido não pertence ao cliente")
    
    novo_pagamento = Pagamento(**pagamento.dict())
    db.add(novo_pagamento)
    db.commit()
    db.refresh(novo_pagamento)
    return novo_pagamento


@router.get("", response_model=List[PagamentoResponse])
def listar_pagamentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = None,
    cliente_id: int = None,
    metodo: str = None,
    db: Session = Depends(get_db)
):
    """Listar pagamentos com filtros e paginação"""
    query = db.query(Pagamento)
    
    if status:
        query = query.filter(Pagamento.status == status)
    
    if cliente_id:
        query = query.filter(Pagamento.cliente_id == cliente_id)
    
    if metodo:
        query = query.filter(Pagamento.metodo == metodo)
    
    return query.order_by(Pagamento.data_pagamento.desc()).offset(skip).limit(limit).all()


@router.get("/{pagamento_id}", response_model=PagamentoResponse)
def obter_pagamento(pagamento_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de um pagamento"""
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento


@router.put("/{pagamento_id}", response_model=PagamentoResponse)
def atualizar_pagamento(
    pagamento_id: int,
    pagamento_update: PagamentoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar dados de um pagamento"""
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    for key, value in pagamento_update.dict(exclude_unset=True).items():
        setattr(pagamento, key, value)
    
    db.commit()
    db.refresh(pagamento)
    return pagamento


@router.delete("/{pagamento_id}", response_model=MessageResponse)
def deletar_pagamento(pagamento_id: int, db: Session = Depends(get_db)):
    """Deletar um pagamento"""
    pagamento = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    db.delete(pagamento)
    db.commit()
    return {"message": "Pagamento deletado com sucesso"}


@router.get("/relatorio/resumo", response_model=dict, tags=["Relatórios"])
def resumo_pagamentos(db: Session = Depends(get_db)):
    """Resumo de pagamentos por status e método"""
    resultado = db.query(
        Pagamento.status,
        Pagamento.metodo,
        func.count(Pagamento.id).label("quantidade"),
        func.sum(Pagamento.valor).label("total")
    ).group_by(Pagamento.status, Pagamento.metodo).all()
    
    return {
        "resumo": [
            {
                "status": r[0],
                "metodo": r[1],
                "quantidade": r[2],
                "total": float(r[3]) if r[3] else 0
            }
            for r in resultado
        ]
    }


@router.get("/cliente/{cliente_id}", response_model=List[PagamentoResponse])
def pagamentos_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Listar todos os pagamentos de um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return db.query(Pagamento).filter(
        Pagamento.cliente_id == cliente_id
    ).order_by(Pagamento.data_pagamento.desc()).all()
