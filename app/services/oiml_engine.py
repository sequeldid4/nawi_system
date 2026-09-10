def get_mpe(load, e, accuracy_class='III'):
    """
    Calculate Maximum Permissible Errors (MPE).
    Uses verification scale interval (e) and accuracy class.
    """
    # Calculate number of verification intervals
    m = load / e

    # If-else lookup rules for Class III (Standard industrial/retail NAWI)
    if accuracy_class == 'III':
        if 0 <= m <= 500:
            return 1.0 * e
        elif 500 < m <= 2000:
            return 2.0 * e
        elif 2000 < m <= 10000:
            return 3.0 * e
        return None

    # Placeholder for Classes I, II, and IIII
    return None

def check_pass_fail(actual_weight, displayed_weight, mpe):
    """
    Evaluates if the error is within legal limits.
    """
    error = abs(displayed_weight - actual_weight)
    return "PASS" if error <= mpe else "FAIL"

if __name__ == "__main__":
    # Terminal test case: 1000g load, 1g verification scale interval (e)
    test_load = 1000
    e_value = 1

    mpe_limit = get_mpe(test_load, e_value, 'III')

    print(f"Calculated MPE: {mpe_limit}g")

    # Simulate reading a live weight of 999g (1g error)
    result_1 = check_pass_fail(test_load, 999, mpe_limit)
    print(f"Reading 999g (1g error): {result_1}")

    # Simulate reading a live weight of 997g (3g error)
    result_2 = check_pass_fail(test_load, 997, mpe_limit)
    print(f"Reading 997g (3g error): {result_2}")

