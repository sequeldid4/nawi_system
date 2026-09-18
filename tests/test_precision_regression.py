import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.oiml_engine import get_mpe, check_repeatability, format_to_instrument_precision

def test_repeatability_precision_bug():
    # Repro case context
    accuracy_class = 'I'
    e = 0.001
    load = 10
    readings = [9.99, 9.9995, 9.99]
    
    # 1. Check MPE
    mpe_limit = get_mpe(load, e, accuracy_class)
    assert mpe_limit == 0.0005, f"Expected MPE 0.0005, got {mpe_limit}"
    
    # 2. Check Pass/Fail logic (using raw floats)
    status = check_repeatability(readings, mpe_limit)
    assert status == "FAIL", f"Expected FAIL, got {status}"
    
    # 3. Check formatted Max Diff
    raw_max_diff = max(readings) - min(readings)
    formatted_max_diff = format_to_instrument_precision(raw_max_diff, e)
    
    # e=0.001 has 3 decimals, +1 = 4 decimals target precision
    # 9.9995 - 9.99 = 0.0095
    # Expect "0.0095" exactly
    assert formatted_max_diff == "0.0095", f"Expected '0.0095', got {formatted_max_diff}"
    
    print("ALL TESTS PASSED: Precision regression verified.")

if __name__ == '__main__':
    test_repeatability_precision_bug()
