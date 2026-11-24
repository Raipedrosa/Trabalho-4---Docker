# RUNBOOK — Operação do serviço-web

Este roteiro permite que outra pessoa construa, configure, inicie, teste, monitore, simule uma falha e pare o serviço.

## A. Preparação

1. Instale e inicie o Docker Desktop com o motor Linux.
2. Abra o PowerShell na pasta do projeto.
3. Confirme:

```powershell
docker version
docker info
```

Se `docker info` não funcionar, inicie o Docker Desktop e aguarde o motor ficar pronto.

## B. Construir a imagem

```powershell
docker build -t servico-web:1.0 .
docker images
```

Critério de verificação: a imagem `servico-web` com tag `1.0` aparece na listagem.

## C. Configurar e iniciar

Se já existir um container com esse nome, remova-o antes:

```powershell
docker rm -f servico-web
```

Inicie o serviço:

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

Confirme o estado:

```powershell
docker ps
docker ps -a
```

O estado esperado é `Up`.

## D. Testar a aplicação

No navegador, acesse:

- `http://localhost:5000/`
- `http://localhost:5000/teste`

Ou pelo PowerShell:

```powershell
Invoke-RestMethod http://localhost:5000/teste
```

Resposta esperada: `status` igual a `OK`.

## E. Verificar usuário e permissões

```powershell
docker exec servico-web id
```

Resultado esperado: UID `10001` e GID `10001`, diferentes de zero.

O processo usa usuário sem privilégios administrativos. Os arquivos da aplicação são somente leitura para esse usuário; não há necessidade de escrita em `/app`. A aplicação escuta na porta interna 5000, sem precisar de uma porta privilegiada.

Verifique também que o container não está em modo privilegiado:

```powershell
docker inspect --format='Privileged={{.HostConfig.Privileged}}' servico-web
```

Resultado esperado: `Privileged=false`.

## F. Verificar configuração externa

```powershell
docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' servico-web
```

Devem aparecer `PORT=5000`, `LOG_LEVEL=INFO` e `ALLOW_FAILURE=true`.

Para demonstrar alteração sem editar o código, recrie o container alterando `LOG_LEVEL` para `DEBUG` no comando de execução. A configuração de ambiente é aplicada na criação do container; por isso, é necessário recriá-lo.

## G. Consultar logs e recursos

Gere uma requisição à rota de teste e consulte:

```powershell
docker logs servico-web
docker stats --no-stream servico-web
docker top servico-web
```

Verifique os limites:

```powershell
docker inspect --format='NanoCpus={{.HostConfig.NanoCpus}}' servico-web
docker inspect --format='Memory={{.HostConfig.Memory}} bytes' servico-web
docker inspect --format='PidsLimit={{.HostConfig.PidsLimit}}' servico-web
```

Valores configurados: 0,5 CPU, 128 MiB de memória e 64 PIDs. Se o ambiente de laboratório não aplicar algum limite, registre a saída real e explique a limitação observada.

## H. Simular falha e comprovar recuperação

**Faça esta etapa somente no laboratório.** A rota `/falhar` encerra o processo principal deliberadamente. Não a exponha em uma implantação real.

1. Confirme que a aplicação responde:

```powershell
Invoke-RestMethod http://localhost:5000/teste
```

2. Registre o contador inicial:

```powershell
$antes = [int](docker inspect --format='{{.RestartCount}}' servico-web)
"Reinícios antes da falha: $antes"
```

3. Garanta que o container já esteja executando há pelo menos 10 segundos:

```powershell
Start-Sleep -Seconds 12
```

4. Provoque a falha. A chamada pode terminar com erro de conexão porque o servidor encerra o processo durante a requisição:

```powershell
try {
    Invoke-RestMethod http://localhost:5000/falhar
}
catch {
    Write-Host "A conexão foi interrompida durante a falha controlada."
}
```

5. Aguarde a política de reinício atuar e consulte o estado:

```powershell
Start-Sleep -Seconds 5
docker ps -a
```

6. Consulte o contador novamente:

```powershell
$depois = [int](docker inspect --format='{{.RestartCount}}' servico-web)
"Reinícios antes: $antes"
"Reinícios depois: $depois"
```

O contador posterior deve ser maior que o inicial. Se ainda não aumentou, aguarde alguns segundos e consulte novamente:

```powershell
Start-Sleep -Seconds 5
docker ps -a
docker inspect --format='{{.RestartCount}}' servico-web
```

7. Consulte os logs para encontrar a mensagem de falha e a inicialização seguinte:

```powershell
docker logs --timestamps servico-web
```

8. Teste novamente:

```powershell
Invoke-RestMethod http://localhost:5000/teste
```

A resposta `OK`, junto ao aumento do `RestartCount` e aos logs de nova inicialização, demonstra a recuperação.

**Observação:** `on-failure:3` limita a três tentativas de reinício. Não faça várias falhas desnecessárias durante a apresentação. A política `on-failure` não reinicia o container quando ele é parado normalmente com `docker stop`.

## I. Parada normal

Finalize usando:

```powershell
docker stop servico-web
docker ps -a
```

O estado esperado é `Exited`. Essa é a parada administrativa normal e deve ser diferenciada da falha controlada.

## J. Limpeza opcional

Depois da apresentação:

```powershell
docker rm servico-web
```

Para remover também a imagem:

```powershell
docker rmi servico-web:1.0
```