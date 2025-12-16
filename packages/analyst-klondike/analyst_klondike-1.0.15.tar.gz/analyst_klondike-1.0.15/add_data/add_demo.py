def get_palindroms(words: list[str]) -> list[list[str] | str]:
    """
        Группировка палиндромов
        Написать функцию, которая группирует слова-палиндромы вместе.
        Например для списка слов ['eat','tea','the','teh','hte','abc','edf'] функция должна вернуть
        [['eat','tea'], ['the','teh','hte'], 'abc','edf'].
        Два слова являются палиндромами если они состоят из одних и тех же букв, но в разном порядке.
    """
    return []


assert get_palindroms(['eat', 'tea', 'the', 'teh', 'hte', 'abc', 'edf']) == [
    ['eat', 'tea'], ['the', 'teh', 'hte'], 'abc', 'edf']


def get_substrings(subs: str, long_string: str) -> list[int]:
    """
        Поиск подстрок
        Написать функцию, которая принимает строку subs и строку long_string.
        Функция вернет список индексов всех вхождений подстроки subs в строке long_string. 
        Номера позиций начинаются с нуля.
        Например:
         - подстрока "hello" встречается в строке "hello, world, all people hello" два раза: на позиции 0 (начало строки) и 25.
         - подстрока "xyz" встречается в строке "abc def xyz ghr" один раз на позиции 8.
        Таким образом:
         - solution("hello, world, all people hello") -> [0, 25]
         - solution("xyz", "abc def xyz ghr") -> [8]
         - solution("", "my string") -> [] (для пустой строки вернет пустой список)
         - solution("hello", "ok, great!") -> [] (нет вхождений)
    """
    return []


assert get_substrings("abc", "_abc_abc") == [1, 5]
assert get_substrings("hello", "hello world hello") == [0, 12]
assert get_substrings("xyz", "abc def xyz ghr") == [8]
