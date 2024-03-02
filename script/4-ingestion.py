from dotenv import load_dotenv
import os

from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders import TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import TextLoader

from azure.search.documents.indexes.models import (SearchableField, SearchField, SearchFieldDataType, SimpleField)
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

print("Index building POSTE started...")

load_dotenv()

azure_endpoint: str = os.getenv("AZURE_OPENAI_BASE") or ""
api_key: str = os.getenv("AZURE_OPENAI_KEY") or ""
api_version: str = os.getenv("AZURE_OPENAI_API_VERSION") or ""
model: str = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL") or ""
azure_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL") or ""
azure_search_service : str = os.getenv("AZURE_SEARCH_SERVICE") or ""
azure_search_key : str = os.getenv("AZURE_SEARCH_KEY") or ""
azure_openai_deployment : str = os.getenv("AZURE_OPENAI_MODEL_NAME") or ""
index_name = "poste-search-parents"

credential = AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
index_client = SearchIndexClient(os.environ["AZURE_SEARCH_SERVICE"], credential)

embeddings = AzureOpenAIEmbeddings(azure_endpoint=azure_endpoint, api_key=api_key, azure_deployment=azure_embedding_deployment)
embedding_function = embeddings.embed_query

fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
    ),
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=len(embedding_function("Text"))
    ),
    SearchableField(
        name="metadata",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    # Additional field to store the title
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
        facetable=True,
    ),
    # Additional field for filtering on document source
    SearchableField(
        name="description",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
]

vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=azure_search_service,
    azure_search_key=azure_search_key,
    index_name=index_name,
    embedding_function=embedding_function,
    fields=fields
)

# Caricamento con uso di chunking
for root, dirs, files in os.walk("c:/poste/www.poste.it-3"):
    for file in files:
        try:
            print(f"Processing file {os.path.join(root, file)}")
            loader = TextLoader(os.path.join(root, file), autodetect_encoding=True)
            documents = loader.load()
            contents = documents[0].page_content
            documents[0].metadata["title"] = file #TODO: lavorare sulla source
            documents[0].metadata["description"] = ""
            text_splitter = SemanticChunker(embeddings)
            docs = text_splitter.split_documents(documents)
            vector_store.add_documents(documents=docs)
            print(f"\tChunked in {len(docs)}.")
        except Exception as e:
            print(f"Error processing file {os.path.join(root, file)}: {e}")