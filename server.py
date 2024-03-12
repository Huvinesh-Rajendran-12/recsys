from sanic import Blueprint, Sanic
from sanic.exceptions import SanicException
from sanic.response import json
from model import get_product_recommendations

app = Sanic("TelemeRecsys")


@app.get("/")
async def index(request):
    return json({"message": "Hello World"})

@app.get("api/medicine/recommend", name="product_recommendation")
async def recommender(request):
    query = request.args.get("query")
    limit = int(request.args.get("limit", 5))
    recs = get_product_recommendations(query, limit)
    if recs is None:
        raise SanicException(status_code=500, message="Internal Server Error")
    return json(recs)


assert app.url_for("product_recommendation", query="eye", limit=5) == "/api/medicine/recommend?query=eye&limit=5"


