# -------------------------------
# Function to compute ranking difference
# -------------------------------
def calculate_ranking_score(expected_priorities, actual_times):
    """
    Compare actual times ranking vs expected priorities ranking.
    Returns a dictionary with ranking difference for each element.
    """
    # Sort actual times descending (highest attention first)
    sorted_actual = sorted(actual_times.items(), key=lambda x: x[1], reverse=True)
    sorted_selectors = [sel for sel, _ in sorted_actual]

    # Sort expected priorities ascending (1 = highest priority)
    expected_sorted = sorted(expected_priorities.items(), key=lambda x: x[1])
    expected_selectors = [sel for sel, _ in expected_sorted]

    ranking_scores = {}
    for selector in sorted_selectors:
        actual_rank = sorted_selectors.index(selector) + 1
        expected_rank = expected_selectors.index(selector) + 1
        ranking_scores[selector] = actual_rank - expected_rank  # positive = actual lower than expected
    return ranking_scores

# -------------------------------
# Dataset
# -------------------------------
expected_priorities = {
    "div.main-page-responsive-columns.main-page-first-row": 1,
    "div.main-page-responsive-columns.main-page-second-row": 2,
    "div.main-page.main-page-third-row > div:nth-of-type(1) > div:nth-of-type(2)": 3,
    "#firstHeading": 4,
    "div.minerva-header": 5
}

actual_times = {
    "div.main-page-responsive-columns.main-page-first-row": 38,
    "div.main-page-responsive-columns.main-page-second-row": 24,
    "div.main-page.main-page-third-row > div:nth-of-type(1) > div:nth-of-type(2)": 15,
    "#firstHeading": 11,
    "div.minerva-header": 9
}

# -------------------------------
# Build clean dataset for GemSuggest
# -------------------------------
attention_data = []
ranking_scores = calculate_ranking_score(expected_priorities, actual_times)

for selector, desired_priority in expected_priorities.items():
    attention_data.append({
        "desiredAttention": desired_priority,
        "actualAttention": actual_times.get(selector, 0),
        "rankingScore": ranking_scores.get(selector, 0),
        "html_component": f"<div class='{selector}'>{selector}</div>"  # placeholder HTML
    })

# Optional: test printing
if __name__ == "__main__":
    for entry in attention_data:
        print(entry)
