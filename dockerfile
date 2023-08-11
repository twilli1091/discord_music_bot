FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN wget https://ffmpeg.org/releases/ffmpeg-6.0.tar.xz
CMD ["python3", "-m", "commands.py"]