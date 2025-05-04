import streamlit as st
from revisionai import build_revision_ai_output
import os
import tempfile

# Initialize session_state variables
if 'quizzes' not in st.session_state:
    st.session_state['quizzes'] = {}

if 'output' not in st.session_state:
    st.session_state['output'] = {}

if 'callGPT' not in st.session_state:
    st.session_state['callGPT'] = False

if 'tmp_path' not in st.session_state:
    st.session_state['tmp_path'] = None

def update_selection(selected_key, correct_answer):
    selected_value = st.session_state.get(selected_key)
    if selected_value:
        if selected_value == correct_answer:
            st.session_state['quizzes'][f"{selected_key}_result"] = "correct"
        else:
            st.session_state['quizzes'][f"{selected_key}_result"] = "wrong"

st.set_page_config(page_title="Revision AI", page_icon="📚", layout="wide")
st.title("Revision AI - Study Smarter!")

uploaded_file = st.file_uploader("Upload a Course PDF", type=["pdf"])

# Handle uploaded file
if uploaded_file is not None and not st.session_state['callGPT']:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        st.session_state['tmp_path'] = tmp_file.name

    st.success("PDF uploaded successfully! Processing...")
    st.session_state['output'] = build_revision_ai_output(st.session_state['tmp_path'], title=uploaded_file.name)
    st.session_state['callGPT'] = True

# Use st.radio to simulate tabs with persistent state
tab_labels = ["Summary", "Flashcards", "Quiz"]

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Summary"

selected_tab = st.radio("Select Tab", tab_labels, index=tab_labels.index(st.session_state.active_tab), horizontal=True)

st.session_state.active_tab = selected_tab

if selected_tab == "Summary":
    st.header("Summary")
    if st.session_state['output']:
        st.write(st.session_state['output'].get("summary", ""))

elif selected_tab == "Flashcards":
    st.header("Flashcards")
    if st.session_state['output']:
        for i, flashcard in enumerate(st.session_state['output'].get("flashcards", [])):
            st.subheader(f"Q: {flashcard['question']}")
            st.write(f"**A:** {flashcard['answer']}")


elif selected_tab == "Quiz":
    st.header("📝 Quiz")
    if st.session_state['output']:
        for i, quiz in enumerate(st.session_state['output'].get("quizzes", [])):
            st.subheader(quiz["question"])
            options = quiz["options"]

            selected_key = f"quiz_{i}"

            st.radio(
                "Choose an option:",
                options,
                key=selected_key,
                index=None,
                on_change=update_selection,
                args=(selected_key, quiz["answer"])
            )

            if f"{selected_key}_result" in st.session_state['quizzes']:
                if st.session_state['quizzes'][f"{selected_key}_result"] == "correct":
                    st.success(f"✅ Correct! Your answer: {st.session_state[selected_key]}")
                else:
                    st.error(f"❌ Wrong! You selected: {st.session_state[selected_key]}")
                    st.success(f"✅ Correct answer: {quiz['answer']}")

# Clean up temp file safely after first time processing
if st.session_state.get('tmp_path') and os.path.exists(st.session_state['tmp_path']):
    os.remove(st.session_state['tmp_path'])
    st.session_state['tmp_path'] = None
