import os

class DatabaseConnections:
    _chroma_client = None
    _neo4j_driver = None

    @classmethod
    def get_chroma_client(cls):
        if cls._chroma_client is None:
            try:
                import chromadb
                chroma_path = os.path.join(os.path.dirname(__file__), "chromadb")
                cls._chroma_client = chromadb.PersistentClient(path=chroma_path)
            except Exception as e:
                print(f"[database] ChromaDB not available ({e}), using fallback")
                cls._chroma_client = False
        return cls._chroma_client if cls._chroma_client is not False else None

    @classmethod
    def get_neo4j_driver(cls):
        if cls._neo4j_driver is None:
            try:
                from neo4j import GraphDatabase
                uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
                user = os.environ.get("NEO4J_USER", "neo4j")
                password = os.environ.get("NEO4J_PASSWORD", "password")
                cls._neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
            except Exception as e:
                print(f"[database] Neo4j not available ({e}), using fallback")
                cls._neo4j_driver = False
        return cls._neo4j_driver if cls._neo4j_driver is not False else None

    @classmethod
    def close_all(cls):
        try:
            if cls._neo4j_driver and cls._neo4j_driver is not False:
                cls._neo4j_driver.close()
        except Exception:
            pass
