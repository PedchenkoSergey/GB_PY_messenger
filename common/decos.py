import functools
import inspect
import logging
import sys
import traceback

if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    LOGGER = logging.getLogger('app.server')
else:
    # ну, раз не сервер, то клиент
    LOGGER = logging.getLogger('app.client')


# Реализация в виде класса для функции
class Log:
    """Класс-декоратор"""
    def __call__(self, cls):
        def decorate(func_log):
            def log_saver(*args, **kwargs):
                """Обертка"""
                LOGGER.debug(f'Была вызвана функция {func_log.__name__} c параметрами args={args}, kwargs={kwargs}. '
                             f'Вызов из модуля {func_log.__module__}. Вызов из'
                             f' объекта {traceback.format_stack()[0].strip().split()[-1]}.'
                             f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
                return_value = func_log(*args, **kwargs)
                return return_value

            return log_saver

        cls.__init__ = decorate(cls.__init__)
        cls.process_client_message = decorate(cls.process_client_message)
        return cls


# Реализация в виде функции
def log(func_log):
    """Функция-декоратор"""
    @functools.wraps(func_log)
    def log_saver(*args, **kwargs):
        """Обертка"""
        LOGGER.debug(f'log-func: Была вызвана функция {func_log.__name__} c параметрами args={args}, kwargs={kwargs}. '
                     f'Вызов из модуля {func_log.__module__}. Вызов из'
                     f' объекта {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return_value = func_log(*args, **kwargs)
        return return_value
    return log_saver
