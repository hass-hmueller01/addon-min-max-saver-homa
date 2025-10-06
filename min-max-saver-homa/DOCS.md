# Home Assistant add-on: HomA MQTT min/max saver

This add-on is a universal min/max saver used by HomA MQTT framework.

## How to use

Once installed, the add-on subscribes to `/sys/<systemId>/+/+/+` to configure messages that will be saved and published to the according min/max values.
The subscribed topics must have the form
```
/sys/<systemId>/min/<minSystemId>/<minControlId>, payload: <interval time in hours>
/sys/<systemId>/max/<maxSystemId>/<maxControlId>, payload: <interval time in hours>
```
e.g. `/sys/123456-min-max-saver/min/123456-energy/Current Power, payload: 24`

Once the given interval time is over it will publish
```
/devices/<minSystemId>/controls/<minControlId> min, payload: min value in given intervall
/devices/<minSystemId>/controls/<minControlId> min/meta/unit, payload: copy of /devices/<minSystemId>/controls/<minControlId>/meta/unit
/devices/<maxSystemId>/controls/<maxControlId> max, payload: max value in given intervall
/devices/<maxSystemId>/controls/<maxControlId> max/meta/unit, payload: copy of /devices/<maxSystemId>/controls/<maxControlId>/meta/unit
```
It's possible to save only the min or max value if configured accordingly.

## Configuration

The add-on supports the internal (Home Assistant) or an external MQTT broker. To configure the external MQTT broker you have to activate the _"Show unused optional configuration options"_.

You can modify the subscribed topic id `<systemId>` by setting _"HomA System ID"_.

A sample config Python script to setup the `/sys/<systemId>/...` messages is located in

[./rootfs/etc/services.d/min-max-saver/setup.py](./rootfs/etc/services.d/min-max-saver/setup.py)

It runs outside the Home Assistant docker environment by eigther setting the environment variables `MQTT_HOST`, `MQTT_PORT`, `MQTT_USER`, `MQTT_PASSWORD` or providing a config file `~/.config/mqtt_config.py`.
```shell
./setup.py
[12:00:00] INFO: Home Assistant configuration file not found: /data/options.json
[12:00:00] INFO: No environment variables found: MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
[12:00:00] INFO: Using mqtt_config.py configured MQTT Host: mqtt:1883
Publishing HomA setup data to mqtt  (systemId 123456-min-max-saver) ...
/sys/123456-min-max-saver/max/123456-windsensor/Wind speed => 24
/sys/123456-min-max-saver/min/123456-vito/Aussentemperatur => 24
/sys/123456-min-max-saver/max/123456-vito/Aussentemperatur => 24
/sys/123456-min-max-saver/min/123456-vito/Raumtemperatur => 24
/sys/123456-min-max-saver/max/123456-vito/Raumtemperatur => 24
/sys/123456-min-max-saver/min/123456-energy/Current Power => 24
/sys/123456-min-max-saver/max/123456-energy/Current Power => 24
```
