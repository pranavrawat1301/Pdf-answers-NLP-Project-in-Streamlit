# -*- coding: utf-8 -*-
"""Untitled16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/142WmE5e3XxG0gb3mfixHh-SYRUxJ9M-4
"""

# pip install streamlit pymupdf transformers torch

import streamlit as st
import fitz
from transformers import pipeline
import torch

from io import BytesIO

def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf_document = fitz.open(stream=BytesIO(uploaded_file.read()), filetype="pdf")
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    return text

def answer_question(pdf_text, question):
    nlp_qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

    inputs = nlp_qa.tokenizer.encode_plus(question, pdf_text, return_tensors="pt", max_length=512, truncation=True)
    input_ids = inputs["input_ids"]

    start_scores, end_scores = nlp_qa.model(**inputs)

    all_tokens = nlp_qa.tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
    answer_start = torch.argmax(start_scores, dim=1).item()
    answer_end = torch.argmax(end_scores, dim=1).item() + 1
    answer = nlp_qa.tokenizer.decode(input_ids[0, answer_start:answer_end].tolist())

    return answer



def main():
    st.title("PDF Question Answering App")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)

        st.subheader("PDF Content:")
        st.write(pdf_text)

        st.subheader("Ask Questions:")
        question = st.text_input("Type your question:")

        if st.button("Ask"):
            if not pdf_text:
                st.warning("Please upload a valid PDF file.")
            elif not question:
                st.warning("Please type a question.")
            else:
                answer = answer_question(pdf_text, question)
                st.success(f"Answer: {answer}")

if __name__ == "__main__":
    main()

