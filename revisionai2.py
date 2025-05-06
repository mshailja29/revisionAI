from openai import OpenAI
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tempfile

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY_STEVENS")
client = OpenAI(api_key=api_key)

# One-shot unified prompt
system_prompt = """
You are a study assistant. Given a passage of academic or technical text, extract and return a JSON object containing the following:

1. "summary" - A concise 3-5 sentence paragraph summarizing the core ideas.
2. "web_links" - A list of 3-5 relevant and trusted URLs (.gov, .edu, .org).
3. "flashcards" - Exactly 5 flashcards, each with:
   - "question": a short, factual question
   - "answer": a brief, direct answer
4. "quizzes" – A list of exactly 5 multiple-choice questions. Each item must be a dictionary with:
   - "question": a clearly worded, self-contained question that tests understanding of a key point in the passage
   - "options": an array of exactly 4 plausible and distinct answer choices (labeled A, B, C, D not required)
     - Ensure that at least two distractors (wrong answers) are reasonable but clearly incorrect
     - Do NOT use repeated, vague, or overly similar options
   - "answer": the exact string from one of the options that is correct (must match one of the options exactly, including punctuation and spacing)

Avoid yes/no questions. Prioritize fact-based or concept-checking questions over opinion or speculation. Ensure the correct answer is not obviously longer or more detailed than the distractors.

### Output Format:
Return only valid JSON, without markdown, explanations, or labels. The format must match:

{
  "summary": "string",
  "web_links": ["string", "..."],
  "flashcards": [
    {"question": "string", "answer": "string"}
  ],
  "quizzes": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "answer": "string"
    }
  ]
}
"""

def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def one_shot_query(text):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}  # <-- Ensures JSON output
    )
    return json.loads(completion.choices[0].message.content)

def fetch_ocw_text_from_url(ocw_url):
    print("📅 Fetching course materials from:", ocw_url)
    response = requests.get(ocw_url)
    soup = BeautifulSoup(response.content, "html.parser")

    text_content = ""

    # Step 1: Grab readable text
    for tag in soup.find_all(["p", "li", "h1", "h2", "h3"]):
        if tag.get_text(strip=True):
            text_content += tag.get_text(separator=" ", strip=True) + "\n"

    # Step 2: Download PDFs (up to 3)
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
    full_pdfs = [urljoin(ocw_url, link) for link in pdf_links]

    for pdf_url in full_pdfs[:3]:
        try:
            r = requests.get(pdf_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(r.content)
                tmp_path = tmp_file.name

            text_content += "\n" + extract_text_from_pdf(tmp_path)
        except Exception as e:
            print(f"⚠️ Could not download PDF: {pdf_url} — {e}")

    return text_content.strip()

def build_revision_ai_output(input, title="Document", is_url=False):
    if is_url:
        extracted_text = fetch_ocw_text_from_url(input)
    else:
        extracted_text = extract_text_from_pdf(input)

    result = one_shot_query(extracted_text)

    return {
        "title": title,
        "summary": json.dumps({
            "summary": result.get("summary", ""),
            "web_links": result.get("web_links", [])
        }),
        "flashcards": result.get("flashcards", []),
        "quizzes": result.get("quizzes", [])
    }
