import pandas as pd
import re
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Batch
from sentence_transformers import SentenceTransformer


client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="products",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)

model = SentenceTransformer("BAAI/bge-m3")

df_products = pd.read_csv('./Data/products.csv')

# clean the data
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]','',text)
    text = re.sub(r'\s+',' ',text)
    return text

df_products['medicine_name'] = df_products['name'].apply(lambda x: clean_text(x))

# define the get embeddings function
def get_embeddings(text):
    return model.encode([text])[0]

# get the embeddings for each product
embds = df_products['medicine_name'].apply(get_embeddings)

status = client.upsert(
    collection_name="products",
    points=Batch(
        ids=list(range(len(df_products))),
        vectors=[emb for emb in embds],
        payloads=df_products.to_dict(orient='records')
    )
)

print(status)
