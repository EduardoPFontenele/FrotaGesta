<template>
  <div class="pagina">
    <div class="block-lista">
      <RouterLink to="/" class="link-voltar">Voltar ao Menu</RouterLink>

      <h1>LISTAGEM DE MOTORISTAS</h1>

      <div class="campo">
        <label>Buscar por CPF ou Nome</label>
      </div>

      <input
        type="text"
        v-model="busca"
        placeholder="Ex: 123.456.789-10 ou Eduardo"
      />

      <table class="tabela-motoristas" v-if="motoristasFiltrados.length">
        <thead>
          <tr>
            <th>CPF</th>
            <th>Nome</th>
            <th>Categoria CNH</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="motorista in motoristasFiltrados" :key="motorista.cpf">
            <td>{{ motorista.cpf }}</td>
            <td>{{ motorista.nome }}</td>
            <td>{{ motorista.categoria_cnh.join(', ') }}</td>
          </tr>
        </tbody>
      </table>

      <p class="mensagem-vazio" v-else>Nenhum motorista encontrado.</p>
    </div>
  </div>
</template>

<script>
import { getMotoristas } from '../services/dados'

export default {
  data() {
    return {
      busca: '',
      motoristas: [],
    }
  },

  created() {
    this.motoristas = getMotoristas()
  },

  computed: {
    motoristasFiltrados() {
      const termo = this.busca.trim().toLowerCase()

      if (!termo) {
        return this.motoristas
      }

      return this.motoristas.filter(motorista =>
        motorista.cpf.toLowerCase().includes(termo) ||
        motorista.nome.toLowerCase().includes(termo)
      )
    },
  },
}
</script>

<style>
.block-lista {
  margin-top: 10%;
  display: flex;
  flex-direction: column;
  border: 1px solid rgb(0, 0, 0);
  border-radius: 10px;
  width: 700px;
  padding: 100px;
  background: #e6e5e5;
  box-shadow: 0 0 120px rgba(0, 0, 0);
}

.tabela-motoristas {
  margin-top: 20px;
  width: 100%;
  border-collapse: collapse;
}

.tabela-motoristas th,
.tabela-motoristas td {
  border: 1px solid #999;
  padding: 8px 12px;
  text-align: left;
  font-size: 16px;
}

.tabela-motoristas th {
  background: #cfcfcf;
}

.mensagem-vazio {
  margin-top: 20px;
  font-size: 16px;
  color: #555;
}
</style>
