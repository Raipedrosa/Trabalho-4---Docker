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
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel de Monitoramento</title>

        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }

            body {
                background: #f1f5f9;
                color: #1e293b;
            }

            header {
                background: #ffffff;
                padding: 22px 8%;
                border-bottom: 1px solid #e2e8f0;
            }

            header h1 {
                color: #1e40af;
                font-size: 23px;
            }

            header p {
                color: #64748b;
                margin-top: 5px;
                font-size: 13px;
            }

            main {
                max-width: 1100px;
                margin: 45px auto;
                padding: 0 20px;
            }

            .titulo {
                margin-bottom: 25px;
            }

            .titulo h2 {
                font-size: 25px;
                margin-bottom: 8px;
            }

            .titulo p {
                color: #64748b;
            }

            .status {
                background: #dcfce7;
                color: #15803d;
                padding: 8px 14px;
                border-radius: 20px;
                display: inline-block;
                font-size: 13px;
                font-weight: bold;
                margin-top: 15px;
            }

            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-top: 25px;
            }

            .card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.03);
            }

            .card h3 {
                color: #64748b;
                font-size: 14px;
                margin-bottom: 15px;
            }

            .card strong {
                font-size: 22px;
                color: #1e40af;
            }

            .api {
                margin-top: 30px;
                background: white;
                padding: 25px;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }

            button {
                margin-top: 15px;
                background: #2563eb;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
            }

            button:hover {
                background: #1d4ed8;
            }

            footer {
                text-align: center;
                color: #94a3b8;
                padding: 30px;
                font-size: 12px;
            }
        </style>
    </head>

    <body>
        <header>
            <h1>System Monitor</h1>
            <p>Painel de monitoramento do serviço web</p>
        </header>

        <main>
            <section class="titulo">
                <h2>Visão geral</h2>
                <p>Acompanhe o estado atual da aplicação.</p>
                <span class="status">● SERVIÇO ONLINE</span>
            </section>

            <section class="cards">
                <div class="card">
                    <h3>Status da aplicação</h3>
                    <strong>Operacional</strong>
                </div>

                <div class="card">
                    <h3>Servidor</h3>
                    <strong>Docker</strong>
                </div>

                <div class="card">
                    <h3>Porta de acesso</h3>
                    <strong>5000</strong>
                </div>
            </section>

            <section class="api">
                <h2>Teste da API</h2>
                <p style="color:#64748b; margin-top:10px;">
                    Utilize o botão abaixo para verificar a resposta do serviço.
                </p>

                <button onclick="testarAPI()">Testar conexão</button>
                <p id="resultado" style="margin-top:15px;"></p>
            </section>
        </main>

        <footer>
            Projeto acadêmico - Sistemas Operacionais | Serviço Web Docker
        </footer>

        <script>
            async function testarAPI() {
                const resultado = document.getElementById("resultado");
                resultado.innerText = "Verificando conexão...";

                try {
                    const resposta = await fetch("/teste");
                    const dados = await resposta.json();

                    resultado.innerText =
                        "Conexão realizada! Status: " + dados.status;
                    resultado.style.color = "#15803d";
                } catch (erro) {
                    resultado.innerText = "Erro ao conectar com o serviço.";
                    resultado.style.color = "#dc2626";
                }
            }
        </script>
    </body>
    </html>
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
