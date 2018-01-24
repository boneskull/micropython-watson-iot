"""
This example shows how a device can publish an event using Quickstart.
Get a device ID from https://quickstart.internetofthings.ibmcloud.com

"""

from watson_iot import Device
import utime as time

# options can be loaded from watson_iot.json by omitting parameters.
# see watson_iot.example.json for example
device = Device(device_id='my-device-id')

# connect to MQTT broker
device.connect()

# this will publish an event called "my-event-id" every minute containing JSON
# object {"alive": true}
while True:
    # default is JSON format with QoS 0
    device.publishEvent('my-event-id', {'alive': True})
    time.sleep(60)

