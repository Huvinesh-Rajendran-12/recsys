from typing import Any, Dict, List
from neo4j import GraphDatabase
from sentence_transformers.SentenceTransformer import ndarray


class Neo4jClient:
    def __init__(self, uri, username, password, database=None):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        self.driver.close()

    def hello(self):
        result = self.driver.execute_query("MATCH (n) RETURN n LIMIT 1")
        print(result)
        return result

    def get_product_recommendations(self, query_embeddings: ndarray, limit: int):
        query = """CALL db.index.vector.queryNodes(`product_text_embeddings`,
                                                   $limit, $queryVector),
        YIELD node AS product, score,
                RETURN product.productCode AS productCode, product.text AS text,
                score"""
        result = self.driver.execute_query(
                query,
                parameters={
                    "queryVector": query_embeddings,
                    "limit": limit,
                    },
                )
        print(result)
        return result

    def store_product_vector_embeddings(self, data: List[Dict[str, Any]], index_name: str):
        i: int = 0
        chunk_size: int = 100
        total_size: int = len(data)
        print("Total embeddings: {}".format(total_size))
        while i < total_size:
            chunk_end = min(i + chunk_size, total_size)
            rows = data[i:chunk_end]
            query = """
            UNWIND $data AS row
            CREATE(p:Product {name: row.name, price: row.price})
            CALL db.create.setNodeVectorProperty(p, "textEmbedding", row.textEmbedding)
            RETURN count(n) AS propertySetCount
            """
            self.driver.execute_query(query, parameters={"data": rows})
            print("Stored {} of {} embeddings".format(i + chunk_size, total_size))
            i += chunk_size
        query_ = """
        CREATE VECTOR INDEX $index_name IF NOT EXISTS FOR (n:Product) ON 
        (n.textEmbedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: toInteger($dim),
            `vector.similarity_function`: 'cosine'
            }}
        """
        result = self.driver.execute_query(
                query_, parameters={"dim": 784, "index_name": index_name}
                )
        return result
