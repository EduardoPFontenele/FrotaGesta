# FrotaGesta

**Autores:** Pedro Sales e Eduardo Prudencio

Sistema de controle de frota e manutenção preventiva, desenvolvido para a disciplina de
Laboratório de Banco de Dados. Cobre o cadastro de veículos e motoristas, o registro de
viagens (com atualização automática do odômetro) e a geração de alertas de manutenção
preventiva com base na quilometragem rodada (ex.: troca de óleo a cada 10.000 km).

## Estrutura do projeto

```
der/          # Modelagem relacional (DER) — Fase 1 do trabalho
database/     # Scripts SQL do banco — Fase 2 do trabalho
backend/      # API REST (FastAPI) que expõe o banco para a interface
src/          # Interface web (Vue) — ver seção "Como rodar"
```

## Banco de dados

Toda a regra de negócio crítica exigida no enunciado (restrição de CNH, gatilho de
alerta por quilometragem e o procedimento de encerramento de viagem) vive no banco,
não no backend. Os scripts em `database/` são aplicados nesta ordem:

| Arquivo | Conteúdo |
|---|---|
| `01_schema.sql` | Tabelas (`motorista`, `veiculo`, `viagem`, `abastecimento`, `tipo_manutencao`, `alerta_manutencao`), `CHECK` constraints e `FOREIGN KEY`s. |
| `02_functions.sql` | `status_veiculo()` (classifica um veículo em `DISPONIVEL`/`EM_ROTA`/`MANUTENCAO`), `fn_valida_cnh()` (restrição de CNH x tipo de veículo) e `fn_gera_alerta_manutencao()` (verifica se o odômetro cruzou o `intervalo_km` de algum tipo de manutenção). |
| `03_triggers.sql` | `trg_valida_cnh` (`BEFORE INSERT` em `viagem`) e `trg_alerta_manutencao` (`AFTER UPDATE OF km_atual` em `veiculo`) — este último é o gatilho de alerta pedido no enunciado. |
| `04_procedures.sql` | `encerrar_viagem()`, o procedimento armazenado exigido: valida a quilometragem final, atualiza status/km_final da viagem e o odômetro do veículo em uma única transação, disparando o gatilho de alerta. |
| `05_seed.sql` | Povoamento inicial (dados de teste), para a interface não nascer vazia. |
| `00_reset.sql` | Script manual de reset (`TRUNCATE ... RESTART IDENTITY CASCADE`), usado só em desenvolvimento — não faz parte do bootstrap automático do banco. |

As consultas simples de CRUD (inserir motorista, listar veículos, etc.) **não** ficam em
arquivos `.sql` à parte: elas estão embutidas como SQL puro diretamente nas rotas do
backend, em `backend/routers/*.py` (via `asyncpg`, sem ORM). Só a lógica crítica acima
mora no banco, em function/trigger/procedure.

## Como rodar

Pré-requisito: Docker e Docker Compose.

Na raiz do projeto:

```bash
docker compose up --build
```

Isso sobe três containers e já deixa tudo pronto para testar, sem nenhum passo manual:

- **`db`** — Postgres, com o banco criado e populado automaticamente (`01_schema.sql` →
  `05_seed.sql` rodam sozinhos na primeira subida). Exposto em `localhost:5433` (mapeado
  para não colidir com um Postgres local na 5432; internamente os outros containers
  falam com `db:5432`).
- **`backend`** — API FastAPI em `http://localhost:8000`. Docs interativos (Swagger) em
  `http://localhost:8000/docs`.
- **`frontend`** — interface web em `http://localhost:5173`.

Para derrubar os containers:

```bash
docker compose down
```

Para derrubar e também apagar os dados do banco (a próxima subida recria e repovoa do
zero):

```bash
docker compose down -v
```

### Alternativa sem Docker

- **Backend**: crie `backend/.env` com `DATABASE_URL=postgresql://usuario:senha@localhost:5432/frotagesta`
  apontando para um Postgres já criado com os scripts de `database/` (`01` → `05`), depois:
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```
- **Frontend**: `npm install && npm run dev` na raiz do projeto.
