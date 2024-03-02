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
	question_default = """Si chiede se nell’obbligo giuridico in capo al datore di lavoro della valutazione di tutti i rischi per la salute e la sicurezza con la conseguente elaborazione del documento di valutazione dei rischi (DVR), così come disciplinato dagli artt. 15, 17 e 28 del D.Lgs. n. 81/2008 sia ricompresa anche la valutazione della situazione ambientale e di sicurezza intesa anche come security, in particolare in paesi esteri ma non solo, legata a titolo esemplificativo ma non esaustivo ad eventi di natura geo politica, atti criminali di terzi, belligeranza e più in generale di tutti quei fattori potenzialmente pericolosi per l’integrità psicofisica dagli equipaggi nei luoghi (tipicamente aeroporti, alberghi, percorso da e per gli stessi e loro immediate vicinanze) dove il personale navigante si trovi ad operare/alloggiare quando comandati in servizio"""
	question = st.text_area("Domanda", key="question", value=question_default, height=250)
	st.button("Risposta...", on_click=search, args=[question])
	
except Exception as e:
	st.error(traceback.format_exc())