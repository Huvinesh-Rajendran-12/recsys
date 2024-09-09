from sentence_transformers import SentenceTransformer
from app.graph_database import Neo4jClient
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASS")
database = os.getenv("NEO4J_DB")

client = Neo4jClient(uri, username, password, database)

embedding_model_path = os.environ.get("EMBEDDING_MODEL_PATH", None)

model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=1024)


# define the get embeddings function
def get_embeddings(text):
    embeddings = model.encode([text])
    return embeddings[0].tolist()


def get_product_recommendations(
    query: str, limit: int, allergens: str = "None", gender: str = "Unisex"
):
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
