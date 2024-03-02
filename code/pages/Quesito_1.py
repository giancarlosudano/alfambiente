from turtle import title
from langchain_openai import AzureChatOpenAI
import streamlit as st
import os
import traceback
from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import StreamlitCallbackHandler

def search(question):

	azure_endpoint: str = os.getenv("AZURE_OPENAI_BASE") or ""
	api_key: str = os.getenv("AZURE_OPENAI_KEY") or ""
	api_version: str = os.getenv("AZURE_OPENAI_API_VERSION") or ""
	azure_openai_deployment: str = os.getenv("AZURE_OPENAI_MODEL_NAME") or ""

	cont = st.container()
	st_callback = StreamlitCallbackHandler(cont)
	 
	llm = AzureChatOpenAI(
		azure_deployment=azure_openai_deployment,
		temperature=0.7, streaming=True,
		azure_endpoint=azure_endpoint,
		api_key=api_key, api_version=api_version, callbacks=[st_callback])

	prompt_template = """Sei uno specialista sulle normative italiane in merito ad argomenti HSE.

Domanda: {question}

- Mostra il tuo ragionamento
- Cita ove possibile le leggi e gli articoli a cui ti riferisci per la risposta
- cita ove possibile articoli del codice civile, penale, del lavoro, italiano a completamento della risposta
 
Risposta:
"""

	prompt = PromptTemplate(template= prompt_template, input_variables=["context", "question"])

	# Chain
	rag_chain = prompt | llm | StrOutputParser()

	# Run
	generation = rag_chain.invoke({"question": question})
  
	return

try:
	load_dotenv()
	st.set_page_config(page_title="Chat with HSE bot", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Chat with HSE bot")
	st.sidebar.image(os.path.join('images','alfambiente.png'), use_column_width=True)	
	question_default = " ll datore di lavoro deve sempre predisporre obbligatoriamente misure di protezione collettiva, ai sensi dell’art. 148 c. 1 D.Lgs. 81/2008 e smi, ovvero ha la facoltà di valutare caso per caso quali misure di protezione (collettiva o individuale) adottare?"
	question = st.text_area("Domanda", key="question", value=question_default, height=150)
	st.button("Risposta...", on_click=search, args=[question])
	
except Exception as e:
	st.error(traceback.format_exc())