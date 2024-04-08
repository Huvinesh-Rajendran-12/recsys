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
        result = self.driver.execute_query(
            "CREATE(g:Greeting {greeting: 'Hello'}) return g.greeting",
            database_=self.database,
        )
        print(result)
        return result

    def get_product_recommendations(
        self,
        query_embeddings: ndarray,
        limit: int = 5,
        allergens: str = "None",
        gender: str = "Unisex",
        index_vector: str = "product_text_embeddings",
    ):
        if allergens == "Not-Known":
            query = """CALL db.index.vector.queryNodes('product_text_embeddings',
             $limit, $queryVector)
            YIELD node AS product, score
            WHERE score > 0.65
            MATCH(product)-[:HAS_ALLERGY]->(a:Allergens),
            (product)-[:GENDER]->(g:Gender)
            where (g.type = $gender or g.type = "Unisex")
            RETURN product.name as name,product.description as description,product.price as price, score"""
        else:
            query = """CALL db.index.vector.queryNodes('product_text_embeddings',
             $limit, $queryVector)
            YIELD node AS product, score
            WHERE score > 0.65
            MATCH(product)-[:HAS_ALLERGY]->(a:Allergens),
            (product)-[:GENDER]->(g:Gender)
            where a.type <> $allergens and (g.type = $gender or g.type = "Unisex")
            RETURN product.name as name,product.description as description,product.price as price, score"""
        result = self.driver.execute_query(
            query,
            index_vector_name=index_vector,
            queryVector=query_embeddings,
            allergens=allergens,
            gender=gender,
            limit=limit,
            database_=self.database,
        )
        print(result)
        return result

    def store_product_vector_embeddings(
        self, data: List[Dict[str, Any]], index_name: str
    ):
        i: int = 0
        chunk_size: int = 100
        total_size: int = len(data)
        print("Total embeddings: {}".format(total_size))
        while i < total_size:
            chunk_end = min(i + chunk_size, total_size)
            rows = data[i:chunk_end]
            query = """
            UNWIND $data AS row
            CREATE(p:Product {name: row.name, description: row.description, 
            price: row.price})-[:HAS_ALLERGY]->(a:Allergens {type: row.allergen})
            , (p)-[:GENDER]->(g:Gender {type: row.gender})
            SET p.textEmbedding = row.embeddings
            """
            result = self.driver.execute_query(
                query, data=rows, database_=self.database
            )
            print("Stored {} of {} embeddings".format(i + chunk_size, total_size))
            i += chunk_size
        query_ = """
        CREATE VECTOR INDEX $index_name FOR (n:Product) ON 
        (n.textEmbedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: toInteger($dim),
            `vector.similarity_function`: 'cosine'
            }}
        """
        result = self.driver.execute_query(query_, dim=1024, index_name=index_name)
        return result
