import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from graph_database import Neo4jClient

client = Neo4jClient(uri="neo4j://localhost:7474", username="neo4j", password="huvinesh99")
df = pd.read_csv("./Data/products.csv")

model = SentenceTransformer("BAAI/bge-m3")


# clean the data
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


df["medicine_name"] = df["name"].apply(lambda x: clean_text(x))


# define the get embeddings function
def get_embeddings(text):
    return model.encode([text])[0]


# get the embeddings for each product
df['embeddings'] = df["medicine_name"].apply(get_embeddings)

records = df.to_dict(orient="records")

result = client.store_product_vector_embeddings(data=records, index_name="product_vector_embeddings")

print(result)



