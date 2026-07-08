# routers/motoristas.py
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

import db
import schemas

# o router e como um "mini-app". O prefix evita repetir "/motoristas"
# em cada rota, e as tags agrupam no /docs.
router = APIRouter(prefix="/motoristas", tags=["Motoristas"])


# Ranking da CNH: quanto maior, mais abrangente. A regra de negocio so olha
# D/E (caminhao), e a CNH e hierarquica (quem tem D dirige o que B dirige),
# entao reduzimos a lista de categorias digitada para a de maior rank.
_RANK_CNH = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def maior_categoria(categorias: list[str]) -> str:
    """Reduz uma lista de categorias de CNH a maior delas.

    A CNH e hierarquica (quem tem D dirige o que B dirige), entao o
    cadastro guarda so a categoria de maior rank (A < B < C < D < E).

    Raises:
        HTTPException 422: nenhuma categoria valida na lista.
    """
    normalizadas = [c.strip().upper() for c in categorias if c and c.strip()]
    validas = [c for c in normalizadas if c in _RANK_CNH]
    if not validas:
        raise HTTPException(status_code=422, detail="Categoria de CNH invalida")
    return max(validas, key=lambda c: _RANK_CNH[c])


@router.post("", response_model=schemas.MotoristaResponse, status_code=201)
async def criar_motorista(
    motorista: schemas.MotoristaCreate,
    conexao=Depends(db.get_conexao),
):
    """Cadastra um motorista, reduzindo a lista de CNH a maior categoria.

    Raises:
        HTTPException 409: CPF ja cadastrado.
        HTTPException 422: categoria de CNH invalida.
    """
    categoria = maior_categoria(motorista.categoria_cnh)
    try:
        linha = await conexao.fetchrow(
            """
            INSERT INTO motorista (cpf, nome, categoria_cnh)
            VALUES ($1, $2, $3)
            RETURNING id_motorista, cpf, nome, categoria_cnh
            """,
            motorista.cpf, motorista.nome, categoria,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="CPF ja cadastrado")
    except asyncpg.CheckViolationError:
        raise HTTPException(status_code=422, detail="Categoria de CNH invalida")
    return dict(linha)


@router.get("", response_model=list[schemas.MotoristaResponse])
async def listar_motoristas(busca: str = "", conexao=Depends(db.get_conexao)):
    """Lista motoristas, filtrando por CPF ou nome (ILIKE) quando `busca` e informado."""
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