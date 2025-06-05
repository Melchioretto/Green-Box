<!-- src/views/Controle.vue -->
<template>
  <div class="app">
    <div class="card">
      <h1>🌿 GreenBox Monitor</h1>

      <div class="status">
        <p><strong>🌡️ Temperatura:</strong> {{ temp }}°C</p>
        <p><strong>💧 Umidade:</strong> {{ umid }}%</p>
      </div>

      <div class="controle">
        <div class="item">
          <p>💡 Branco: <strong>{{ branco }}</strong></p>
          <button @click="enviarControle('branco', branco === 'ON' ? 'desligar' : 'ligar')">
            {{ branco === 'ON' ? 'Desligar' : 'Ligar' }}
          </button>
        </div>

        <div class="item">
          <p>🔆 Amarelo: <strong>{{ amarelo }}</strong></p>
          <button @click="enviarControle('amarelo', amarelo === 'ON' ? 'desligar' : 'ligar')">
            {{ amarelo === 'ON' ? 'Desligar' : 'Ligar' }}
          </button>
        </div>

        <div class="item">
          <p>🌀 Desumidificador: <strong>{{ desumidificador }}</strong></p>
          <button @click="enviarControle('desumidificador', desumidificador === 'ON' ? 'desligar' : 'ligar')">
            {{ desumidificador === 'ON' ? 'Desligar' : 'Ligar' }}
          </button>
        </div>
      </div>

      <p class="footer">📡 Atualizando a cada 5 segundos</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TelaControle',
  data() {
    return {
      temp: '--',
      umid: '--',
      branco: '--',
      amarelo: '--',
      desumidificador: '--'
    }
  },
  methods: {
    async fetchDados() {
      try {
        const res = await fetch('http://10.10.20.207:5000/api/sensor', {
          credentials: 'include'
        })
        const json = await res.json()
        this.temp = json.temp
        this.umid = json.umid
        this.branco = json.branco
        this.amarelo = json.amarelo
        this.desumidificador = json.desumidificador
      } catch (e) {
        console.error('Erro ao buscar dados:', e)
      }
    },
    async enviarControle(alvo, acao) {
      try {
        await fetch('http://10.10.20.207:5000/api/controle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ alvo, acao })
        })
        this.fetchDados()
      } catch (e) {
        console.error('Erro ao enviar comando:', e)
      }
    }
  },
  mounted() {
    this.fetchDados()
    setInterval(this.fetchDados, 5000)
  }
}
</script>

<style scoped>
.app {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(to bottom right, #d3f2e6, #a0e3ca);
  padding: 1rem;
}

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  text-align: center;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: #2f855a;
}

.status p {
  font-size: 1.2rem;
  margin: 0.5rem 0;
}

.controle {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.item p {
  margin: 0;
}

button {
  margin-top: 0.5rem;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.6rem;
  background-color: #38a169;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background-color: #2f855a;
}

.footer {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #666;
}

@media (max-width: 400px) {
  h1 {
    font-size: 1.5rem;
  }

  .card {
    padding: 1rem;
  }

  button {
    width: 100%;
  }
}
</style>
