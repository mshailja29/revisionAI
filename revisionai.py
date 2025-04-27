from openai import OpenAI
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import json
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY_STEVENS")
client = OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def query_gpt(prompt, task="summary"):
#     system_prompts = {
#     "summary": "Summarize the given text into a concise paragraph.",
#     "flashcard": "Create exactly 5 flashcards from the given text. Each flashcard must have a 'Question' and 'Answer'. Return ONLY the JSON array, no explanations.",
#     "quiz": "Generate exactly 5 multiple-choice questions from the given text. Each quiz must have 'question', 4 'options', and one 'answer'. Return ONLY the JSON array, no explanations."
# }

    system_prompts = {
    "summary": "Summarize the given text into a concise paragraph.",
    "flashcard": """Create exactly 5 flashcards from the given text.
Each flashcard must have the following fields:
- "question": the flashcard question
- "answer": the answer to the flashcard
Return ONLY the JSON array of flashcards without any explanation.""",
    "quiz": """Generate exactly 5 multiple-choice questions from the given text.
Each quiz question must have:
- "question": the question text
- "options": an array of 4 choices
- "answer": the correct answer
Return ONLY the JSON array of quiz questions without any explanation."""
}

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompts[task]},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content.strip()
def clean_json_string(gpt_output):
    """Extract JSON array from messy GPT output."""
    match = re.search(r'(\[.*\])', gpt_output, re.DOTALL)
    if match:
        return match.group(1)
    else:
        raise ValueError("No valid JSON array found in GPT output.")

def build_revision_ai_output(pdf_path, title="Document"):
    extracted_text = extract_text_from_pdf(pdf_path)
    
    # Get summary (just text)
    summary_text = query_gpt(extracted_text, task="summary")
    
    # Get flashcards (as JSON array)
    flashcards_json_str = query_gpt(extracted_text, task="flashcard")
    flashcards = json.loads(clean_json_string(flashcards_json_str))
    
    # Get quizzes (as JSON array)
    quizzes_json_str = query_gpt(extracted_text, task="quiz")
    quizzes = json.loads(clean_json_string(quizzes_json_str))
    
    # Assemble everything
    output = {
        "title": title,
        "summary": summary_text,
        "flashcards": flashcards,
        "quizzes": quizzes
    }
    
    return output

# Example usage
# pdf_path = "week12.pdf"  # Your PDF
# final_output = build_revision_ai_output(pdf_path, title="Sample PDF Document")

# # Save output to JSON file
# with open("revision_ai_output.json", "w", encoding="utf-8") as f:
#     json.dump(final_output, f, indent=4)

# print("✅ Output saved to revision_ai_output.json")
