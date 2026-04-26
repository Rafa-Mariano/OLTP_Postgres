"""
Script para aplicar scripts SQL ao banco de dados PostgreSQL
Funciona em Windows, Linux e Mac sem precisar de psql instalado
"""
import psycopg2
import os
import sys
from pathlib import Path


# Caminho dos scripts
SCRIPTS_DIR = Path(__file__).parent / "database"
SCRIPTS = [
    "schema.sql",
    "indexes.sql"
]

def executar_script(conn, filepath):
    """Executar um arquivo SQL"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()
        print(f"✅ {filepath.name} executado com sucesso!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao executar {filepath.name}: {e}")
        return False

def main():
    print("=" * 60)
    print("🗄️  SETUP DO BANCO DE DADOS - SISTEMA OLTP DE VENDAS")
    print("=" * 60)
    
    try:
        # Conectar ao PostgreSQL
        print("\n🔌 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✅ Conectado com sucesso!")
        
        # Executar scripts
        print("\n📝 Executando scripts SQL...\n")
        for script_name in SCRIPTS:
            script_path = SCRIPTS_DIR / script_name
            if not script_path.exists():
                print(f"⚠️  Arquivo não encontrado: {script_path}")
                continue
            
            if not executar_script(conn, script_path):
                conn.close()
                return 1
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✨ SETUP CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\n📌 Próximos passos:")
        print("   1. pip install -r requirements.txt")
        print("   2. python populate_db.py  (para dados de teste)")
        print("   3. cd api")
        print("   4. uvicorn main:app --reload --port 8000")
        print("\n🌐 Depois acesse: http://localhost:8000/docs")
        
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("\n💡 Dicas:")
        print("   - Verifique se PostgreSQL está rodando")
        print("   - Verifique host, porta, usuário e senha")
        print("   - Use pgAdmin para verificar conexão")
        return 1
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
