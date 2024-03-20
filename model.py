from typing import Dict, List
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

client = QdrantClient(host="localhost", port=6333)

# define the model name
model_name = "BAAI/bge-m3"

model = SentenceTransformer(model_name)


# define the get embeddings function
def get_embeddings(text):
    return model.encode([text])


def get_product_recommendations(query: str, limit: int) -> List[Dict]:
    # get the embeddings for the query
    query_embeddings = get_embeddings(query)
    print(query_embeddings)
    results = client.search(
        collection_name="products",
        query_vector=query_embeddings[0],
        limit=limit,
        with_payload=["name", "price"],
    )
    result_dict = [
        {
            "name": result.payload["name"],
            "price": result.payload["price"],
            "score": result.score,
        }
        for result in results
    ]
    return result_dict


def get_product_recommendations_neo4j(query: str, limit: int) -> List[Dict]:
    # get the embeddings for the query
    query_embeddings = get_embeddings(query)
    print(query_embeddings)
    results = client.search(
        collection_name="products",
        query_vector=query_embeddings[0],
        limit=limit,
        with_payload=["name", "price"],
    )
    result_dict = [
        {
            "name": result.payload["name"],
            "price": result.payload["price"],
            "score": result.score,
        }
        for result in results
    ]
    return result_dict
