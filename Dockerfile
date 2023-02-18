FROM python:3.10-alpine

WORKDIR /app
RUN apk add build-base
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
