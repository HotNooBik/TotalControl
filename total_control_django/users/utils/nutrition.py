"""Модуль для расчёта нормы КБЖУ и нормы выпитой воды пользователя, на основании его данных"""

from datetime import date
from users.utils.age_calculator import calculate_age


def get_users_calorie_norm(
    sex: str,
    weight: float,
    height: float,
    birth_date: date,
    activity_coef: float,
    goal: str,
) -> int:
    """
    Функция для расчёта дневной нормы калорий пользователя.

    В качестве основной формулы для расчёта выступает формула Миффлин-Сен Жеора, в которой
    учитывается вес (в кг), рост (в см) и возраст человека, затем полученный результат умножается
    на коэффициент активности. Далее полученная норма калорий изменяется в зависимости от цели
    пользователя (похудение, набор массы, поддержание формы или сушка).

    Args:
        sex: пол;
        weight: Вес в кг;
        heigh: Рост в см;
        birth_date: дата рождения (date объект);
        activity_coef: коэффициент активности;
        goal: цель ();

    Returns:
        Дневную норму калорий (int)
    """

    # bmr - норма калорий по формуле
    bmr = 10 * weight + 6.25 * height - 5 * calculate_age(birth_date)

    if sex == "man":
        bmr += 5
    else:
        bmr -= 161

    match goal:
        case "lose_weight":
            bmr *= 0.85
        case "gain_muscle":
            bmr *= 1.15
        case "cutting":
            bmr *= 0.9

    return int(bmr * activity_coef)


def get_users_pfc_norm():
    return ()


def get_users_water_norm():
    return
