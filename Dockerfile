FROM python:3.12-slim

WORKDIR /app

# Instala as dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY app.py .

# Cria usuário sem privilégios administrativos
RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid app \
    --no-create-home --shell /usr/sbin/nologin app

# Define configurações padrão
ENV PORT=5000
ENV LOG_LEVEL=INFO
ENV ALLOW_FAILURE=true
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Executa como usuário não root
USER 10001:10001

EXPOSE 5000

CMD ["python", "app.py"]
