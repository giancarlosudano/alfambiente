import os
import yaml
import re

def read_file(file_name):
	with open(file_name, "r") as file:
		return file.read()

def get_selected_files_from_answer(generation):
	linee = generation.splitlines()
	linea_selezionata = ""
	for linea in reversed(linee):
		if linea.lower().startswith("selected files:"):
			linea_selezionata = linea
			break

	# Se abbiamo trovato una linea, estraiamo i nomi dei file
	if linea_selezionata:
		pattern = r"FTC\d+\.md"
		document_names = re.findall(pattern, linea_selezionata)
	return document_names

def extract_yaml_front_matter(content: str):
	
	# Cerca l'inizio e la fine del front matter YAML
	start = content.find('---') + 3
	end = content.find('---', start)
	
	# Verifica se il front matter è stato trovato
	if start != -1 and end != -1:
		yaml_content = content[start:end]
		try:
			# Prova ad analizzare il contenuto YAML
			data = yaml.safe_load(yaml_content)
			return data
		except yaml.YAMLError as error:
			print(f"Errore durante l'analisi YAML: {error}")
			return {}
	else:
		# Front matter non trovato
		return {}
