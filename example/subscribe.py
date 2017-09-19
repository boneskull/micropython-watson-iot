from uibmiotf import create


def ping(message):
    print('pong %s' % message)


# read config data from uibmiotf.json
device = create()
# create a command handler
device.set_command('ping', ping)
# connect to MQTT broker
device.connect()

# blocking wait for command
while device.is_connected:
    device.sync_loop()
