# main.py
# Ponto de entrada da API FastAPI do FrotaGesta.
# Conecta ao banco (via db.py) e expoe os endpoints que o front consome.

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg

import db
import schemas


# --- Ciclo de vida da aplicacao ---
# Cria o pool de conexoes quando a API sobe e fecha quando ela desliga.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.criar_pool()   # startup: abre o pool
    yield                   # (aqui a aplicacao roda)
    await db.fechar_pool()  # shutdown: fecha o pool


app = FastAPI(title="FrotaGesta API", lifespan=lifespan)


# --- CORS ---
# Libera o front (Vue, em outra porta) a chamar esta API.
# Sem isso, o navegador bloqueia as requisicoes por seguranca.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # endereco do front (Vite)
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health check ---
# Endpoint simples para confirmar que a API esta no ar E conectada ao banco.
@app.get("/health")
async def health(conexao=Depends(db.get_conexao)):
    resultado = await conexao.fetchval("SELECT 1")
    return {"status": "ok", "banco": resultado == 1}

@app.post("/motoristas", response_model=schemas.MotoristaResponse, status_code=201)
async def criar_motorista(
    motorista: schemas.MotoristaCreate,
    conexao=Depends(db.get_conexao),
):
    try:
        linha = await conexao.fetchrow(
            """
            INSERT INTO motorista (cpf, nome, categoria_cnh)
            VALUES ($1, $2, $3)
            RETURNING id_motorista, cpf, nome, categoria_cnh
            """,
            motorista.cpf,
            motorista.nome,
            motorista.categoria_cnh,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="CPF ja cadastrado")
    except asyncpg.CheckViolationError:
        raise HTTPException(status_code=422, detail="Categoria de CNH invalida")

    return dict(linha)


@app.get("/motoristas", response_model=list[schemas.MotoristaResponse])
async def listar_motoristas(
    busca: str = "",
    conexao=Depends(db.get_conexao),
):
    linhas = await conexao.fetch(
        """
        SELECT id_motorista, cpf, nome, categoria_cnh
        FROM motorista
        WHERE cpf ILIKE $1 OR nome ILIKE $1
        ORDER BY nome
        """,
        f"%{busca}%",
    )
    return [dict(linha) for linha in linhas]