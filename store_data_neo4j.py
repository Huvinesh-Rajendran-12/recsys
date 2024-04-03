import pandas as pd
import re
import os
from sentence_transformers import SentenceTransformer
from graph_database import Neo4jClient

embedding_model_path = os.environ.get("EMBEDDING_MODEL_PATH", None)

print("=== Connecting to the client ===")
client = Neo4jClient(
    uri="bolt://127.0.0.1:7687", username="huvi", password="huvinesh#", database="neo4j"
)
print("=== Checking connectivity ===")
result = client.hello()
if result is not None:
    print("Connection successful")

print("=== Loading the embedding model ===")
model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")
print("=== Model loaded ===")

print("=== Loading the product data ===")
df = pd.read_csv("./Data/guardian_fake_data.csv")
print("=== Data loaded ===")


# clean the data
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


print("=== Cleaning the product data ===")
df["medicine_description"] = df["description"].apply(lambda x: clean_text(x))


# define the get embeddings function
def get_embeddings(text):
    return model.encode([text])[0]


print("=== Get embeddings ===")
# get the embeddings for each product
df["embeddings"] = df["medicine_description"].apply(get_embeddings)

records = df.to_dict(orient="records")

print("=== Store the embeddings ===")
result = client.store_product_vector_embeddings(
    data=records, index_name="product_text_embeddings"
)
