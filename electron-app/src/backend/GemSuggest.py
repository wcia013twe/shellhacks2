import os
import google.generativeai as genai
from dotenv import load_dotenv
from gui import SimpleBrowserLauncher
import argparse
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("API Key Loaded:", api_key is not None)

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
        raise ValueError("Gemini response is not in the expected format.")

    # Save the modified HTML to a file
    html_file_path = "output.html"
    with open(html_file_path, "w") as html_file:
        html_file.write(modified_html.strip())

    # Optionally log the explanation
    print("Explanation of changes:", explanation.strip())

    return html_file_path

def launch_web_viewer(expected_dataset, real_dataset, score, html_component):
    viewer = SimpleBrowserLauncher()
    viewer.run()

    # Generate the updated HTML file using Gemini
    html_file = optimize_webpage(expected_dataset, real_dataset, score, html_component)

    # Load the generated HTML file into the viewer
    viewer.load_file(html_file)

    # Monitor the file for updates (optional)
    last_modified_time = os.path.getmtime(html_file)
    try:
        while True:
            time.sleep(1)  # Check for updates every second
            current_modified_time = os.path.getmtime(html_file)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                viewer.load_file(html_file)  # Reload the updated file
    except KeyboardInterrupt:
        print("File monitoring stopped.")


if __name__ == "__main__":
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="Launch the web viewer with Gemini-generated HTML.")
    parser.add_argument("expected_dataset", type=str, help="The expected dataset (developer intent).")
    parser.add_argument("real_dataset", type=str, help="The real dataset (user eye-tracking data).")
    parser.add_argument("score", type=float, help="The score for the optimization.")
    parser.add_argument("html_component", type=str, help="The HTML component to optimize.")

    # Parse the arguments
    args = parser.parse_args()

    # Launch the web viewer with the provided arguments
    launch_web_viewer(args.expected_dataset, args.real_dataset, args.score, args.html_component)