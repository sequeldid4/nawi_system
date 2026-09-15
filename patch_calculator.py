import re

with open('app/services/oiml_engine.py', 'r') as f:
    content = f.read()

val_func = """
def validate_instrument_class(max_cap, min_cap, e, acc_class):
    n = max_cap / e
    limits = {
        'I':    (50000, float('inf'), 100 * e),
        'II':   (100, 100000,         20 * e),
        'III':  (100, 10000,          20 * e),
        'IIII': (100, 1000,           10 * e),
    }
    n_min, n_max, min_required = limits[acc_class]
    return {
        'n': n,
        'n_valid': n_min <= n <= n_max,
        'min_valid': min_cap >= min_required, # I'll use >= because it's mathematically correct for a LOWER limit
        'min_required': min_required,
        'n_min': n_min,
        'n_max': n_max
    }
"""

if "def validate_instrument_class" not in content:
    with open('app/services/oiml_engine.py', 'a') as f:
        f.write(val_func)

