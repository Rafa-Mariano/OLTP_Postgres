"""
Rotas para CRUD de Produtos
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Produto
from ..schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse, MessageResponse

router = APIRouter(prefix="/produtos")


@router.post("", response_model=ProdutoResponse, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """Criar um novo produto"""
    novo_produto = Produto(**produto.dict())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@router.get("", response_model=List[ProdutoResponse])
def listar_produtos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nome: str = None,
    categoria: str = None,
    em_estoque: bool = None,
    db: Session = Depends(get_db)
):
    """Listar produtos com filtros e paginação"""
    query = db.query(Produto)
    
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))
    
    if categoria:
        query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
    
    if em_estoque is not None:
        if em_estoque:
            query = query.filter(Produto.estoque > 0)
        else:
            query = query.filter(Produto.estoque == 0)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Obter detalhes de um produto"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto_update: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar dados de um produto"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    for key, value in produto_update.dict(exclude_unset=True).items():
        setattr(produto, key, value)
    
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", response_model=MessageResponse)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Deletar um produto"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db.delete(produto)
    db.commit()
    return {"message": "Produto deletado com sucesso"}


@router.get("", response_model=List[dict], tags=["Relatórios"])
def produtos_com_baixo_estoque(limite: int = Query(50, gt=0), db: Session = Depends(get_db)):
    """Listar produtos com estoque abaixo de um limite"""
    produtos = db.query(Produto).filter(Produto.estoque < limite).all()
    
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "estoque": p.estoque,
            "status": "CRÍTICO" if p.estoque == 0 else "BAIXO"
        }
        for p in produtos
    ]
