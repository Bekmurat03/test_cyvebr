FROM python:3.11-slim

WORKDIR /app

COPY ctf_platform/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ctf_platform/ .

# Generate challenge files
RUN python scripts/generate_challenges.py

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV SECRET_KEY=ctf_super_secret_key_2024

CMD ["python", "app.py"]
