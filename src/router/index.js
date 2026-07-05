import { createRouter, createWebHistory } from 'vue-router'
import TelaInicial           from '../views/TelaInicial.vue'
import TelaCadastroVeiculo   from '../views/TelaCadastroVeiculo.vue'
import TelaCadastroMotorista from '../views/TelaCadastroMotorista.vue'
import TelaListagemMotorista from '../views/TelaListagemMotorista.vue'
import TelaListagemVeiculo   from '../views/TelaListagemVeiculo.vue'
import TelaViagem            from '../views/TelaViagem.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                   component: TelaInicial           },
    { path: '/cadastro-veiculo',   component: TelaCadastroVeiculo   },
    { path: '/cadastro-motorista', component: TelaCadastroMotorista },
    { path: '/motoristas',         component: TelaListagemMotorista },
    { path: '/veiculos',           component: TelaListagemVeiculo   },
    { path: '/viagem',             component: TelaViagem            },
  ],
})

export default router
