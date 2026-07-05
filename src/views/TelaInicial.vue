<template>
  <div class="pagina-menu">
    <div class="cabecalho">
      <h1>FrotaGesta</h1>
      <p>Sistema de Controle de Frota e Manutenção Preventiva</p>
    </div>

    <div class="grade-opcoes">
      <RouterLink to="/cadastro-veiculo" class="cartao">
        <span class="icone">🚚</span>
        <h2>Cadastro de Veículo</h2>
        <p>Cadastrar placa, modelo, ano e quilometragem.</p>
      </RouterLink>

      <RouterLink to="/cadastro-motorista" class="cartao">
        <span class="icone">🧑‍✈️</span>
        <h2>Cadastro de Motorista</h2>
        <p>Cadastrar CPF, nome e categoria da CNH.</p>
      </RouterLink>

      <RouterLink to="/viagem" class="cartao">
        <span class="icone">🛣️</span>
        <h2>Iniciar Viagem</h2>
        <p>Abrir uma viagem associando motorista e veículo.</p>
      </RouterLink>

      <RouterLink to="/motoristas" class="cartao">
        <span class="icone">📋</span>
        <h2>Listagem de Motoristas</h2>
        <p>Consultar motoristas cadastrados por CPF ou nome.</p>
      </RouterLink>

      <RouterLink to="/veiculos" class="cartao">
        <span class="icone">🚛</span>
        <h2>Listagem de Veículos</h2>
        <p>Consultar veículos cadastrados por placa ou modelo.</p>
      </RouterLink>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TelaInicial',
}
</script>

<style>
.pagina-menu {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  box-sizing: border-box;
}

.cabecalho {
  text-align: center;
  margin-bottom: 40px;
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

.grade-opcoes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  width: 100%;
  max-width: 900px;
}

.cartao {
  background: #e6e5e5;
  border-radius: 10px;
  padding: 30px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  text-decoration: none;
  color: #1a1a1a;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.35);
  transition: transform ease 0.3s, box-shadow ease 0.2s;
}

.cartao:hover {
  background: #aeaeae;
}

.cartao:active {
  transform: translateY(0px);
}

.cartao .icone {
  font-size: 40px;
  margin-bottom: 12px;
}

.cartao h2 {
  font-size: 20px;
  margin: 0 0 8px 0;
}

.cartao p {
  font-size: 14px;
  color: #4a4a4a;
  margin: 0;
}
</style>
