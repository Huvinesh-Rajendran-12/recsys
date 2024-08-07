import uvicorn
from fastapi import FastAPI
from model import get_product_recommendations
from database import get_user_data

app = FastAPI()


@app.get("/api/v1/healthcheck")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/medicine/recommendations")
async def recommendations(userId: int, limit: int, allergens: str = "None", gender: str = "Unisex"):
    (diagnosis, gender, allergy) = get_user_data(userId)
    results = get_product_recommendations(query=diagnosis, limit=limit, allergens=allergy, gender=gender)
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337, reload=True)
