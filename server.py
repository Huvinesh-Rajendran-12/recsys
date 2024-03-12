import uvicorn
from fastapi import FastAPI
from model import get_product_recommendations

app = FastAPI()


@app.get("/api/v1/healthcheck")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/medicine/recommendations")
async def recommendations(query: str, limit: int):
    results = get_product_recommendations(query, limit)
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337, reload=True)
