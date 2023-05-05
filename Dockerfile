FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y ffmpeg

COPY . /tmp/momiji/

RUN pip3 install --trusted-host pypi.python.org -r /tmp/momiji/requirements.txt /tmp/momiji

CMD ["python3", "-m", "momiji"]
