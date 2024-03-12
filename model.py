import pandas as pd
import re
from mlx_llm.model import create_model
from sanic import json
from transformers import BertTokenizer
import mlx.core as mx
from mlx.nn import losses as loss
import jax.numpy as jnp
from mlx_embedding_models.embedding import EmbeddingModel
import json
from typing import Dict, List
import chromadb

# set the chroma client
client = chromadb.PersistentClient('./vectordb')

# get collection from chromadb
collection = client.get_collection('telemerecsys')

# define the model name
model_name = "bge-small"

# clean the data
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]','',text)
    text = re.sub(r'\s+',' ',text)
    return text

# create the embedding model
model = EmbeddingModel.from_registry(f"{model_name}")

# define the get embeddings function
def get_embeddings(text):
    return model.encode([text])

def get_product_recommendations(query: str, limit: int):
    # get the embeddings for the query
    query_embeddings = get_embeddings(query)
    results = collection.query(
            query_embeddings=query_embeddings,
            n_results=limit,
            include=['documents', 'distances']
        )

    print(results)
    ids = results.get('ids')
    documents = results.get('documents')
    distances = results.get('distances')
    return {'ids': ids, 'recommendations' : documents, 'score': distances}



