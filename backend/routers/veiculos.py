# routers/veiculos.py
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

import db
import schemas

router = APIRouter(prefix="/veiculos", tags=["Veiculos"])


@router.post("", response_model=schemas.VeiculoResponse, status_code=201)
async def criar_veiculo(
    veiculo: schemas.VeiculoCreate,
    conexao=Depends(db.get_conexao),
):
    """Cadastra um veiculo.

    Raises:
        HTTPException 409: placa ja cadastrada.
        HTTPException 422: tipo, ano ou km_atual invalidos (violacao de CHECK).
    """
    try:
        linha = await conexao.fetchrow(
            """
            INSERT INTO veiculo (placa, modelo, ano, tipo, km_atual)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id_veiculo, placa, modelo, ano, tipo, km_atual
            """,
            veiculo.placa,
            veiculo.modelo,
            veiculo.ano,
            veiculo.tipo,
            veiculo.km_atual,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Placa ja cadastrada")
    except asyncpg.CheckViolationError:
        raise HTTPException(
            status_code=422,
            detail="Dado invalido: verifique tipo (CARRO/VAN/CAMINHAO), ano ou km",
        )
    return dict(linha)


@router.get("", response_model=list[schemas.VeiculoResponse])
async def listar_veiculos(busca: str = "", conexao=Depends(db.get_conexao)):
    """Lista veiculos, filtrando por placa ou modelo (ILIKE) quando `busca` e informado."""
    linhas = await conexao.fetch(
        """
        SELECT id_veiculo, placa, modelo, ano, tipo, km_atual
        FROM veiculo
        WHERE placa ILIKE $1 OR modelo ILIKE $1
        ORDER BY modelo
        """,
        f"%{busca}%",
    )
    return [dict(linha) for linha in linhas]


@router.get("/{id_veiculo}/qualidade")
async def qualidade_veiculo(id_veiculo: int, conexao=Depends(db.get_conexao)):
    """Retorna o resumo de um veiculo: dados cadastrais, status calculado
    (status_veiculo) e a lista de alertas de manutencao pendentes.

    Raises:
        HTTPException 404: veiculo nao encontrado.
    """
    veiculo = await conexao.fetchrow(
        """
        SELECT id_veiculo, placa, modelo, ano, tipo, km_atual
        FROM veiculo WHERE id_veiculo = $1
        """,
        id_veiculo,
    )
    if veiculo is None:
        raise HTTPException(status_code=404, detail="Veiculo nao encontrado")

    status = await conexao.fetchval("SELECT status_veiculo($1)", id_veiculo)

    alertas = await conexao.fetch(
        """
        SELECT a.id_alerta, a.km_referencia, a.data_geracao, a.resolvido,
               t.descricao, t.intervalo_km
        FROM alerta_manutencao a
        JOIN tipo_manutencao t ON t.id_tipo_manutencao = a.id_tipo_manutencao
        WHERE a.id_veiculo = $1 AND a.resolvido = FALSE
        ORDER BY a.data_geracao DESC
        """,
        id_veiculo,
    )

    return {
        "veiculo": dict(veiculo),
        "status": status,
        "alertas": [dict(a) for a in alertas],
    }
