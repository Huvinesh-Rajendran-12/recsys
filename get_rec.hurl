GET http://0.0.0.0:1337/api/v1/medicine/recommendations
[QueryStringParams]
query: I have red eye 
limit: 5
HTTP 200
[Captures]
results: jsonpath "$"

