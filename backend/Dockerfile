FROM python:3.10-slim

WORKDIR /app

# dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code
COPY . .

# run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]