// Camada única de acesso a dados da aplicação.
// Hoje guarda tudo no localStorage; para integrar com um banco de dados,
// basta reimplementar as funções abaixo (ex: chamadas fetch/axios a uma API),
// sem precisar alterar as telas que as consomem.

const CHAVE_VEICULOS = 'veiculos'
const CHAVE_MOTORISTAS = 'motoristas'
const CHAVE_VIAGENS = 'viagens'
const CHAVE_ALERTAS = 'alertas'

function obter(chave) {
  const contexto = localStorage.getItem(chave)
  return contexto ? JSON.parse(contexto) : []
}

function salvar(chave, dados) {
  localStorage.setItem(chave, JSON.stringify(dados, null, 2))
}

export function getVeiculos() {
  return obter(CHAVE_VEICULOS)
}

export function salvarVeiculos(veiculos) {
  salvar(CHAVE_VEICULOS, veiculos)
}

export function getMotoristas() {
  return obter(CHAVE_MOTORISTAS)
}

export function salvarMotoristas(motoristas) {
  salvar(CHAVE_MOTORISTAS, motoristas)
}

export function getViagens() {
  return obter(CHAVE_VIAGENS)
}

export function salvarViagens(viagens) {
  salvar(CHAVE_VIAGENS, viagens)
}

export function getAlertas() {
  return obter(CHAVE_ALERTAS)
}

export function salvarAlertas(alertas) {
  salvar(CHAVE_ALERTAS, alertas)
}

export function limparTodosOsDados() {
  localStorage.removeItem(CHAVE_VEICULOS)
  localStorage.removeItem(CHAVE_MOTORISTAS)
  localStorage.removeItem(CHAVE_VIAGENS)
  localStorage.removeItem(CHAVE_ALERTAS)
}
