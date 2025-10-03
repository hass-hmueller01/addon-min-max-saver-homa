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
