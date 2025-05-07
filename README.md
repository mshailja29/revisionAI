# RevisionAI

RevisionAI is an AI-powered educational tool that extracts lecture content from MIT OCW PDFs or web pages and generates summaries, quizzes, and flashcards using GPT-4o.

##Features

Upload lecture PDFs or extract from websites
AI-generated:
  Summaries
  Flashcards
  Quizzes
  
Streamlit-based user interface
Powered by OpenAI's GPT-4o

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API Key
- MongoDB (local or cloud)
- Chrome browser (for Selenium)

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/mshailja29/revisionAI.git
   cd revisionAI
2. Create virtual environment and activate it:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set your OpenAI API key and MongoDB URI in a .env file:
   OPENAI_API_KEY=your_openai_key

5. streamlit run app2.py
