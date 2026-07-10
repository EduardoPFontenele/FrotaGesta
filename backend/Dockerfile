FROM python:3.13-slim

WORKDIR /app

# Copia só o requirements.txt primeiro para aproveitar o cache do Docker
# quando o código muda mas as dependências não.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
