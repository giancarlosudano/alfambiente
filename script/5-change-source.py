from dotenv import load_dotenv
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient

def trasforma_url(stringa):
    # Trova l'indice di inizio della sottostringa "www"
    indice_www = stringa.find("www.poste.it\\")
    
    # Rimuove la parte iniziale fino a "www"
    parte_rilevante = stringa[indice_www:]
    
    # Sostituisce i backslash con slash
    url_corretto = parte_rilevante.replace("\\", "/")
    
    # Aggiunge "https://" all'inizio
    url_finale = "https://" + url_corretto
    
    return url_finale

print("Index building POSTE started...")

load_dotenv()

azure_endpoint: str = os.getenv("AZURE_OPENAI_BASE") or ""
azure_search_service : str = os.getenv("AZURE_SEARCH_SERVICE") or ""
azure_search_key : str = os.getenv("AZURE_SEARCH_KEY") or ""
index_name = "poste-search"

# Crea un client per l'indice
index_client = SearchIndexClient(endpoint=azure_search_service,
                                  index_name=index_name,
                                  credential=AzureKeyCredential(azure_search_key))

# Crea un client di ricerca per recuperare i documenti
search_client = SearchClient(endpoint=azure_search_service,
                             index_name=index_name,
                             credential=AzureKeyCredential(azure_search_key))

# Recupera tutti i documenti (attenzione alla paginazione)
results = search_client.search(search_text="*", select="id,source,metadata", top=2000)
documents_to_update = []

print(azure_search_key)
print(azure_search_service)

for result in results:
    # Modifica il campo specifico
    metadata = result["metadata"]
    metadata_dict = eval(metadata)
    source = metadata_dict["source"]
    source_mod = print(trasforma_url(source))
    result["source"] = source_mod
    documents_to_update.append(result)

# Aggiorna i documenti nell'indice
# Puoi scegliere di farlo in batch per ottimizzare le prestazioni
if documents_to_update:
    update_results = index_client(documents=documents_to_update)
    for update_result in update_results:
        if not update_result.succeeded:
            print(f"Failed to update document {update_result.key}")