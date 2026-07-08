# routers/alertas.py
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

import db
import schemas

router = APIRouter(prefix="/alertas", tags=["Alertas"])


# Lista todos os alertas pendentes (visao do gerente / oficina)
@router.get("")
async def listar_alertas(conexao=Depends(db.get_conexao)):
    """Lista todos os alertas de manutencao pendentes (resolvido = FALSE),
    com dados do veiculo e do tipo de manutencao."""
    linhas = await conexao.fetch(
        """
        SELECT a.id_alerta, a.id_veiculo, a.km_referencia, a.data_geracao,
               v.placa, v.modelo, t.descricao
        FROM alerta_manutencao a
        JOIN veiculo v ON v.id_veiculo = a.id_veiculo
        JOIN tipo_manutencao t ON t.id_tipo_manutencao = a.id_tipo_manutencao
        WHERE a.resolvido = FALSE
        ORDER BY a.data_geracao DESC
        """
    )
    return [dict(l) for l in linhas]


# Registra um problema MANUALMENTE (botao "Registrar problema").
# A tabela e populada primariamente pela trigger (alertas por km), mas o
# operador tambem pode registrar um problema fora de ciclo (pneu, barulho, etc).
@router.post("", status_code=201)
async def registrar_alerta(
    alerta: schemas.AlertaCreate,
    conexao=Depends(db.get_conexao),
):
    """Registra manualmente um alerta de manutencao para um veiculo.

    Grava o km_atual do veiculo como km_referencia do alerta.

    Raises:
        HTTPException 404: veiculo ou tipo de manutencao nao encontrado.
    """
    # pega o km atual do veiculo para gravar como km_referencia
    km_atual = await conexao.fetchval(
        "SELECT km_atual FROM veiculo WHERE id_veiculo = $1",
        alerta.id_veiculo,
    )
    if km_atual is None:
        raise HTTPException(status_code=404, detail="Veiculo nao encontrado")

    try:
        linha = await conexao.fetchrow(
            """
            INSERT INTO alerta_manutencao (id_veiculo, id_tipo_manutencao, km_referencia)
            VALUES ($1, $2, $3)
            RETURNING id_alerta, id_veiculo, id_tipo_manutencao,
                      km_referencia, data_geracao, resolvido
            """,
            alerta.id_veiculo,
            alerta.id_tipo_manutencao,
            km_atual,
        )
    except asyncpg.ForeignKeyViolationError:
        raise HTTPException(status_code=404, detail="Tipo de manutencao nao encontrado")
    return dict(linha)


# Marca um alerta como resolvido (botao "Marcar como resolvido")
@router.patch("/{id_alerta}/resolver")
async def resolver_alerta(id_alerta: int, conexao=Depends(db.get_conexao)):
    """Marca um alerta de manutencao como resolvido.

    Raises:
        HTTPException 404: alerta nao encontrado.
    """
    resultado = await conexao.execute(
        "UPDATE alerta_manutencao SET resolvido = TRUE WHERE id_alerta = $1",
        id_alerta,
    )
    if resultado == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Alerta nao encontrado")
    return {"id_alerta": id_alerta, "resolvido": True}