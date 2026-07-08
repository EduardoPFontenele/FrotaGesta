<template>
  <div class="pagina">
    <div class="block-qualidade">
      <RouterLink to="/" class="link-voltar">Voltar ao Menu</RouterLink>

      <h1>QUALIDADE DO VEÍCULO</h1>

      <div class="campo">
        <label>Buscar Veículo por Placa ou Modelo</label>
      </div>

      <div class="autocomplete-wrapper">
        <input
          v-model="busca"
          placeholder="Ex: ABC-1234 ou Corolla"
          @focus="mostrarSugestoes = true"
          @blur="fecharSugestoes"
          autocomplete="off"
        />

        <ul v-if="mostrarSugestoes && sugestoes.length > 0" class="lista-sugestoes">
          <li v-for="veiculo in sugestoes"
            :key="veiculo.placa"
            @mousedown.prevent="selecionarVeiculo(veiculo)"
          >
            <span class="sugestao-nome">{{ veiculo.modelo }}</span>
            <span class="sugestao-cpf">{{ veiculo.placa }}</span>
          </li>
        </ul>
        <p v-if="mostrarSugestoes && busca && sugestoes.length === 0" class="sem-resultado">
          Nenhum veículo encontrado.
        </p>
      </div>

      <div v-if="veiculoSelecionado" class="detalhe-veiculo">
        <div class="cabecalho-veiculo">
          <div>
            <h2>{{ veiculoSelecionado.modelo }} <span class="placa-veiculo">{{ veiculoSelecionado.placa }}</span></h2>
            <p class="info-secundaria">Ano {{ veiculoSelecionado.ano }} · {{ veiculoSelecionado.km }} km</p>
          </div>
          <span class="badge-status" :class="classeStatus(statusAtual)">{{ statusAtual }}</span>
        </div>

        <div class="secao">
          <h3>Abastecimento</h3>

          <ul class="lista-problemas" v-if="abastecimentosVeiculo.length">
            <li v-for="abastecimento in abastecimentosVeiculo" :key="abastecimento.id" class="problema-item">
              <div class="problema-info">
                <span class="problema-tipo">{{ abastecimento.volume }} L · R$ {{ abastecimento.valorTotal.toFixed(2) }}</span>
                <span class="problema-data">{{ abastecimento.km }} km · {{ formatarData(abastecimento.dataHora) }}</span>
              </div>
            </li>
          </ul>
          <p v-else class="mensagem-vazio">Nenhum abastecimento registrado para este veículo.</p>

          <div class="campo">
            <label>Volume (litros abastecidos)</label>
            <input type="number" min="0" step="0.01" v-model="volumeInput" />
          </div>

          <div class="campo">
            <label>Valor total do abastecimento (R$)</label>
            <input type="number" min="0" step="0.01" v-model="valorTotalInput" />
          </div>

          <div class="campo">
            <label>KM em que o abastecimento foi efetuado</label>
            <input type="number" min="0" v-model="kmAbastecimentoInput" />
          </div>

          <div class="campo">
            <label>Data e Hora do abastecimento</label>
            <input type="datetime-local" v-model="dataHoraAbastecimentoInput" />
          </div>

          <div class="linha-acao">
            <button type="button" class="botao-secundario" @click="registrarAbastecimento">Registrar abastecimento</button>
          </div>
        </div>

        <div class="secao">
          <h3>Problemas e Manutenções</h3>

          <ul class="lista-problemas" v-if="alertasVeiculo.length">
            <li v-for="alerta in alertasVeiculo" :key="alerta.id" class="problema-item">
              <div class="problema-info">
                <span class="problema-tipo">{{ alerta.tipo }}</span>
                <span class="problema-data">{{ formatarData(alerta.data) }}</span>
              </div>
              <span class="badge-status status-manutencao">Pendente</span>
              <button
                type="button"
                class="botao-resolver"
                @click="resolverAlerta(alerta)"
              >
                Marcar como resolvido
              </button>
            </li>
          </ul>
          <p v-else class="mensagem-vazio">Nenhum problema registrado para este veículo.</p>

          <div class="linha-acao">
            <select v-model="novoTipoProblema">
              <option v-for="tipo in tiposProblema" :key="tipo.id_tipo_manutencao" :value="tipo.id_tipo_manutencao">{{ tipo.descricao }}</option>
            </select>
            <button type="button" class="botao-secundario" @click="registrarProblema">Registrar problema</button>
          </div>
        </div>

        <div class="secao">
          <button
            type="button"
            class="botao-liberar"
            :disabled="veiculoEmRota || temProblemasPendentes"
            @click="liberarVeiculo"
          >
            DISPONIBILIZAR VEÍCULO
          </button>
          <p v-if="veiculoEmRota" class="aviso-rota">Este veículo está em rota e não pode ser liberado agora.</p>
          <p v-else-if="temProblemasPendentes" class="aviso-rota">Resolva todos os problemas pendentes antes de disponibilizar o veículo.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  getVeiculos,
  getViagens,
  getAlertas,
  getAbastecimentos,
  salvarAbastecimentos,
  registrarAlerta,
  resolverAlerta as resolverAlertaApi,
  getTiposManutencao,
} from '../services/dados'

export default {
  name: 'TelaQualidadeVeiculo',

  data() {
    return {
      veiculos: [],
      viagens: [],
      alertas: [],
      abastecimentos: [],
      busca: '',
      mostrarSugestoes: false,
      veiculoSelecionado: null,
      volumeInput: '',
      valorTotalInput: '',
      kmAbastecimentoInput: '',
      dataHoraAbastecimentoInput: '',
      novoTipoProblema: null,
      tiposProblema: [], // carregado do banco (id_tipo_manutencao + descricao)
    }
  },

  created() {
    this.carregarDados()
  },

  computed: {
    sugestoes() {
      const termo = this.busca.trim().toLowerCase()
      if (!termo) return this.veiculos
      return this.veiculos.filter(v =>
        v.placa.toLowerCase().includes(termo) || v.modelo.toLowerCase().includes(termo)
      )
    },

    veiculoEmRota() {
      if (!this.veiculoSelecionado) return false
      return this.viagens.some(v => v.veiculo.placa === this.veiculoSelecionado.placa && !v.dataChegada)
    },

    alertasVeiculo() {
      if (!this.veiculoSelecionado) return []
      return this.alertas
        .filter(a => a.veiculoPlaca === this.veiculoSelecionado.placa)
        .slice()
        .sort((a, b) => new Date(b.data) - new Date(a.data))
    },

    abastecimentosVeiculo() {
      if (!this.veiculoSelecionado) return []
      return this.abastecimentos
        .filter(a => a.veiculoPlaca === this.veiculoSelecionado.placa)
        .slice()
        .sort((a, b) => new Date(b.dataHora) - new Date(a.dataHora))
    },

    temProblemasPendentes() {
      return this.alertasVeiculo.some(a => a.status === 'Pendente')
    },

    statusAtual() {
      if (!this.veiculoSelecionado) return ''
      if (this.veiculoEmRota) return 'Em rota'
      if (this.temProblemasPendentes) return 'Necessitando de Manutenção Urgente'
      return 'Disponível'
    },
  },

  watch: {
    busca(valor) {
      if (this.veiculoSelecionado && `${this.veiculoSelecionado.modelo} - ${this.veiculoSelecionado.placa}` !== valor) {
        this.veiculoSelecionado = null
      }
    },
  },

  methods: {
    async carregarDados() {
      try {
        const [veiculos, viagens, alertas, abastecimentos, tipos] = await Promise.all([
          getVeiculos(),
          getViagens(),
          getAlertas(),
          getAbastecimentos(),
          getTiposManutencao(),
        ])
        this.veiculos = veiculos
        this.viagens = viagens
        this.alertas = alertas
        this.abastecimentos = abastecimentos
        this.tiposProblema = tipos
        if (this.novoTipoProblema === null && tipos.length) {
          this.novoTipoProblema = tipos[0].id_tipo_manutencao
        }
      } catch (e) {
        alert(`Erro ao carregar dados: ${e.message}`)
      }
    },

    fecharSugestoes() {
      setTimeout(() => { this.mostrarSugestoes = false }, 150)
    },

    selecionarVeiculo(veiculo) {
      this.veiculoSelecionado = veiculo
      this.busca = `${veiculo.modelo} - ${veiculo.placa}`
      this.mostrarSugestoes = false
      this.volumeInput = ''
      this.valorTotalInput = ''
      this.kmAbastecimentoInput = ''
      this.dataHoraAbastecimentoInput = ''
    },

    classeStatus(status) {
      if (status === 'Em rota') return 'status-rota'
      if (status === 'Necessitando de Manutenção Urgente') return 'status-manutencao'
      return 'status-disponivel'
    },

    formatarData(valor) {
      if (!valor) return ''
      return new Date(valor).toLocaleString('pt-BR')
    },

    async registrarAbastecimento() {
      const volume = Number(this.volumeInput)
      const valorTotal = Number(this.valorTotalInput)
      const km = Number(this.kmAbastecimentoInput)

      if (Number.isNaN(volume) || volume <= 0) {
        alert('Informe um volume de abastecimento válido.')
        return
      }

      if (Number.isNaN(valorTotal) || valorTotal <= 0) {
        alert('Informe um valor total de abastecimento válido.')
        return
      }

      if (Number.isNaN(km) || km < 0) {
        alert('Informe o KM do abastecimento.')
        return
      }

      if (!this.dataHoraAbastecimentoInput) {
        alert('Informe a data e hora do abastecimento.')
        return
      }

      try {
        await salvarAbastecimentos({
          id_veiculo: this.veiculoSelecionado.id_veiculo,
          litros: volume,
          valor_total: valorTotal,
          km_abastecimento: km,
          data_hora: new Date(this.dataHoraAbastecimentoInput).toISOString(),
        })
      } catch (e) {
        alert(`Erro ao registrar abastecimento: ${e.message}`)
        return
      }

      const placa = this.veiculoSelecionado.placa
      this.volumeInput = ''
      this.valorTotalInput = ''
      this.kmAbastecimentoInput = ''
      this.dataHoraAbastecimentoInput = ''

      await this.carregarDados()
      alert(`Abastecimento de ${volume} L registrado para o veículo ${placa}.`)
    },

    async registrarProblema() {
      const tipoSelecionado = this.tiposProblema.find(
        t => t.id_tipo_manutencao === this.novoTipoProblema
      )
      if (!tipoSelecionado) {
        alert('Selecione um tipo de problema.')
        return
      }

      const jaPendente = this.alertasVeiculo.some(a =>
        a.tipo === tipoSelecionado.descricao && a.status === 'Pendente'
      )
      if (jaPendente) {
        alert(`Já existe um problema pendente do tipo "${tipoSelecionado.descricao}" para este veículo.`)
        return
      }

      try {
        await registrarAlerta({
          id_veiculo: this.veiculoSelecionado.id_veiculo,
          id_tipo_manutencao: this.novoTipoProblema,
        })
      } catch (e) {
        alert(`Erro ao registrar problema: ${e.message}`)
        return
      }

      await this.carregarDados()
      alert(`Problema "${tipoSelecionado.descricao}" registrado para o veículo ${this.veiculoSelecionado.placa}.`)
    },

    async resolverAlerta(alerta) {
      try {
        await resolverAlertaApi(alerta.id)
      } catch (e) {
        alert(`Erro ao resolver o problema: ${e.message}`)
        return
      }
      await this.carregarDados()
    },

    liberarVeiculo() {
      if (this.veiculoEmRota) {
        alert('Este veículo está em rota e não pode ser liberado agora.')
        return
      }

      if (this.temProblemasPendentes) {
        alert('Resolva todos os problemas pendentes antes de disponibilizar o veículo.')
        return
      }

      alert(`Veículo ${this.veiculoSelecionado.placa} está disponível!`)
    },
  },
}
</script>

<style>
.block-qualidade {
  margin-top: 5%;
  margin-bottom: 5%;
  display: flex;
  flex-direction: column;
  border: 1px solid rgb(0, 0, 0);
  border-radius: 10px;
  width: 600px;
  padding: 60px 80px;
  background: #e6e5e5;
  box-shadow: 0 0 120px rgba(0, 0, 0);
}

label {
  font-size: 18px;
}


select {
  width: 100%;
  height: 36px;
  font-size: 16px;
}

.detalhe-veiculo {
  margin-top: 20px;
}

.cabecalho-veiculo {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #cfcfcf;
}

.cabecalho-veiculo h2 {
  margin: 0;
  font-size: 16px;
}

.placa-veiculo {
  font-size: 14px;
  font-weight: normal;
  color: #666;
}

.info-secundaria {
  margin: 4px 0 0 0;
  color: #555;
  font-size: 14px;
}

.secao {
  margin-top: 24px;
}

.secao h3 {
  margin: 0 0 12px 0;
  font-size: 22px;
  color: #333;
}

.linha-acao {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.linha-acao input,
.linha-acao select {
  flex: 1;
}

.botao-secundario {
  width: auto;
  height: 36px;
  margin-top: 0;
  padding: 0 16px;
  font-size: 14px;
  white-space: nowrap;
}

.lista-problemas {
  list-style: none;
  margin: 0;
  padding: 0;
}

.problema-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #dedede;
}

.problema-item:last-child {
  border-bottom: none;
}

.problema-info {
  display: flex;
  flex-direction: column;
}

.problema-tipo {
  font-weight: 600;
  font-size: 15px;
}

.problema-data {
  font-size: 13px;
  color: #777;
}

.botao-resolver {
  width: auto;
  height: 32px;
  margin-top: 0;
  padding: 0 12px;
  font-size: 13px;
  white-space: nowrap;
}

.botao-liberar {
  width: 100%;
  background: rgb(0, 90, 200);
}

.botao-liberar:hover {
  background: rgb(0, 70, 160);
}

.botao-liberar:disabled {
  background: #a0a0a0;
  cursor: not-allowed;
  transform: none;
}

.aviso-rota {
  margin-top: 8px;
  color: rgb(210, 30, 30);
  font-size: 14px;
}
</style>
