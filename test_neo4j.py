import logging

from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import DriverError, Neo4jError


class App:

    def __init__(self, uri, user, password, database=None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        # Don't forget to close the driver connection when you are finished
        # with it
        self.driver.close()

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and
            # transient errors
            result = self._create_and_return_friendship(person1_name, person2_name)
            print("Created friendship between: " f"{result['p1']}, {result['p2']}")

    def _create_and_return_friendship(self, person1_name, person2_name):

        # To learn more about the Cypher syntax,
        # see https://neo4j.com/docs/cypher-manual/current/

        # The Cheat Sheet is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-cheat-sheet/

        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1.name, p2.name"
        )
        try:
            record = self.driver.execute_query(
                query,
                person1_name=person1_name,
                person2_name=person2_name,
                database_=self.database,
                result_transformer_=lambda r: r.single(strict=True),
            )
            return {"p1": record["p1.name"], "p2": record["p2.name"]}
        # Capture any errors along with the query and data for traceability
        except (DriverError, Neo4jError) as exception:
            logging.error("%s raised an error: \n%s", query, exception)
            raise

    def find_person(self, person_name):
        names = self._find_and_return_person(person_name)
        for name in names:
            print(f"Found person: {name}")

    def _find_and_return_person(self, person_name):
        query = (
            "MATCH (p:Person) " "WHERE p.name = $person_name " "RETURN p.name AS name"
        )
        names = self.driver.execute_query(
            query,
            person_name=person_name,
            database_=self.database,
            routing_=RoutingControl.READ,
            result_transformer_=lambda r: r.value("name"),
        )
        return names


if __name__ == "__main__":
    # For Aura specific connection URI,
    # see https://neo4j.com/developer/aura-connect-driver/ .
    scheme = "bolt"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "127.0.0.1"
    port = 7687
    uri = f"{scheme}://{host_name}:{port}"
    user = "huvi"
    password = "huvinesh#"
    database = "neo4j"
    app = App(uri, user, password, database)
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()
    try:
        app.create_friendship("Alice", "David")
        app.find_person("Alice")
    finally:
        app.close()
