# Тестовий режим
TEST_MODE = False

internal_link = "🔗" # Что ставить вместо внутренней ссылки Telegram
external_link = "🔗" # Что ставить вместо внешней ссылки (на сайты)
bad_word = "🤬" # Что ставить вместо плохих слов
# Лучше ставить емодзи или какой-то один символ.


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

