
import sys
import csv
import re
from io import StringIO
import requests

from constants import CONSTANTS as CO


# URL до сирого CSV-файлу на GitHub з MCC - Merchant Category Codes
url = "https://raw.githubusercontent.com/greggles/mcc-codes/main/mcc_codes.csv"

response = requests.get(url)
response.raise_for_status()

csv_data = StringIO(response.text)
mcc_codes = list(csv.reader(csv_data))

union_data = []


def extract_csv(filename):
    """Дістати дані з файлу csv"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Повертаємо список рядків
        data = list(reader)
    return data


def create_list_dict(data_report, data_mcc_codes):
    """
    Шукає у двох файлах співпадіння по МСС коду
    якщо знаходить збирає словник:
    \n- назва транзакції
    \n- код МСС
    \n- сума
    \n- опис МСС коду\n
    якщо не знаходить співпадіння збирає словник:
    \n- назва транзакції
    \n- код МСС
    \n- сума
    \n- опис МСС коду - 'Не знайшов співпадіння по "MCC"'
    """
    for row in data_report[1:]:
        name = row[1]
        mcc = row[2]
        amount = row[3]

        found_match = False

        for iteration in data_mcc_codes[1:]:
            mcc_code = iteration[0]

            if mcc == mcc_code:
                create_union_data = {
                    'name': name,
                    'mcc': mcc,
                    'amount': amount,
                    'description': iteration[1]
                }
                union_data.append(create_union_data)
                found_match = True
                break
        if not found_match:
            create_union_data = {
                'name': name,
                'mcc': mcc,
                'amount': amount,
                'description': 'Не має збігу по "MCC"'
            }
            union_data.append(create_union_data)


def space_deleter(text):
    """Delete spase in value"""
    return text.replace(' ', '').lower()


def dot_coma_deleter(text):
    """
    Замінює мінус на плюс, крапку на кому.
    :param text: list
    :return: str
    """
    if isinstance(text, list):
        clear_attr = [re.sub("-", "+", text) for text in text]
        # '.' у регулярних виразах позначає будь-який символ. Тому r"\."
        clear_dot = [re.sub(r"\.", ",", clear)
                     for clear in clear_attr]
        result = ''.join(clear_dot)
    else:
        clear_attr = re.sub("-", "+", text)
        clear_dot = re.sub(r"\.", ",", clear_attr)
        result = ''.join(clear_dot)

    return result


def get_ready_data():
    """Отримує елементи списку по одному за."""
    result = []
    for line in union_data:
        result.append(line)

    return result


def see_ready_data():
    """Отримуємо елементи для відображення"""
    raw_report = []  # Створюємо список для рядків сирого звіту
    for line in get_ready_data():
        raw_report.append(str(line) + "\n")

    # Повертаємо результат як один рядок
    return '\n'.join(raw_report)


def search_union_data(*args):
    """
    Приймати кількість значень і шукати по ним.
    :param args:
    :return:
    """
    pass


def search_in_union_data(*search_keys):
    """
    Шукає в імені чи опису і друкує транзакцію.
    Також може шукати по МСС.
    :param search_keys: tuple, може містити кілька рядків для пошуку.
    :return: None
    """
    found = False

    for i in union_data:
        for search_key in search_keys:
            if (space_deleter(search_key) in space_deleter(i['name'])
                    or space_deleter(search_key) in space_deleter(
                        i['description'])
                    or search_key in i['mcc']
                    or search_key in i['amount']):
                print(i)
                found = True
                # Якщо знайшли збіг, виходимо з внутрішнього циклу.
                break
    if not found:
        print(f"Немає збігів для: {', '.join(search_keys)}.")


def create_data_for_exel():
    """
    Перевіряє збіг по категоріях з CONSTANTS.
    Розподіляє amount по категоріях і виводить дані, придатні для копіювання в Excel.
    """
    # Ініціалізація словника для підрахунку сум за категоріями.
    categories_totals = {key: '' for key in CO.keys()}

    for transaction in union_data:
        found_category = False

        for category, descriptions in CO.items():
            if transaction['description'] in descriptions:

                # Перевіряємо чи транзакція має символ '-'.
                if transaction['amount'][0] == '-':
                    # Додаємо суму витрат до відповідної категорії.
                    categories_totals[category] += transaction['amount']
                    found_category = True
                    break
                else:
                    # Сума додатна.
                    categories_totals['INCOMING'] += '+' + transaction['amount'].replace('.', ',')
                    found_category = True
                    break
        if not found_category:
            # Якщо немає збігу, додаємо до категорії UNKNOWN
            categories_totals['UNKNOWN'] += transaction['amount'] + transaction['description']

    return categories_totals


def report_data_for_exel():
    """Підготовка результату для копіювання в Excel"""
    report = []
    for category, total in create_data_for_exel().items():
        if category == 'INCOMING':
            # print(''.join([category, total]))
            # print(f"\n{category}: {total}")
            report.append(f"\n{category}: {total}")
        else:
            # print(''.join([category, dot_coma_deleter(total)]))
            # print(f"\n{category}: {dot_coma_deleter(total)}")
            report.append(f"\n{category}: {dot_coma_deleter(total)}")

    return '\n'.join(report)


MENU = """
1 - Отримати відформатований звіт
2 - Пошук
3 - Показати сирий звіт 
'q' - exit
"""

function_dict = {
    1: report_data_for_exel,
    2: search_in_union_data,
    3: see_ready_data,
    'q': sys.exit
}

"Money Orders – Wire Transfer"
