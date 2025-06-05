from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os
import asyncio
from aiocoap import *
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
Session(app)

# CORS com suporte a cookies e origem do frontend
CORS(app, supports_credentials=True, origins=["http://10.10.20.207:8080"], methods=["GET", "POST", "OPTIONS"])

# Usuários definidos via .env
USUARIOS = {
    os.getenv('USUARIO'): os.getenv('SENHA')
}

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200  # responde o preflight

    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    print("👤 Login:", username, "|", password)
    print("Esperado:", USUARIOS)

    if USUARIOS.get(username) == password:
        session['usuario'] = username
        return jsonify({"status": "ok"})
    return jsonify({"status": "erro", "msg": "Credenciais inválidas"}), 401


# Rota de logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario', None)
    return jsonify({"status": "deslogado"})

# Rota protegida para obter dados via CoAP
@app.route('/api/sensor')
def sensor():
    if 'usuario' not in session:
        return jsonify({"erro": "nao_autenticado"}), 401

    async def get_sensor():
        protocol = await Context.create_client_context()
        request = Message(code=GET, uri='coap://10.10.20.232/sensor')
        try:
            response = await protocol.request(request).response
            return response.payload.decode()
        except Exception as e:
            return f"Erro: {e}"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dados = loop.run_until_complete(get_sensor())

    print("DADOS RECEBIDOS:", dados, flush=True)

    if dados.startswith("Erro"):
        return jsonify({"erro": dados}), 500

    try:
        partes = dados.split(" | ")
        temp = partes[0].split(": ")[1].replace("C", "")
        umid = partes[1].split(": ")[1].replace("%", "")
        branco = partes[2].split(": ")[1]
        amarelo = partes[3].split(": ")[1]
        desumid = partes[4].split(": ")[1]

        return jsonify({
            "temp": temp,
            "umid": umid,
            "branco": branco,
            "amarelo": amarelo,
            "desumidificador": desumid
        })
    except Exception as e:
        return jsonify({"erro": f"Erro no parsing: {e}", "bruto": dados}), 500

# Rota protegida para controle dos relés
@app.route('/api/controle', methods=['POST'])
def controle():
    if 'usuario' not in session:
        return jsonify({"erro": "nao_autenticado"}), 401

    conteudo = request.json
    alvo = conteudo.get("alvo")
    acao = conteudo.get("acao")

    if not alvo or not acao:
        return jsonify({"erro": "dados incompletos"}), 400

    async def enviar():
        protocol = await Context.create_client_context()
        payload = f"alvo={alvo}&acao={acao}".encode('utf-8')
        request_coap = Message(code=POST, uri='coap://10.10.20.232/controle', payload=payload)
        try:
            response = await protocol.request(request_coap).response
            return response.payload.decode()
        except Exception as e:
            return f"Erro: {e}"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resposta = loop.run_until_complete(enviar())

    return jsonify({"resposta": resposta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
