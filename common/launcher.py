"""Модуль запускающий работу сервера и нескольких клиентов"""

import subprocess

PROCESS = []

while True:
    ACTION = input('Выберите действие: quit - выход, '
                   'runserver - запустить сервер и клиенты, stop - закрыть все окна: ')

    if ACTION == 'quit':
        break
    elif ACTION == 'runserver':
        PROCESS.append(subprocess.Popen('python ..\\server\\server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python ..\\client\\client.py -n test1',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python ..\\client\\client.py -n test2',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python ..\\client\\client.py -n test3',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'stop':
        while PROCESS:
            stopping_process = PROCESS.pop()
            stopping_process.kill()


