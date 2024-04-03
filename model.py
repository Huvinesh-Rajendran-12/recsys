from sentence_transformers import SentenceTransformer
from graph_database import Neo4jClient
import numpy as np
import os

client = Neo4jClient(
    uri="bolt://127.0.0.1:7687", username="huvi", password="huvinesh#", database="neo4j"
)

embedding_model_path = os.environ.get("EMBEDDING_MODEL_PATH", None)

model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")


# define the get embeddings function
def get_embeddings(text):
    return model.encode([text])


def get_product_recommendations(query: str, limit: int, allergens: str = "None", gender: str = "Unisex"):
    # get the embeddings for the query
    query_embeddings = get_embeddings(query)
    query_embeddings = np.array(query_embeddings[0])
    results = client.get_product_recommendations(
        query_embeddings=query_embeddings,
        limit=limit,
        allergens=allergens,
        gender=gender,
        index_vector="product_text_embeddings",
    )
    result_arr = []
    for result in results.records:
        result_arr.append(result.data())
    return result_arr


results = get_product_recommendations(query="I have knee pain", limit=5)
print(results)
