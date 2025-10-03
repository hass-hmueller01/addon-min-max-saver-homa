#!/usr/bin/env python3
# -*- coding: utf-8

"""min_max_saver is a universal min/max saver used by HomA framework."""
# Listens to the following topics:
# /sys/<systemId>/min/<minSystemId>/<minControlId>, payload: <time>
# /sys/<systemId>/max/<maxSystemId>/<maxControlId>, payload: <time>
# /devices/<minSystemId>/controls/<minControlId>, payload: <value>
# /devices/<minSystemId>/controls/<minControlId>meta/unit, payload: <value>
# Creates the following retained topics:
# /devices/<minSystemId>/controls/<minControlId> min, payload: min value
# /devices/<minSystemId>/controls/<minControlId> min/meta/unit, payload: unit
# /devices/<minSystemId>/controls/<minControlId> max, payload: max value
# /devices/<minSystemId>/controls/<minControlId> max/meta/unit, payload: unit
#
# Holger Mueller
# 2017/10/24 initial revision
# 2017/10/28 setting/coping unit of min/max value from controlId
# 2018/03/14 Changed constants to caps, changes order of functions for easier reading
# 2019/02/15 Fixed a bug with utf-8 payload messages and Python string functions,
#            fixed bug that messages are not resubscribed after a broker restart (reboot)
# 2020/10/15 made script Python3 compatible
# 2025/07/27 Added support for Home Assistant add-on, drop support for Python2, Pylint cleanup
# 2025/07/29 Switched to CallbackAPIVersion.VERSION2
# 2025/07/30 Switched to logging output instead of print statements

import sys
import time
import argparse
import json
import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import bashio_logging  # provides logging output like bashio, must be imported before logging #pylint: disable=unused-import
import logging  # pylint: disable=wrong-import-order
import mqtt_config  # gets host, port, user, pwd, ca_certs from Home Assistant config

# config here ... # TODO: use debug from config
DEBUG = False

try:
    with open("/data/options.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:  # pylint: disable=broad-except
    logging.error("Loading Home Assistant configuration file: %s", e)
    sys.exit(1)
systemId = config.get("homa_system_id")  # e.g. "123456-min-max-saver"

saver_arr = [] # buffer of registered saver, contents:
# {'saver': min/max, 'system': <systemId>, 'control': <controlId>,
#  'time': reset interval in seconds, 'nextReset': next reset time in seconds,
#  'value': min/max value}

def build_topic(system_id, t1 = None, t2 = None, t3 = None):
    """Create topic string."""
    if not t1:
        print("ERROR get_topic(): t1 not specified!")
        sys.exit(1)
    topic = f"/devices/{system_id}"
    if t1:
        topic += "/"+ t1
    if t2:
        topic += "/"+ t2
    if t3:
        topic += "/"+ t3
    logging.debug("build_topic(): '%s'", topic)
    return topic

def get_next_reset_time(time_value):
    """Calculate the next reset time based on the current time and the given time value."""
    current_time = time.time()
    next_reset = time.localtime(current_time)
    next_reset_time = current_time - ((next_reset.tm_hour * 60 + next_reset.tm_min) * 60 + next_reset.tm_sec)
    while next_reset_time < current_time:
        next_reset_time += time_value
    time_str = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(next_reset_time))
    logging.debug("get_next_reset_time(): %s", time_str)
    return next_reset_time

def get_saver(saver, system, control):
    """Get the saver dictionary for the given saver, system, and control."""
    for saver_dict in saver_arr:
        if saver_dict['saver'] == saver and saver_dict['system'] == system and saver_dict['control'] == control:
            logging.debug("get_saver(): %s, system: %s, control: %s found.", saver, system, control)
            return saver_dict
    logging.debug("get_saver(): %s, system: %s, control: %s NOT found.", saver, system, control)
    return False

def add_saver(client, saver, system, control, time_str):
    """Add or update a saver with the given parameters."""
    time_value = float(time_str) * 3600 # convert time string in hours to seconds
    saver_dict = get_saver(saver, system, control)
    if not saver_dict:
        logging.debug("add_saver(): %s, system: %s, control: %s, time %s added.", saver, system, control, time_value)
        next_reset_time = get_next_reset_time(time_value)
        saver_arr.append({'saver': saver, 'system': system, 'control': control, 'time': time_value, 'nextReset': next_reset_time, 'value': 'SNA'})
    else:
        logging.debug("add_saver(): %s, system: %s, control: %s, time %s updated.", saver, system, control, time_value)
        saver_dict['time'] = time_value
    if DEBUG:
        logging.debug("saver_arr:")
        for entry in saver_arr:
            print(json.dumps(entry, indent=4, ensure_ascii=False))
    # subscribe topic "/devices/<system>/controls/<control>"
    # e.g. "/devices/123456-energy/controls/Current Power"
    client.subscribe(build_topic(system, "controls", control))
    client.subscribe(build_topic(system, "controls", control, "meta/unit"))

def remove_saver(client, saver, system, control):
    """Remove a saver with the given parameters."""
    # Topic and array cleanup:
    # unsubscribe("/devices/<system>/controls/<control>")
    # publish("/devices/<system>/controls/<control> <saver>", "")
    # If the saver is not found, do nothing.
    saver_dict = get_saver(saver, system, control)
    if saver_dict:
        logging.debug("remove_saver(): %s, system: %s, control: %s removed.", saver, system, control)
        client.unsubscribe(build_topic(system, "controls", control))
        client.unsubscribe(build_topic(system, "controls", control, "meta/unit"))
        # remove topic
        client.publish(build_topic(system, "controls", control + " " + saver), "", retain=True)
        client.publish(build_topic(system, "controls", control + " " + saver, "meta/unit"), "", retain=True)
        saver_arr.remove(saver_dict)

def update_saver(client, system, control, value):
    """Update the min/max saver with the given value."""
    current_time = time.time()
    saver_dict = get_saver("min", system, control)
    if saver_dict:
        # check if max. save time is over
        if current_time > float(saver_dict['nextReset']):
            saver_dict['nextReset'] = float(saver_dict['nextReset']) + float(saver_dict['time'])
            saver_dict['value'] = "SNA" # set SNA, to make next if true
        if saver_dict['value'] == "SNA" or float(value) < float(saver_dict['value']):
            # new value is less than last min value
            logging.debug("update_saver(): min, system: %s, control: %s, value: %s updated.", system, control, value)
            saver_dict['value'] = value
            client.publish(build_topic(system, "controls", control + " min"), value, retain=True)

    saver_dict = get_saver("max", system, control)
    if saver_dict:
        # check if max save time is over
        if current_time > float(saver_dict['nextReset']):
            saver_dict['nextReset'] = float(saver_dict['nextReset']) + float(saver_dict['time'])
            saver_dict['value'] = "SNA" # set SNA, to make next if true
        if saver_dict['value'] == "SNA" or float(value) > float(saver_dict['value']):
            # new value is greater than last max value
            logging.debug("update_saver(): max, system: %s, control: %s, value: %s updated.", system, control, value)
            saver_dict['value'] = value
            client.publish(build_topic(system, "controls", control + " max"), value, retain=True)

def update_saver_unit(client, system, control, unit):
    """Update the unit of the min/max saver."""
    saver_dict = get_saver("min", system, control)
    if saver_dict:
        logging.debug("update_saver_unit(): min, system: %s, control: %s, unit: %s updated.", system, control, unit)
        client.publish(build_topic(system, "controls", control + " min", "meta/unit"), unit, retain=True)

    saver_dict = get_saver("max", system, control)
    if saver_dict:
        logging.debug("update_saver_unit(): max, system: %s, control: %s, unit: %s updated.", system, control, unit)
        client.publish(build_topic(system, "controls", control + " max", "meta/unit"), unit, retain=True)

def on_connect(client, userdata, flags, reason_code, properties):  # pylint: disable=unused-argument
    """The callback for when the client receives a CONNACK response from the broker."""
    logging.debug("on_connect(): Connected with result code %s", str(reason_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # subscribe topic "/sys/<systemId>/<min/max>/<minSystemId>/<minControlId>"
    # e.g. "/sys/123456-min-max-saver/min/123456-energy/Current Power"
    client.subscribe(f"/sys/{systemId}/+/+/+")

def on_message(client, userdata, msg):  # pylint: disable=unused-argument
    """The callback for when a PUBLISH message is received from the broker."""
    payload_str = msg.payload.decode("utf-8")  # payload is bytes since API version 2
    logging.debug("on_message(): "+ msg.topic+ ":"+ payload_str)
    # subscribed topics:
    # /sys/<systemId>/<min/max>/<minSystemId>/<minControlId>, payload: time in hours
    # /devices/<minSystemId>/controls/<minControlId>
    # /devices/<minSystemId>/controls/<minControlId>/meta/unit
    # e.g. "/sys/123456-min-max-saver/min/123456-energy/Current Power", payload: 24
    # "/devices/123456-energy/controls/Current Power", payload: 123
    topic = msg.topic.split("/") # topic[0] is "" (string before first "/")
    topic.remove("") #  remove this first empty topic
    if topic[0] == "sys" and topic[1] == systemId:
        if payload_str == "":
            logging.info("removing saver %s", msg.topic)
            remove_saver(client, topic[2], topic[3], topic[4])
        else:
            logging.info("adding saver %s: %s", msg.topic, payload_str)
            add_saver(client, topic[2], topic[3], topic[4], payload_str)
    elif topic[0] == "devices" and topic[2] == "controls":
        if len(topic) == 6 and topic[4] == "meta":
            if topic[5] == "unit":
                update_saver_unit(client, topic[1], topic[3], payload_str)
        else:
            update_saver(client, topic[1], topic[3], payload_str)
    else:
        print("[ERROR] on_message(): Unkown topic '%s'.", msg.topic)

def on_publish(client, userdata, mid, reason_code, properties):  # pylint: disable=unused-argument
    """The callback for when a message is published to the broker."""
    logging.debug("on_publish(): message send %s", str(mid))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Universal min/max saver.")
    parser.add_argument('-d', action='store_true', help='Enable debug output')
    parser.add_argument('--brokerHost', type=str, default=None, help='Set MQTT broker host')
    parser.add_argument('--brokerPort', type=int, default=None, help='Set MQTT broker port')
    return parser.parse_args()

args = parse_args()
if args.d:
    DEBUG = True
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Debug output enabled.")
if args.brokerHost is not None:
    logging.debug("set mqtt_config.host = %s", args.brokerHost)
    mqtt_config.host = args.brokerHost
if args.brokerPort is not None:
    logging.debug("set mqtt_config.port = %s", args.brokerPort)
    mqtt_config.port = args.brokerPort

# connect to MQTT broker
#mqttc = mqtt.Client()
mqttc = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_publish = on_publish
if mqtt_config.ca_certs != "":
    #mqttc.tls_insecure_set(True) # Do not use this "True" in production!
    mqttc.tls_set(mqtt_config.ca_certs, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqttc.username_pw_set(mqtt_config.user, password=mqtt_config.pwd)
logging.debug("Connecting to host '%s', port '%s'", mqtt_config.host, mqtt_config.port)
mqttc.connect(mqtt_config.host, port=mqtt_config.port)
mqttc.loop_start()

while True:
    # endless loop
    try:
        time.sleep(1000)
    except (KeyboardInterrupt, SystemExit):
        print('\nKeyboardInterrupt found! Stopping program.')
        break

# wait until all queued topics are published
mqttc.loop_stop()
mqttc.disconnect()
