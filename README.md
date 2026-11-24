# Serviço Web Linux com Docker

**Disciplina:** Sistemas Operacionais  
**Professor:** Guibson Krause  
**Trabalho:** Trabalho 4 - Operacionalização segura de um serviço Linux com Docker  
**Entrega/apresentação:** 24/11/2026

## Integrante ##

RAI GIL PEDROSA



## 1. Objetivo

Empacotar uma aplicação HTTP simples em um container Linux Docker e documentar como outra pessoa pode construir a imagem, configurar, iniciar, testar, monitorar, provocar uma falha controlada, confirmar a recuperação automática e parar o serviço.

A aplicação foi desenvolvida em Python com Flask e disponibiliza:

- `/` — página inicial;
- `/teste` — rota de verificação que retorna JSON;
- `/falhar` — rota de laboratório que encerra o processo principal com código 1 para testar a política de reinício.

**Atenção:** `/falhar` existe exclusivamente para a demonstração acadêmica. Não habilite essa rota em um serviço exposto à internet ou em produção.

## 2. Estrutura do repositório

```text
servico-web/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── RUNBOOK.md
└── evidencias/
    └ 01_build
    └ 02_container_ativo
    └ 03_aplicacao
    └ 04_usuario
    └ 05_logs
    └ 06_recursos
    └ 07_recuperacao

```

## 3. Pré-requisitos

- Windows 10/11 ou outro sistema compatível com Docker;
- Docker Desktop instalado e iniciado (motor Linux/`docker-desktop-linux`);
- Git instalado;
- PowerShell ou terminal equivalente;
- Portas TCP 5000 disponível no computador.

Verifique a instalação:

```powershell
docker version
docker info
git --version
```

## 4. Construir a imagem

Na pasta que contém o `Dockerfile`:

```powershell
docker build -t servico-web:1.0 .
docker images
```

## 5. Executar

O comando abaixo publica a aplicação apenas na interface local do computador, usa usuário não-root, remove capacidades Linux adicionais, impede ganho de novos privilégios, limita recursos e configura reinício em caso de falha:

```powershell
docker run -d `
  --name servico-web `
  --restart on-failure:3 `
  --cpus=0.5 `
  --memory=128m `
  --pids-limit=64 `
  --cap-drop=ALL `
  --security-opt=no-new-privileges:true `
  -p 127.0.0.1:5000:5000 `
  -e PORT=5000 `
  -e LOG_LEVEL=INFO `
  -e ALLOW_FAILURE=true `
  servico-web:1.0
```

A aplicação fica disponível em:

- Página inicial: <http://localhost:5000/>
- Teste: <http://localhost:5000/teste>

Exemplo esperado para `/teste`:

```json
{
  "status": "OK",
  "servico": "servico-web",
  "mensagem": "Serviço funcionando corretamente!"
}
```

## 6. Configuração externa

As configurações são recebidas por variáveis de ambiente:

| Variável | Padrão | Descrição |
|---|---:|---|
| `PORT` | `5000` | Porta HTTP dentro do container |
| `LOG_LEVEL` | `INFO` | Nível de registro: `DEBUG`, `INFO`, `WARNING` ou `ERROR` |
| `ALLOW_FAILURE` | `true` | Habilita a rota de falha controlada do laboratório |

Para mudar o nível de log, remova o container e crie-o novamente com `-e LOG_LEVEL=DEBUG`. Não é necessário editar o código nem reconstruir a imagem:

```powershell
docker rm -f servico-web
```

Depois repita o comando `docker run`, alterando para:

```powershell
-e LOG_LEVEL=DEBUG
```

Para desabilitar a rota de falha, use `-e ALLOW_FAILURE=false`.

Não armazene senhas, tokens ou credenciais reais no Git. Este projeto não necessita de credenciais.

## 7. Segurança, usuário e permissões

O Dockerfile cria o usuário `app` com UID/GID `10001` e executa a aplicação com:

```dockerfile
USER 10001:10001
```

Comprove o usuário efetivo:

```powershell
docker exec servico-web id
```

Resultado esperado, de forma equivalente:

```text
uid=10001(app) gid=10001(app) groups=10001(app)
```

A aplicação precisa apenas ler os arquivos da aplicação e executar o interpretador Python. Ela não grava arquivos no diretório `/app` e escuta na porta 5000, uma porta não privilegiada. O container não usa `--privileged`; adicionalmente, o comando remove capabilities e ativa `no-new-privileges`.

## 8. Logs e monitoramento

```powershell
docker logs servico-web
docker logs --tail 50 -f servico-web
docker stats --no-stream servico-web
docker top servico-web
docker ps
docker ps -a
```

Consulte os limites configurados:

```powershell
docker inspect --format='CPU (NanoCpus): {{.HostConfig.NanoCpus}}' servico-web
docker inspect --format='Memória (bytes): {{.HostConfig.Memory}}' servico-web
docker inspect --format='PIDs limit: {{.HostConfig.PidsLimit}}' servico-web
```

Os limites definidos são 0,5 CPU, 128 MiB de memória e 64 processos. O consumo real exibido por `docker stats` varia conforme a execução.

## 9. Falha controlada e recuperação

Siga o procedimento detalhado em [RUNBOOK.md](RUNBOOK.md). A demonstração deve ser feita somente no ambiente de laboratório:

1. confirme que o serviço responde;
2. registre o `RestartCount` inicial;
3. deixe o container em execução por pelo menos 10 segundos;
4. chame `/falhar`, que encerra o processo com código 1;
5. confirme o aumento do contador e a nova inicialização nos logs;
6. teste `/teste` novamente;
7. finalize com `docker stop`.

A política `on-failure:3` permite até três tentativas de reinício após saídas com código diferente de zero. O comportamento deve ser comprovado no ambiente utilizado.

## 10. Parar e remover

Parada normal:

```powershell
docker stop servico-web
docker ps -a
```

Remover o container:

```powershell
docker rm servico-web
```

A imagem pode ser removida depois que não for mais necessária:

```powershell
docker rmi servico-web:1.0
```
