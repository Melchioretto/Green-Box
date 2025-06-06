import asyncio
from aiocoap import resource, Message, Context
from aiocoap.numbers.codes import BAD_REQUEST, CHANGED, INTERNAL_SERVER_ERROR
import adafruit_dht
import board
import RPi.GPIO as GPIO

# Pinos dos relés
RELE_BRANCO = 17
RELE_AMARELO = 27
RELE_DESUMIDIFICADOR = 22

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([RELE_BRANCO, RELE_AMARELO, RELE_DESUMIDIFICADOR], GPIO.OUT)

# Estados iniciais
GPIO.output(RELE_BRANCO, GPIO.HIGH)
GPIO.output(RELE_DESUMIDIFICADOR, GPIO.HIGH)
GPIO.output(RELE_AMARELO, GPIO.LOW)

# Sensor DHT11
sensor = adafruit_dht.DHT11(board.D4)

# Função auxiliar para verificar estado dos relés
def estado_rele(pino, ligado_em_nivel_baixo=True):
    estado = GPIO.input(pino)
    if ligado_em_nivel_baixo:
        return "ON" if estado == GPIO.LOW else "OFF"
    else:
        return "ON" if estado == GPIO.HIGH else "OFF"

class SensorResource(resource.Resource):
    async def render_get(self, request):
        try:
            temp = sensor.temperature
            umid = sensor.humidity
        except Exception as e:
            return Message(payload=f"Erro ao ler sensor: {e}".encode('utf8'))

        branco = estado_rele(RELE_BRANCO)
        amarelo = estado_rele(RELE_AMARELO, ligado_em_nivel_baixo=False)
        desumid = estado_rele(RELE_DESUMIDIFICADOR)

        resposta = f"TEMP: {temp}C | UMID: {umid}% | BRANCO: {branco} | AMARELO: {amarelo} | DESUMIDIFICADOR: {desumid}"
        return Message(payload=resposta.encode('utf8'))
    
class ControleResource(resource.Resource):
    async def render_post(self, request):
        payload = request.payload.decode()
        print(f"Recebido: {payload}")

        try:
            dados = dict(item.split('=') for item in payload.split('&'))
            alvo = dados.get('alvo')
            acao = dados.get('acao')

            if alvo == "branco":
                GPIO.output(RELE_BRANCO, GPIO.LOW if acao == "ligar" else GPIO.HIGH)
            elif alvo == "amarelo":
                GPIO.output(RELE_AMARELO, GPIO.HIGH if acao == "ligar" else GPIO.LOW)
            elif alvo == "desumidificador":
                GPIO.output(RELE_DESUMIDIFICADOR, GPIO.LOW if acao == "ligar" else GPIO.HIGH)
            else:
                return Message(code=BAD_REQUEST, payload="Alvo inválido".encode('utf-8'))

            return Message(code=CHANGED, payload=f"{alvo} {acao}".encode())
        except Exception as e:
            return Message(code=INTERNAL_SERVER_ERROR, payload=str(e).encode())


async def main():
    root = resource.Site()
    root.add_resource(['sensor'], SensorResource())
    root.add_resource(['controle'], ControleResource())
    await Context.create_server_context(root)
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        GPIO.cleanup()
        sensor.exit()
