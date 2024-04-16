POST http://0.0.0.0:1337/api/v1/products/add
{
    "name": "sore throat reliever",
    "description": "relieves sore throat pain",
    "price": "MYR 10.00",
    "allergens": "Not-Known",
    "gender": "Unisex"
}
HTTP 200
[Captures]
results: jsonpath "$"
