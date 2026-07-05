<template>
  <div class="pagina">
    <form @submit.prevent="registrarViagem" novalidate>
      <div class="block-form">
        <RouterLink to="/" class="link-voltar">&larr; Voltar ao Menu</RouterLink>

        <h1>ABRIR VIAGEM</h1>

        <!-- Motorista -->
        <div class="campo">
          <label>Motorista</label>
        </div>

        <div class="autocomplete-wrapper">
          <input
            v-model="buscaMotorista"
            placeholder="Digite o nome do motorista"
            @focus="mostrarSugestoes = true"
            @blur="fecharSugestoes"
            autocomplete="off"
            :class="{'input-erro': erros.motorista}"
          />

          <ul v-if="mostrarSugestoes && sugestoes.length > 0" class="lista-sugestoes">
            <li v-for="motorista in sugestoes"
              :key="motorista.cpf"
              @mousedown.prevent="selecionarMotorista(motorista)"
            >
              <span class="sugestao-nome">{{ motorista.nome }}</span>
              <span class="sugestao-cpf">{{ motorista.cpf }}</span>
            </li>
          </ul>
          <p v-if="mostrarSugestoes && buscaMotorista && sugestoes.length === 0" class="sem-resultado">
            Nenhum motorista encontrado.
          </p>
        </div>

        <span class="mensagem-erro" v-if="erros.motorista">{{ erros.motorista }}</span>

        <!-- Veículo -->
        <div class="campo">
          <label>Veículo</label>
        </div>

        <div class="autocomplete-wrapper">
          <input
            v-model="buscaVeiculo"
            placeholder="Digite o modelo ou placa"
            @focus="mostrarSugestoesVeiculo = true"
            @blur="fecharSugestoesVeiculo"
            autocomplete="off"
            :class="{'input-erro': erros.veiculo}"
          />

          <ul v-if="mostrarSugestoesVeiculo && sugestoesVeiculo.length > 0" class="lista-sugestoes">
            <li v-for="veiculo in sugestoesVeiculo"
              :key="veiculo.placa"
              @mousedown.prevent="selecionarVeiculo(veiculo)"
            >
              <span class="sugestao-nome">{{ veiculo.modelo }}</span>
              <span class="sugestao-cpf">{{ veiculo.placa }}</span>
            </li>
          </ul>
          <p v-if="mostrarSugestoesVeiculo && buscaVeiculo && sugestoesVeiculo.length === 0" class="sem-resultado">
            Nenhum veículo encontrado.
          </p>
        </div>

        <span class="mensagem-erro" v-if="erros.veiculo">{{ erros.veiculo }}</span>

        <!-- Data/Hora de Saída -->
        <div class="campo">
          <label>Data/Hora de Saída</label>
        </div>
        <input
          type="datetime-local"
          v-model="dataSaida"
          :class="{'input-erro': erros.dataSaida}"
        />
        <span class="mensagem-erro" v-if="erros.dataSaida">{{ erros.dataSaida }}</span>

        <!-- KM Inicial -->
        <div class="campo">
          <label>Quilometragem Inicial</label>
        </div>
        <input
          type="number"
          v-model="kmInicial"
          placeholder="Ex: 85000"
          min="0"
          :class="{'input-erro': erros.kmInicial}"
        />
        <span class="mensagem-erro" v-if="erros.kmInicial">{{ erros.kmInicial }}</span>

        <button type="submit">ABRIR VIAGEM</button>

      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      buscaMotorista: '',
      motoristaSelecionado: null,
      mostrarSugestoes: false,
      motoristas: [],
      buscaVeiculo: '',
      veiculos: [],
      veiculoSelecionado: null,
      mostrarSugestoesVeiculo: false,
      dataSaida: '',
      kmInicial: '',
      erros: {
        motorista: '',
        veiculo: '',
        dataSaida: '',
        kmInicial: '',
      }
    }
  },

  computed: {
    sugestoes() {
      if (!this.buscaMotorista.trim()) return this.motoristas
      const termo = this.buscaMotorista.toLowerCase()
      return this.motoristas.filter(m => m.nome.toLowerCase().includes(termo))
    },
    sugestoesVeiculo() {
      if (!this.buscaVeiculo.trim()) return this.veiculos
      const termo = this.buscaVeiculo.toLowerCase()
      return this.veiculos.filter(v =>
        v.modelo.toLowerCase().includes(termo) || v.placa.toLowerCase().includes(termo)
      )
    }
  },

  mounted() {
    const contextoMotoristas = localStorage.getItem('motoristas')
    this.motoristas = contextoMotoristas ? JSON.parse(contextoMotoristas) : []

    const contextoVeiculos = localStorage.getItem('veiculos')
    this.veiculos = contextoVeiculos ? JSON.parse(contextoVeiculos) : []
  },

  watch: {
    buscaMotorista(valor) {
      if (this.motoristaSelecionado && this.motoristaSelecionado.nome !== valor) {
        this.motoristaSelecionado = null
      }
      if (valor) this.erros.motorista = ''
    }
  },

  methods: {
    selecionarMotorista(motorista) {
      this.motoristaSelecionado = motorista
      this.buscaMotorista = motorista.nome
      this.mostrarSugestoes = false
    },

    fecharSugestoes() {
      setTimeout(() => { this.mostrarSugestoes = false }, 150)
    },

    fecharSugestoesVeiculo() {
      setTimeout(() => { this.mostrarSugestoesVeiculo = false }, 150)
    },

    selecionarVeiculo(veiculo) {
      this.veiculoSelecionado = veiculo
      this.buscaVeiculo = `${veiculo.modelo} - ${veiculo.placa}`
      this.mostrarSugestoesVeiculo = false
      this.kmInicial = veiculo.km
      this.erros.veiculo = ''
    },

    validar() {
      this.erros = { motorista: '', veiculo: '', dataSaida: '', kmInicial: '' }
      let valido = true

      if (!this.motoristaSelecionado) {
        this.erros.motorista = 'Selecione um motorista cadastrado.'
        valido = false
      }

      if (!this.veiculoSelecionado) {
        this.erros.veiculo = 'Selecione um veículo.'
        valido = false
      }

      if (!this.dataSaida) {
        this.erros.dataSaida = 'Informe a data/hora de saída.'
        valido = false
      }

      if (!this.kmInicial && this.kmInicial !== 0) {
        this.erros.kmInicial = 'Informe a quilometragem inicial.'
        valido = false
      } else if (this.kmInicial < 0) {
        this.erros.kmInicial = 'Quilometragem inválida.'
        valido = false
      }

      return valido
    },

    registrarViagem() {
      if (!this.validar()) return

      const viagem = {
        motorista: this.motoristaSelecionado,
        veiculo: this.veiculoSelecionado,
        dataSaida: this.dataSaida,
        kmInicial: Number(this.kmInicial),
        dataChegada: null,
        kmFinal: null,
      }

      const contexto = localStorage.getItem('viagens')
      const viagens = contexto ? JSON.parse(contexto) : []
      viagens.push(viagem)
      localStorage.setItem('viagens', JSON.stringify(viagens, null, 2))

      alert(`Viagem aberta para ${this.motoristaSelecionado.nome} com o veículo ${this.veiculoSelecionado.placa}!`)

      this.buscaMotorista = ''
      this.motoristaSelecionado = null
      this.buscaVeiculo = ''
      this.veiculoSelecionado = null
      this.dataSaida = ''
      this.kmInicial = ''
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
</style>
