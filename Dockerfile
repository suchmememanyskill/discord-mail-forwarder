FROM python:3.11-alpine
WORKDIR /app
COPY *.py requirements.txt /app/
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "./main.py"]