def get_mpe(load, e, accuracy_class='III', test_type='initial'):
    """
    Calculate Maximum Permissible Errors (MPE) based on OIML R-76 Table 6.
    Uses verification scale interval (e), load, and accuracy class.
    """
    if e <= 0:
        return None
        
    # Calculate number of verification intervals
    m = load / e
    mpe_multiplier = 0.0

    # OIML R-76 Class III Limits
    if accuracy_class == 'III':
        if 0 <= m <= 500:
            mpe_multiplier = 0.5
        elif 500 < m <= 2000:
            mpe_multiplier = 1.0
        elif 2000 < m <= 10000:
            mpe_multiplier = 1.5
        else:
            return None # Out of bounds for Class III
            
    # OIML R-76 Class II Limits (Adding this since it's a common SIH requirement)
    elif accuracy_class == 'II':
        if 0 <= m <= 5000:
            mpe_multiplier = 0.5
        elif 5000 < m <= 20000:
            mpe_multiplier = 1.0
        elif 20000 < m <= 100000:
            mpe_multiplier = 1.5
        else:
            return None

    # In-service field inspections generally double the initial MPE limits
    if test_type == 'in-service':
        mpe_multiplier *= 2

    return mpe_multiplier * e


def check_pass_fail(actual_weight, displayed_weight, mpe):
    """
    Evaluates if the error is within legal limits.
    """
    error = abs(displayed_weight - actual_weight)
    return "PASS" if error <= mpe else "FAIL"

def check_repeatability(readings, mpe):
    """
    OIML R-76: The difference between the maximum and minimum 
    readings for the same load must not exceed the absolute value of the MPE.
    """
    if not readings: return "FAIL"
    max_val = max(readings)
    min_val = min(readings)
    return "PASS" if (max_val - min_val) <= mpe else "FAIL"

def check_eccentricity(actual_weight, readings, mpe):
    """
    OIML R-76: The error at any off-center position must not exceed the MPE.
    """
    for r in readings:
        if abs(r - actual_weight) > mpe:
            return "FAIL"
    return "PASS"
