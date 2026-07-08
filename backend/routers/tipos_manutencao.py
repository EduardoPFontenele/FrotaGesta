# routers/tipos_manutencao.py
# Lista os tipos de manutencao cadastrados. Usado pelo dropdown
# "Registrar problema" da tela de Qualidade do Veiculo, que precisa do
# id_tipo_manutencao para o POST /alertas.
from fastapi import APIRouter, Depends

import db

router = APIRouter(prefix="/tipos-manutencao", tags=["Tipos de Manutencao"])


@router.get("")
async def listar_tipos_manutencao(conexao=Depends(db.get_conexao)):
    """Lista os tipos de manutencao cadastrados, ordenados por descricao."""
    linhas = await conexao.fetch(
        """
        SELECT id_tipo_manutencao, descricao, intervalo_km
        FROM tipo_manutencao
        ORDER BY descricao
        """
    )
    return [dict(linha) for linha in linhas]
