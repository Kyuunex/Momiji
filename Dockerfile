FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /tmp/momiji/
COPY . ./

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt .

CMD ["python3", "-m", "momiji"]
