"""
Aplicação FastAPI - Sistema OLTP de Vendas
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import engine, Base
from .routes import clientes, produtos, pedidos, pagamentos

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Criar aplicação
app = FastAPI(
    title="Sistema OLTP de Vendas",
    description="API completa para gerenciar vendas, clientes, produtos e pagamentos",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(clientes.router, prefix="/api/v1", tags=["Clientes"])
app.include_router(produtos.router, prefix="/api/v1", tags=["Produtos"])
app.include_router(pedidos.router, prefix="/api/v1", tags=["Pedidos"])
app.include_router(pagamentos.router, prefix="/api/v1", tags=["Pagamentos"])


@app.get("/", tags=["Root"])
def root():
    """Endpoint raiz da API"""
    return {
        "message": "Sistema OLTP de Vendas",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check da API"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
