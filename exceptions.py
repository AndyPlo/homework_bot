"""
Модуль с кастомнымим ошибками для Телеграм-бота.

Вывод для всех ошибок, включая стандартные: Имя класса --> Сообщение.
"""

from telegram import TelegramError

# Переопределяем вывод стандартных ошибок


class TelegramError(TelegramError):
    """Переопределяем __str__ метод TelegramError."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'


class SystemExit(SystemExit):
    """Переопределяем __str__ метод SystemExit."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'


class KeyError(KeyError):
    """Переопределяем __str__ метод KeyError."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'

# Определяем кастомные ошибки


class SendMessageError(Exception):
    """Ошибка: Сбой при отправке сообщения."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'


class EndpointAccessError(Exception):
    """Ошибка: Проблема с доступом к эндпоинт."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'


class HomeworksTypeError(Exception):
    """Ошибка: Не правильный тип ответа API."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'


class HomeworksEmptyError(Exception):
    """Ошибка: Словарь homework пуст."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{self.message}'


class UnknownStatusError(Exception):
    """Ошибка: Неизвестный статус в homework_status."""

    def __init__(self, message):
        """Конструктор класса."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Форматируем вывод сообщения об ошибке."""
        return f'{type(self).__name__} --> {self.message}'
