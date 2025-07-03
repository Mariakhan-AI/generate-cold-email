import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path="C:/Users/Administrator/Documents/cold email/portfolio.csv"):
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                combined_text = f"{row['Title']} - {row['Description']} - {row['Techstack']}"
                self.collection.add(
                    documents=[combined_text],
                    metadatas={
                        "title": row["Title"],
                        "description": row["Description"],
                        "link": row["Links"],
                    },
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills_list):
        result = self.collection.query(query_texts=skills_list, n_results=2)
        return result.get("metadatas", [[]])[0]
