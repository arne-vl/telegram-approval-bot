FROM python:3.11-slim

WORKDIR /bot

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD ["python", "main.py"]
