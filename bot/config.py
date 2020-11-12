# Тестовий режим
TEST_MODE = False

# Авторизаційні дані
if not bool(TEST_MODE):
    TOKEN = 'тут токен бота'
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASS = 'root'
    DB_NAME = 'bot'
elif bool(TEST_MODE):
    TOKEN = ''
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASS = 'root'
    DB_NAME = 'bot'

