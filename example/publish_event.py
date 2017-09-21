"""
This example shows how a device can publish an event.

Per https://console.bluemix.net/docs/services/IoT/iotplatform_overview.html
(as of September 20, 2017):

"Events are the mechanism by which devices publish data to the Watson IoT
Platform. Devices control the content of their messages, and assign a name for
each event that is sent. The Watson IoT Platform uses the credentials that are
attached to each event received to determine which device sent the event. This
architecture prevents devices from impersonating one another.

Applications can process events in real time, and see the source of the event
and the data contained in the event. Applications must be configured to define
which devices and events they subscribe to."
"""

from watson_iot import Device
import utime as time

# options can be loaded from watson_iot.json; see
# watson_iot.example.json for example
device = Device(
    device_id='my-device-id',
    device_type='my-device-type',
    org='my-org-id',
    token='my-device-token'
)

# connect to MQTT broker
device.connect()

# this will publish an event called "my-event-id" every minute containing JSON
# object {"alive": true}
while True:
    # default is JSON format with QoS 0
    device.publishEvent('my-event-id', {'alive': True})
    time.sleep(60)

