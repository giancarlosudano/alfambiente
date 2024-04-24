import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

import streamlit as st
from dotenv import load_dotenv
import os
import helpers.storage_helper as storage_helper
import pandas as pd
import costants as c

def init_page(title:str):
    load_dotenv()
    st.set_page_config(page_title="RFP Copilot", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
    st.sidebar.title("RFP Copilot")
    st.sidebar.image(os.path.join('images','logo-rfp-copilot.png'), use_column_width=True)
    st.sidebar.image(os.path.join('images','logo-ms.png'), use_column_width=True)
    st.markdown(f"### {title}")

def show_rfp_data_expander(rfp):
    exp = st.expander(f"RFP Session Info", expanded=True)
    exp.write(f"Id: {rfp.id}")
    exp.write(f"Description: {rfp.description}")
    exp.write(f"Is Customer in FSI: {str(rfp.is_customer_finance)}")
    exp.write(f"Domain: {rfp.domain}")

def get_sessions_dataframe():
    file_names = []
    container_client = storage_helper.get_container_client(c.BLOB_CONTAINER_SESSIONS)
    for blob in container_client.list_blobs():
        file_names.append(blob.name)

    # Creare un DataFrame con i nomi dei file
    df = pd.DataFrame(file_names, columns=['session'])
    return df