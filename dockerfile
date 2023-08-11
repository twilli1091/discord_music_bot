FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python3 commands.py"]