# main.py
# Ponto de entrada da API FrotaGesta.
# Configura o app, o CORS e o ciclo de vida do pool, e inclui os routers.

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import db
from routers import (
    motoristas,
    veiculos,
    viagens,
    alertas,
    abastecimentos,
    dashboard,
    tipos_manutencao,
)


# Ciclo de vida: cria o pool de conexoes no startup, fecha no shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.criar_pool()
    yield
    await db.fechar_pool()


app = FastAPI(title="FrotaGesta API", lifespan=lifespan)


# CORS: libera o front (Vue/Vite) a chamar esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registra todos os routers.
app.include_router(motoristas.router)
app.include_router(veiculos.router)
app.include_router(viagens.router)
app.include_router(alertas.router)
app.include_router(abastecimentos.router)
app.include_router(dashboard.router)
app.include_router(tipos_manutencao.router)


# Health check: confirma que a API esta no ar e conectada ao banco.
@app.get("/health")
async def health(conexao=Depends(db.get_conexao)):
    resultado = await conexao.fetchval("SELECT 1")
    return {"status": "ok", "banco": resultado == 1}