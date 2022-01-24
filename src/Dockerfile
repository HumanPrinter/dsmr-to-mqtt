FROM python:3.9.0-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY dsmr-to-mqtt.py ./

CMD [ "python", "./dsmr-to-mqtt.py" ]