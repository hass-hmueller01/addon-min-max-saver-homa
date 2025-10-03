"""Module providing the MQTT configuration for the service. Can be used for other options too."""

import json
import os
import sys
import bashio_logging  # provides logging output like bashio, must be imported before logging #pylint: disable=unused-import
import logging  # pylint: disable=wrong-import-order

homeassistant_options: str = "/data/options.json"
if not os.path.exists(homeassistant_options):
    logging.error("Home Assistant configuration file not found: %s", homeassistant_options)
    sys.exit(1)

with open(homeassistant_options, "r", encoding="utf-8") as f:
    options = json.load(f)
if "mqtt_host" in options and "mqtt_port" in options:
    mqtt_host = options.get("mqtt_host")
    mqtt_port = options.get("mqtt_port")
    mqtt_user = options.get("mqtt_user", "")
    mqtt_pwd = options.get("mqtt_password", "")
    mqtt_ca_certs = options.get("mqtt_ca_certs", "") # do not use with port 1883
    logging.info("Using configured MQTT Host: %s:%s", mqtt_host, mqtt_port)
elif "mqtt" in options:
    mqtt_cfg = options["mqtt"]
    mqtt_host = mqtt_cfg.get("host")
    mqtt_port = mqtt_cfg.get("port")
    mqtt_user = mqtt_cfg.get("username", "")
    mqtt_pwd = mqtt_cfg.get("password", "")
    mqtt_ca_certs = mqtt_cfg.get("mqtt_ca_certs", "")
    logging.info("Using internal MQTT Host: %s:%s", mqtt_host, mqtt_port)
else:
    logging.error("No MQTT broker configured and no internal MQTT service available.")
    sys.exit(1)
