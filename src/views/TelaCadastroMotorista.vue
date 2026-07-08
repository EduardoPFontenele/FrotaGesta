<template>
  <div class="pagina">
    <form @submit.prevent="registrarMotorista">
      <div class="block-form">
        <RouterLink to="/" class="link-voltar">Voltar ao Menu</RouterLink>

        <h1>CADASTRO DE MOTORISTA</h1>
        <div class="campo">
          <label>CPF</label>
        </div>

        <input
          type="text"
          v-model="cpf"
          placeholder="Ex: 123.456.789-10"
          :class="{'input-erro': erros.cpf}"
        />

        <span class="mensagem-erro" v-if="erros.cpf">{{ erros.cpf }}</span>

        <div class="campo">
          <label>Nome Completo</label>
        </div>

        <input
          type="text"
          v-model="nome"
          placeholder="Ex: Eduardo Prudêncio Fontenele"
          :class="{'input-erro': erros.nome}"
        />

        <span class="mensagem-erro" v-if="erros.nome">{{ erros.nome }}</span>

        <div class="campo">
          <label>Categoria da CNH</label>
        </div>

        <input
          type="text"
          v-model="categoria_cnh"
          placeholder="Ex: A,B,C,..."
          :class="{'input-erro': erros.categoria_cnh}"
        />

        <span class="mensagem-erro" v-if="erros.categoria_cnh">{{ erros.categoria_cnh }}</span>

        <button type="submit">CADASTRAR</button>

      </div>
    </form>
  </div>
</template>

<script>
import { salvarMotoristas } from '../services/dados'

export default {
  data() {
    return {
      cpf: '',
      nome: '',
      categoria_cnh: '',

      erros: {
        cpf: '',
        nome: '',
        categoria_cnh: '',

      }
    }
  },

  watch: {
    cpf(valorDigitado) {
      this.cpf = this.formatarCPF(valorDigitado)
      if (valorDigitado) this.erros.cpf=''
    },

    nome(valorDigitado) {
      if (valorDigitado) this.erros.nome=''
    },

    categoria_cnh(valorDigitado) {
      if (valorDigitado) this.erros.categoria_cnh=''
    }

  },

  methods: {
      async registrarMotorista() {

        if(!this.validar()) {
          return
        }

      // divide pelo "," e limpa espaços de cada categoria
        const categorias = this.categoria_cnh
        .split(',')
        .map(cat => cat.trim().toUpperCase())
        .filter(cat => cat !== '')  // remove entradas vazias

        try {
          await salvarMotoristas({
            cpf: this.cpf,
            nome: this.nome,
            categoria_cnh: categorias,
          })
        } catch (e) {
          this.erros.cpf = e.message
          return
        }

        alert(`Motorista ${this.nome} cadastrado com sucesso!`)
        this.nome = ''
        this.cpf = ''
        this.categoria_cnh = ''

      },

      formatarCPF(valor) {
        // remove tudo que não é número
        valor = valor.replace(/\D/g, '')


        if (valor.length <= 3) {
          return valor
        }

        if (valor.length <= 6) {
          return `${valor.slice(0,3)}.${valor.slice(3)}`
        }

        if (valor.length <= 9) {
          return `${valor.slice(0,3)}.${valor.slice(3,6)}.${valor.slice(6)}`

        }

        return `${valor.slice(0,3)}.${valor.slice(3,6)}.${valor.slice(6,9)}-${valor.slice(9,11)}`
      },

      validar() {
        this.erros = { cpf: '', nome: '', categoria_cnh: '' }
        let valido = true

        if (!this.cpf) {
          this.erros.cpf = 'Insira seu CPF.'
          valido = false
        }

        if (!this.nome) {
          this.erros.nome = 'Insira seu nome completo.'
          valido = false
        }

        if (!this.categoria_cnh.trim()) {
          this.erros.categoria_cnh = 'Insira pelo menos uma categoria.'
          valido = false
        }
        else {

          const categoriasValidas = ['A', 'B', 'C', 'D', 'E']

          const categorias = this.categoria_cnh
          .split(',')
          .map(cat => cat.trim().toUpperCase())
          .filter(cat => cat !== '')

            // verifica se alguma categoria não é válida
            const invalidas = categorias.filter(cat => !categoriasValidas.includes(cat))
            if (invalidas.length > 0) {
              this.erros.categoria_cnh = `Categoria inválida.`
              valido = false
            }

            // verifica se tem categorias repetidas
            const semRepetidas = [...new Set(categorias)]
            if (semRepetidas.length !== categorias.length) {
              this.erros.categoria_cnh = 'Você inseriu categorias repetidas.'
              valido = false
            }
        }

        return valido
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
}
</style>
