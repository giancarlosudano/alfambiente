import os
import re

def format_docs(docs):
	elementi_formattati = []

	# Iterazione attraverso le coppie chiave-valore nel dizionario
	for chiave, valore in docs.items():
		# Aggiunta della stringa formattata alla lista
		elementi_formattati.append(f"Documento: {chiave}\n{valore}")

	# Unione di tutte le stringhe formattate in una singola stringa, separandole con due newline per chiarità
	stringa_unica = "\n\n".join(elementi_formattati)
	return stringa_unica

def format_fewshot(docs):
	return "\n\n".join(doc.page_content for doc in docs)

def format_strings(strings):
	return "\n\n".join(strings)

def print_chain_summary(title, relevant_chunks, parents, fewshots, generation):
	print("Metodo: " + title)
	print("Chunk rilevati:" + str(len(relevant_chunks)))
	print('\n'.join([chunk.metadata["source"] for chunk in relevant_chunks]))
	print("Parent rilevati:" + str(len(parents)))
	print('\n'.join(parents.keys()))
	# print("Fewshots:" + str(len(fewshots)))
	print("Generation:")
	print(generation)
