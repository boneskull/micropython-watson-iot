# micropython-ibmiotf

> Unofficial IBM Watson IoT Platform SDK for Devices Running Micropython

## Install (*nix)

Install with [micropython](https://github.com/micropython/micropython)'s `upip`:

```bash
$ micropython -m upip install micropython-umqtt.simple micropython-umqtt.robust micropython-ibmiotf
```

## Usage

### Connecting

```python
from uibmiotf import Device

my_device = Device(
    device_id='my-device-id', # required
    device_type='my-device-type', # required
    token='my-device-token', # required
    # optional parameters shown with defaults below
    org='quickstart', 
    username='use-token-auth',
    port=8883, # this is 1883 if default `org` used
    clean_session=True,
    domain='internetofthings.ibmcloud.com',
    ssl_params=None,
    log_level='info'
)

my_device.connect()
```

When finished, you can disconnect:

```python
my_device.disconnect()
```

### Publishing an Event

Assuming the Device is connected, this example will publish a single event with ID `my_event_id`.

```python
my_device.publishEvent(
    'my_event_id', # event name
    {'ok': True}, # message payload
    
    message_format='json', # 'text' is also built-in
    qos=0 # QoS 0 or QoS 1
)
```

### Handling a Command

The following will execute the `my_handler` function when command `my-command` is received by the Device.

```python
def my_handler(message):
  """
  does something with `message`
  """
  pass

my_device.set_command('my-command', my_handler)

# blocking wait for command
while my_device.is_connected:
    my_device.sync_loop()
```

Alternatively, a non-blocking approach:

```python
import utime as time

# non-blocking wait for command
while my_device.is_connected:
    my_device.loop()
    # do other stuff like sleep
    time.sleep(1)
```

To *stop* handling the command `my-command`:

```python
my_device.unset_command('my-command')
```

### Registering a Custom Message Format

`micropython-ibmiotf` comes with built-in encoders and decoders for JSON (`json`) and plain text (`text`) message formats.

**All incoming messages (via commands, for example) are byte literals!** 

You can add a custom encoder and decoder:

```python
def to_csv(my_list):
    """
    `my_list` is likely a list or tuple; returns a str
    """
    return ','.join(my_list)

def from_csv(data):
    """
    `data` is a byte literal and must be coerced to a str first
    """
    return str(data).split(',')
    
my_device.set_encoder('csv', to_csv)
my_device.set_decoder('csv', from_csv)
```

Now, whenever an event is published with `message_format='csv'`, the *encoder* will modify the outbound message.  Likewise, whenever a command is received in the `csv` format, the incoming message will be run through the *decoder* before it's given to the command handler.

You can also remove them, if you wish:

```python
my_device.unset_encoder('csv')
my_device.unset_decoder('csv')
```

### Potentially Useful Properties

- `is_connected` - `bool`, whether or not the Device is currently connected
- `is_secure` - `bool`, whether or not the active or inactive connection is encrypted

## Limitations

`micropython-ibmiotf` is designed to run on severely resource-constrained microcontrollers.

If your use case falls outside of the limitations listed below, take a look at [the official Python SDK](https://github.com/ibm-watson-iot/iot-python) instead.

### No "Applications" Nor "Gateways"

`micropython-ibmiotf` supports "unmanaged devices" only:

> A device is anything that has a connection to the internet and has data to send to or receive from the cloud. You can use devices to send event information such as sensor readings to the cloud, and to accept commands from applications in the cloud.

That means you cannot create an [application](https://console.bluemix.net/docs/services/IoT/applications/app_dev_index.html#app_dev_index) or [gateway](https://console.bluemix.net/docs/services/IoT/gateways/gw_dev_index.html#gw_dev_index)  with `micropython-ibmiotf`.

### No "Managed Devices"

`micropython-ibmiotf` (as of this writing) does not support [managed devices](https://console.bluemix.net/docs/services/IoT/devices/device_mgmt/index.html#index).

This may or may not be feasible.

### No XML Support

`micropython-ibmiotf` does not (and likely *will not*) parse commands received as XML; nor does it provide any "helpers" to publish events as XML.  

### No Support for QoS 2

As of Sep 20, 2017, the official Micropython MQTT client does not support QoS 2, so neither does `micropython-ibmiotf`.

### Micropython Itself

Micropython [is not CPython](http://docs.micropython.org/en/latest/pyboard/genrst/index.html).  While Micropython is *based on* Python 3, `micropython-ibmiotf` is not targeting Python 3, nor is it targeting any forks of Micropython.

# License

© 2017 [Christopher Hiller](https://boneskull.com).  Licensed Apache-2.0
