FROM python:3.8
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN apt update && apt install -y ffmpeg
CMD ["python3", "-m", "commands.py"]