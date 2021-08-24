import json
from common.variables import MAX_PACKET_LENGTH, ENCODING


class Connector:
    def __init__(self, sock):
        self.sock = sock

    def get_message(self):
        encoded_response = self.sock.recv(MAX_PACKET_LENGTH)
        if isinstance(encoded_response, bytes):
            json_response = encoded_response.decode(ENCODING)
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError
        raise ValueError

    def send_message(self, message):
        js_message = json.dumps(message, ensure_ascii=False)
        encoded_message = js_message.encode(ENCODING)
        self.sock.send(encoded_message)
