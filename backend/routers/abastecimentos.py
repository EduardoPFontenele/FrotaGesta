# routers/abastecimentos.py
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

import db
import schemas

router = APIRouter(prefix="/abastecimentos", tags=["Abastecimentos"])


@router.post("", status_code=201)
async def criar_abastecimento(
    abastecimento: schemas.AbastecimentoCreate,
    conexao=Depends(db.get_conexao),
):
    """Registra um abastecimento de um veiculo.

    Raises:
        HTTPException 404: id_veiculo nao existe.
        HTTPException 422: litros, valor_total ou km_abastecimento
            violam os CHECK da tabela (ex.: litros fora de 0-300).
    """
    try:
        linha = await conexao.fetchrow(
            """
            INSERT INTO abastecimento (id_veiculo, litros, valor_total, km_abastecimento, data_hora)
            VALUES ($1, $2, $3, $4, COALESCE($5, CURRENT_TIMESTAMP))
            RETURNING id_abastecimento, id_veiculo, data_hora,
                      litros, valor_total, km_abastecimento
            """,
            abastecimento.id_veiculo,
            abastecimento.litros,
            abastecimento.valor_total,
            abastecimento.km_abastecimento,
            abastecimento.data_hora,
        )
    except asyncpg.ForeignKeyViolationError:
        raise HTTPException(status_code=404, detail="Veiculo nao encontrado")
    except asyncpg.CheckViolationError:
        raise HTTPException(
            status_code=422,
            detail="Valores invalidos: verifique litros, valor ou km",
        )
    return dict(linha)


@router.get("")
async def listar_abastecimentos(conexao=Depends(db.get_conexao)):
    """Lista todos os abastecimentos, do mais recente para o mais antigo,
    com placa e modelo do veiculo associado."""
    linhas = await conexao.fetch(
        """
        SELECT a.id_abastecimento, a.id_veiculo, a.data_hora,
               a.litros, a.valor_total, a.km_abastecimento,
               v.placa, v.modelo
        FROM abastecimento a
        JOIN veiculo v ON v.id_veiculo = a.id_veiculo
        ORDER BY a.data_hora DESC
        """
    )
    return [dict(l) for l in linhas]