# micropython-ibmiotf

> Unofficial Micropython Device SDK for IBM's Watson IoT Platform

## Install

Install with [micropython](https://github.com/micropython/micropython)'s `upip`:

```bash
$ micropython -m upip install micropython-ibmiotf
```

## Usage

TODO

## Limitations

If your use case falls outside of the limitations listed below, take a look at [the official Python SDK](https://github.com/ibm-watson-iot/iot-python) instead.

### No "Applications", No "Gateways"

`micropython-ibmiotf` supports "unmanaged devices" only:

> A device is anything that has a connection to the internet and has data to send to or receive from the cloud. You can use devices to send event information such as sensor readings to the cloud, and to accept commands from applications in the cloud.

That means you cannot create an [application](https://console.bluemix.net/docs/services/IoT/applications/app_dev_index.html#app_dev_index) or [gateway](https://console.bluemix.net/docs/services/IoT/gateways/gw_dev_index.html#gw_dev_index)  with `micropython-ibmiotf`.

### No "Managed Devices"

`micropython-ibmiotf` (as of this writing) does not support [managed devices](https://console.bluemix.net/docs/services/IoT/devices/device_mgmt/index.html#index).

This may or may not be feasible.

### No XML Support

`micropython-ibmiotf` does not (and likely *will not*) parse commands received as XML; nor does it provide any "helpers" to publish events as XML. 

### Micropython

Micropython [is not CPython](http://docs.micropython.org/en/latest/pyboard/genrst/index.html).  While Micropython is *based on* Python 3, `micropython-ibmiotf` is not targeting Python 3, nor is it targeting any forks of Micropython.
