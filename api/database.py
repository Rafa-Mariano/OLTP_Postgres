"""
Configuração de conexão com o banco de dados PostgreSQL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URL de conexão com PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/vendas_oltp"
)

# Criar engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # True para debug (mostra SQL)
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_size=20,  # Tamanho do pool de conexões
    max_overflow=40  # Máximo de conexões adicionais
)

# Criar session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
