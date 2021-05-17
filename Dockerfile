FROM python:3.9-slim

WORKDIR /app

COPY reqs.txt reqs.txt
RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get install -y libpq-dev gcc ffmpeg
RUN pip3 install -r reqs.txt --no-cache-dir
COPY . .
CMD ["python3", "Bot.py"]
