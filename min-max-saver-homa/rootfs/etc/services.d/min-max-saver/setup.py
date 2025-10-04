#!/usr/bin/env python3
# -*- coding: utf-8

"""Setup min_max_saver. This is a min/max saver used by HomA framework."""
# Creates the following retained topics:
# /sys/<systemId>/min/<minSystemId>/<minControlId>, payload: <time>
# /sys/<systemId>/max/<maxSystemId>/<maxControlId>, payload: <time>
#
# Holger Mueller
# 2017/10/24 initial revision
# 2020/10/15 checked Python3 compatibility
# 2025/10/04 Added support for Home Assistant add-on system

import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import config  # provides Home Assistant config (and gets MQTT host, port, user, pwd, ca_certs)

# config here ...
debug = False
systemId = config.options.get("homa_system_id")  # e.g. "123456-min-max-saver"

# config min/max saver here
mqtt_arr = [
    {'saver': 'max', 'system': '123456-windsensor', 'control': 'Wind speed', 'time': '24'},
    {'saver': 'min', 'system': '123456-vito', 'control': 'Aussentemperatur', 'time': '24'},
    {'saver': 'max', 'system': '123456-vito', 'control': 'Aussentemperatur', 'time': '24'},
    {'saver': 'min', 'system': '123456-vito', 'control': 'Raumtemperatur', 'time': '24'},
    {'saver': 'max', 'system': '123456-vito', 'control': 'Raumtemperatur', 'time': '24'},
    {'saver': 'min', 'system': '123456-energy', 'control': 'Current Power', 'time': '24'},
    {'saver': 'max', 'system': '123456-energy', 'control': 'Current Power', 'time': '24'}]


def homa_init(mqttc):
    """Publish HomA setup messages for min/max saver."""
    print(f"Publishing HomA setup data to {config.mqtt_host} (systemId {systemId}) ...")
    # setup controls
    for mqtt_dict in mqtt_arr:
        topic = f"/sys/{systemId}/{mqtt_dict['saver']}/{mqtt_dict['system']}/{mqtt_dict['control']}"
        mqttc.publish(topic, mqtt_dict['time'], retain=True)
        print(f"{topic} => {mqtt_dict['time']}")


# The callback for when the client receives a CONNACK response from the broker.
def on_connect(client, userdata, flags, reason_code, properties):  # pylint: disable=unused-argument
    """The callback for when the client receives a CONNACK response from the broker."""
    if debug: print("on_connect(): Connected with result code "+ str(reason_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the broker.
def on_message(client, userdata, msg):  # pylint: disable=unused-argument
    """The callback for when a PUBLISH message is received from the broker."""
    payload_str = msg.payload.decode("utf-8")  # payload is bytes since API version 2
    if debug: print("on_message(): "+ msg.topic+ ":"+ payload_str)


# The callback for when a message is published to the broker.
def on_publish(client, userdata, mid, reason_code, properties):  # pylint: disable=unused-argument
    """The callback for when a message is published to the broker."""
    if debug: print("on_publish(): message send "+ str(mid))


def main():
    """Main function to setup and run the min-max saver."""
    # connect to MQTT broker
    mqttc = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_publish = on_publish
    if config.mqtt_ca_certs != "":
        #mqttc.tls_insecure_set(True) # Do not use this "True" in production!
        mqttc.tls_set(config.mqtt_ca_certs, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    mqttc.username_pw_set(config.mqtt_user, password=config.mqtt_pwd)
    mqttc.connect(config.mqtt_host, port=config.mqtt_port)
    mqttc.loop_start()

    homa_init(mqttc)        # setup HomA MQTT device and control settings

    # wait until all queued topics are published
    mqttc.loop_stop()
    mqttc.disconnect()


if __name__ == "__main__":
    main()
