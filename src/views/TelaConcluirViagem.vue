<template>
  <div class="pagina">
    <form @submit.prevent="concluirViagem" novalidate>
      <div class="block-form">
        <RouterLink to="/" class="link-voltar">Voltar ao Menu</RouterLink>

        <h1>CONCLUIR VIAGEM</h1>

        <!-- Veículo em rota -->
        <div class="campo">
          <label>Veículo</label>
        </div>

        <div class="autocomplete-wrapper">
          <input
            v-model="buscaVeiculo"
            placeholder="Digite o modelo ou placa do veículo em rota"
            @focus="mostrarSugestoes = true"
            @blur="fecharSugestoes"
            autocomplete="off"
            :class="{'input-erro': erros.viagem}"
          />

          <ul v-if="mostrarSugestoes && sugestoes.length > 0" class="lista-sugestoes">
            <li v-for="viagem in sugestoes"
              :key="viagem.id"
              @mousedown.prevent="selecionarViagem(viagem)"
            >
              <span class="sugestao-nome">{{ viagem.veiculo.modelo }} - {{ viagem.veiculo.placa }}</span>
              <span class="sugestao-cpf">Motorista: {{ viagem.motorista.nome }}</span>
            </li>
          </ul>
          <p v-if="mostrarSugestoes && buscaVeiculo && sugestoes.length === 0" class="sem-resultado">
            Nenhum veículo em rota encontrado.
          </p>
        </div>

        <span class="mensagem-erro" v-if="erros.viagem">{{ erros.viagem }}</span>

        <!-- Resumo da viagem selecionada -->
        <div class="resumo-viagem" v-if="viagemSelecionada">
          <p><strong>Motorista:</strong> {{ viagemSelecionada.motorista.nome }}</p>
          <p><strong>Saída:</strong> {{ formatarData(viagemSelecionada.dataSaida) }}</p>
          <p><strong>Km inicial:</strong> {{ viagemSelecionada.kmInicial }}</p>
        </div>

        <!-- Data/Hora de Chegada -->
        <div class="campo">
          <label>Data/Hora de Chegada</label>
        </div>
        <input
          type="datetime-local"
          v-model="dataChegada"
          :min="viagemSelecionada ? viagemSelecionada.dataSaida : null"
          :class="{'input-erro': erros.dataChegada}"
        />
        <span class="mensagem-erro" v-if="erros.dataChegada">{{ erros.dataChegada }}</span>

        <!-- KM Final -->
        <div class="campo">
          <label>Quilometragem Final</label>
        </div>
        <input
          type="number"
          v-model="kmFinal"
          placeholder="Ex: 85320"
          min="0"
          :class="{'input-erro': erros.kmFinal}"
        />
        <span class="mensagem-erro" v-if="erros.kmFinal">{{ erros.kmFinal }}</span>

        <button type="submit">CONCLUIR VIAGEM</button>

      </div>
    </form>
  </div>
</template>

<script>
import { getViagens, encerrarViagem } from '../services/dados'

export default {
  data() {
    return {
      buscaVeiculo: '',
      viagemSelecionada: null,
      mostrarSugestoes: false,
      viagensAbertas: [],
      dataChegada: '',
      kmFinal: '',
      erros: {
        viagem: '',
        dataChegada: '',
        kmFinal: '',
      }
    }
  },

  computed: {
    sugestoes() {
      if (!this.buscaVeiculo.trim()) return this.viagensAbertas
      const termo = this.buscaVeiculo.toLowerCase()
      return this.viagensAbertas.filter(v =>
        v.veiculo.modelo.toLowerCase().includes(termo) || v.veiculo.placa.toLowerCase().includes(termo)
      )
    }
  },

  async mounted() {
    await this.carregarViagensAbertas()
  },

  watch: {
    buscaVeiculo(valor) {
      if (this.viagemSelecionada && `${this.viagemSelecionada.veiculo.modelo} - ${this.viagemSelecionada.veiculo.placa}` !== valor) {
        this.viagemSelecionada = null
      }
      if (valor) this.erros.viagem = ''
    }
  },

  methods: {
    async carregarViagensAbertas() {
      try {
        const viagens = await getViagens()
        this.viagensAbertas = viagens.filter(v => !v.dataChegada)
      } catch (e) {
        alert(`Erro ao carregar viagens: ${e.message}`)
      }
    },

    formatarData(valor) {
      if (!valor) return ''
      const data = new Date(valor)
      return data.toLocaleString('pt-BR')
    },

    selecionarViagem(viagem) {
      this.viagemSelecionada = viagem
      this.buscaVeiculo = `${viagem.veiculo.modelo} - ${viagem.veiculo.placa}`
      this.mostrarSugestoes = false
      this.erros.viagem = ''
    },

    fecharSugestoes() {
      setTimeout(() => { this.mostrarSugestoes = false }, 150)
    },

    validar() {
      this.erros = { viagem: '', dataChegada: '', kmFinal: '' }
      let valido = true

      if (!this.viagemSelecionada) {
        this.erros.viagem = 'Selecione um veículo em rota.'
        valido = false
      }

      if (!this.dataChegada) {
        this.erros.dataChegada = 'Informe a data/hora de chegada.'
        valido = false
      } else if (this.viagemSelecionada && new Date(this.dataChegada) < new Date(this.viagemSelecionada.dataSaida)) {
        this.erros.dataChegada = 'A chegada não pode ser antes da saída.'
        valido = false
      }

      if (!this.kmFinal && this.kmFinal !== 0) {
        this.erros.kmFinal = 'Informe a quilometragem final.'
        valido = false
      } else if (this.viagemSelecionada && Number(this.kmFinal) < this.viagemSelecionada.kmInicial) {
        this.erros.kmFinal = 'A quilometragem final não pode ser menor que a inicial.'
        valido = false
      }

      return valido
    },

    // Encerramento da viagem: uma única chamada à procedure encerrar_viagem,
    // que valida, atualiza status/km/chegada e dispara a trigger de manutenção.
    async concluirViagem() {
      if (!this.validar()) return

      const placa = this.viagemSelecionada.veiculo.placa

      try {
        await encerrarViagem(this.viagemSelecionada.id, this.kmFinal, this.dataChegada)
      } catch (e) {
        // erros da procedure (viagem já encerrada / km incoerente)
        this.erros.kmFinal = e.message
        return
      }

      alert(`Viagem concluída para o veículo ${placa}!`)

      this.buscaVeiculo = ''
      this.viagemSelecionada = null
      this.dataChegada = ''
      this.kmFinal = ''
      await this.carregarViagensAbertas()
    },
  },
}
</script>

<style>
body {
  min-height: 100vh;
  margin: 0;
  background: linear-gradient(to bottom left, rgb(35, 35, 35), rgb(38, 38, 38), rgb(40, 40, 40));
  font-family: 'Inter';
}

.pagina {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

h1 {
  display: flex;
  justify-content: center;
  align-items: center;
}

input {
  width: 100%;
  height: 30px;
  font-size: 18px;
}

.block-form {
  margin-top: 5%;
  display: flex;
  flex-direction: column;
  border: 1px solid rgb(0, 0, 0);
  width: 500px;
  padding: 60px 100px;
  background: #e6e5e5;
  box-shadow: 0 0 120px rgba(0, 0, 0);
}

label {
  display: flex;
  font-size: 18px;
  justify-content: flex-start;
  margin-top: 2%;
}

button {
  font-size: 20px;
  margin-top: 5%;
  height: 50px;
  width: 102%;
  background: rgb(13, 179, 13);
  color: white;
  font-weight: bold;
  transition: all ease 0.2s;
}

button:hover {
  background: rgb(11, 151, 11);
  transform: translateY(-1px);
}

button:active {
  background: rgb(7, 232, 7);
  transform: translateY(1px);
}

.mensagem-erro {
  color: rgb(255, 0, 0);
  font-size: 15px;
}

.autocomplete-wrapper {
  position: relative;
}

.lista-sugestoes {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  list-style: none;
  margin: 2px 0 0 0;
  padding: 0;
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.lista-sugestoes li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.lista-sugestoes li:last-child {
  border-bottom: none;
}

.lista-sugestoes li:hover {
  background: #f0f0f0;
}

.sugestao-nome {
  font-weight: 600;
  font-size: 16px;
}

.sugestao-cpf {
  font-size: 13px;
  color: #777;
}

.sem-resultado {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  margin: 2px 0 0 0;
  padding: 10px 12px;
  font-size: 15px;
  color: #888;
  z-index: 10;
}

.input-erro {
  border: 1px solid red;
}

.link-voltar {
  align-self: flex-start;
  color: rgb(9, 121, 9);
  font-weight: bold;
  text-decoration: none;
  font-size: 15px;
}

.link-voltar:hover {
  text-decoration: underline;
}

.resumo-viagem {
  margin-top: 15px;
  padding: 12px 16px;
  background: #d9d9d9;
  border-radius: 6px;
}

.resumo-viagem p {
  margin: 4px 0;
  font-size: 15px;
}
</style>
