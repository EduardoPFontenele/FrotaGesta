<template>
  <div class="pagina">
    <div class="block-lista">
      <RouterLink to="/" class="link-voltar">Voltar ao Menu</RouterLink>

      <h1>LISTAGEM DE VEÍCULOS</h1>

      <div class="campo">
        <label>Buscar por Placa ou Modelo</label>
      </div>

      <input
        type="text"
        v-model="busca"
        placeholder="Ex: ABC-1234 ou Corolla"
      />

      <table class="tabela-motoristas" v-if="veiculosFiltrados.length">
        <thead>
          <tr>
            <th>Placa</th>
            <th>Modelo</th>
            <th>Ano</th>
            <th>Km atual</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="veiculo in veiculosFiltrados" :key="veiculo.placa">
            <td>{{ veiculo.placa }}</td>
            <td>{{ veiculo.modelo }}</td>
            <td>{{ veiculo.ano }}</td>
            <td>{{ veiculo.km }}</td>
          </tr>
        </tbody>
      </table>

      <p class="mensagem-vazio" v-else>Nenhum veículo encontrado.</p>
    </div>
  </div>
</template>

<script>
import { getVeiculos } from '../services/dados'

export default {
  data() {
    return {
      busca: '',
      veiculos: [],
    }
  },

  created() {
    this.veiculos = getVeiculos()
  },

  computed: {
    veiculosFiltrados() {
      const termo = this.busca.trim().toLowerCase()

      if (!termo) {
        return this.veiculos
      }

      return this.veiculos.filter(veiculo =>
        veiculo.placa.toLowerCase().includes(termo) ||
        veiculo.modelo.toLowerCase().includes(termo)
      )
    },
  },
}
</script>
