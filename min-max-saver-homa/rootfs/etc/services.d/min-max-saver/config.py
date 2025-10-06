"""Module providing the MQTT configuration for the service. Can be used for other options too."""

import json
import os
import sys
import bashio_logging  # provides logging output like bashio, must be imported before logging #pylint: disable=unused-import
import logging  # pylint: disable=wrong-import-order

homeassistant_options: str = "/data/options.json"
if os.path.exists(homeassistant_options):
    with open(homeassistant_options, "r", encoding="utf-8") as f:
        options = json.load(f)
    if "mqtt_host" in options and "mqtt_port" in options:
        mqtt_host = options.get("mqtt_host")
        mqtt_port = options.get("mqtt_port", 1883)
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
        mqtt_ca_certs = ""  # not supported in Home Assistant internal MQTT
        logging.info("Using internal MQTT Host: %s:%s", mqtt_host, mqtt_port)
    else:
        logging.error("No MQTT broker configured and no internal MQTT service available.")
        sys.exit(1)
else:
    logging.info("Home Assistant configuration file not found: %s", homeassistant_options)
    options = {}
    mqtt_host = os.getenv('MQTT_HOST', "")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_user = os.getenv("MQTT_USER", "")
    mqtt_pwd = os.getenv("MQTT_PASSWORD", "")
    mqtt_ca_certs = os.getenv("MQTT_CA_CERTS", "")  # not used with port 1883
    if mqtt_host != "":
        logging.info("Using environment configured MQTT Host: %s:%s", mqtt_host, mqtt_port)
    else:
        logging.info("No environment variables found: MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD")
        import importlib.util
        mqtt_config_file_path = os.path.join(os.getenv('HOME', ""), ".config", "mqtt_config.py")
        mqtt_config_spec = importlib.util.spec_from_file_location("mqtt_config", mqtt_config_file_path)
        if os.path.exists(mqtt_config_file_path) and mqtt_config_spec is not None and mqtt_config_spec.loader is not None:
            mqtt_config = importlib.util.module_from_spec(mqtt_config_spec)
            mqtt_config_spec.loader.exec_module(mqtt_config)
            mqtt_host = mqtt_config.host
            mqtt_port = mqtt_config.port
            mqtt_user = mqtt_config.user
            mqtt_pwd = mqtt_config.pwd
            mqtt_ca_certs = mqtt_config.ca_certs
            logging.info("Using mqtt_config.py configured MQTT Host: %s:%s", mqtt_host, mqtt_port)
        else:
            logging.error("Could not load ~/.config/mqtt_config.py to get MQTT broker configuration. Exiting.")
            sys.exit(1)
