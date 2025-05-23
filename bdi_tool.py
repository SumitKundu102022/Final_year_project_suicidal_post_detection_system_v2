def calculate_bdi_score(responses):
    """
    Calculates the Beck Depression Inventory (BDI) score based on user responses.
    :param responses: List of 21 integers (0 to 3) corresponding to questionnaire answers.
    :return: Total BDI score (0 to 63) and severity classification.
    """
    if len(responses) != 21:
        raise ValueError("BDI responses must contain exactly 21 values.")
    
    total_score = sum(responses)
    
    # Classify depression severity based on score
    if total_score <= 13:
        severity = "Minimal Depression"
    elif 14 <= total_score <= 19:
        severity = "Mild Depression"
    elif 20 <= total_score <= 28:
        severity = "Moderate Depression"
    else:
        severity = "Severe Depression"
    
    return total_score, severity