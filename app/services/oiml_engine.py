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

def evaluate_discrimination(reading_before, reading_after, additional_weight, d):
    """
    OIML R-76-1:2006 Section 3.6.3 / T.4.2:
    The discrimination threshold is the smallest additional load
    that, when gently added, causes a perceptible change in
    indication. Pass condition: the added weight is small enough
    to be a valid threshold test (<= 1.4d) AND the instrument
    actually registered a visible change (>= d).
    """
    if d <= 0:
        return None
    threshold_required = 1.4 * d
    change_detected = abs(reading_after - reading_before) >= d
    weight_within_threshold = additional_weight <= threshold_required
    status = 'PASS' if (change_detected and weight_within_threshold) else 'FAIL'
    return {
        'threshold_required': round(threshold_required, 3),
        'actual_change': round(abs(reading_after - reading_before), 3),
        'change_detected': change_detected,
        'status': status
    }
