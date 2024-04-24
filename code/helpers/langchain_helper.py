from dotenv import load_dotenv
import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
import costants as c

# Uso per lo streaming
# get_gpt4(with_callback=True)
# st.session_state[c.SESSION_STREAMING_CONTAINER] = st.empty()   <-- Bisogna assegnare un container per lo streaming
# st.session_state[c.SESSION_STREAMING] = ""  <-- se già esistente va cancellata la variabile di sessione che contiene i token di streaming
class MyCustomSyncHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        st.session_state[c.SESSION_STREAMING] = st.session_state.get(c.SESSION_STREAMING, "") + token
        container = st.session_state[c.SESSION_STREAMING_VISUAL]
        container.write(st.session_state[c.SESSION_STREAMING])

def get_gpt4(with_callback : bool = True):
    load_dotenv()
    azure_endpoint: str = os.getenv("AZURE_OPENAI_BASE") or ""
    api_key: str = os.getenv("AZURE_OPENAI_KEY") or ""
    api_version: str = os.getenv("AZURE_OPENAI_API_VERSION") or ""
    azure_openai_deployment : str = os.getenv("AZURE_OPENAI_MODEL_NAME") or ""
    
    if with_callback:
        llm = AzureChatOpenAI(azure_deployment=azure_openai_deployment, temperature=0, streaming=True, azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version, callbacks=[MyCustomSyncHandler()])
    else:
        llm = AzureChatOpenAI(azure_deployment=azure_openai_deployment, temperature=0, streaming=True, azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version)
    
    return llm

def get_embedding():
    load_dotenv()
    azure_endpoint: str = os.getenv("AZURE_OPENAI_BASE") or ""
    api_key: str = os.getenv("AZURE_OPENAI_KEY") or ""
    azure_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL") or ""
    embeddings = AzureOpenAIEmbeddings(azure_endpoint=azure_endpoint, api_key=api_key, azure_deployment=azure_embedding_deployment)
    return embeddings