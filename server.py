import os
from dotenv import load_dotenv
from fastapi.requests import Request
import uvicorn
from fastapi import FastAPI
from model import get_product_recommendations, get_embeddings
from database import get_user_data
from graph_database import Neo4jClient

load_dotenv()

app = FastAPI()


@app.get("/api/v1/healthcheck")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/medicine/recommendations")
async def recommendations(query: str, userId: int, limit: int):
    (gender, date_of_birth, allergy) = get_user_data(userId)
    results = get_product_recommendations(
        query=query, limit=limit, allergens=allergy, gender=gender
    )
    return results


@app.get("/api/v1/products")
async def get_products():
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
    results = client.get_products()
    return results


@app.post("/api/v1/products/add")
async def add_product(
    request: Request
):
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
    name = prod_data["name"]
    description = prod_data["description"]
    price = prod_data["price"]
    allergens = prod_data["allergens"]
    gender = prod_data["gender"]
    embeddings = get_embeddings(description)
    result = client.add_product(
        name=name, description=description, price=price, allergens=allergens, gender=gender, embeddings=embeddings
    )
    result_arr = []
    for result in result.records:
        result_arr.append(result.data())
    return result_arr

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337, reload=True)
