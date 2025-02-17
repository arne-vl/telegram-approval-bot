FROM python:3.11-slim

WORKDIR /bot

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py main.py

CMD ["python", "main.py"]
