// Camada única de acesso a dados da aplicação.
// Fala com a API FrotaGesta (FastAPI) via fetch. Mantém os NOMES das funções
// que as telas já usavam (quando era localStorage) e faz aqui o mapeamento
// entre o snake_case do banco e o formato camelCase que as telas consomem.
// Também normaliza placa/CPF (o front formata com traço/pontos, o banco não).

const API_URL = 'http://localhost:8000'

// ----------------------------------------------------------------------------
// Helper central de requisição: trata erro lendo `detail` (mensagem do backend,
// das triggers e da procedure) e lança Error para a tela exibir.
// ----------------------------------------------------------------------------
async function requisitar(rota, opcoes = {}) {
  const resposta = await fetch(`${API_URL}${rota}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opcoes,
  })

  if (!resposta.ok) {
    let detalhe = `Erro ${resposta.status}`
    try {
      const corpo = await resposta.json()
      if (Array.isArray(corpo.detail)) {
        detalhe = corpo.detail.map(e => e.msg || JSON.stringify(e)).join('; ')
      } else if (corpo && corpo.detail) {
        detalhe = corpo.detail
      }
    } catch (_) { /* resposta sem corpo JSON */ }
    throw new Error(detalhe)
  }

  if (resposta.status === 204) return null
  return resposta.json()
}

// ----------------------------------------------------------------------------
// Formatação de exibição (placa e CPF), para as telas continuarem mostrando
// os valores como o usuário digitou.
// ----------------------------------------------------------------------------
function limparPlaca(valor) {
  return String(valor || '').replace(/[^A-Za-z0-9]/g, '').toUpperCase()
}

function formatarPlaca(valor) {
  const v = limparPlaca(valor)
  return v.length === 7 ? `${v.slice(0, 3)}-${v.slice(3)}` : v
}

function limparCpf(valor) {
  return String(valor || '').replace(/\D/g, '')
}

function formatarCpf(valor) {
  const d = limparCpf(valor)
  if (d.length !== 11) return valor
  return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9, 11)}`
}

// ----------------------------------------------------------------------------
// Mapeadores banco -> tela
// ----------------------------------------------------------------------------
function mapVeiculo(v) {
  return {
    id_veiculo: v.id_veiculo,
    placa: formatarPlaca(v.placa),
    modelo: v.modelo,
    ano: v.ano,
    tipo: v.tipo,
    km: v.km_atual,
  }
}

function mapMotorista(m) {
  return {
    id_motorista: m.id_motorista,
    cpf: formatarCpf(m.cpf),
    nome: m.nome,
    // banco guarda uma categoria; telas esperam array (listagem faz .join)
    categoria_cnh: Array.isArray(m.categoria_cnh) ? m.categoria_cnh : [m.categoria_cnh],
  }
}

function mapViagem(v) {
  return {
    id: v.id_viagem,
    veiculo: { placa: formatarPlaca(v.placa), modelo: v.modelo },
    motorista: { nome: v.motorista },
    dataSaida: v.data_hora_saida,
    kmInicial: v.km_inicial,
    dataChegada: v.data_hora_chegada, // null enquanto ABERTA
    kmFinal: v.km_final,
    status: v.status,
  }
}

function mapAlerta(a) {
  return {
    id: a.id_alerta,
    veiculoPlaca: formatarPlaca(a.placa),
    veiculoModelo: a.modelo,
    tipo: a.descricao,
    data: a.data_geracao,
    status: 'Pendente', // o backend só devolve os pendentes (resolvido = FALSE)
  }
}

function mapAbastecimento(a) {
  return {
    id: a.id_abastecimento,
    veiculoPlaca: formatarPlaca(a.placa),
    veiculoModelo: a.modelo,
    volume: Number(a.litros),
    valorTotal: Number(a.valor_total),
    km: a.km_abastecimento,
    dataHora: a.data_hora,
  }
}

// ----------------------------------------------------------------------------
// Veículos
// ----------------------------------------------------------------------------
export async function getVeiculos() {
  const lista = await requisitar('/veiculos')
  return lista.map(mapVeiculo)
}

// Cria UM veículo (antes salvava a lista inteira no localStorage).
export async function salvarVeiculos(veiculo) {
  return requisitar('/veiculos', {
    method: 'POST',
    body: JSON.stringify({
      placa: limparPlaca(veiculo.placa),
      modelo: veiculo.modelo,
      ano: Number(veiculo.ano),
      tipo: veiculo.tipo, // já vem CARRO/VAN/CAMINHAO da tela
      km_atual: Number(veiculo.km),
    }),
  })
}

// ----------------------------------------------------------------------------
// Motoristas
// ----------------------------------------------------------------------------
export async function getMotoristas() {
  const lista = await requisitar('/motoristas')
  return lista.map(mapMotorista)
}

// Cria UM motorista. Envia o array de categorias; o backend reduz para a maior.
export async function salvarMotoristas(motorista) {
  return requisitar('/motoristas', {
    method: 'POST',
    body: JSON.stringify({
      cpf: limparCpf(motorista.cpf),
      nome: motorista.nome,
      categoria_cnh: motorista.categoria_cnh, // array
    }),
  })
}

// ----------------------------------------------------------------------------
// Viagens
// ----------------------------------------------------------------------------
export async function getViagens() {
  const lista = await requisitar('/viagens')
  return lista.map(mapViagem)
}

// Abre uma viagem. Dispara a trigger da CNH no banco (erro vira Error com detail).
export async function abrirViagem({ id_motorista, id_veiculo, km_inicial, data_hora_saida }) {
  return requisitar('/viagens', {
    method: 'POST',
    body: JSON.stringify({
      id_motorista,
      id_veiculo,
      km_inicial: Number(km_inicial),
      data_hora_saida: data_hora_saida || null,
    }),
  })
}

// Encerra a viagem (CALL encerrar_viagem no banco: atualiza status/km e dispara
// a trigger de manutenção). Erros da procedure viram Error com detail.
export async function encerrarViagem(idViagem, kmFinal, dataChegada) {
  return requisitar(`/viagens/${idViagem}/encerrar`, {
    method: 'PATCH',
    body: JSON.stringify({
      km_final: Number(kmFinal),
      data_hora_chegada: dataChegada || null,
    }),
  })
}

// Stub: no modo API a viagem é criada/encerrada pelos endpoints acima.
export function salvarViagens() { /* no-op */ }

// ----------------------------------------------------------------------------
// Alertas
// ----------------------------------------------------------------------------
export async function getAlertas() {
  const lista = await requisitar('/alertas')
  return lista.map(mapAlerta)
}

// Registra um problema manual (botão "Registrar problema").
export async function registrarAlerta({ id_veiculo, id_tipo_manutencao }) {
  return requisitar('/alertas', {
    method: 'POST',
    body: JSON.stringify({ id_veiculo, id_tipo_manutencao }),
  })
}

// Marca um alerta como resolvido.
export async function resolverAlerta(idAlerta) {
  return requisitar(`/alertas/${idAlerta}/resolver`, { method: 'PATCH' })
}

// Stub: alertas nascem no banco (trigger) ou pelo registrarAlerta acima.
export function salvarAlertas() { /* no-op */ }

// ----------------------------------------------------------------------------
// Abastecimentos
// ----------------------------------------------------------------------------
export async function getAbastecimentos() {
  const lista = await requisitar('/abastecimentos')
  return lista.map(mapAbastecimento)
}

// Cria UM abastecimento.
export async function salvarAbastecimentos({ id_veiculo, litros, valor_total, km_abastecimento, data_hora }) {
  return requisitar('/abastecimentos', {
    method: 'POST',
    body: JSON.stringify({
      id_veiculo,
      litros: Number(litros),
      valor_total: Number(valor_total),
      km_abastecimento: Number(km_abastecimento),
      data_hora: data_hora || null,
    }),
  })
}

// ----------------------------------------------------------------------------
// Tipos de manutenção (popula o dropdown "Registrar problema")
// ----------------------------------------------------------------------------
export async function getTiposManutencao() {
  return requisitar('/tipos-manutencao') // [{ id_tipo_manutencao, descricao, intervalo_km }]
}

// ----------------------------------------------------------------------------
// Reset geral: no modo API é feito via scripts SQL (database/00_reset.sql).
// Mantido como no-op para não quebrar a TelaInicial.
// ----------------------------------------------------------------------------
export function limparTodosOsDados() { /* no-op */ }
