import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_openai import AzureChatOpenAI
import streamlit as st
import costants as c
from dotenv import load_dotenv
from rfp_brain import vanilla_retrieval, parentdoc_retrieval, summary_fixed_retrieval
import helpers.formatting_helper as formatting_helper
import traceback

try:
	load_dotenv()
	st.set_page_config(page_title="Chat with HSE bot", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Chat with HSE bot")
	st.sidebar.image(os.path.join('images','alfambiente.png'), use_column_width=True)	
	question_default = ""
	question = st.text_area("Domanda", key="question", value=question_default)
	if st.button("Risposta..."):
		answer, chunks = vanilla_retrieval(question, c.INDEX_SOURCE)
		st.success(answer)
		st.info(formatting_helper.format_docs(chunks))
	
except Exception as e:
	st.error(traceback.format_exc())