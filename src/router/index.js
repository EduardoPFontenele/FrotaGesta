import { createRouter, createWebHistory } from 'vue-router'
import TelaCadastroVeiculo   from '../views/TelaCadastroVeiculo.vue'
import TelaCadastroMotorista from '../views/TelaCadastroMotorista.vue'
import TelaViagem            from '../views/TelaViagem.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',                   component: TelaCadastroVeiculo   },
    { path: '/cadastro-veiculo',   component: TelaCadastroVeiculo   },
    { path: '/cadastro-motorista', component: TelaCadastroMotorista },
    { path: '/viagem',             component: TelaViagem            },
  ],
})

export default router
