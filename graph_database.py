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
                RETURN distinct p.id as id, p.name as name,p.description as description,p.price as
                price, a.type as allergens, g.type as gender order by p.id DESC""",
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
            RETURN distinct product.id as id, product.name as name,product.description as description,product.price as price, score"""
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

    def add_product(self, name: str, description: str, price: str, 
                    allergens: str, gender: str, embeddings: List[float]):
        query = """
        MATCH(i:Index {name: "product_index"})
        SET i.value = i.value + 1
        CREATE(p:Product {id: i.value, name: $name, description: $description, price: $price}),
        (p)-[:HAS_ALLERGY]->(a:Allergens {type: $allergens}),
        (p)-[:GENDER]->(g:Gender {type: $gender}) set p.textEmbedding = $embeddings
        return p.id as id
        """
        result = self.driver.execute_query(query, name=name, description=description, 
        price=price, allergens=allergens, 
        gender=gender, embeddings=embeddings[0],  database_=self.database)
        return result

    def edit_product(self, id: int, name: str, description: str, price: str, 
                     allergens: str, gender: str, embeddings: List[float]):
        query = """
        MATCH (p:Product {id: $id}), (p)-->(a:Allergens), (p)-->(g:Gender)
        SET p.name = $name, p.description = $description, p.price = $price,
        p.textEmbedding = $embeddings,
        a.type = $allergens, g.type = $gender
        return distinct p.id as id
        """
        result = self.driver.execute_query(query, id=id, name=name, 
                                           description=description, price=price,
                                           embeddings=embeddings[0], allergens=allergens,
        gender=gender, database_=self.database)
        return result

    def create_product_index_constraint(self):
        query = """
        CREATE CONSTRAINT product_id IF NOT EXISTS FOR  (p:Product) REQUIRE p.id IS UNIQUE
        """
        result = self.driver.execute_query(query, database_=self.database)
        return result

    def create_product_index(self):
        query="""
        MERGE (i:Index {name: 'product_index'})
        ON CREATE SET i.value = 0
        RETURN i
        """
        result = self.driver.execute_query(query, database_=self.database)
        return result

    def store_product_vector_embeddings(
            self, data: List[Dict[str, Any]], index_name: str, 
            embedding_dim: int = 1024
    ):
        i: int = 0
        chunk_size: int = 100
        total_size: int = len(data)
        self.create_product_index()
        self.create_product_index_constraint()
        print("Total embeddings: {}".format(total_size))
        while i < total_size:
            chunk_end = min(i + chunk_size, total_size)
            rows = data[i:chunk_end]
            query = """
            UNWIND $data AS row
            MATCH(i:Index {name: 'product_index'})
            SET i.value = row.id
            CREATE(p:Product {id: row.id, name: row.name, description: row.description, 
            price: row.price})-[:HAS_ALLERGY]->(a:Allergens {type: row.allergens})
            , (p)-[:GENDER]->(g:Gender {type: row.gender})
            SET p.textEmbedding = row.embeddings
            """
            self.driver.execute_query(query, data=rows, database_=self.database)
            print("Stored {} of {} embeddings".format(i + chunk_size, total_size))
            i += chunk_size
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
