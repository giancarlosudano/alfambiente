import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import costants as c
import streamlit as st
import pandas as pd
import rfp_brain as brain
import rfp_state_management as rfp_state_management
import helpers.streamlit_helper as streamlit_helper
from st_aggrid import AgGrid, GridOptionsBuilder

def update_questions_from_dataframe(pd_dataframe, rfp: rfp_state_management.RfpSession):
    for i, row in pd_dataframe.iterrows():
        rfp.answers[i]["question"] = row["question"]
        rfp.answers[i]["final_answer"] = row["final_answer"]
    return rfp

def call_generation():

    st_container = st.session_state[c.SESSION_LOG_VISUAL]
    rfp : rfp_state_management.RfpSession = st.session_state[c.SESSION_RFP]

    for question_row in rfp.answers:
        if question_row["final_answer"] == "" or st.session_state["rewrite"]:
            st_container.info(f"Question: {question_row['question']}")
            question = question_row["question"]
            result = brain.retrieval_by_domain(rfp, question)
            
            # salvaggio ad ogni iterazione
            question_row["question"] = result["question"]
            question_row["final_answer"] = result["final_answer"]
            rfp.save()
            st.session_state[c.SESSION_RFP] = rfp
            st_container.divider()
        else:
            st_container.warning(f"Question: {question_row['question']} SKIPPED")
    return

def call_generation_selected_list(questions : list[str]):

    st_container = st.session_state[c.SESSION_LOG_VISUAL]
    rfp : rfp_state_management.RfpSession = st.session_state[c.SESSION_RFP]

    for question_row in rfp.answers:
        if question_row["question"] in questions:
            question = question_row["question"]
            st_container.write(f"Question: {question}")
            result = brain.retrieval_by_domain(rfp, question)
            
            # salvaggio ad ogni iterazione
            question_row["question"] = result["question"]
            question_row["final_answer"] = result["final_answer"]
            rfp.save()
            st.session_state[c.SESSION_RFP] = rfp
    return

#START PAGE
streamlit_helper.init_page("Generate Answers for the RFP")
st.warning("Leave this page open to monitor the answer generation process")

rfp : rfp_state_management.RfpSession = st.session_state[c.SESSION_RFP]

if rfp is None:
    st.error('No RFP session loaded. Please load a session before generating answers')
    st.stop()

streamlit_helper.show_rfp_data_expander(rfp)

df = pd.DataFrame(rfp.answers)

df.reset_index(inplace=True)
df.rename(columns={'index': 'Index'}, inplace=True)
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(groupable=False, editable=True, sortable=False, resizable=True, filter=False)
gb.configure_columns("Index", width=70)
grid_options = gb.build()

button_container = st.container()
grid_container = st.container()

grid_response = AgGrid(df, gridOptions=grid_options, height=600, width='100%')
selected = grid_response["selected_rows"]

answer_container = st.empty()
st.session_state[c.SESSION_LOG_VISUAL] = answer_container
st.session_state[c.SESSION_STREAMING] = ""

cols = button_container.columns([1, 2, 2, 2], gap="small")
with cols[0]:
    st.write("Answer Generation: ")
with cols[1]:
    if st.button("Unanswered", type="primary"):
        st.session_state["rewrite"] = False
        update_questions_from_dataframe(grid_response.data, rfp)
        call_generation()
with cols[2]:
    if st.button("All (rewrite)"):
        st.session_state["rewrite"] = True
        update_questions_from_dataframe(grid_response.data, rfp)
        call_generation()
with cols[3]:
    cola, colb = st.columns([1, 1])
    with cola:
        stringa_indici = st.text_input("List of Question Index (comma separated)", value="")
    with colb:
        if st.button("Only Selected"):
            update_questions_from_dataframe(grid_response.data, rfp)
            lista_indici = [int(i) for i in stringa_indici.split(',')]
            questions = [df.iloc[i]['question'] for i in lista_indici]
            call_generation_selected_list(questions)
