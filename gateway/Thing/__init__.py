import paho.mqtt.client as mqtt
import settings
import re
import json

def on_message(client, userdata, message):
    """Wrapper for the paho on_message function.
    The excpected format of an command payload is as follows:
        payload = '[{"Time" : "%f","Command": "get_config_from_sensor", "MAC" : "F0:CB:45:2B:51:0B"}]'
    Message will be converted as dictionary.
    settings.Queue is a global queue to handle the incomming commands and share the commands with
    other modules and threads.
    """
    msg_decode = message.payload.decode("utf-8")
    msg_decode = re.findall("\[(.*?)\]", msg_decode)[0]
    msg_decode = json.loads(msg_decode)
    try:
        settings.ComQueue.put([msg_decode['Command'],msg_decode['MAC']])
    except:
        print(msg_decode)
        print("Failure while decoding")
    
def on_disconnect(client, userdata, rc):
    """Reconnects the thing to the broker if the disconnect happened on accident.
    """
    if rc != 0:
        client.reconnect()
        return "Unexpected disconnection."

def on_publish(client,userdata,result):            
    print("data published \n")
    
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print(userdata, mid)



class Thing:
    """
    A class that represents a thing from mqtt.

    The is a wrapper for certain functions of the phao.mqtt module regarding things.
    A thing in mqtt can be a sensor for example. This sensor need to publish its data
    to a broker.
    This class aims to make it easy create a new client, and publish messages to the
    broker.

    Methods
    connect_to_broker(address)
    set_username_userpassword(username, password)
    pub_to_channel(topic, payload)
    disconnect_from_broker()
    reset_to_factory()

    """

    def __init__(self, username, password):
        """Creates a new phao-client."""
        # self.thing_id = thing_id
        # self.thing_key = thing_key
        self.client = mqtt.Client(client_id='', clean_session=True, userdata=None, transport='tcp')
        self.client.username_pw_set(username=username, password=password)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.on_publish = on_publish
        self.client.on_subscribe = on_subscribe
        self.address = ''

    def connect_to_broker(self, address: str):
        """Wrapper for the paho connect method.

        Connects the thing to the broker. Then calls the phao loop_start-method.

        Args
        address: str
            Hostname or ip of the broker
        """
        self.address = address
        self.client.connect(address)
        self.client.loop_start()

    def pub_to_channel(self, topic: str, payload: str, subtopic=None):
        """Wrapper for the paho publish method.

        Causes the message to be published to a broker and all from there to be send to all devices subscribed to it.

        Args
        topic: str
            The topic/channel the message should be published to
        payload: str
            The contents of the message
        """
        if subtopic is not None:
            topic += "/" + subtopic
        return self.client.publish(topic=topic, payload=payload)

    def disconnect_from_broker(self):
        """Wrapper for the phao disconnect method.

        Disconnects the client/Thing from the broker.
        """
        self.client.disconnect()

    def sub_to_channel(self, topic, qos):
        """Wrapper for the paho subscribe method.

            Subscribe the client to one or more topics.

            Args
                topic: The Topic to which to subscribe
                qos: Quality of service level default = 0
        """
        return self.client.subscribe(topic, qos=0)

    def reset_to_factory(self):
        """Wrapper for the paho reinitialise method

        resets the client/Thing to its starting state i.e. as if it was freshly created."""
        self.client.reinitialise()
