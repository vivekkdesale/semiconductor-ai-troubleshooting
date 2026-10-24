from neo4j import GraphDatabase

from semiconductor.config import Settings


class KnowledgeGraph:
    def __init__(self, settings: Settings):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )

    def ensure_schema(self) -> None:
        queries = [
            "CREATE CONSTRAINT equipment_id IF NOT EXISTS FOR (n:Equipment) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT sensor_id IF NOT EXISTS FOR (n:Sensor) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT failure_id IF NOT EXISTS FOR (n:FailureMode) REQUIRE n.id IS UNIQUE",
        ]
        with self.driver.session() as session:
            for query in queries:
                session.run(query).consume()

    def close(self) -> None:
        self.driver.close()
