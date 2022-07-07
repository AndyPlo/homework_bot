"""
Бот для Telegram.

Передает в чат информацию о статусе домашней работы ЯндексПрактикум.
"""

import os
import sys
import logging
import requests
import time
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
homework_status_cache = {}
last_message_cache = ''

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def logger_error(bot, message):
    """Логирует ошибку и отправляет сообщение."""
    logger.error(message)
    global last_message_cache
    if message != last_message_cache:
        send_message(bot, message)
        last_message_cache = message


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение отправлено: {message}')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к API ЯндексПрактикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return (response.json() if response.status_code == 200
            else response.status_code)


def check_response(response):
    """Возвращает список домашних работ."""
    homeworks = response.get('homeworks')
    return None if homeworks is None else homeworks


def parse_status(homework):
    """Получает статус домашней работы."""
    global homework_status_cache
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict is not None:
        if homework_status != homework_status_cache.get(homework_name):
            homework_status_cache[homework_name] = homework_status
            return (f'Изменился статус проверки работы "{homework_name}". '
                    f'{verdict}')
        logger.debug(f'Статус работы "{homework_name}" не изменился')
        return
    logger_error(
        Bot(token=TELEGRAM_TOKEN),
        f'Неизвестный статус "{homework_status}" у работы "{homework_name}"'
    )


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return True if (PRACTICUM_TOKEN
                    and TELEGRAM_TOKEN
                    and TELEGRAM_CHAT_ID) else False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise logger.critical('Отсутствуют обязательные переменные окружения!')
    bot = Bot(token=TELEGRAM_TOKEN)
    send_message(bot, '--- Бот запущен ---')
    current_timestamp = int(time.time()) - (20 * 24 * 60 * 60)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if type(response) == int:
                message = (f'Проблема с доступом к {ENDPOINT}. '
                           f'Код ответа: {response}')
                logger_error(bot, message)
                time.sleep(RETRY_TIME)
                continue
            homeworks = check_response(response)
            if homeworks is None:
                message = 'В ответе API  отсутствует ключ "homeworks"'
                logger_error(bot, message)
                time.sleep(RETRY_TIME)
                continue
            for homework in homeworks:
                message = parse_status(homework)
                if message:
                    send_message(bot, message)
            current_timestamp = int(time.time()) - (20 * 24 * 60 * 60)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger_error(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
