# micropython-watson-iot

> Unofficial IBM Watson IoT Platform SDK for Devices Running MicroPython

This is a "SDK" in the loosest sense.

## Installation

**This library is intended to be used with an [ESP32](https://espressif.com/en/products/hardware/esp32/overview)-based device**, or at least something with connectivity that has more RAM than a ESP8266, and runs [MicroPython](https://micropython.org).

The device you're using should already have been flashed with [MicroPython](https://micropython.org).

### Installation via REPL

Open a serial terminal, e.g.:

```bash
$ python3 -m serial.tools.miniterm --raw /dev/your-com-port 115200
```

Ensure your device has internet connectivity, then:

```python
import upip
upip.install('micropython-watson-iot')
```

The above will install the latest release of this module (and its dependencies) within `lib/`. 

### Installation via Host Computer

1. Clone [this repo](https://github.com/boneskull/micropython-watson-iot), or download a `.zip`.
1. From your working copy, copy the `watson_iot/` directory to your device
1. Create a `umqtt` directory on your device
1. Clone [micropython-lib](https://github.com/micropython/micropython-lib) or download a `.zip`
1. From the `micropython-lib` working copy, put: 
    1. `umqtt.simple/umqtt/simple.py` into `umqtt/simple.py`
    1. `umqtt.robust/umqtt/robust.py` into `umqtt/robust.py`

#### Using Adafruit's MicroPython Tool

A tool you can use to copy files is [adafruit-ampy](https://github.com/adafruit/ampy), which can be installed via `pip3 install adafruit-ampy`.  

This oughtta do it: 

```bash
$ PORT=/dev/tty.SLAB_USBtoUART && \
ampy --port "${PORT}" put /path/to/micropython-watson-iot/watson_iot && \
ampy --port "${PORT}" mkdir umqtt && \
ampy --port "${PORT}" put \
  /path/to/micropython-lib/umqtt.simple/umqtt/simple.py umqtt/simple.py && \
ampy --port "${PORT}" put \
  /path/to/micropython-lib/umqtt.robust/umqtt/robust.py umqtt/robust.py
```

(Replace the working copy paths and the value of `PORT` with your device path.)

## IBM Cloud & Watson IoT Platform

You have a couple options here.

- To experiment, you can use [Watson IoT Platform Quickstart](https://quickstart.internetofthings.ibmcloud.com/), or
- [Sign up for a (free) IBM Cloud account](https://console.bluemix.net/registration/), then [create an Watson IoT Platform service](https://console.bluemix.net/catalog/services/internet-of-things-platform) from the catalog

## Usage

In lieu of proper API documentation, here are a bunch of examples:

### Connecting

```python
from watson_iot import Device

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

`micropython-watson-iot` comes with built-in encoders and decoders for JSON (`json`) and plain text (`text`) message formats.

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

If your use case falls outside of the limitations listed below, take a look at [the official Python SDK](https://github.com/ibm-watson-iot/iot-python) instead.  

*That being said*, I'm open to collaboration on the following items, whether they make sense within this project, or others.

### No "Applications" Nor "Gateways"

`micropython-watson-iot` supports "unmanaged" devices only.  A "device" in the context of Watson IoT Platform is: 

> A device is anything that has a connection to the internet and has data to send to or receive from the cloud. You can use devices to send event information such as sensor readings to the cloud, and to accept commands from applications in the cloud.

That means you cannot create an [application](https://console.bluemix.net/docs/services/IoT/applications/app_dev_index.html#app_dev_index) or [gateway](https://console.bluemix.net/docs/services/IoT/gateways/gw_dev_index.html#gw_dev_index) with `micropython-watson-iot`.

### No "Managed Devices"

`micropython-watson-iot` (as of this writing) does not support [managed devices](https://console.bluemix.net/docs/services/IoT/devices/device_mgmt/index.html#index).

This may or may not be feasible.

### No XML Support

`micropython-watson-iot` does not (and likely *will not*) parse commands received as XML; nor does it provide any "helpers" to publish events as XML.  

### No Support for QoS 2

As of Sep 20, 2017, the official MicroPython MQTT client module does not support QoS 2, so neither does `micropython-watson-iot`.

I'd be cool with using a *non-official* MQTT client module which *did* support QoS 2, if such a thing existed!

### MicroPython Itself

MicroPython [is not CPython](http://docs.micropython.org/en/latest/pyboard/genrst/index.html).  While MicroPython is *based on* Python 3, `micropython-watson-iot` is not targeting Python 3, nor is it targeting any forks of MicroPython (e.g., [CircuitPython](https://github.com/adafruit/circuitpython)).

## Development Notes

### Publish

```bash
$ ./setup.py sdist upload
```

Enter your PyPi pizassword at the pizrompt.

# License

© 2017-2018 [Christopher Hiller](https://boneskull.com).  Licensed Apache-2.0
