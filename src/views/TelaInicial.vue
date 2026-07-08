<template>
  <div class="pagina-menu">
    <div class="grade-opcoes">
      <RouterLink to="/cadastro-veiculo" class="cartao">Cadastro de Veículo</RouterLink>
      <RouterLink to="/cadastro-motorista" class="cartao">Cadastro de Motorista</RouterLink>
      <RouterLink to="/viagem" class="cartao">Iniciar Viagem</RouterLink>
      <RouterLink to="/concluir-viagem" class="cartao">Concluir Viagem</RouterLink>
      <RouterLink to="/qualidade-veiculo" class="cartao">Qualidade do Veículo</RouterLink>
      <RouterLink to="/motoristas" class="cartao">Listagem de Motoristas</RouterLink>
      <RouterLink to="/veiculos" class="cartao">Listagem de Veículos</RouterLink>

      <button type="button" class="botao-limpar-dados" @click="confirmarLimpezaDados">
        Limpar todos os dados
      </button>
    </div>

    <div class="area-conteudo">
      <div class="cabecalho">
        <h1>FrotaGesta</h1>
        <p>Sistema de Controle de Frota e Manutenção Preventiva</p>
      </div>

      <div class="conteudo-principal">
        <div class="painel-status">
          <h2>Status da Frota</h2>

          <div class="resumo-status">
            <div class="resumo-item resumo-disponivel">
              <span class="resumo-numero">{{ veiculosDisponiveis.length }}</span>
              <span class="resumo-label">Disponíveis</span>
            </div>
            <div class="resumo-item resumo-rota">
              <span class="resumo-numero">{{ veiculosEmRota.length }}</span>
              <span class="resumo-label">Em Rota</span>
            </div>
            <div class="resumo-item resumo-manutencao">
              <span class="resumo-numero">{{ veiculosManutencao.length }}</span>
              <span class="resumo-label">Manutenção Urgente</span>
            </div>
          </div>

          <table class="tabela-status" v-if="veiculosComStatus.length">
            <thead>
              <tr>
                <th>Placa</th>
                <th>Modelo</th>
                <th>Tipo</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="veiculo in veiculosComStatus" :key="veiculo.placa">
                <td>{{ veiculo.placa }}</td>
                <td>{{ veiculo.modelo }}</td>
                <td>{{ veiculo.tipo }}</td>
                <td>
                  <span class="badge-status" :class="classeStatus(veiculo.status)">{{ veiculo.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="mensagem-vazio">Nenhum veículo cadastrado.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getVeiculos, getViagens, getAlertas, limparTodosOsDados } from '../services/dados'

export default {
  name: 'TelaInicial',

  data() {
    return {
      veiculos: [],
      viagens: [],
      alertas: [],
    }
  },

  created() {
    this.carregarDados()
  },

  computed: {
    veiculosComStatus() {
      return this.veiculos.map(veiculo => ({
        ...veiculo,
        status: this.statusVeiculo(veiculo.placa),
      }))
    },

    veiculosDisponiveis() {
      return this.veiculosComStatus.filter(v => v.status === 'Disponível')
    },

    veiculosEmRota() {
      return this.veiculosComStatus.filter(v => v.status === 'Em rota')
    },

    veiculosManutencao() {
      return this.veiculosComStatus.filter(v => v.status === 'Necessitando de Manutenção Urgente')
    },
  },

  methods: {
    carregarDados() {
      this.veiculos = getVeiculos()
      this.viagens = getViagens()
      this.alertas = getAlertas()
    },

    confirmarLimpezaDados() {
      const confirmado = confirm(
        'Isso vai apagar todos os veículos, motoristas, viagens e alertas cadastrados. Deseja continuar?'
      )
      if (!confirmado) return

      limparTodosOsDados()
      this.carregarDados()
      alert('Todos os dados foram removidos.')
    },

    statusVeiculo(placa) {
      const emRota = this.viagens.some(v => v.veiculo.placa === placa && !v.dataChegada)
      if (emRota) return 'Em rota'

      const manutencaoPendente = this.alertas.some(a => a.veiculoPlaca === placa && a.status === 'Pendente')
      if (manutencaoPendente) return 'Necessitando de Manutenção Urgente'

      return 'Disponível'
    },

    classeStatus(status) {
      if (status === 'Em rota') return 'status-rota'
      if (status === 'Necessitando de Manutenção Urgente') return 'status-manutencao'
      return 'status-disponivel'
    },
  },
}
</script>

<style>
.pagina-menu {
  min-height: 100vh;
  box-sizing: border-box;
}

.area-conteudo {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  margin-left: 280px;
  padding: 40px 20px;
  box-sizing: border-box;
}

.cabecalho {
  text-align: center;
  margin-bottom: 32px;
}

.cabecalho h1 {
  color: #ffffff;
  font-size: 42px;
  margin: 0;
}

.cabecalho p {
  color: #b5b5b5;
  font-size: 16px;
  margin-top: 8px;
}

.conteudo-principal {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  width: 100%;
  flex: 1;
}

.painel-status {
  flex: 1;
  min-width: 0;
  background: #e6e5e5;
  border-radius: 10px;
  padding: 28px 32px;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.35);
}

.painel-status h2 {
  margin: 0 0 20px 0;
  color: #1a1a1a;
}

.resumo-status {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.resumo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18px 12px;
  color: #ffffff;
}

.resumo-numero {
  font-size: 32px;
  font-weight: bold;
}

.resumo-label {
  font-size: 14px;
  margin-top: 4px;
}

.resumo-disponivel {
  background: rgb(13, 179, 13);
}

.resumo-rota {
  background: rgb(230, 162, 0);
}

.resumo-manutencao {
  background: rgb(210, 30, 30);
}

.tabela-status {
  width: 100%;
  border-collapse: collapse;
}

.tabela-status th,
.tabela-status td {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid #cfcfcf;
}

.tabela-status th {
  color: #4a4a4a;
  font-size: 14px;
  text-transform: uppercase;
}

.badge-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: bold;
  color: #ffffff;
}

.status-disponivel {
  background: rgb(13, 179, 13);
}

.status-rota {
  background: rgb(230, 162, 0);
}

.status-manutencao {
  background: rgb(210, 30, 30);
}

.mensagem-vazio {
  color: #4a4a4a;
}

.grade-opcoes {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  width: 280px;
  background: #000000;
  box-shadow: 4px 0 40px rgba(0, 0, 0, 0.35);
  overflow-y: auto;
  z-index: 10;
}

.cartao {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  text-align: left;
  text-decoration: none;
  color: #b5b5b5;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #2a2a2a;
  transition: color ease 0.2s;
}

.cartao:last-child {
  border-bottom: none;
}

.cartao:hover {
  color: #ffffff;
}

.botao-limpar-dados {
  margin-top: auto;
  padding: 14px 20px;
  width: 100%;
  height: auto;
  background: transparent;
  border: none;
  border-top: 1px solid #2a2a2a;
  border-radius: 0;
  color: rgb(210, 30, 30);
  font-size: 13px;
  font-weight: bold;
  text-align: left;
  cursor: pointer;
  transition: color ease 0.2s, background ease 0.2s;
}

.botao-limpar-dados:hover {
  color: #ffffff;
  background: rgb(210, 30, 30);
  transform: none;
}

.botao-limpar-dados:active {
  background: rgb(170, 20, 20);
  transform: none;
}

@media (max-width: 900px) {
  .grade-opcoes {
    position: static;
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .area-conteudo {
    margin-left: 0;
  }

  .conteudo-principal {
    flex-direction: column;
  }

  .grade-opcoes .cartao {
    flex: 1 1 200px;
    border-bottom: none;
  }
}
</style>
