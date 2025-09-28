import os
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client
import uuid


RUN_ID = str(uuid.uuid4())
print("Using run_id:", RUN_ID)
with open("current_run_id.txt", "r") as f:
    RUN_ID = f.read().strip()
print("Using run_id from GemSuggest.py:", RUN_ID)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY_SECOND")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("API Key Loaded:", api_key is not None)
print("Supabase Config Loaded:", supabase_url is not None and supabase_key is not None)

genai.configure(api_key=api_key)

supabase = create_client(supabase_url, supabase_key)

def store_summary_in_supabase(summary_text):
    """Insert summary into Supabase."""
    data_row = {"summary": summary_text,"run_id": RUN_ID}
    response = supabase.table("gemini_summary").insert(data_row).execute()
    if response.data:
        print("✅ Stored summary of weaknesses in Supabase.")
    else:
        print("❌ Error storing summary:", response)

def generate_summary():
    """Fetch explanations and generate overall weaknesses summary."""
    # Fetch all explanations
    response = supabase.table("gemini_explanations") \
            .select("explanation") \
            .eq("run_id", RUN_ID) \
            .execute()


    if not explanations:
        print("⚠️ No explanations found, skipping summary.")
        return

    # Generate summary using Gemini
    joined_explanations = "\n\n".join(explanations)
    model = genai.GenerativeModel("gemini-2.0-flash")

    user_prompt = f"""
        You are an AI UX optimization assistant specializing in ADHD-friendly and accessible webpage design. 
        You are provided with detailed explanations of optimizations made to individual webpage components.

        Your task:
        - Write a high-level **summary overview** of the webpage based on these explanations.
        - Identify both **strengths** and **weaknesses** of the current design.
        - Highlight the **overall changes made** and what impact they are expected to have.
        - Assess the site's **accessibility alignment** with Google Lighthouse guidelines.
        - Suggest **3-5 general areas of improvement** that apply to the website as a whole 
        (not per-component tweaks).

        Output style:
        - Keep the summary **professional, concise, and actionable**.
        - Present information in a way that is easy to scan for readers with ADHD and UI Designers.
        - Use short paragraphs, bullets, or structured formatting.
        - Prioritize clarity and focus over long explanations.

        Input:
        Explanations of changes to components:
        {joined_explanations}
     """

    response = model.generate_content(
        [user_prompt],
        generation_config={"temperature": 0.3}
    )
    summary_text = response.text.strip()

    # Save summary to Supabase
    store_summary_in_supabase(summary_text)

    # Print summary
    print("\n=== WEBSITE WEAKNESSES SUMMARY ===\n")
    print(summary_text)
    print("\n==================================\n")

if __name__ == "__main__":
    generate_summary()
