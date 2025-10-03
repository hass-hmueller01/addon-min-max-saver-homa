"""Module providing the MQTT configuration for the service."""

import json
import os
import sys
import bashio_logging  # provides logging output like bashio, must be imported before logging #pylint: disable=unused-import
import logging  # pylint: disable=wrong-import-order

homeassistant_config: str = "/data/options.json"
if not os.path.exists(homeassistant_config):
    logging.error("Home Assistant configuration file not found: %s", homeassistant_config)
    sys.exit(1)

with open(homeassistant_config, "r", encoding="utf-8") as f:
    config = json.load(f)
if "mqtt_host" in config and "mqtt_port" in config:
    host = config.get("mqtt_host")
    port = config.get("mqtt_port")
    user = config.get("mqtt_user", "")
    pwd = config.get("mqtt_password", "")
    ca_certs = config.get("mqtt_ca_certs", "") # do not use with port 1883
    logging.info("Using configured MQTT Host: %s:%s", host, port)
elif "mqtt" in config:
    mqtt_cfg = config["mqtt"]
    host = mqtt_cfg.get("host")
    port = mqtt_cfg.get("port")
    user = mqtt_cfg.get("username", "")
    pwd = mqtt_cfg.get("password", "")
    ca_certs = mqtt_cfg.get("mqtt_ca_certs", "")
    logging.info("Using internal MQTT Host: %s:%s", host, port)
else:
    logging.error("No MQTT broker configured and no internal MQTT service available.")
    sys.exit(1)
