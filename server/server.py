import argparse
import select
import socket
import time

from common.utils import Connector
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, \
    MESSAGE, MESSAGE_TEXT, SENDER, FROM, TO, RESPONSE_200, RESPONSE_400, EXIT
import logging
from logs.conf import conf_log_server
from common.decos import Log, log


@Log()
class Server:

    def argsParser(self, arguments=None):
        """Парсер аргументов коммандной строки"""
        if arguments is None:
            arguments = []

        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument('-a', default='', nargs='?')
        argument_parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        namespace = argument_parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p

        # проверка получения корретного номера порта для работы сервера.
        if not 1023 < listen_port < 65536:
            self.SERVER_LOG.critical(
                f'Попытка запуска сервера с указанием неподходящего порта '
                f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

        return listen_address, listen_port

    def __init__(self, arguments=None):
        if arguments is None:
            arguments = []

        self.SERVER_LOG = logging.getLogger('app.server')
        # Более лаконичный работы через argparse:
        listen_address, listen_port = self.argsParser(arguments)
        # список клиентов , очередь сообщений
        self.clients = []
        self.messages = []
        self.names = dict()

        self.SERVER_LOG.debug((f'Запущен сервер, порт для подключений: {listen_port}, '
                               f'адрес с которого принимаются подключения: {listen_address}. '
                               f'Если адрес не указан, принимаются соединения с любых адресов.'))
        self.SERV_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERV_SOCK.bind((listen_address, listen_port))
        self.SERV_SOCK.listen(MAX_CONNECTIONS)
        self.SERV_SOCK.settimeout(0.5)
        self.server_working()

    def process_client_message(self, message, client):
        # Проверяем, если это сообщение о присутствии, принимаем и отвечаем, если успех
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                Connector(client).send_message(RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                Connector(client).send_message(response)
                self.clients.remove(client)
                self.client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                TIME in message and MESSAGE_TEXT in message and \
                TO in message and FROM in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            Connector(client).send_message(response)
            return

    def process_message(self, message, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        """
        if message[TO] in self.names and self.names[message[TO]] in listen_socks:
            Connector(self.names[message[TO]]).send_message(message)
            self.SERVER_LOG.info(f'Отправлено сообщение пользователю {message[TO]} '
                                 f'от пользователя {message[FROM]}.')
        elif message[TO] in self.names.keys() and self.names[message[TO]] not in listen_socks:
            raise ConnectionError
        else:
            self.SERVER_LOG.error(
                f'Пользователь {message[TO]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def server_working(self):
        while True:
            try:
                CLIENT_SOCK, CLIENT_ADDR = self.SERV_SOCK.accept()
            except OSError:
                pass  # Время ожидания вышло и генерирует ошибку, но мы пропускаем и ждем дальше
            else:
                self.SERVER_LOG.debug(f'Установлено соединение с ПК по адресу: {CLIENT_ADDR}')
                self.clients.append(CLIENT_SOCK)

            # Начинаем работать с несколькими клиентами и информацией от них
            received_data_lst = []
            send_data_lst = []
            error_lst = []
            # Словарь, содержащий имена пользователей и соответствующие им сокеты.
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    received_data_lst, send_data_lst, error_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if received_data_lst:
                for client_with_message in received_data_lst:
                    try:
                        message_from_client = Connector(client_with_message).get_message()
                        self.process_client_message(message_from_client, client_with_message)
                        self.SERVER_LOG.info(f'Список принятых сообщений: {self.messages}')
                    except:
                        self.SERVER_LOG.info(f'Клиент {client_with_message.getpeername()} '
                                             f'отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except Exception:
                    self.SERVER_LOG.info(f'Клиент {message[TO]} отключился от сервера.')
                    self.clients.remove(self.names[message[TO]])
                    del self.names[message[TO]]
            self.messages.clear()


if __name__ == '__main__':
    Server(sys.argv)
