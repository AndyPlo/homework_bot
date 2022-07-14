"""
Бот для Telegram.

Передает в чат информацию о статусе домашней работы ЯндексПрактикум.
"""

import os
import sys
import time
import logging
from json import decoder
from http import HTTPStatus

import requests
from telegram import Bot, TelegramError
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuse/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
homework_status_cache = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class CustomException(Exception):
    """Создание своего типа исключения."""

    pass


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение отправлено: {message}')
    except TelegramError as error:
        logger.error(f'Сбой при отправке сообщения: {error}')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к API ЯндексПрактикум."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        raise SystemExit(f'Эндпоинт не доступен: {error}')
    if response.status_code != HTTPStatus.OK:
        raise CustomException(f'Проблема с доступом к {ENDPOINT}. '
                              f'Код ответа: {response.status_code}')
    try:
        return response.json()
    except decoder.JSONDecodeError as error:
        raise decoder.JSONDecodeError(
            f'Ответ API не преобразуется в JSON: {error}'
        )


def check_response(response):
    """Возвращает список домашних работ."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        raise KeyError('Ответ API не содержит ключа "homeworks"')
    if type(homeworks) is not list:
        raise Exception('Ключ "homeworks" не является словарем')
    elif len(homeworks) == 0:
        raise Exception('Словарь "homeworks" пуст')
    return homeworks


def parse_status(homework):
    """Получает статус домашней работы."""
    global homework_status_cache
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Ответ API не содержит ключа "homework_name"')
    homework_status = homework.get('status')
    if homework_status is None:
        raise Exception('Ответ API не содержит ключа "homework_status"')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict is None:
        raise Exception(f'Неизвестный статус "{homework_status}" '
                        f'у работы "{homework_name}"')
    if homework_status != homework_status_cache.get(homework_name):
        homework_status_cache[homework_name] = homework_status
        return (f'Изменился статус проверки работы "{homework_name}". '
                f'{verdict}')
    logger.debug(f'Статус работы "{homework_name}" не изменился')


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return True if (PRACTICUM_TOKEN
                    and TELEGRAM_TOKEN
                    and TELEGRAM_CHAT_ID) else False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise logger.critical('Отсутствуют обязательные переменные окружения. '
                              'Программа остановлена!')
    last_message_cache = ''
    bot = Bot(token=TELEGRAM_TOKEN)
    send_message(bot, '--- Бот запущен ---')
    current_timestamp = int(time.time()) - 1
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                if message:
                    send_message(bot, message)
            current_timestamp = int(time.time()) - 1
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != last_message_cache:
                send_message(bot, message)
                last_message_cache = message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
