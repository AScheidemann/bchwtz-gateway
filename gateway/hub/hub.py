import asyncio
import logging
from threading import Thread
import time
import uuid
from gateway.tag.tag import Tag
from gateway.tag.tag_builder import TagBuilder
from gateway.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from gateway.config import Config
import json
from paho.mqtt.client import Client, MQTTMessage
import aiopubsub

class Hub(object):
    """ Hub has all tags of a gateway and enables you to search for specific tags. It also scans for tags or listens for advertisments and logs everything to mqtt.
    """

    def __init__(self):
        """ Initializes a new Hub.
        """
        self.tags: list[Tag] = []
        self.ble_conn = BLEConn()
        self.logger = logging.getLogger("Hub")
        self.logger.setLevel(logging.DEBUG)
        self.mqtt_client: Client = None
        self.pubsub_hub: aiopubsub.Hub = aiopubsub.Hub()
        self.main_loop: asyncio.BaseEventLoop = asyncio.get_event_loop()
        self.mqtt_topics: list[str] = []

    async def discover_tags(self, timeout: float = 5.0, rediscover: bool = False, autoload_config: bool = True) -> None:
        """ Starts a classic bluetooth scan and search for any tags matching our manufacturer_id.
            Arguments:
                timeout: when should we stop the scan?
                rediscover: should already known tags be rediscovered and all their measurements be deleted from ram?
                autoload_config: if this is true each tag will be configured on its first discovery. If rediscover is on, this will be done on every contact.
        """
        devices = await self.ble_conn.scan_tags(Config.GlobalConfig.bluetooth_manufacturer_id.value, timeout)
        if not rediscover:
            self.__check_tags_online_state(devices)
            if not self.__has_new_devices(devices):
                self.logger.debug("found no new devices")
                return
            devices = filter(lambda dev: not any(dev.address == t.address for t in self.tags), devices)
        self.logger.debug("found new devices")
        self.__devices_to_tags(devices)
        if autoload_config:
            for dev in devices:
                tag = self.get_tag_by_address(dev.address)
                tag.get_config()
        self.log_mqtt()
    
    async def listen_for_advertisements(self, timeout: float = 50) -> None:
        """ Listens for advertisements and calls tha listen_advertisements_cb on every received advertisement.
            Arguments:
                timeout: When should we stop listening for advertisements? Can be looped.
        """
        await self.ble_conn.listen_advertisements(timeout, self.cb_advertisements)
    
    async def cb_advertisements(self, device: BLEDevice, data: AdvertisementData):
        """ Is called on every received advertisment. Sets up a new tag or adds advertisements to a known tag.
            Arguments:
                device: ble_device that was discovered
                data: AdvertismentData as dit
        """
        device.metadata = data.__dict__
        devices = self.ble_conn.validate_manufacturer([device], Config.GlobalConfig.bluetooth_manufacturer_id.value)
        if len(devices) <= 0:
            return
        device = devices[0]
        tag = self.get_tag_by_address(devices[0].address)
        if tag is None:
            tag = TagBuilder().from_device(device = device, pubsub_hub = self.pubsub_hub, mqtt_client = self.mqtt_client).build()
            self.tags.append(tag)
            await tag.get_config()
            if Config.GlobalConfig.forced_time_sync.value:
                await tag.set_time()
                await tag.get_time()
            self.logger.info(f"setting up new device with address {tag.address}")
        # if tag.config is None or tag.config.samplerate == 0:
        #     self.logger.warn("tag config was not loaded yet!")
        #     return
        tag.read_sensor_data(data.manufacturer_data.get(Config.GlobalConfig.bluetooth_manufacturer_id.value))
        tag.last_seen = time.time()
        tag.online = True
        self.log_mqtt()

    def log_mqtt(self):
        """ used to log data on the mqtt_log channel.
        """
        if self.mqtt_client is not None:
            self.logger.info("logging to channel %s", Config.MQTTConfig.topic_listen_adv.value)
            self.mqtt_client.publish(Config.MQTTConfig.topic_listen_adv.value, json.dumps(self, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

    async def on_log_event(self, key: aiopubsub.Key, tag: Tag):
        """ Listener callback for internal pubsub. Will forward everything to mqtt-log-channel
            Arguments:
                key: the key that the event was received on
                tag: the tag object that has to be sent to log_mqtt
        """
        self.logger.info("logging to mqtt for key %s", key)
        self.log_mqtt()

    async def on_command_event(self, key: aiopubsub.Key, cmd: dict):
        """ Called when a command via mqtt was discovered (deprecated)
        """
        self.logger.info("fetching time")
        for t in self.tags:
            await t.get_time()

    def get_tag_by_address(self, address: str = None) -> Tag:
        """Get a tag object by a known mac adress.
        :param address: mac adress from a BLE device, defaults to None
        Arguments:
            mac: the mac address of the tag
        Returns:
            a tag object
        """
        if address is not None:
            for tag in self.tags:
                if tag.address == address:
                    return tag
        return None

    def get_tag_by_name(self, name: str = None) -> Tag:
        """Get a tag object by a known mac adress.
        Arguments:
            mac: mac adress from a BLE device, defaults to None
        Returns:
            Returns a tag object.
        """
        # TODO: REFACTOR - this is slower than needed
        if name is not None:
            for tag in self.tags:
                if tag.name == name:
                    return tag
        return None

    def __devices_to_tags(self, devices: list[BLEDevice]) -> list[Tag]:
        self.tags = [TagBuilder().from_device(dev, self.pubsub_hub, self.mqtt_client).build() for dev in devices]
        return self.tags

    def __has_new_devices(self, devices: list[BLEDevice]) -> bool:
        for device in devices:
            if not any(t.address == device.address for t in self.tags):
                return True
        return False

    def __check_tags_online_state(self, devices: list[BLEDevice]) -> None:
        for tag in self.tags:
            self.logger.debug(tag.__dict__)
            if not any(tag.address == dev.address for dev in devices):
                tag.online = False
                self.logger.debug(f"setting tag offline: {tag.address}")
            else:
                tag.online = True
                tag.last_seen = time.time()
                self.logger.debug(f"setting tag online: {tag.address}")

    def get_props(self) -> dict:
        """ Returns self as a dict
            Returns:
                self as dict
        """
        return {'tags': self.tags}

    async def subscribe_to_log_events(self):
        """ Subscribes to log events on internal pubsub.
        """
        self.log_subscriber: aiopubsub.Subscriber = aiopubsub.Subscriber(self.pubsub_hub, "events")
        subscribe_key = aiopubsub.Key('*', 'log', '*')
        self.log_subscriber.add_async_listener(subscribe_key, self.on_log_event)

    def mqtt_on_connect(self, client, userdata, flags, rc):
        """ Connect callback for mqtt.
            Arguments:
                client: MQTT-client (paho)
                userdata: MQTT userdata
                flags: MQTT flags
                rc: MQTT result
        """
        self.logger.info("connected to mqtt")
        self.logger.debug("result: %s"%rc)
        sub = Config.MQTTConfig.topic_command.value
        res = self.mqtt_client.subscribe(sub, 0)
        sub = "gateway/hub/get_all"
        res = self.mqtt_client.subscribe(sub, 0)
        self.logger.info(sub)

    def mqtt_on_command(self, client, userdata, message: MQTTMessage):
        """ MQTT listener for the command channel. Will execute the command submitted to mqtt. Will respond with a status to mqtt.
            Arguments:
                client: MQTT-client
                userdata: MQTT-userdata
                message: Message received by the client
        """
        msg_dct: dict = json.loads(message.payload)
        self.logger.info(msg_dct)
        id = msg_dct["id"]
        payload = msg_dct["payload"]
        tags = []
        for t in self.tags:
            tags.append(t.get_props())
        # print(self.internal_command_publisher.__dict__)

        self.forward_mqtt_functions_to_ns_handler(topic_name = message.topic, client = client, msg = message)
        

        self.logger.debug("sent payload")

    def forward_mqtt_functions_to_ns_handler(self, topic_name: str, client: Client, msg: MQTTMessage) -> None:
        self.logger.warn(topic_name)
        parts = topic_name.split("/")
        namespace = parts[1]
        if namespace == "tag":
            tag_address = parts[2]
            command = parts[3]
            tag = self.get_tag_by_address(tag_address)
            if tag is None:
                self.logger.error("tag with address %s not found!" % tag_address)
            tag.handle_mqtt_cmd(mqtt_client=client, command=command, msg=msg)
        elif namespace == "tags":
            for tag in self.tags:
                command = parts[2]
                tag.handle_mqtt_cmd(mqtt_client=client, command=command, msg=msg)
        elif namespace == "hub":
            command = parts[2]
            self.handle_mqtt_cmd(cmd=command, msg=msg)

    def handle_mqtt_cmd(self, cmd: str, msg: MQTTMessage):
        msg_dct: dict = json.loads(msg.payload)
        req_id = msg_dct["id"]
        if cmd == "get_all":
            self.logger.error("printing tags to mqtt")
            self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "payload": {"status": "success", "tags": self.tags}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

        else:
            self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "payload": {"status": "error", "msg": "did not find any fitting command for your request"}}))
            return