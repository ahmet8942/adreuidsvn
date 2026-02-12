FROM python:3.12-slim

WORKDIR /app/telegram-bot

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot/ bot/
COPY main.py .

# Copy .env if exists (can also mount at runtime)
COPY .env* ./

CMD ["python", "main.py"]
