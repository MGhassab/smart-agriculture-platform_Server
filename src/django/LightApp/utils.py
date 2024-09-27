from unidecode import unidecode


def replace_farsi_num(string):
    string = unidecode(string)
    replacements_farsi_numbers_to_english = {
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "۰": "0",
    }
    return "".join([replacements_farsi_numbers_to_english.get(c, c) for c in string])
