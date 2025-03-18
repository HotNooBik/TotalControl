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
        goal: цель ("lose_weight", "gain_muscle", "cutting");

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


def get_users_pfc_norm(calories: int, goal: str) -> tuple[(int, int, int)]:
    """
    Функция для расчёта дневной нормы БЖУ в граммах.

    Для расчета используется формула, основанная на кол-ве калорий и цели пользователя.

    Args:
        calories: дневная норма калорий;
        goal: цель ("lose_weight", "gain_muscle", "cutting");

    Returns:
        Дневную норму БЖУ tuple(кол-во белков в гр (int), кол-во жиров в гр (int), кол-во углеводов в гр (int))
    """

    match goal:
        case "lose_weight":
            protein = round(calories * 0.3 / 4)
            fat = round(calories * 0.25 / 9)
            carbs = round(calories * 0.45 / 4)
        case "gain_muscle":
            protein = round(calories * 0.25 / 4)
            fat = round(calories * 0.2 / 9)
            carbs = round(calories * 0.55 / 4)
        case "cutting":
            protein = round(calories * 0.35 / 4)
            fat = round(calories * 0.25 / 9)
            carbs = round(calories * 0.40 / 4)
        case _:
            protein = round(calories * 0.25 / 4)
            fat = round(calories * 0.25 / 9)
            carbs = round(calories * 0.5 / 4)

    return (protein, fat, carbs)


def get_users_water_norm(
    sex: str,
    weight: float,
    height: float,
    activity_coef: float,
    goal: str,
) -> int:
    """
    Функция для расчета нормы воды пользователя (в мл)
    Минимальная норма воды - 1500 мл.

    Args:
        sex: пол;
        weight: Вес в кг;
        heigh: Рост в см;
        activity_coef: коэффициент активности;
        goal: цель ("lose_weight", "gain_muscle", "cutting");

    Returns:
        Дневную норму воды (int)
    """
    match goal:
        case "lose_weight":
            goal_coef = 1.2
        case "gain_muscle":
            goal_coef = 1.1
        case _:
            goal_coef = 1

    if sex == "man":
        amount_of_water = (
            (weight * 35 + max(height - 170, 0) * 10)
            * goal_coef
            * (activity_coef - 0.35)
        )
    else:
        amount_of_water = (
            (weight * 30 + max(height - 170, 0) * 10)
            * goal_coef
            * (activity_coef - 0.35)
        )

    return int((amount_of_water // 100) * 100) if amount_of_water > 1500 else 1500
