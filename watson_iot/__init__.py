from umqtt.robust import MQTTClient
import logging
import ujson as json
import ure as re

DOMAIN = 'internetofthings.ibmcloud.com'
QUICKSTART_ORG = 'quickstart'
DEVICE_COMMAND_TOPIC = 'iot-2/cmd/+/fmt/+'
LOG_LEVELS = {v.lower(): k for k, v in logging._level_dict.items()}
TOPIC_REGEX = re.compile('^iot-2/cmd/(.+?)/fmt/(.+)$')


def bytes_to_utf8(value):
    """
    Converts byte literal to utf8 string
    :param value: Byte literal
    :type value: bytes
    :return: UTF-8 encoded string
    :rtype: str
    """
    return str(value, 'utf8')


def bytes_to_json(value):
    """
    Convert byte literal to Python object
    :param value: Raw bytes
    :type value: bytes
    :return: JSON object, array, etc
    :rtype: Any
    """
    return json.loads(bytes_to_utf8(value))


def Device(**kwargs):
    """
    Creates a Device object by merging parameters into contents of
    `watson_iot.json`, if present.
    :return: New Device
    :rtype: UnmanagedDevice
    """
    try:
        fh = open('watson_iot.json')
        # noinspection PyTypeChecker
        config = dict(json.loads(fh.read()))
        kwargs.update(**config)
    except OSError:
        pass
    return UnmanagedDevice(**kwargs)


class UnmanagedDevice:
    """
    An "unmanaged device" for the Watson IoT platform
    """
    decoders = {}
    encoders = {}
    commands = {}

    def __init__(self, org='quickstart', device_type=None, device_id=None,
                 username='use-token-auth', token=None,
                 port=8883, clean_session=True, domain=DOMAIN, ssl_params=None,
                 log_level='info'):
        """
        Builds proper params for connecting to IoT platform MQTT broker.
        Registers JSON encoder & decoder.
        Creates MQTT client object, but does not connect.

        `quickstart` implies an *insecure* connection!

        :param log_level: Logging level
        :type log_level: str
        :param org: IoT platform organization
        :type org: str
        :param device_type: IoT platform device type
        :type device_type: str
        :param device_id: IoT platform client identifier
        :type device_id: str
        :param username: IoT platform username
        :type username: str
        :param token: IoT platform API token
        :type token: str
        :param port: MQTT broker port
        :type port: int
        :param clean_session: Whether to use a clean session when connecting
        :type clean_session: bool
        :param domain: IoT platform domain name
        :type domain: str
        :param ssl_params: Additional SSL parameters for a secure connection
        :type ssl_params: dict
        """
        if not device_type:
            raise Exception('"device_type" parameter required')
        if not device_id:
            raise Exception('"client_id" parameter required')
        if not token:
            raise Exception('"token" parameter required')

        self.org = org
        self.username = username
        self.token = token
        self.device_type = device_type
        self.address = '%s.messaging.%s' % (org, domain)
        self.client_id = 'd:%s:%s:%s' % (self.org, self.device_type, device_id)
        self.port = port
        self.keep_alive = 60
        self.logger = logging.getLogger(
            '%s.%s' % (self.__module__, self.__class__.__name__))
        self.logger.level = LOG_LEVELS[log_level]

        self.clean_session = clean_session
        self.ssl_params = ssl_params or {}

        self.client = MQTTClient(self.client_id, self.address,
                                 user=self.username,
                                 password=self.token,
                                 ssl=self.is_secure, ssl_params=self.ssl_params)
        if self.logger.level == logging.DEBUG:
            self.client.DEBUG = True
        self.set_decoder('json', bytes_to_json)
        self.set_encoder('json', json.dumps)
        self.set_decoder('text', bytes_to_utf8)
        # noinspection PyTypeChecker
        self.set_encoder('text', str)

    @property
    def is_connected(self):
        """
        Crudely checks connectivity by pinging
        :return: Whether or not socket is alive
        :rtype: bool
        """
        try:
            self.client.ping()
            return True
        except OSError:
            return False

    def set_encoder(self, name, func):
        """
        "Registers" an encoder
        :param name: Name of encoder
        :type name: str
        :param func: Encoding function
        :type func: function
        """
        self.encoders[name] = func

    def unset_encoder(self, name):
        """
        "Un-registers" a encoder
        :param name: Name of existing encoder
        :type name: str
        """
        try:
            del self.encoders[name]
        except KeyError:
            pass

    def set_decoder(self, name, func):
        """
        "Registers" a decoder
        :param name: Name of decoder
        :type name: str
        :param func: Decoding function
        :type func: function
        """
        self.decoders[name] = func

    def unset_decoder(self, name):
        """
        "Un-registers" a decoder
        :param name: Name of existing decoder
        :type name: str
        """
        try:
            del self.decoders[name]
        except KeyError:
            pass

    def set_command(self, command_id, handler):
        """
        "Registers" a command handler (if org is not "quickstart")
        :param command_id: Command ID
        :type command_id: str
        :param handler: Command handler
        :type handler: function
        """
        if self.is_quickstart:
            raise Exception('"quickstart" org does not support commands')
        self.commands[command_id] = handler

    def unset_command(self, command_id):
        """
        "Unregisters" a command
        :param command_id: Command ID
        :type command_id: str
        """
        try:
            del self.commands[command_id]
        except KeyError:
            pass

    @property
    def is_secure(self):
        """
        Secure connection? `False` if `org` is `quickstart`
        :return: Whether or not SSL is enabled.
        :rtype: bool
        """
        return self.port == 8883 and not self.is_quickstart

    @property
    def is_quickstart(self):
        """
        Is "quickstart" org?
        :return: Whether or not `org` is `quickstart`
        :rtype: bool
        """
        return self.org == QUICKSTART_ORG

    def connect(self):
        """
        Connects to the MQTT broker.  If not a "quickstart" org,
        then subscribes to commands.
        """
        self.client.connect(self.clean_session)
        self.logger.debug('client "%s" connected to %s:%s' % (
            self.client_id, self.address, self.port))

        if not self.is_quickstart:
            def message_callback(topic, message):
                """
                Callback executed when a msg for a subscribed topic is received
                :param topic: Raw MQTT topic
                :type topic: bytes
                :param message: Raw MQTT message
                :type message: bytes
                """
                topic = bytes_to_utf8(topic)
                matches = TOPIC_REGEX.match(topic)
                command_id = matches.group(1)
                message_format = matches.group(2)
                if message_format in self.decoders:
                    message = self.decoders[message_format](message)
                else:
                    self.logger.debug(
                        'no suitable decoder for message format "%s"' %
                        message_format)
                self.logger.debug('topic: %s\nmessage: %s' % (topic, message))
                if command_id in self.commands:
                    self.logger.info('received command "%s"' % command_id)
                    self.commands[command_id](message)
                else:
                    self.logger.warning('command "%s" received, \
but no handler registered' % command_id)

            self.client.set_callback(message_callback)
            self.client.subscribe(DEVICE_COMMAND_TOPIC)
            self.logger.debug('subscribed to device command topic: %s',
                              DEVICE_COMMAND_TOPIC)

    def publishEvent(self, event_id, payload, message_format='json', qos=0):
        """
        Publishes an event
        :param event_id: Event ID
        :type event_id: str
        :param payload: Event payload
        :type payload: Any
        :param message_format: Message format
        :type message_format: str
        :param qos: Quality of Service
        :type qos: int
        """
        if not self.is_connected:
            raise Exception('client is not connected')
        if qos == 2:
            raise Exception('QoS level 2 not implemented')
        event_id = event_id.strip()
        if message_format in self.encoders:
            payload = self.encoders[message_format](payload)
        self.client.publish('iot-2/evt/%s/fmt/%s' % (event_id, message_format),
                            payload, qos)

    def disconnect(self):
        """
        Disconnects (if connected)
        """
        try:
            self.client.disconnect()
            self.logger.warning('Closed connection to the IBM Watson \
IoT Platform')
        except OSError:
            self.logger.warning('Attempted to disconnect from a \
            disconnected socket')

    def loop(self):
        """
        Non-blocking check-for-messages.  You need to do something else
        after this, such as `time.sleep(1)`, or other meaningful work,
        if you are going to do this in a busy-loop.

        This appears unsupported in some environments (incl. unix)
        """
        self.client.check_msg()

    def sync_loop(self):
        """
        Blocking check-for-messages.  Run this in a busy-loop.
        """
        self.client.wait_msg()
