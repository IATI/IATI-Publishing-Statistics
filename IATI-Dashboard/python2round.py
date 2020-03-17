# This file contains a drop-in replacement for Python2's "Banker" rounding.
from decimal import Decimal, getcontext, ROUND_HALF_UP
context = getcontext()
context.rounding = ROUND_HALF_UP


def round2(value, digits=0):
    value_dec = Decimal(value)
    if digits == 0:
        return int(value_dec.__round__(0))
    return value_dec.__round__(digits)
