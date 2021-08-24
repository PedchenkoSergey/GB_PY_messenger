import os
import sys
import logging
import logging.handlers
from common.variables import LOGGING_LEVEL

# Подготовка имени файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, '../logs/server_log.log')

# Создать логгер - регистратор верхнего уроовня с именем app.server
SERVER_LOG = logging.getLogger('app.server')
# Присваиваем уровень лога из переменной LOGGING_LEVEL=DEBUG
SERVER_LOG.setLevel(LOGGING_LEVEL)

# Создать обработчик для записи в файл
FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
# выводит сообщения с уровнем DEBUG
FILE_HANDLER.setLevel(logging.DEBUG)

# Создать обработчик для записи в поток
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
# выводит сообщения с уровнем ERROR
STREAM_HANDLER.setLevel(logging.ERROR)

# Создаем формат по ТЗ
SRV_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Прислаиваем формат по ТЗ
FILE_HANDLER.setFormatter(SRV_FORMATTER)
STREAM_HANDLER.setFormatter(SRV_FORMATTER)

# Добавляем обработчики в регистратор:
SERVER_LOG.addHandler(FILE_HANDLER)
SERVER_LOG.addHandler(STREAM_HANDLER)

if __name__ == '__main__':
    SERVER_LOG.debug('Тестовое сообщение')  # пишем только в файл
    SERVER_LOG.info('Тестовое сообщение')  # пишем только в файл
    SERVER_LOG.error('Тестовое сообщение')  # Пишем и в файл и в консоль
    SERVER_LOG.critical('Тестовое сообщение')  # Пишем и в файл и в консоль
