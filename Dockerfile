FROM node:22-alpine

WORKDIR /app

# Copia só os manifestos primeiro para aproveitar o cache do Docker
# quando o código muda mas as dependências não.
COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 5173

# --host 0.0.0.0 é necessário para o Vite aceitar conexões de fora do container.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
