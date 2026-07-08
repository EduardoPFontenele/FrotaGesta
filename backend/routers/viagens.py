# routers/viagens.py
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

import db
import schemas

router = APIRouter(prefix="/viagens", tags=["Viagens"])


@router.post("", status_code=201)
async def abrir_viagem(
    viagem: schemas.ViagemCreate,
    conexao=Depends(db.get_conexao),
):
    """Abre uma nova viagem (status ABERTA).

    A trigger trg_valida_cnh confere se a CNH do motorista e compativel
    com o tipo do veiculo antes de permitir o INSERT.

    Raises:
        HTTPException 404: motorista ou veiculo nao encontrado.
        HTTPException 422: CNH incompativel com o tipo de veiculo (trigger)
            ou km_inicial invalido.
    """
    try:
        linha = await conexao.fetchrow(
            """
            INSERT INTO viagem (id_motorista, id_veiculo, data_hora_saida, km_inicial)
            VALUES ($1, $2, COALESCE($3, CURRENT_TIMESTAMP), $4)
            RETURNING id_viagem, id_motorista, id_veiculo,
                      data_hora_saida, km_inicial, data_hora_chegada, km_final, status
            """,
            viagem.id_motorista,
            viagem.id_veiculo,
            viagem.data_hora_saida,
            viagem.km_inicial,
        )
    except asyncpg.ForeignKeyViolationError:
        raise HTTPException(status_code=404, detail="Motorista ou veiculo nao encontrado")
    except asyncpg.RaiseError as e:
        # erro lancado pela trigger da CNH (RAISE EXCEPTION)
        raise HTTPException(status_code=422, detail=str(e))
    except asyncpg.CheckViolationError:
        raise HTTPException(status_code=422, detail="Km inicial invalido")
    return dict(linha)


@router.patch("/{id_viagem}/encerrar")
async def encerrar_viagem(
    id_viagem: int,
    dados: schemas.ViagemEncerrar,
    conexao=Depends(db.get_conexao),
):
    """Encerra uma viagem chamando a procedure encerrar_viagem.

    A procedure marca a viagem como CONCLUIDA e atualiza o km_atual do
    veiculo, o que pode disparar a trigger de geracao de alerta de
    manutencao. Retorna a viagem ja atualizada.

    Raises:
        HTTPException 422: viagem nao encontrada, ja encerrada, ou
            km_final menor que o km_inicial (erros da procedure).
    """
    try:
        await conexao.execute(
            "CALL encerrar_viagem($1, $2, $3)",
            id_viagem,
            dados.km_final,
            dados.data_hora_chegada,
        )
    except asyncpg.RaiseError as e:
        # erros lancados pela procedure (viagem nao encontrada, ja encerrada, km incoerente)
        raise HTTPException(status_code=422, detail=str(e))

    # devolve a viagem ja atualizada
    linha = await conexao.fetchrow(
        """
        SELECT id_viagem, id_motorista, id_veiculo,
               data_hora_saida, km_inicial, data_hora_chegada, km_final, status
        FROM viagem WHERE id_viagem = $1
        """,
        id_viagem,
    )
    return dict(linha)


@router.get("")
async def listar_viagens(conexao=Depends(db.get_conexao)):
    """Lista todas as viagens, com nome do motorista e placa/modelo do
    veiculo, da mais recente para a mais antiga."""
    linhas = await conexao.fetch(
        """
        SELECT v.id_viagem, v.status, v.km_inicial, v.km_final,
               v.data_hora_saida, v.data_hora_chegada,
               m.nome AS motorista, ve.placa, ve.modelo
        FROM viagem v
        JOIN motorista m ON m.id_motorista = v.id_motorista
        JOIN veiculo ve ON ve.id_veiculo = v.id_veiculo
        ORDER BY v.data_hora_saida DESC
        """
    )
    return [dict(l) for l in linhas]