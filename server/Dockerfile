FROM python:3.10-alpine

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

COPY lightsaber_server.py .

CMD ["python3", "-u", "lightsaber_server.py"]