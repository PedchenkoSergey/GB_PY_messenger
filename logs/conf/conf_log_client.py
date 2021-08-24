import os
import sys
import logging
import logging.handlers
from common.variables import LOGGING_LEVEL

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '../logs/client_log.log')

# Создать логгер - регистратор верхнего уроовня с именем app.server
CLIENT_LOG = logging.getLogger('app.client')
# Присваиваем уровень лога из переменной LOGGING_LEVEL=DEBUG
CLIENT_LOG.setLevel(LOGGING_LEVEL)

# Создать обработчик для записи в файл
FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
# выводит сообщения с уровнем DEBUG
FILE_HANDLER.setLevel(logging.DEBUG)

# Создать обработчик для записи в поток
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
# выводит сообщения с уровнем ERROR
STREAM_HANDLER.setLevel(logging.ERROR)

# Создаем формат по ТЗ
CLNT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Прислаиваем формат по ТЗ
FILE_HANDLER.setFormatter(CLNT_FORMATTER)
STREAM_HANDLER.setFormatter(CLNT_FORMATTER)

# Добавляем обработчики в регистратор:
CLIENT_LOG.addHandler(FILE_HANDLER)
CLIENT_LOG.addHandler(STREAM_HANDLER)

if __name__ == '__main__':
    CLIENT_LOG.debug('Тестовое сообщение')  # пишем только в файл
    CLIENT_LOG.info('Тестовое сообщение')  # пишем только в файл
    CLIENT_LOG.error('Тестовое сообщение')  # Пишем и в файл и в консоль
    CLIENT_LOG.critical('Тестовое сообщение')  # Пишем и в файл и в консоль
