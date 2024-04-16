from fastapi.requests import Request
import uvicorn
from fastapi import FastAPI
from model import get_product_recommendations, get_embeddings
from database import get_user_data
from graph_database import Neo4jClient

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
    client = Neo4jClient(
        uri="bolt://127.0.0.1:7687",
        username="huvi",
        password="huvinesh#",
        database="neo4j",
    )
    results = client.get_products()
    return results


@app.post("/api/v1/products/add")
async def add_product(
    request: Request
):
    client = Neo4jClient(
        uri="bolt://127.0.0.1:7687",
        username="huvi",
        password="huvinesh#",
        database="neo4j",
    )
    prod_data = await request.json()
    print(prod_data)
    name = prod_data["name"]
    description = prod_data["description"]
    price = prod_data["price"]
    allergens = prod_data["allergens"]
    gender = prod_data["gender"]
    result = client.add_product(
        name=name, description=description, price=price, allergens=allergens, gender=gender
    )
    result_arr = []
    for result in result.records:
        result_arr.append(result.data())
    return result_arr

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337, reload=True)
