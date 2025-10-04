# Imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos (caso queira criar requirements.txt)
COPY requirements.txt .

# Instala as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do backend para dentro do container
COPY . .

# Define variável de ambiente para o Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Expõe a porta padrão do Flask
EXPOSE 5000

# Comando padrão ao iniciar o container
CMD ["flask", "run"]
