FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate challenge files on build
RUN python scripts/generate_challenges.py

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV SECRET_KEY=ctf_super_secret_key_2024
ENV RENDER=true

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
