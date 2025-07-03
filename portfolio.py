import pandas as pd
import chromadb
from chromadb.config import Settings
import uuid

class Portfolio:
    def __init__(self, file_path="C:/Users\Administrator\Documents\generate email"):
        """
        Initializes the Portfolio class:
        - Reads the CSV with your portfolio items.
        - Sets up ChromaDB with in-memory EphemeralAPI to avoid sqlite issues.
        - Creates or retrieves a collection named 'portfolio'.
        """
        self.file_path = file_path
        self.data = pd.read_csv(file_path)

        # Use ChromaDB in-memory only, avoiding sqlite
        self.chroma_client = chromadb.Client(
            Settings(
                chroma_api_impl="chromadb.api.ephemeral.EphemeralAPI"
            )
        )

        # Create or get the 'portfolio' collection
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        """
        Loads the portfolio data into the vector database.
        Only loads if the collection is currently empty.
        """
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row["Techstack"]],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        """
        Given a list of skills, queries the vector database
        and returns the most relevant portfolio links.
        """
        results = self.collection.query(query_texts=skills, n_results=2)
        return results.get('metadatas', [])
