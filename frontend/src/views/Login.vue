<!-- src/views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h2>🔐 Login</h2>
      <input v-model="username" type="text" placeholder="Usuário" />
      <input v-model="password" type="password" placeholder="Senha" />
      <button @click="fazerLogin">Entrar</button>
      <p v-if="erro" class="erro-msg">Credenciais inválidas</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "AppLogin",
  data() {
    return {
      username: '',
      password: '',
      erro: false
    }
  },
  methods: {
    async fazerLogin() {
      try {
        const res = await fetch('http://10.10.20.207:5000/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username: this.username, password: this.password })
        })

        if (res.ok) {
          localStorage.setItem('usuario', this.username)
          this.$router.push('/controle')
        } else {
          this.erro = true
        }
      } catch (e) {
        this.erro = true
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(to bottom right, #d3f2e6, #a0e3ca);
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  width: 100%;
  max-width: 350px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

input {
  display: block;
  width: 100%;
  padding: 0.6rem;
  margin: 1rem 0;
  border-radius: 0.5rem;
  border: 1px solid #ccc;
}

button {
  width: 100%;
  padding: 0.6rem;
  border: none;
  border-radius: 0.5rem;
  background-color: #38a169;
  color: white;
  font-weight: bold;
  cursor: pointer;
}

button:hover {
  background-color: #2f855a;
}

.erro-msg {
  color: red;
  margin-top: 0.5rem;
}
</style>
