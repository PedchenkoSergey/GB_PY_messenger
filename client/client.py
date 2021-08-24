import argparse
import logging
import sys
import socket
import threading
import time
import json
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, \
    DEFAULT_PORT, STATUS, AUTHENTICATE, MESSAGE, TO, FROM, ENCODING_FIELD, ENCODING, SENDER, MESSAGE_TEXT, EXIT
from common.utils import Connector
from logs.conf import conf_log_client
from common.decos import Log, log


class Client:
    CLIENT_LOG = logging.getLogger('app.client')

    @log
    def argsParser(self, arguments=None):
        """Парсер аргументов коммандной строки"""
        """Создаём парсер аргументов коммандной строки
            и читаем параметры, возвращаем 3 параметра
            """
        if arguments is None:
            arguments = []

        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, nargs='?')
        argument_parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        argument_parser.add_argument('-n', '--name', default=None, nargs='?')
        namespace = argument_parser.parse_args(sys.argv[1:])
        server_address = namespace.a
        server_port = namespace.p
        client_name = namespace.name

        # проверка получения корретного номера порта для работы сервера.
        if not 1023 < server_port < 65536:
            self.CLIENT_LOG.critical(
                f'Попытка запуска сервера с указанием неподходящего порта '
                f'{server_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

        return server_address, server_port, client_name

    @log
    def __init__(self, arguments=[]):
        # Первый вариант проверки аргументов запуска
        # try:
        #     self.server_address = arguments[1]
        #     self.server_port = int(arguments[2])
        #     if self.server_port < 1024 or self.server_port > 65535:
        #         Client.CLIENT_LOG.error(
        #             'В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        #         raise ValueError
        # except IndexError:
        #     self.server_address = DEFAULT_IP_ADDRESS
        #     self.server_port = DEFAULT_PORT
        # except ValueError:
        #     # print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        #     sys.exit(1)
        #
        # Client.CLIENT_LOG.debug(f'Запущен клиент для связи с сервером по адресу: {self.server_address} '
        #                         f'и порту:{self.server_port}')

        self.server_address, server_port, self.client_name = self.argsParser(arguments)

        if not self.client_name:
            self.client_name = input('Введите имя клиента: ')

        self.SERVER_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.server_address, server_port, self.client_name)
        self.SERVER_SOCK.connect((self.server_address, server_port))

        self.connector = Connector(self.SERVER_SOCK)

        Client.CLIENT_LOG.info(
            f'Запущен клиент с парамертами: адрес сервера: {self.server_address}, '
            f'порт: {server_port}, имя клиента: {self.client_name}')

        self.receiver = threading.Thread(
            target=self.read_message_from_server,
            args=(), daemon=True
        )

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        self.user_interface = threading.Thread(
            target=self.user_interactive,
            args=(), daemon=True
        )

        self.client_working()

    @log
    def create_message(self):
        """Функция запрашивает текст сообщения и возвращает его.
            Так же завершает работу при вводе подобной комманды
            """
        account_name = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки или \'~\' для завершения работы: ')
        if message == '~':
            self.SERVER_SOCK.close()
            Client.CLIENT_LOG.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        out = {
            ACTION: MESSAGE,
            TIME: int(time.time()),
            TO: account_name,
            FROM: self.client_name,
            ENCODING_FIELD: ENCODING,
            MESSAGE_TEXT: message,
        }
        Client.CLIENT_LOG.debug(f'Сформировано {out} сообщение для пользователя {account_name}')
        try:
            self.connector.send_message(out)
            Client.CLIENT_LOG.info(f'Отправлено сообщение для пользователя {account_name}')
        except:
            Client.CLIENT_LOG.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @log
    def create_presence(self):
        out = {
            ACTION: PRESENCE,
            TIME: int(time.time()),
            USER: {
                ACCOUNT_NAME: self.client_name,
                STATUS: "Yep, I am here!"
            }
        }
        Client.CLIENT_LOG.debug(f'Сформировано {PRESENCE} сообщение для пользователя {self.client_name}')
        return out

    @log
    def create_authenticate(account_name='Guest'):
        out = {
            ACTION: AUTHENTICATE,
            TIME: int(time.time()),
            USER: {
                ACCOUNT_NAME: account_name,
                STATUS: "Yep, I am here!"
            }
        }
        Client.CLIENT_LOG.debug(f'Сформировано {AUTHENTICATE} сообщение для пользователя {account_name}')

        return out

    @log
    def process_response_answer(message):
        Client.CLIENT_LOG.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        elif AUTHENTICATE in message:
            if message[AUTHENTICATE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    @log
    def read_message_from_server(self):
        """Функция - обработчик сообщений от других пользователей, поступающих с сервера"""
        while True:
            try:
                message = self.connector.get_message()
                if ACTION in message and message[ACTION] == MESSAGE and \
                        FROM in message and TO in message \
                        and MESSAGE_TEXT in message and message[TO] == self.client_name:
                    print(f'\nПолучено сообщение от пользователя {message[FROM]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    Client.CLIENT_LOG.info(f'Получено сообщение от пользователя {message[FROM]}:'
                                           f'\n{message[MESSAGE_TEXT]}')
                else:
                    Client.CLIENT_LOG.error(f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                Client.CLIENT_LOG.critical(f'Потеряно соединение с сервером.')
                break

    @log
    def user_interactive(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.connector.send_message(self.create_exit_message())
                print('Завершение соединения.')
                Client.CLIENT_LOG.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @log
    def print_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')
        # print(f'Актуальный статус соединения: {self.receiver.is_alive()}  {self.user_interface.is_alive()}')

    @log
    def create_exit_message(self):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_name
        }

    def client_working(self):
        # Инициализация сокета и сообщение серверу о нашем появлении
        # Пробуем установить подключение к серверу:
        try:
            presence_message = self.create_presence()
            Client.CLIENT_LOG.debug(f'Сформировано сообщение для передачи серверу: {presence_message}')
            self.connector.send_message(presence_message)
            answer_from_server = self.connector.get_message()
            answer_from_server_processed = Client.process_response_answer(answer_from_server)
            Client.CLIENT_LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer_from_server_processed}')
            print(f'Установлено соединение с сервером.')
        except ConnectionResetError:
            Client.CLIENT_LOG.error(f'[WinError 10054] Удаленный хост принудительно разорвал существующее '
                                    f'подключение к серверу: {self.server_address}')
            sys.exit(1)
        except ConnectionRefusedError:
            Client.CLIENT_LOG.error(f'[WinError 10061] Подключение не установлено, т.к. конечный компьютер '
                                    f'отверг запрос на подключение: {self.server_address}')
            sys.exit(1)
        except json.JSONDecodeError:
            Client.CLIENT_LOG.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # начинаем обмен с ним, согласно требуемому режиму.
            # основной цикл прогрммы:
            # Код, когда мы запускаем клиент в режиме отправки или приема сообщений:
            # if self.client_mode == 'send':
            #     print('Режим работы - отправка сообщений.')
            # else:
            #     print('Режим работы - приём сообщений.')
            # while True:
            #     # режим работы - отправка сообщений
            #     if self.client_mode == 'send':
            #         try:
            #             Connector(self.SERVER_SOCK).send_message(self.create_message())
            #         except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            #             Client.CLIENT_LOG.error(f'Соединение с сервером {self.server_address} было потеряно.')
            #             sys.exit(1)
            #
            #     # Режим работы приём сообщений:
            #     if self.client_mode == 'listen':
            #         try:
            #             message_from_server = Connector(self.SERVER_SOCK).get_message()
            #             Client.CLIENT_LOG.info(f'Получено сообщение: {message_from_server} от сервера.')
            #             Client.read_message_from_server(message_from_server)
            #         except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            #             Client.CLIENT_LOG.error(f'Соединение с сервером {self.server_address} было потеряно.')
            #             sys.exit(1)
            # Код, когда мы запускаем клиент в режиме приемки/отправки сообщений:

            self.receiver.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.

            self.user_interface.start()
            Client.CLIENT_LOG.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if self.receiver.is_alive() and self.user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    print(sys.argv)
    Client(sys.argv)
