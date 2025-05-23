FROM python:3.11-slim

WORKDIR /app

COPY server.py .
COPY products.json .

RUN pip install flask requests

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-u", "server.py"]
