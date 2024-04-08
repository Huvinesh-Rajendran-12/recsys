import uvicorn
from fastapi import FastAPI
from model import get_product_recommendations
from database import get_user_data

app = FastAPI()


@app.get("/api/v1/healthcheck")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/medicine/recommendations")
async def recommendations(query: str, userId: int, limit: int, allergens: str = "None", gender: str = "Unisex"):
    (gender, date_of_birth, allergy) = get_user_data(userId)
    print(gender)
    print(date_of_birth)
    print(allergy)
    results = get_product_recommendations(query=query, limit=limit, allergens=allergy, gender=gender)
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337, reload=True)
