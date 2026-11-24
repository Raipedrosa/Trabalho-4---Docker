import os
import logging
from flask import Flask, jsonify

# Configurações externas
PORT = int(os.getenv("PORT", "5000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ALLOW_FAILURE = os.getenv("ALLOW_FAILURE", "true").lower() == "true"

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True
)

app = Flask(__name__)

@app.route("/")
def inicio():
    app.logger.info("Página inicial acessada")

    return """
    <h1>Serviço Docker funcionando!</h1>
    <p>Aplicação executada em um container Linux.</p>
    <p>Status: Online</p>
    """

@app.route("/teste")
def teste():
    app.logger.info("Rota de teste acessada")

    return jsonify({
        "status": "OK",
        "servico": "servico-web",
        "mensagem": "Serviço funcionando corretamente!"
    })

@app.route("/falhar")
def falhar():
    if not ALLOW_FAILURE:
        return jsonify({
            "status": "ERRO",
            "mensagem": "Simulação de falha desabilitada"
        }), 403

    app.logger.error(
        "Falha controlada solicitada. Encerrando processo principal."
    )

    # Encerra o processo com código diferente de zero.
    os._exit(1)

if __name__ == "__main__":
    app.logger.info(
        "Iniciando serviço na porta %s com PID %s",
        PORT,
        os.getpid()
    )

    app.run(
        host="0.0.0.0",
        port=PORT
    )
