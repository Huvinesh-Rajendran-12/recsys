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

    def get_products(self):
        result = self.driver.execute_query(
            """MATCH (p:Product), (p)-->(a:Allergens), (p)-->(g:Gender)
                RETURN p.name as name,p.description as description,p.price as
                price, a.type as allergens, g.type as gender""",
            database_=self.database,
        )
        result_arr = []
        for result in result.records:
            result_arr.append(result.data())
        return result_arr

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
        print(len(result))
        return result

    def check_vector_index_exists(self, index_name: str) -> bool:
        query = """show indexes yield name where name = $index_name return *"""
        result = self.driver.execute_query(
            query, index_name=index_name, database_=self.database
        )
        if len(result) == 0:
            return False
        else:
            return True

    def add_product(self, name: str, description: str, price: int, 
                    allergens: str, gender: str, embeddings: List[float]):
        query = """
        CREATE(p:Product {name: $name, description: $description, price: $price})
        -[:HAS_ALLERGY]->(a:Allergens {type: $allergens}),
        (p)-[:GENDER]->(g:Gender {type: $gender}) set p.textEmbedding = $embeddings
        return p
        """
        result = self.driver.execute_query(query, name=name, description=description, 
        price=price, allergens=allergens, 
        gender=gender, embeddings=embeddings,  database_=self.database)
        return result

    def store_product_vector_embeddings(
            self, data: List[Dict[str, Any]], index_name: str, 
            embedding_dim: int = 1024
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
            price: row.price})-[:HAS_ALLERGY]->(a:Allergens {type: row.allergens})
            , (p)-[:GENDER]->(g:Gender {type: row.gender})
            SET p.textEmbedding = row.embeddings
            """
            self.driver.execute_query(query, data=rows, database_=self.database)
            print("Stored {} of {} embeddings".format(i + chunk_size, total_size))
            i += 1
        is_index_exists = self.check_vector_index_exists(index_name)
        if is_index_exists is False:
            query_ = """
            CREATE VECTOR INDEX $index_name FOR (n:Product) ON 
            (n.textEmbedding)
            OPTIONS {indexConfig: {
                `vector.dimensions`: toInteger($dim),
                `vector.similarity_function`: 'cosine'
                }}
            """
            self.driver.execute_query(query_, dim=embedding_dim, 
                                      index_name=index_name)
