# Файл констант

DEFAULT_PORT = 8080
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 10
MAX_PACKET_LENGTH = 4096
ENCODING_FIELD = 'encoding'
ENCODING = 'utf-8'

ACTION = 'action'
EXIT = 'exit'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'

AUTHENTICATE = 'authenticate'
QUIT = 'quit'
PROBE = 'probe'
MESSAGE = 'msg'
JOIN_GROUP = 'join'
LEAVE_GROUP = 'leave'
STATUS = 'status'
LOGGING_LEVEL = 'DEBUG'

MESSAGE_TEXT = 'message_text'
SENDER = 'sender'
TO = 'to'
FROM = 'from'

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}


