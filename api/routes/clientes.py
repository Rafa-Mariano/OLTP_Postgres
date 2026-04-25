"""
Rotas para CRUD de Clientes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Cliente
from ..schemas import ClienteCreate, ClienteUpdate, ClienteResponse, MessageResponse

router = APIRouter(prefix="/clientes")


@router.post("", response_model=ClienteResponse, status_code=201)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Criar um novo cliente"""
    # Verificar se email já existe
    db_cliente = db.query(Cliente).filter(Cliente.email == cliente.email).first()
    if db_cliente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criar novo cliente
    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente


@router.get("", response_model=List[ClienteResponse])
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nome: str = None,
    email: str = None,
    db: Session = Depends(get_db)
):
    """Listar clientes com filtros e paginação"""
    query = db.query(Cliente)
    
    if nome:
        query = query.filter(Cliente.nome.ilike(f"%{nome}%"))
    
    if email:
        query = query.filter(Cliente.email.ilike(f"%{email}%"))
    
    return query.offset(skip).limit(limit).all()


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar dados de um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar email único
    if cliente_update.email and cliente_update.email != cliente.email:
        email_existe = db.query(Cliente).filter(
            Cliente.email == cliente_update.email
        ).first()
        if email_existe:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Atualizar
    for key, value in cliente_update.dict(exclude_unset=True).items():
        setattr(cliente, key, value)
    
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", response_model=MessageResponse)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Deletar um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente deletado com sucesso"}


@router.get("/{cliente_id}/pedidos", response_model=List[dict])
def listar_pedidos_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Listar todos os pedidos de um cliente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return [
        {
            "id": pedido.id,
            "data_pedido": pedido.data_pedido,
            "status": pedido.status,
            "total": float(pedido.total)
        }
        for pedido in cliente.pedidos
    ]
