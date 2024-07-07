# Dockerfile
FROM python:3.8.10-slim
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt update && apt -y install gunicorn
RUN pip install -r requirements.txt
COPY . /app
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]