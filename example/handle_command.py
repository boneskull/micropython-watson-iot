"""
This example shows how you can handle a command sent to the device.

Per https://console.bluemix.net/docs/services/IoT/iotplatform_overview.html
(as of September 20, 2017):

"Commands are the mechanism by which applications communicate with devices. Only
applications can send commands, and the commands are sent to specific devices.
The device must determine which action to take on receipt of any given command.
Devices can be designed to listen for any command or to subscribe to a
specified list of commands."

Commands can also be sent via RESTful API.
"""

from watson_iot import Device

# options can be loaded from watson_iot.json; see
# watson_iot.example.json for example
my_device = Device(
    device_id='my-device-id',
    device_type='my-device-type',
    org='my-org-id',
    token='my-device-token'
)


def disconnect():
    my_device.disconnect()
    print('disconnected')


# create a command handler
my_device.set_command('disconnect', disconnect)
# connect to MQTT broker
my_device.connect()

# blocking wait for command
while my_device.is_connected:
    my_device.sync_loop()
