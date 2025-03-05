"""Модуль для расчета возраста пользователя"""

from datetime import date


def calculate_age(birth_date: date) -> int | None:
    """
    Функция для расчёта возраста пользователя по строке с датой рождения.

    Args:
        birth_date: дата рождения;

    Returns:
        возраст (int)
    """

    today = date.today()

    if birth_date > today:
        return None  # Дата рождения в будущем

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age
