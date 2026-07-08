# FrotaGesta — Backend

API REST feita com **FastAPI** para gestão de frota: motoristas, veículos, viagens, abastecimentos e manutenção preventiva. Fala com um banco **PostgreSQL** via **asyncpg**, e a maior parte das regras de negócio (validação de CNH, geração de alertas de manutenção, encerramento de viagem) vive no próprio banco, em functions/triggers/procedures — o backend Python é uma camada fina de HTTP + validação de entrada em cima disso.

## Stack

| Peça | Papel |
|---|---|
| **FastAPI** | Framework web: define rotas, valida request/response, gera o `/docs` (Swagger) automaticamente. |
| **Pydantic** | Valida e serializa os dados que entram/saem da API (os `schemas.py`). |
| **asyncpg** | Driver assíncrono de PostgreSQL — usado direto, sem ORM. Todas as queries são SQL puro. |
| **python-dotenv** | Carrega a `DATABASE_URL` do arquivo `.env`. |
| **uvicorn** | Servidor ASGI que roda a aplicação. |

## Estrutura

```
backend/
├── main.py              # cria o app, CORS, lifespan (pool), inclui os routers
├── db.py                 # pool de conexões asyncpg + dependency get_conexao
├── schemas.py             # modelos Pydantic (request/response)
├── routers/
│   ├── motoristas.py
│   ├── veiculos.py
│   ├── viagens.py
│   ├── alertas.py
│   ├── abastecimentos.py
│   ├── dashboard.py
│   └── tipos_manutencao.py
└── requirements.txt

database/
├── 00_reset.sql          # TRUNCATE de todas as tabelas (dev)
├── 01_schema.sql          # CREATE TABLE
├── 02_functions.sql       # functions (status_veiculo, triggers)
├── 03_triggers.sql        # CREATE TRIGGER
├── 04_procedures.sql      # stored procedures (encerrar_viagem)
└── 05_seed.sql            # dados de exemplo
```

## Como rodar

1. Suba um PostgreSQL e crie o banco; rode os scripts de `database/` em ordem (`01` → `05`).
2. Crie um `.env` em `backend/` com:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/frotagesta
   ```
3. Instale as dependências e suba o servidor:
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
4. Docs interativos (Swagger) em `http://localhost:8000/docs`.

O CORS em `main.py` libera apenas `http://localhost:5173` (front Vue/Vite em dev).

---

## `db.py` — conexão com o banco

Não usa ORM: guarda um **pool de conexões asyncpg** em uma variável global do módulo.

- `criar_pool()` — cria o pool (`min_size=1`, `max_size=10`) a partir de `DATABASE_URL`. Chamada uma única vez no `startup` do FastAPI (ver `lifespan` em `main.py`).
- `fechar_pool()` — fecha o pool no `shutdown` da aplicação.
- `get_conexao()` — **dependency** do FastAPI (`Depends(db.get_conexao)`). É um *generator* assíncrono: pega uma conexão emprestada do pool com `async with pool.acquire()`, entrega (`yield`) para o endpoint usar, e devolve automaticamente ao pool quando a requisição termina — não fecha a conexão, só a libera para reuso.

Todo endpoint que precisa do banco declara `conexao=Depends(db.get_conexao)` na assinatura.

## `schemas.py` — modelos Pydantic

Definem o formato dos dados que entram (`*Create`) e saem (`*Response`) da API. O FastAPI usa esses modelos para validar automaticamente o corpo das requisições (erro 422 se não bater) e para serializar as respostas.

| Modelo | Uso |
|---|---|
| `MotoristaCreate` | `cpf` (11 chars), `nome`, `categoria_cnh: List[str]` — o front pode mandar mais de uma categoria (ex.: `["B", "D"]`); o backend reduz para a mais abrangente antes de gravar. |
| `MotoristaResponse` | motorista já persistido, com `id_motorista` e `categoria_cnh` já reduzida a uma única letra. |
| `VeiculoCreate` / `VeiculoResponse` | `placa`, `modelo`, `ano`, `tipo` (`CARRO`/`VAN`/`CAMINHAO`), `km_atual`. |
| `ViagemCreate` | `id_motorista`, `id_veiculo`, `km_inicial`, `data_hora_saida` opcional (se omitido, o banco usa `CURRENT_TIMESTAMP`). |
| `ViagemEncerrar` | `km_final`, `data_hora_chegada` opcional — usado no PATCH que fecha a viagem. |
| `ViagemResponse` | viagem completa, incluindo `status` (`ABERTA`/`CONCLUIDA`) e os campos de chegada (`Optional`, pois só existem depois de encerrada). |
| `AlertaCreate` | `id_veiculo` + `id_tipo_manutencao`, para registro manual de um alerta. |
| `AbastecimentoCreate` | `litros`, `valor_total`, `km_abastecimento`, `data_hora` opcional. |

Datas ficam como `datetime` (Python) ↔ `TIMESTAMP` (Postgres), convertidos automaticamente pelo asyncpg.

---

## Routers e Endpoints

Cada arquivo em `routers/` é um `APIRouter` com um `prefix` próprio, incluído em `main.py`. Padrão geral: recebem o schema Pydantic validado, montam a query SQL com `conexao.fetchrow`/`fetch`/`execute`, e traduzem erros do Postgres (`asyncpg.UniqueViolationError`, `ForeignKeyViolationError`, `CheckViolationError`, `RaiseError`) em `HTTPException` com status HTTP apropriado (409, 404, 422).

### `motoristas.py` — prefix `/motoristas`

- **`POST /motoristas`** — cria motorista. Recebe uma lista de categorias de CNH e usa `maior_categoria()` para reduzir à categoria de maior "posto" (a CNH é hierárquica: quem tem `D` também dirige o que `B` dirige — ranking `A < B < C < D < E`). 409 se CPF já existe, 422 se categoria inválida.
- **`GET /motoristas?busca=`** — lista motoristas, filtrando por CPF ou nome (`ILIKE`) se `busca` for informado.

### `veiculos.py` — prefix `/veiculos`

- **`POST /veiculos`** — cria veículo. 409 se placa duplicada, 422 se tipo/ano/km inválidos (violação de `CHECK`).
- **`GET /veiculos?busca=`** — lista veículos, filtrando por placa ou modelo.
- **`GET /veiculos/{id_veiculo}/qualidade`** — endpoint "resumo" de um veículo: dados cadastrais + `status_veiculo()` (function do banco) + lista de alertas de manutenção pendentes (`resolvido = FALSE`). 404 se o veículo não existir.

### `viagens.py` — prefix `/viagens`

- **`POST /viagens`** — abre uma viagem (`INSERT INTO viagem`). Dispara a trigger `trg_valida_cnh`, que barra a viagem se a CNH do motorista for incompatível com o tipo de veículo — vira 422. FK inválida (motorista/veículo inexistente) vira 404.
- **`PATCH /viagens/{id_viagem}/encerrar`** — chama a **procedure** `encerrar_viagem` (`CALL`), que fecha a viagem e atualiza o odômetro do veículo. Erros de negócio (viagem inexistente, já encerrada, km final menor que o inicial) são `RAISE EXCEPTION` na procedure, capturados como `asyncpg.RaiseError` e virando 422. Depois de encerrar, o endpoint busca e retorna a viagem já atualizada.
- **`GET /viagens`** — lista todas as viagens com `JOIN` em motorista e veículo (nome do motorista, placa, modelo), ordenadas da mais recente para a mais antiga.

### `alertas.py` — prefix `/alertas`

- **`GET /alertas`** — lista todos os alertas de manutenção pendentes (`resolvido = FALSE`), com dados do veículo e do tipo de manutenção.
- **`POST /alertas`** — registro **manual** de um problema (ex.: botão "Registrar problema" na tela de qualidade do veículo). A tabela `alerta_manutencao` é populada primariamente pela trigger de km (veja abaixo), mas o operador pode abrir um alerta fora de ciclo. Busca o `km_atual` do veículo para gravar como `km_referencia`. 404 se veículo ou tipo de manutenção não existirem.
- **`PATCH /alertas/{id_alerta}/resolver`** — marca um alerta como resolvido. 404 se o alerta não existir.

### `abastecimentos.py` — prefix `/abastecimentos`

- **`POST /abastecimentos`** — registra um abastecimento (litros, valor, km). 404 se veículo não existe, 422 se valores violam os `CHECK` da tabela (ex.: litros fora de 0–300).
- **`GET /abastecimentos`** — lista abastecimentos com placa/modelo do veículo, mais recentes primeiro.

### `dashboard.py` — prefix `/dashboard`

- **`GET /dashboard`** — usa a function `status_veiculo()` para classificar cada veículo da frota e agrega em três contadores: `disponiveis`, `em_rota`, `manutencao_urgente`. Inicializa os três em zero antes de somar, para não faltar chave no JSON quando algum status não tiver nenhum veículo.

### `tipos_manutencao.py` — prefix `/tipos-manutencao`

- **`GET /tipos-manutencao`** — lista os tipos de manutenção cadastrados (ex.: troca de óleo, pastilhas de freio). Usado para popular o dropdown da tela "Registrar problema", que precisa do `id_tipo_manutencao` para o `POST /alertas`.

### `main.py` — endpoint avulso

- **`GET /health`** — healthcheck: roda `SELECT 1` no banco e retorna `{"status": "ok", "banco": true/false}`.

---

## Banco de dados

### Tabelas (`01_schema.sql`)

| Tabela | Campos principais | Observações |
|---|---|---|
| **`motorista`** | `id_motorista`, `cpf` (único), `nome`, `categoria_cnh` | `categoria_cnh` restrita por `CHECK` a `A,B,C,D,E,AB,AC,AD,AE`. |
| **`veiculo`** | `id_veiculo`, `placa` (única), `modelo`, `ano`, `tipo`, `km_atual` | `tipo` restrito a `CARRO/VAN/CAMINHAO`; `ano` entre 1900–2100; `km_atual >= 0`. |
| **`viagem`** | `id_viagem`, `id_motorista` (FK), `id_veiculo` (FK), `data_hora_saida`, `km_inicial`, `data_hora_chegada`, `km_final`, `status` | `status` é `ABERTA` ou `CONCLUIDA`; `CHECK chk_odometro` garante `km_final >= km_inicial` quando preenchido. |
| **`abastecimento`** | `id_abastecimento`, `id_veiculo` (FK), `data_hora`, `litros`, `valor_total`, `km_abastecimento` | `litros` entre 0–300; `valor_total >= 0`. |
| **`tipo_manutencao`** | `id_tipo_manutencao`, `descricao`, `intervalo_km` | Ex.: "Troca de óleo" a cada 10.000 km. `intervalo_km > 0`. |
| **`alerta_manutencao`** | `id_alerta`, `id_veiculo` (FK), `id_tipo_manutencao` (FK), `km_referencia`, `data_geracao`, `resolvido` | Gerada automaticamente pela trigger de km, ou manualmente via `POST /alertas`. |

### Functions (`02_functions.sql`)

- **`status_veiculo(p_id_veiculo)`** — classifica um veículo em `MANUTENCAO` (tem alerta não resolvido), `EM_ROTA` (tem viagem `ABERTA`) ou `DISPONIVEL`, nessa ordem de prioridade. Usada por `GET /veiculos/{id}/qualidade` e `GET /dashboard`.
- **`fn_valida_cnh()`** *(trigger function)* — antes de inserir uma viagem, confere se a CNH do motorista é compatível com o tipo do veículo. Regra implementada: `CAMINHAO` exige categoria `D` ou `E`; caso contrário, `RAISE EXCEPTION`.
- **`fn_gera_alerta_manutencao()`** *(trigger function)* — depois que `km_atual` de um veículo é atualizado, verifica para cada `tipo_manutencao` se o odômetro "cruzou" o múltiplo do `intervalo_km` (ex.: passou de 9.900 para 10.200 km, cruzando o marco de 10.000). Se cruzou e não existe alerta pendente desse tipo para o veículo, insere um novo `alerta_manutencao`.

### Triggers (`03_triggers.sql`)

- **`trg_valida_cnh`** — `BEFORE INSERT ON viagem`, executa `fn_valida_cnh()`. É o que faz `POST /viagens` responder 422 quando a CNH não é compatível.
- **`trg_alerta_manutencao`** — `AFTER UPDATE OF km_atual ON veiculo`, executa `fn_gera_alerta_manutencao()`. Disparada indiretamente pela procedure `encerrar_viagem` (que atualiza `km_atual` ao fechar uma viagem).

### Procedures (`04_procedures.sql`)

- **`encerrar_viagem(p_id_viagem, p_km_final, p_data_hora_chegada)`** — chamada por `PATCH /viagens/{id}/encerrar`. Passos:
  1. Busca a viagem; `RAISE EXCEPTION` se não existir ou já estiver `CONCLUIDA`.
  2. Valida que `km_final >= km_inicial`.
  3. Atualiza a viagem (`status='CONCLUIDA'`, `km_final`, `data_hora_chegada`, com `COALESCE` para `CURRENT_TIMESTAMP` se a data não vier).
  4. Atualiza `veiculo.km_atual` com o `km_final` — o que dispara `trg_alerta_manutencao` e pode gerar alertas de manutenção automaticamente.

### Scripts auxiliares

- **`00_reset.sql`** — `TRUNCATE ... RESTART IDENTITY CASCADE` em todas as tabelas; usado para resetar o ambiente de desenvolvimento.
- **`05_seed.sql`** — dados de exemplo (tipos de manutenção, motoristas, veículos, viagens) para popular o banco em dev.

## Fluxo de negócio ponta a ponta (exemplo)

1. `POST /veiculos` cadastra um caminhão; `POST /motoristas` cadastra um motorista com CNH `B`.
2. `POST /viagens` tentando usar esse motorista no caminhão → trigger `trg_valida_cnh` dispara `RAISE EXCEPTION` → API responde 422.
3. Com um motorista `D`, a viagem abre normalmente (`status='ABERTA'`).
4. `PATCH /viagens/{id}/encerrar` chama a procedure `encerrar_viagem`, que fecha a viagem e atualiza `km_atual` do veículo.
5. Se esse novo `km_atual` cruzar o `intervalo_km` de algum `tipo_manutencao`, a trigger `trg_alerta_manutencao` insere um `alerta_manutencao`.
6. `GET /veiculos/{id}/qualidade` e `GET /dashboard` agora refletem o veículo como `MANUTENCAO` (via `status_veiculo()`), até alguém chamar `PATCH /alertas/{id}/resolver`.
