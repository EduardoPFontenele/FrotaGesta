<template>
  <div class="pagina">
    <form @submit.prevent="registrarVeiculo">
      <div class="block-form">
        <RouterLink to="/" class="link-voltar">Voltar ao Menu</RouterLink>
        <h1>CADASTRO DE VEÍCULOS</h1>

        <div class="campo">
          <label>Placa</label>
        </div>
        <input
          type="text"
          v-model="placa"
          placeholder="Ex: ABC-1234"
          :class="{'input-erro': erros.placa}"
        />
        <span class="mensagem-erro" v-if="erros.placa">{{ erros.placa }}</span>

        <div class="campo">
          <label>Modelo</label>
        </div>
        <input
          type="text"
          v-model="modelo"
          placeholder="Ex: Corolla"
          :class="{'input-erro': erros.modelo}"
        />
        <span class="mensagem-erro" v-if="erros.modelo">{{ erros.modelo }}</span>

        <div class="campo">
          <label>Tipo do Veículo</label>
        </div>
        <select v-model="tipo" :class="{'input-erro': erros.tipo}">
          <option value="" disabled>Selecione o tipo</option>
          <option v-for="opcao in tiposVeiculo" :key="opcao" :value="opcao">{{ opcao }}</option>
        </select>
        <span class="mensagem-erro" v-if="erros.tipo">{{ erros.tipo }}</span>

        <div class="campo">
          <label>Ano</label>
        </div>
        <input
          type="number"
          v-model="ano"
          placeholder="Ex: 2020"
          :class="{'input-erro': erros.ano}"
        />
        <span class="mensagem-erro" v-if="erros.ano">{{ erros.ano }}</span>

        <div class="campo">
          <label>Km atual</label>
        </div>
        <input
          type="number"
          v-model="km"
          placeholder="Ex: 85000"
        />
        <span class="mensagem-erro" v-if="erros.km">{{ erros.km }}</span>

        <button type="submit">CADASTRAR</button>
      </div>
    </form>
  </div>
</template>

<script>
import { getVeiculos, salvarVeiculos } from '../services/dados'

export default {
  data() {
    return {
      placa: '',
      modelo: '',
      tipo: '',
      ano: '',
      km: '',
      tiposVeiculo: ['Carro', 'Van', 'Caminhão'],
      erros: {
        placa: '',
        modelo: '',
        tipo: '',
        ano: '',
        km: '',
      }
    }
  },

  watch: {
    placa(valorDigitado) {
      this.placa = this.formatarPlaca(valorDigitado)
      if (valorDigitado) {
        this.erros.placa =''
      }
    }
  },

  methods: {

    formatarPlaca(valor) {
      // Remove tudo que não é letra ou número
      valor = valor.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()

      // Define o máximo de 7 caracteres
      valor = valor.slice(0,7)

      // Força que os primeiros 3 digitos sejam letras
      const letras = valor.slice(0,3).replace(/[^A-Z]/g, '')
      // Força que os digitos 4->7 sejam apenas numeros
      const numeros = valor.slice(3).replace(/[^0-9]/g, '')

      if (numeros.length > 0) {
        return `${letras}-${numeros}`
      }

      return letras
    },
    validar() {
      this.erros = { placa: '', modelo: '', tipo: '', ano: '', km: '' }
      let valido = true

      if (!this.placa) {
        this.erros.placa = 'Insira a placa do veículo.'
        valido = false
      } else {
        const veiculos = getVeiculos()
        if (veiculos.some(v => v.placa === this.placa)) {
          this.erros.placa = 'Já existe um veículo cadastrado com esta placa.'
          valido = false
        }
      }

      if (!this.modelo) {
        this.erros.modelo = 'Insira o modelo do veículo.'
        valido = false
      }

      if (!this.tipo) {
        this.erros.tipo = 'Selecione o tipo do veículo.'
        valido = false
      }

      if (!this.ano) {
        this.erros.ano = 'Insira o ano do veículo.'
        valido = false

      } else if (this.ano <= 0) {
        this.erros.ano = 'Insira um ano válido.'
        valido = false
      }

      if (!this.km) {
        this.erros.km = 'Insira a quilometragem do veículo.'
        valido = false
      }

      if (this.km < 0) {
        this.erros.km = 'Insira uma quilometragem válida.'
      }

      return valido
    },

    registrarVeiculo() {
      if (!this.validar()) return

      const veiculo = {
        placa: this.placa,
        modelo: this.modelo,
        tipo: this.tipo,
        ano: this.ano,
        km: this.km,
      }

      const veiculos = getVeiculos()
      veiculos.push(veiculo)
      salvarVeiculos(veiculos)

      alert(`Veículo ${this.placa} cadastrado com sucesso!`)

      this.placa = ''
      this.modelo = ''
      this.tipo = ''
      this.ano = ''
      this.km = ''
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

input,
select {
  width: 100%;
  height: 30px;
  font-size: 18px;
}

option {
  font-size: 18px;
}

.block-form {
  margin-top: 20%;
  display: flex;
  flex-direction: column;
  border: 1px solid rgb(0, 0, 0);
  border-radius: 10px;
  width: 500px;
  padding: 100px;
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
  font-weight:bold;
  transition: all ease 0.2s
}

button:hover {
  background: rgb(11, 151, 11);
  transform:translateY(-1px);
}

button:active{
  background: rgb(9, 121, 9);
  transform:translateY(1px);

}

.mensagem-erro {
  color: rgb(255, 0, 0);
  font-size:15px;
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
  color: rgb(6, 91, 6);
}
</style>

