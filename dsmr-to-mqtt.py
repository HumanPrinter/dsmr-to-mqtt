from datetime import time, datetime, timezone
from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5
from dsmr_parser.objects import CosemObject, MBusObject, Telegram
from dsmr_parser.parsers import TelegramParser
import os
import time
import json
import paho.mqtt.client as paho

usbDevice = os.environ.get('USB_DEVICE', '/dev/ttyUSB0')
mqttBroker = os.environ.get('MQTT_BROKER', 'mosquitto.lan')
mqttClientName = os.environ.get('MQTT_CLIENT_NAME', 'dsmr-reader')
mqttUsername = os.environ.get('MQTT_USERNAME', '')
mqttPassword = os.environ.get('MQTT_PASSWORD', '')
mqttTopic = os.environ.get('MQTT_TOPIC', 'dsmr/telegram')
publishInterval = os.environ.get('PUBLISH_INTERVAL', 10)

print('Connecting to serial device...')
serial_reader = SerialReader(
    device=usbDevice,
    serial_settings=SERIAL_SETTINGS_V5,
    telegram_specification=telegram_specifications.V5
)

client= paho.Client(mqttClientName)

if mqttUsername and mqttPassword:
  client.username_pw_set(mqttUsername, mqttPassword)

print("Connecting to broker...", mqttBroker)
client.connect(mqttBroker)

print("Subscribing to the MQTT topic...")
client.subscribe(mqttTopic)

lastPublished = datetime.now(timezone.utc)
for telegram in serial_reader.read_as_object():
    if (telegram.P1_MESSAGE_TIMESTAMP.value - lastPublished).total_seconds() >= publishInterval:
        lastPublished = telegram.P1_MESSAGE_TIMESTAMP.value
        client.publish(mqttTopic + '/P1_MESSAGE_TIMESTAMP', telegram.P1_MESSAGE_TIMESTAMP.value.strftime("%d-%m-%Y %H:%M:%S%z"))
        client.publish(mqttTopic + '/EQUIPMENT_IDENTIFIER', bytearray.fromhex(telegram.EQUIPMENT_IDENTIFIER.value).decode())
        client.publish(mqttTopic + '/ELECTRICITY_USED_TARIFF_1', float(telegram.ELECTRICITY_USED_TARIFF_1.value))
        client.publish(mqttTopic + '/ELECTRICITY_USED_TARIFF_2', float(telegram.ELECTRICITY_USED_TARIFF_2.value))
        client.publish(mqttTopic + '/ELECTRICITY_DELIVERED_TARIFF_1', float(telegram.ELECTRICITY_DELIVERED_TARIFF_1.value))
        client.publish(mqttTopic + '/ELECTRICITY_DELIVERED_TARIFF_2', float(telegram.ELECTRICITY_DELIVERED_TARIFF_2.value))
        client.publish(mqttTopic + '/ELECTRICITY_ACTIVE_TARIFF', telegram.ELECTRICITY_ACTIVE_TARIFF.value)
        client.publish(mqttTopic + '/CURRENT_ELECTRICITY_USAGE', float(telegram.CURRENT_ELECTRICITY_USAGE.value))
        client.publish(mqttTopic + '/CURRENT_ELECTRICITY_DELIVERY', float(telegram.CURRENT_ELECTRICITY_DELIVERY.value))
        client.publish(mqttTopic + '/SHORT_POWER_FAILURE_COUNT', telegram.SHORT_POWER_FAILURE_COUNT.value)
        client.publish(mqttTopic + '/LONG_POWER_FAILURE_COUNT', telegram.LONG_POWER_FAILURE_COUNT.value)
        client.publish(mqttTopic + '/VOLTAGE_SAG_L1_COUNT', telegram.VOLTAGE_SAG_L1_COUNT.value)
        client.publish(mqttTopic + '/VOLTAGE_SAG_L2_COUNT', telegram.VOLTAGE_SAG_L2_COUNT.value)
        client.publish(mqttTopic + '/VOLTAGE_SAG_L3_COUNT', telegram.VOLTAGE_SAG_L3_COUNT.value)
        client.publish(mqttTopic + '/VOLTAGE_SWELL_L1_COUNT', telegram.VOLTAGE_SWELL_L1_COUNT.value)
        client.publish(mqttTopic + '/VOLTAGE_SWELL_L2_COUNT', telegram.VOLTAGE_SWELL_L2_COUNT.value)
        client.publish(mqttTopic + '/VOLTAGE_SWELL_L3_COUNT', telegram.VOLTAGE_SWELL_L3_COUNT.value)
        if telegram.TEXT_MESSAGE.value:
            client.publish(mqttTopic + '/TEXT_MESSAGE', bytearray.fromhex(telegram.TEXT_MESSAGE.value).decode())
        
        client.publish(mqttTopic + '/INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE', float(telegram.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE', float(telegram.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE', float(telegram.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE', float(telegram.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE', float(telegram.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE', float(telegram.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_CURRENT_L1', float(telegram.INSTANTANEOUS_CURRENT_L1.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_CURRENT_L2', float(telegram.INSTANTANEOUS_CURRENT_L2.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_CURRENT_L3', float(telegram.INSTANTANEOUS_CURRENT_L3.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_VOLTAGE_L1', float(telegram.INSTANTANEOUS_VOLTAGE_L1.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_VOLTAGE_L2', float(telegram.INSTANTANEOUS_VOLTAGE_L2.value))
        client.publish(mqttTopic + '/INSTANTANEOUS_VOLTAGE_L3', float(telegram.INSTANTANEOUS_VOLTAGE_L3.value))
        client.publish(mqttTopic + '/DEVICE_TYPE', telegram.DEVICE_TYPE.value)
        payload = {}
        payload["timestamp"] = telegram.HOURLY_GAS_METER_READING.datetime.strftime("%d-%m-%Y %H:%M:%S%z")
        payload["value"] = float(telegram.HOURLY_GAS_METER_READING.value)
        client.publish(mqttTopic + '/5MINUTE_GAS_METER_READING', json.dumps(payload))
        client.publish(mqttTopic + '/EQUIPMENT_IDENTIFIER_GAS', bytearray.fromhex(telegram.EQUIPMENT_IDENTIFIER_GAS.value).decode())
        payload = [{ "datetime": item.datetime, "duration": item.value } for item in telegram.POWER_EVENT_FAILURE_LOG.buffer]
        client.publish(mqttTopic + '/POWER_EVENT_FAILURE_LOG', json.dumps(payload))
        
        client.publish(mqttTopic, telegram.to_json())

client.disconnect()
