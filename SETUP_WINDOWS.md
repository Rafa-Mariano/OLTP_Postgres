# 🪟 Guia de Setup para Windows

## Pré-requisitos

- ✅ PostgreSQL instalado (você já tem)
- ✅ Python 3.9+ instalado
- ✅ Banco `vendas_oltp` criado no pgAdmin (você já fez)

---

## 🚀 Setup Passo a Passo (Windows)

### Passo 1: Abra PowerShell

Clique em **Iniciar** → digite **PowerShell** → clique

### Passo 2: Navegue para a pasta do projeto

```powershell
cd C:\Users\Ana Clara\Downloads\Projeto_OLTP\OLTP_Postgres
```

Verifique se está certo:

```powershell
# Listar arquivos
ls

# Deve mostrar: README.md, database, api, requirements.txt, etc
```

### Passo 3: Criar ambiente virtual Python

```powershell
# Criar venv
python -m venv venv

# Ativar (PowerShell)
.\venv\Scripts\Activate

# Seu prompt deve ficar assim: (venv) C:\Users\...>
```

### Passo 4: Instalar dependências

```powershell
pip install -r requirements.txt

# Isso vai instalar: fastapi, uvicorn, sqlalchemy, psycopg2, etc
# Demora um pouco...
```

### Passo 5: Aplicar scripts SQL ao banco

#### Opção 1️⃣: Com Python (Mais fácil)

```powershell
python setup_database.py

# Quando pedir senha, digite a senha do PostgreSQL
# (geralmente é 'postgres' se não mudou na instalação)
```

**Pronto! ✅ Tabelas e índices criados!**

---

#### Opção 2️⃣: Com pgAdmin (Se preferir interface gráfica)

1. Abra o **pgAdmin** (ícone na área de trabalho)
2. Abra a pasta **Servers** → **PostgreSQL** → **vendas_oltp**
3. Clique com botão direito em **vendas_oltp** → **Query Tool**
4. Cole o conteúdo de `database/schema.sql` e clique em ▶️
5. Depois cole `database/indexes.sql` e execute novamente

---

### Passo 6: Popular banco com dados de teste (Opcional)

```powershell
python populate_db.py

# Isso cria:
# - 5 clientes de teste
# - 6 produtos
# - 10 pedidos
# - 10 pagamentos
```

### Passo 7: Iniciar a API

```powershell
# Entrar na pasta api
cd api

# Iniciar servidor
uvicorn main:app --reload --port 8000
```

**Você deve ver algo assim:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### Passo 8: Acessar a API

Abra no navegador:

- 📖 **Documentação**: http://localhost:8000/docs
- 📚 **ReDoc**: http://localhost:8000/redoc
- 💚 **Health Check**: http://localhost:8000/health

---

## 🧪 Testar Endpoints da API

### Dentro do Swagger (http://localhost:8000/docs):

1. Clique em **POST /api/v1/clientes**
2. Clique em **Try it out**
3. Cole este JSON:

```json
{
  "nome": "Ana Silva",
  "email": "ana@example.com",
  "telefone": "11987654321",
  "endereco": "Rua Principal, 100 - São Paulo"
}
```

4. Clique em **Execute** ✅

Pronto! Seu cliente foi criado!

---

## 🔄 Parar a API

```powershell
# No PowerShell onde a API está rodando, pressione:
CTRL + C
```

---

## 📦 Próximas Vezes (Ativar venv)

Toda vez que abrir PowerShell, faça:

```powershell
cd C:\Users\Ana Clara\Downloads\Projeto_OLTP\OLTP_Postgres
.\venv\Scripts\Activate
```

Depois é só rodar a API normalmente.

---

## 🆘 Troubleshooting

### Erro: "psycopg2 not found"

```powershell
pip install psycopg2-binary
```

### Erro: "ModuleNotFoundError: No module named 'fastapi'"

```powershell
# Verifique se está com venv ativado (deve ter (venv) antes do prompt)
pip install -r requirements.txt
```

### Erro: "Access denied" no banco

- Verifique a senha do PostgreSQL
- Tente mudar DB_PASSWORD em setup_database.py

### API não abre em http://localhost:8000

- Verifique se a API ainda está rodando no PowerShell
- Tente outra porta: `uvicorn main:app --port 8001`

---

## 📊 Executar Queries Analíticas

Depois que o banco está funcionando, use pgAdmin para rodar as queries:

1. Abra pgAdmin
2. Query Tool no banco vendas_oltp
3. Abra `database/queries.sql`
4. Copie e execute as queries que quiser

**Exemplos:**
- Faturamento mensal
- Clientes que mais gastam
- Produtos mais vendidos
- Análise RFM

---

## ✨ Pronto para Começar!

Agora você tem:

✅ Banco PostgreSQL com 5 tabelas  
✅ Índices para performance  
✅ API REST completa em FastAPI  
✅ Documentação interativa  
✅ Dados de teste  

**Explore em: http://localhost:8000/docs** 🚀
