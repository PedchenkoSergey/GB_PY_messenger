import sys
import os
import unittest
import json
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import Connector


class TestSocket:
    def __init__(self, test_message):
        self.test_message = test_message
        self.enc_message = None
        self.rec_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_message)
        self.enc_message = json_test_message.encode(ENCODING)
        self.rec_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_message)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.test_message_send = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        self.test_message_rec_ok = {RESPONSE: 200}
        self.test_message_rec_err = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def test_send_message(self):
        test_socket = TestSocket(self.test_message_send)
        Connector(test_socket).send_message(self.test_message_send)
        self.assertEqual(test_socket.enc_message, test_socket.rec_message)
        with self.assertRaises(Exception):
            Connector(test_socket).send_message(test_socket)

    def test_get_message(self):
        test_sock_ok = TestSocket(self.test_message_rec_ok)
        test_sock_err = TestSocket(self.test_message_rec_err)
        self.assertEqual(Connector(test_sock_ok).get_message(), self.test_message_rec_ok)
        self.assertEqual(Connector(test_sock_err).get_message(), self.test_message_rec_err)


if __name__ == '__main__':
    unittest.main()
