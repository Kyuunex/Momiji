FROM python:3.11-slim-bullseye

COPY . ./
RUN pip3 install .
RUN pip3 install -r requirements.txt
CMD ["python3", "-m momiji"]
