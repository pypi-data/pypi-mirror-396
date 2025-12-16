from .constnum import NUMBER


class STRUCT:
    EMPTY_LIST = []
    EMPTY_DICT = dict()


class SLICE:
    FIRST_ITEM = slice(None, NUMBER.ONE)        # e.g., assert [0, 1, 3, 5][SLICE.FIRST_ITEM] == [0]
    LAST_ITEM = slice(-NUMBER.ONE, None)        # e.g., assert [0, 1, 3, 5][SLICE.LAST_ITEM] == [5]

    GET_FIRST = slice(None, NUMBER.ONE)        # e.g., assert [0, 1, 3, 5][SLICE.GET_FIRST] == [0]
    GET_LAST = slice(-NUMBER.ONE, None)        # e.g., assert [0, 1, 3, 5][SLICE.GET_LAST] == [5]

    # e.g., lst = [0, 1, 3, 5]; assert lst[SLICE.EVERYTHING] == lst and id(lst[SLICE.EVERYTHING] != id(lst)
    EVERYTHING = slice(None, None)

    SKIP_FROM_FIRST = slice(NUMBER.ONE, None)           # e.g., assert [0, 1, 3, 5][SLICE.SKIP_FROM_FIRST] == [1, 3, 5]
    SKIP_FROM_SECOND = slice(NUMBER.TWO, None)          # e.g., assert [0, 1, 3, 5][SLICE.SKIP_FROM_SECOND] == [3, 5]
    SKIP_FROM_THIRD = slice(NUMBER.THREE, None)         # e.g., assert [0, 1, 3, 5][SLICE.SKIP_FROM_THIRD] == [5]
    TAKE_TO_LAST = slice(None, -NUMBER.ONE)             # e.g., assert [0, 1, 3, 5][SLICE.TAKE_TO_LAST] == [0, 1, 3]
    TAKE_TO_SECOND_LAST = slice(None, -NUMBER.TWO)      # e.g. assert [0, 1, 3, 5][SLICE.TAKE_TO_SECOND_LAST] == [0, 1]
    TAKE_TO_THIRD_LAST = slice(None, -NUMBER.THREE)     # e.g. assert [0, 1, 3, 5][SLICE.TAKE_TO_THIRD_LAST] == [0]

    # e.g., assert '01234567'[SLICE.FIRST_TO_LAST] == '123456'
    FIRST_TO_LAST = slice(NUMBER.ONE, -NUMBER.ONE)
    # e.g., assert '01234567'[SLICE.SECOND_TO_SECOND_LAST] == '2345'
    SECOND_TO_SECOND_LAST = slice(NUMBER.TWO, -NUMBER.TWO)
    # e.g., assert e.g. '01234567'[SLICE.THIRD_TO_THIRD_LAST] == '4'
    THIRD_TO_THIRD_LAST = slice(NUMBER.THREE, -NUMBER.THREE)
