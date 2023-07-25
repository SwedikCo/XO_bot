from random import choice


game_numbers: list[str] = ['']  # список всех номер игр

numbers: list[str] = list(map(str, range(10)))
simbols: list[str] = list(map(chr, range(65, 91)))
mix: list[str] = numbers + simbols  # символы для составления номера игры


def is_new_number(number) -> bool:
    '''Функция проверяет, есть ли такой номер уже или нет.'''
    if number in game_numbers:
        return False
    else:
        return True
    

def get_number() -> str:
    '''Функция генерирует номер игры.'''
    number: str = ''
    while not is_new_number(number):
        number = ''
        for _ in range(7):
            number += choice(mix)
    game_numbers.append(number)
    return number