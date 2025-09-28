def calculate_attention_score(desired_attention, actual_time_on_component, total_test_time):
    
    margine_error = 5

    actual_attention = (actual_time_on_component / total_test_time) * 100
    attention_gap = actual_attention - desired_attention

    # Determine if the actual attention is within the margin of error
    within = abs(attention_gap) <= margine_error

    return {
        "score": attention_gap,
        "within": within,
        "desiredAttention": desired_attention,
        "actualAttention": round(actual_attention, 2),
    }
