# This file contains a drop-in replacement for Python2's "Banker" rounding.
from decimal import Decimal, getcontext, ROUND_HALF_UP
context = getcontext()
context.rounding = ROUND_HALF_UP


def round2(value, digits=0):
    return float(Decimal(value).__round__(digits))
