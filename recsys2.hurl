GET http://0.0.0.0:1337/api/medicine/recommend
[QueryStringParams]
query: My eyes are itchy and red
limit: 5
HTTP 200
[Captures]
ids: jsonpath "$['ids']"
recommendations: jsonpath "$['recommendations']"
score: jsonpath "$['score']"
