FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN apt update && apt install -y ffmpeg
CMD ["python3", "-m", "main.py"]