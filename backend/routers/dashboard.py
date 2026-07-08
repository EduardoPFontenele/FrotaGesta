# routers/dashboard.py
from fastapi import APIRouter, Depends
import db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
async def dashboard(conexao=Depends(db.get_conexao)):
    """Conta os veiculos da frota por status (status_veiculo): disponiveis,
    em rota e em manutencao urgente."""
    # usa a function status_veiculo para classificar cada veiculo,
    # depois conta quantos caem em cada status
    linhas = await conexao.fetch(
        """
        SELECT status_veiculo(id_veiculo) AS status, COUNT(*) AS total
        FROM veiculo
        GROUP BY status_veiculo(id_veiculo)
        """
    )

    # inicia os tres contadores em zero (caso nao haja veiculo em algum status)
    contagem = {"DISPONIVEL": 0, "EM_ROTA": 0, "MANUTENCAO": 0}
    for linha in linhas:
        contagem[linha["status"]] = linha["total"]

    return {
        "disponiveis": contagem["DISPONIVEL"],
        "em_rota": contagem["EM_ROTA"],
        "manutencao_urgente": contagem["MANUTENCAO"],
    }