import os
import asyncpg
from dotenv import load_dotenv

# Le o arquivo .env e carrega as variaveis
load_dotenv()

# Pega a string de conexao do .env.
DATABASE_URL = os.getenv("DATABASE_URL")

# Variavel global que vai guardar o pool de conexoes.
pool: asyncpg.Pool | None = None


async def criar_pool():
    """
    Cria o pool de conexoes com o banco.
    Chamada UMA vez, quando o FastAPI sobe (no evento de startup).
    """
    global pool
    pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,   
        min_size=1,         
        max_size=10,        
    )
    print("Pool de conexoes criado com sucesso.")


async def fechar_pool():
    """
    Fecha o pool de conexoes.
    Chamada quando o FastAPI desliga (no evento de shutdown),
    para liberar as conexoes de forma limpa.
    """
    global pool
    if pool:
        await pool.close()
        print("Pool de conexoes fechado.")

async def get_conexao():
    """
    Fornece uma conexao do pool para um endpoint usar.

    Usada como "dependencia" do FastAPI: o endpoint declara que precisa
    de uma conexao, e o FastAPI chama esta funcao para entregar uma.

    O 'async with' pega uma conexao emprestada do pool e, ao terminar,
    devolve automaticamente (nao fecha - volta pro pool para reutilizar).
    """
    if pool is None:
        raise RuntimeError("Pool nao inicializado. O startup do FastAPI rodou?")
    async with pool.acquire() as conexao:
        yield conexao