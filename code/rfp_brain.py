import os
import costants as c
import helpers.langchain_helper as lc_hlp
import helpers.azure_search_helper as search_hlp
import helpers.storage_helper as storage_helper
import helpers.formatting_helper as formatting_helper
import helpers.utility_helper as utility_helper
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
import streamlit as st

def vanilla_retrieval(question, index_source):
	"""Retrieval vanilla, recupera N chunk e li passa al LLM come contesto"""

	store_source = search_hlp.get_vector_store_by_name(index_source)
	llm = lc_hlp.get_gpt4()

	chunks = store_source.similarity_search(query=question, k=15, search_type="hybrid")
	
	prompt = PromptTemplate(template=utility_helper.read_file(os.path.join("prompts", "prompt.txt")), input_variables=["question"])
	chain = prompt | llm | StrOutputParser()
	generation = chain.invoke({"question": question, "context": formatting_helper.format_docs(chunks)})

	return generation, chunks

def parentdoc_retrieval(question, index_source, blob_container) -> str:
	"""Retrieval parent-doc, recupera N chunk e prende come riferimento M parent (con M <= N). il LLM prende in contesto i doc completi"""

	log_visual = st.session_state[c.SESSION_LOG_VISUAL]
	log_visual.markdown(":gray[Start Parent-Child Retrieval...]")

	store_source = search_hlp.get_vector_store_by_name(index_source)
	llm = lc_hlp.get_gpt4()

	chunks = store_source.similarity_search(query=question, k=8, search_type="hybrid")
	parents = search_hlp.get_parent_from_chunks(chunks, blob_container)

	log_visual.markdown(f":gray[Chunks: {len(chunks)} - Parents:{len(parents)}]")
	
	for parent in parents.keys():
		log_visual.markdown(f":gray[ - {parent}]")

	prompt = PromptTemplate(template=utility_helper.read_file(os.path.join("prompts", "prompt.txt")), input_variables=["question"])
	chain = prompt | llm | StrOutputParser()
	generation = chain.invoke({"question": question, "context": formatting_helper.format_parents(parents)})

	return generation, chunks, parents

def summary_fixed_retrieval(question, container, summary_file_path, is_customer_finance=False) -> dict:
	"""Retrieval con numero fisso di documenti di cui viene presentata una summary"""

	st_container = st.session_state[c.SESSION_LOG_VISUAL]
	st_container.markdown(":gray[Start Summary Fixed Retrieval...]")

	llm = lc_hlp.get_gpt4()
	summary = utility_helper.read_file(summary_file_path)
	prompt_summary = PromptTemplate(template=utility_helper.read_file(os.path.join("prompts","summary_prompt.txt")), input_variables=["rfp", "question", "summary"])
	chain = prompt_summary | llm | StrOutputParser()
	generation = chain.invoke({"question": question, "summary": summary})
	
	st_container.markdown(f"Selection Files:\n{generation}")

	# Trovare l'ultima linea che inizia con "Selected files:"
	document_names = utility_helper.get_selected_files_from_answer(generation)
	st_container.markdown(f":gray[Selected Files:{len(document_names)}]")
	
	answers = []	
	for document_name in document_names:
		st_container.markdown(f":gray[Document to use:\n {document_name}]")
		content = storage_helper.get_blob_content(container, document_name)
		prompt_single_document = PromptTemplate(template=utility_helper.read_file(os.path.join("prompts","trusted_prompt.txt")), input_variables=["rfp", "question", "context"])	
		chain = prompt_single_document | llm | StrOutputParser()
		answer = chain.invoke({"rfp": rfp_description, "question": question, "context": content})
		answers.append(f"Risposta fornita con documento: {document_name}\n{answer}\n\n")
		st_container.markdown(f"Answer:\n{answer}")
	
	ensamble_prompt = PromptTemplate(template=utility_helper.read_file(os.path.join("prompts", "ensemble_prompt.txt")), input_variables=["rfp", "question", "answers"])
	
	chain = ensamble_prompt | llm | StrOutputParser()
	ensemble_answer = chain.invoke({
		"question": question, 
		"answers": formatting_helper.format_strings(answers)})

	st_container.success(f"Ensemble Answer:\n{ensemble_answer}")
	
	result={'question': question, 'final_answer': generation}
	
	return result

def ensemble_parent_hyde_retrieval(question, index_source, container) -> dict:
	"""Retrieval Ensemble, usa due metodi (parent_child e parent_child_hyde) e crea la migliore risposta"""
	llm = lc_hlp.get_gpt4()
	st_container = st.session_state[c.SESSION_LOG_VISUAL]
	st_container.markdown(":gray[Start Ensemble Parent-Hyde Retrieval...]")
	
	parent_hyde_answer = parent_child_with_hyde_retrieval(rfp_descriprion, question, index_source, index_fewshot, container, is_customer_finance)
	parent_answer = parent_child_retrieval(rfp_descriprion, question, index_source, index_fewshot, container)

	answers = [parent_hyde_answer["final_answer"], parent_answer["final_answer"]]
	ensamble_prompt = PromptTemplate(template=utility_helper.read_file(os.path.join("prompts", "ensemble_prompt.txt")), input_variables=["rfp", "question", "answers"])
	
	chain = ensamble_prompt | llm | StrOutputParser()
	ensemble_answer = chain.invoke({"rfp": rfp_descriprion, "question": question, "answers": formatting_helper.format_strings(answers)})

	st_container.success(f"Ensemble Answer:\n{ensemble_answer}")
	
	result={'question': question, 'final_answer': ensemble_answer}
	
	return result