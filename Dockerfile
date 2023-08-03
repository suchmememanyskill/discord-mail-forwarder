FROM python:3.11-alpine
WORKDIR /app
COPY *.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "./main.py"]