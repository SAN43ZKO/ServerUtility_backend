FROM python:3.12-slim

WORKDIR /app

# Insstall requirements
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy porject
COPY app/ .

# Run app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
