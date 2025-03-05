import sqlite3
from pathlib import Path

def get_first_birthdate(db_path=Path(__file__).resolve().parent.joinpath("db.sqlite3"), table_name="users_userprofile"):
    """
    Извлекает первую дату рождения из указанной таблицы в базе данных SQLite.

    Args:
        db_path: Путь к файлу базы данных SQLite.
        table_name: Название таблицы.

    Returns:
        Первую дату рождения в формате строки, или None, если таблица пуста или произошла ошибка.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT height FROM {table_name} LIMIT 1")
        result = cursor.fetchone()

        conn.close()

        if result:
            return result[0]  # Возвращаем только значение birth_date
        else:
            return None  # Таблица пуста

    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return None
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return None

# Пример использования:
birthdate = get_first_birthdate()
if birthdate:
    print(f"Первая дата рождения: {type(birthdate)}")
else:
    print("Не удалось получить дату рождения.")