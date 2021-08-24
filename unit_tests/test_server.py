import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR,AUTHENTICATE, STATUS
from server.server import Server


class TestServerClass(unittest.TestCase):
    def setUp(self):
        self.error_response = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

        self.ok_response = {RESPONSE: 200}

        self.presense_message = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {ACCOUNT_NAME: 'Guest'}
        }

        self.authenticate_message = {
            ACTION: AUTHENTICATE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: "Yep, I am here!"
            }
        }

    def tearDown(self):
        # Выполнить завершающие действия (если необходимо)
        pass

    def test_ok_response(self):
        """Корректный запрос"""
        self.assertEqual(Server.process_client_message(
            message=self.presense_message), self.ok_response)

    def test_error_authenticate(self):
        """Запрос с неизвестным параметром"""
        self.assertEqual(Server.process_client_message(
            message=self.authenticate_message), self.error_response)

    def test_no_action_error(self):
        """Запрос без параметра ACTION"""
        self.assertEqual(Server.process_client_message(
            message={TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.error_response)

    def test_no_time_error(self):
        """Запрос без параметра TIME"""
        self.assertEqual(Server.process_client_message(
            message={ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_response)

    def test_no_user_error(self):
        """Запрос без параметра USER"""
        self.assertEqual(Server.process_client_message(
            message={ACTION: PRESENCE, TIME: '1.1'}), self.error_response)

    def test_wrong_user_error(self):
        """Запрос с неверным параметром USER"""
        self.assertEqual(Server.process_client_message(
            message={ACTION: PRESENCE, TIME: '1.1', USER: {ACCOUNT_NAME: 'NON_GUEST'}}), self.error_response)

    def test_no_action_no_time_error(self):
        """Запрос с неверным параметром USER"""
        self.assertEqual(Server.process_client_message(
            message={USER: {ACCOUNT_NAME: 'NON_GUEST'}}), self.error_response)


if __name__ == '__main__':
    unittest.main()
