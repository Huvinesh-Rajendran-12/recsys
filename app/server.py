import os
from dotenv import load_dotenv
from fastapi.requests import Request
import uvicorn
from fastapi import FastAPI
from app.model import get_embeddings
from app.graph_database import Neo4jClient

load_dotenv()

app = FastAPI()


@app.get("/api/v1/healthcheck")
async def root():
    return {"message": "Hello World"}


@app.post("/api/v1/products/add")
async def add_product(request: Request):
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASS")
    uri = os.getenv("NEO4J_URI")
    database = os.getenv("NEO4J_DB")
    client = Neo4jClient(
        uri=uri,
        username=username,
        password=password,
        database=database,
    )
    prod_data = await request.json()
    name = prod_data["name"]
    description = prod_data["description"]
    price = prod_data["price"]
    allergens = prod_data["allergens"]
    gender = prod_data["gender"]
    embeddings = get_embeddings(description)
    result = client.add_product(
        name=name,
        description=description,
        price=price,
        allergens=allergens,
        gender=gender,
        embeddings=embeddings,
    )
    result_arr = []
    for result in result.records:
        result_arr.append(result.data())
    return result_arr


@app.get("/api/v1/generate/embeddings")
async def generate_embeddings(request: Request):
    text = request.query_params.get("text")
    if text is None:
        return {"error": "Missing 'text' parameter"}
    embeddings = get_embeddings(text)
    # Make sure embeddings is a sequence (e.g., a list)
    if not isinstance(embeddings, (list, tuple)):
        return {"error": "Invalid embeddings format"}
    return {"embeddings": embeddings}


@app.post("/api/v1/products/edit")
async def edit_product(request: Request):
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASS")
    uri = os.getenv("NEO4J_URI")
    database = os.getenv("NEO4J_DB")
    client = Neo4jClient(
        uri=uri,
        username=username,
        password=password,
        database=database,
    )
    prod_data = await request.json()
    print(prod_data)
    id = prod_data["id"]
    name = prod_data["name"]
    description = prod_data["description"]
    price = prod_data["price"]
    allergens = prod_data["allergens"]
    gender = prod_data["gender"]
    embeddings = get_embeddings(description)
    result = client.edit_product(
        id=id,
        name=name,
        description=description,
        price=price,
        allergens=allergens,
        gender=gender,
        embeddings=embeddings,
    )
    result_arr = []
    for result in result.records:
        result_arr.append(result.data())
    return result_arr


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337, reload=True)
