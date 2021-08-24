import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    AUTHENTICATE, STATUS
from client.client import Client


class TestClientClass(unittest.TestCase):
    def setUp(self) -> None:
        self.ok_dict = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: "Yep, I am here!"
            }
        }

    def test_presense_ok(self):
        test_presence_message = Client.create_presence('Guest')
        test_presence_message[TIME] = 1.1
        self.assertEqual(test_presence_message, {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: "Yep, I am here!"
            }
        })

    def test_presense_err(self):
        """Тетсимруем, что функция не генерирует неправильное сообщение PRESENCE"""
        test_presence_message = Client.create_presence()
        test_presence_message[TIME] = 1.1
        self.assertNotEqual(test_presence_message, {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'NON_USER',
                STATUS: "Yep, I am here!"
            }
        })

    def test_authinticate_ok(self):
        test_authinticate_message = Client.create_authenticate('Guest')
        test_authinticate_message[TIME] = 1.1
        self.assertEqual(test_authinticate_message, {
            ACTION: AUTHENTICATE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: "Yep, I am here!"
            }
        })

    def test_authinticate_err(self):
        """Тетсимруем, что функция не генерирует неправильное сообщение AUTHENTICATE"""
        test_authinticate_message = Client.create_authenticate()
        test_authinticate_message[TIME] = 1.1
        self.assertNotEqual(test_authinticate_message, {
            ACTION: AUTHENTICATE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'NON_USER',
                STATUS: "Yep, I am here!"
            }
        })

    def test_process_ans_return_200(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(Client.process_ans({RESPONSE: 200}), '200 : OK')

    def test_process_ans_return_400(self):
        """Тест корректного разбора 400"""
        self.assertEqual(Client.process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_process_ans_return_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, Client.process_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
