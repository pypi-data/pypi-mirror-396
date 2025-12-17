import json
import base64
from datetime import datetime
from typing import Dict

PUBSUB_UID = 'pubsub@arcane.run'


def myconverter(o):
    if isinstance(o, datetime):
        return o.strftime('%Y-%m-%dT%H:%M:%SZ')


def pubsub_json_message_encoder(parameters: dict) -> str:
    """ Encodes a dictionary to a Base64 string """
    return base64.b64encode(json.dumps(parameters, default=myconverter).encode('utf-8')).decode('utf-8')


def pubsub_json_message_decoder(message_data: str) -> dict:
    """ Decodes a Base64 string to a dictionary """
    return json.loads(base64.b64decode(message_data).decode('utf-8'))


def build_json_message(message_data: Dict) -> Dict:
    return {'data': pubsub_json_message_encoder({'parameters': message_data})}


def pubsub_string_message_encoder(message: str) -> str:
    """ Encodes a string to a Base64 string """
    return base64.b64encode(message.encode('utf-8')).decode('utf-8')


def pubsub_string_message_decoder(message_data: str) -> str:
    """ Encodes a string to a Base64 string """
    return base64.b64decode(message_data).decode('utf-8')
