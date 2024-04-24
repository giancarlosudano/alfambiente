import os
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.vectorstores.azuresearch import AzureSearch
import helpers.langchain_helper as langchain_helper
from azure.search.documents.indexes.models import (SearchableField, SearchField, SearchFieldDataType, SimpleField)
import helpers.storage_helper as storage_helper

def get_parent_from_chunks(relevant_chunks, container_name):
	parents = {}
	source_urls = [chunk.metadata["source"] for chunk in relevant_chunks]
	for source_url in source_urls:
			content = storage_helper.get_blob_content(container_name, source_url)
			if source_url not in parents:
				parents[source_url] = content
	return parents

def get_vector_store_by_name(index_name: str):
	load_dotenv()

	embedding_function = langchain_helper.get_embedding().embed_query

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
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchableField(
        name="description",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    ]

	azure_search_service : str = os.getenv("AZURE_SEARCH_SERVICE") or ""
	azure_search_key : str = os.getenv("AZURE_SEARCH_KEY") or ""

	vector_store: AzureSearch = AzureSearch(
		azure_search_endpoint=azure_search_service,
		azure_search_key=azure_search_key,
		index_name=index_name,
		embedding_function=embedding_function,
		fields=fields
	)

	vector_store: AzureSearch = AzureSearch(azure_search_endpoint=azure_search_service, 
										azure_search_key=azure_search_key, 
										index_name=index_name,
										embedding_function=embedding_function,
										fields=fields)
	return vector_store

