FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN wget https://ffmpeg.org/download.html
CMD ["python3", "-m", "commands.py"]