import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .faiss_kb import create_kowledgebase, find


def create_knowledge_base_from_file(knowledge_base_name: str, knowledge_base_folder: str, file_path: str):
    """Crate a RAG collection from a Markdown document.

    Args:
        knowledge_base_name (str): Nome da coleção/vector store que será criada ou atualizada.
        knowledge_base_folder (str): Diretório onde a coleção do RAG será persistida.
        file_path (str): Caminho para o arquivo Markdown fonte utilizado na indexação.

    Returns:
        None: A função persiste os dados diretamente na coleção RAG sem retornar valor.

    Raises:
        FileNotFoundError: Se o `file_path` não apontar para um arquivo existente.
    """
    create_kowledgebase(file_path, knowledge_base_folder, knowledge_base_name)


def query_knowledge_base(query: str, knowledge_base_name: str, knowledge_base_folder: str, num_of_itens: int=5) -> list[str]:
    """
    Queries a knowledge base to retrieve a specified number of relevant items.

    This function takes a query string, the knowledge base name, folder path to the
    knowledge base, and the number of items to retrieve. It searches the knowledge
    base and returns a list of textual content from the most relevant items.

    Args:
        query: The query string used to search the knowledge base.
        knowledge_base_name: The name of the knowledge base index to query.
        knowledge_base_folder: The folder path where the knowledge base is stored.
        num_of_itens: The number of relevant items to retrieve. Defaults to 5.

    Returns:
        A list of strings, where each string is the text content from a relevant
        item in the knowledge base.
    """
    results = find(query=query, num_of_itens=num_of_itens, folder=knowledge_base_folder, index_name=knowledge_base_name)
    return [res['text'] for res in results]


def search_web(query: str) -> str:
    """
    Searches the web using the SerpAPI and returns formatted search results.

    This function queries the SerpAPI for Google search results based on the given query
    string and formats the results for better readability. It allows retrieving up to
    five organic results with their titles, summaries, and URLs.

    In case of a network issue, HTTP error, or invalid query, an appropriate error
    message is returned.

    Args:
        query (str): The search string to be queried on Google using SerpAPI.

    Returns:
        str: A formatted string with up to five search results or an appropriate
        error message if the query fails or no results are found.
    """
    query = (query or "").strip()
    if not query:
        return "Consulta de busca vazia."

    api_key = os.getenv("SERPAPI_API_KEY")

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": 5,
        "gl": "br",
        "hl": "pt-BR",
    }

    try:
        with urlopen(f"https://serpapi.com/search.json?{urlencode(params)}", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return f"Falha ao consultar SerpAPI (HTTP {exc.code})."
    except URLError:
        return "Falha de rede ao consultar SerpAPI."
    except Exception:
        return "Erro inesperado ao consultar SerpAPI."

    if isinstance(payload, dict) and payload.get("error"):
        return f"SerpAPI retornou erro: {payload.get('error')}."

    organic_results: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        organic_results = payload.get("organic_results") or []

    if not organic_results:
        return "Nenhum resultado encontrado para a consulta."

    formatted_chunks: list[str] = []
    for idx, item in enumerate(organic_results[:5], start=1):
        title = item.get("title") or item.get("snippet") or "Resultado sem título"
        snippet = item.get("snippet") or item.get("snippet_highlighted_words")
        if isinstance(snippet, list):
            snippet = " ... ".join(snippet)
        link = item.get("link") or item.get("displayed_link")
        formatted = f"{idx}. {title}"
        if snippet:
            formatted += f"\nResumo: {snippet}"
        if link:
            formatted += f"\nURL: {link}"
        formatted_chunks.append(formatted)

    return "\n\n".join(formatted_chunks)
