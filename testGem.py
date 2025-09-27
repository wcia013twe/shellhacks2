from flask import Flask, render_template_string
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("API Key Loaded:", api_key is not None)

app = Flask(__name__)

SYSTEM_PROMPT = """
You are an AI UX optimization assistant specializing in ADHD-friendly webpage design.
You analyze discrepancies between developer-defined attention priorities and real user attention (measured by eyetracking).

Guidelines for changes:
- Over-performing elements → reduce visual weight (contrast, size, animations, text density, positioning).
- Under-performing elements → increase prominence (hierarchy, spacing, contrast, placement).
- Maintain a linear, focused attention flow suitable for ADHD-friendly design.
- Keep HTML changes minimal and efficient unless a stronger redesign is necessary.
- Look into Google's Lighthouse Accessability guidelines and rules. Try your absolute best to make changes that will result in the highest score.

Output Instructions:
- First section: Modified HTML code (apply changes to the original HTML)
- Second section: Explanation of changes (plain text)
- Use '===EXPLANATION===' as a separator between HTML and explanation
- Include reasoning for each element changed, the issue (over/under-performing), and what was changed.
- Do NOT use JSON.
- You may include line breaks, HTML tags, and detailed reasoning in the explanation.
"""

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def optimize_webpage(expected_dataset, real_dataset, score, html_component):
    model = genai.GenerativeModel("gemini-2.0-flash")  # Replace with your working model

    user_prompt = f"""
Expected Dataset (developer intent):
{expected_dataset}

Real Dataset (user eyetracking):
{real_dataset}

Score:
{score}

HTML Component:
{html_component}
"""

    response = model.generate_content(
        [SYSTEM_PROMPT, user_prompt],
        generation_config={"temperature": 0.3}
    )

    raw = response.text.strip()

    # Split into modified HTML and explanation
    if "===EXPLANATION===" in raw:
        modified_html, explanation = raw.split("===EXPLANATION===", 1)
    else:
        modified_html = raw
        explanation = "No explanation provided."

    return html_component.strip(), modified_html.strip(), explanation.strip()


# Fake datasets for testing
expected_dataset = """
1. <main> (high attention)
2. <h1> (medium attention)
3. <aside> (low attention)
"""

real_dataset = """
1. <aside> (highest attention)
2. <main> (medium attention)
3. <h1> (low attention)
"""

score = 0.62

html_component = """
<main>
  <h1>Product Overview</h1>
  <p>Discover the key features of our latest product line.</p>
</main>

<aside>
  <div class="promo-banner">
    <h2>🔥 Limited Offer!</h2>
    <p>Get 50% off today only.</p>
  </div>
</aside>
"""

@app.route("/")
def index():
    original_html, modified_html, explanation = optimize_webpage(expected_dataset, real_dataset, score, html_component)

    page = f"""
    <html>
    <head>
        <title>Gemini UX Test</title>
        <style>
            body {{ display: flex; flex-direction: column; gap: 30px; font-family: Arial, sans-serif; margin: 20px; }}
            .section {{ border: 1px solid #ccc; padding: 20px; }}
            .html-section, .modified-html {{ background: #fff; }}
            .explanation-section {{ background: #f9f9f9; max-height: 400px; overflow-y: auto; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            h2 {{ margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="section html-section">
            <h2>Original HTML</h2>
            {original_html}
        </div>

        <div class="section modified-html">
            <h2>Modified HTML</h2>
            {modified_html}
        </div>

        <div class="section explanation-section">
            <h2>Explanation Section</h2>
            <pre>{explanation}</pre>
        </div>
    </body>
    </html>
    """
    return page


if __name__ == "__main__":
    app.run(debug=True)
