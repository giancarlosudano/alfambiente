from dotenv import load_dotenv
import os

from langchain_openai import AzureOpenAIEmbeddings
from azure.search.documents.indexes.models import (SearchIndex, SearchableField, SearchField, SearchFieldDataType, SimpleField, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration)
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

print("Index creation started...")

load_dotenv()
azure_endpoint: str = os.getenv("AZURE_OPENAI_BASE") or ""
api_key: str = os.getenv("AZURE_OPENAI_KEY") or ""
api_version: str = os.getenv("AZURE_OPENAI_API_VERSION") or ""
model: str = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL") or ""
azure_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL") or ""
azure_search_service : str = os.getenv("AZURE_SEARCH_SERVICE") or ""
azure_search_key : str = os.getenv("AZURE_SEARCH_KEY") or ""
azure_openai_deployment : str = os.getenv("AZURE_OPENAI_MODEL_NAME") or ""
index_name = "poste-search-2"
print(azure_search_service)
input("Press Enter to continue...")

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
        vector_search_dimensions=len(embedding_function("Text")),
        vector_search_profile_name="my-vector-config",
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
        facetable=True,
        searchable=True,
    ),
    # Additional field for filtering on document source
    SearchableField(
        name="description",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
]

vector_search = VectorSearch(
        profiles=[VectorSearchProfile(name="my-vector-config", algorithm_configuration_name="my-algorithms-config")],
        algorithms=[HnswAlgorithmConfiguration(name="my-algorithms-config")],
)

index_definition = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

# INDEX CREATION NEXT LINE
index_client.create_index(index_definition)
print("Index created")