import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from gui import SimpleBrowserLauncher
from supabase import create_client
import data  # <-- old import style

# Load environment variables

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("API Key Loaded:", api_key is not None)
print("Supabase Config Loaded:", supabase_url is not None and supabase_key is not None)
genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
You are an AI UX optimization assistant specializing in ADHD-friendly webpage design.
You analyze discrepancies between developer-defined attention priorities and real user attention (measured by eyetracking).

You are always provided:
1. The entire HTML component to optimize.
2. A score between 1-100 that measures how well actual attention matches developer intent.
   - A score of 100 means nearly perfect alignment, so no changes should be made.
   - The lower the score, the more drastic the changes required.
   - If the score is within ±5 of 100 (margin of error), do not apply changes.

Guidelines for changes:
- Over-performing elements → reduce visual weight (contrast, size, animations, text density, positioning).
- Under-performing elements → increase prominence (hierarchy, spacing, contrast, placement).
- Maintain a linear, focused attention flow suitable for ADHD-friendly design.
- Keep HTML changes minimal and efficient unless a stronger redesign is necessary.
- Look into Google's Lighthouse Accessibility guidelines and rules. Always try to make changes that would increase the accessibility score.

Output Instructions:
- First section: Modified HTML code (apply changes directly to the original HTML provided).
- Second section: Explanation of changes (plain text).
- Use '===EXPLANATION===' as a separator between HTML and explanation.
- In the explanation, include:
    - Which elements were changed
    - Whether they were over-performing or under-performing
    - What was changed
    - Why it was changed (expected impact on attention flow and accessibility)
- Do NOT use JSON.

 """ 

# Supabase client

supabase = create_client(supabase_url, supabase_key)

def store_explanation_in_supabase(component, desired_attention, actual_attention, ranking_score, explanation):
    """Insert Gemini explanation into Supabase table."""
    data_row = {
        "component": component,
        "desired_attention": desired_attention,
        "actual_attention": actual_attention,
        "ranking_score": ranking_score,
        "explanation": explanation
    }
    response = supabase.table("gemini_explanations").insert(data_row).execute()
    if response.data:
        print(f"Stored explanation for component: {component}")
    else:
        print("Error storing explanation:", response)


# Gemini optimization

def optimize_webpage(expected_attention, actual_attention, ranking_score, html_component):
    model = genai.GenerativeModel("gemini-2.0-flash")

    user_prompt = f"""
Expected Attention:
{expected_attention}

Actual Attention:
{actual_attention}

Ranking Score:
{ranking_score}

HTML Component:
{html_component}
"""

    response = model.generate_content(
        [SYSTEM_PROMPT, user_prompt],
        generation_config={"temperature": 0.3}
    )

    raw = response.text.strip()

    if "===EXPLANATION===" in raw:
        modified_html, explanation = raw.split("===EXPLANATION===", 1)
    else:
        modified_html = raw
        explanation = "No explanation provided"
        print("Warning: Gemini response did not include an explanation.")

    # Save to Supabase
    store_explanation_in_supabase(
        component=html_component,
        desired_attention=expected_attention,
        actual_attention=actual_attention,
        # ranking_score=ranking_score,
        explanation=explanation.strip()
    )

    # Save HTML locally
    html_file_path = "output.html"
    with open(html_file_path, "w") as html_file:
        html_file.write(modified_html.strip())

    print("Gemini Explanation:", explanation.strip())

    return html_file_path


# Viewer

def launch_web_viewer(attention_dataset):
    viewer = SimpleBrowserLauncher()
    viewer.run()

    for item in attention_dataset:
        html_file = optimize_webpage(
            expected_attention=item["desiredAttention"],
            actual_attention=item["actualAttention"],
            ranking_score=item["rankingScore"],
            html_component=item["html_component"]
        )
        viewer.load_file(html_file)

    # Monitor last file for changes
    last_modified_time = os.path.getmtime("output.html")
    try:
        while True:
            time.sleep(1)
            current_modified_time = os.path.getmtime("output.html")
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                viewer.load_file("output.html")
    except KeyboardInterrupt:
        print("File monitoring stopped.")


# Main
if __name__ == "__main__":
    launch_web_viewer(data.attention_data)
