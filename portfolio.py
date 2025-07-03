import pandas as pd
import uuid
import logging
import os
from typing import List, Dict, Any

# Fix SQLite issue for Streamlit Cloud
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import chromadb
from chromadb.config import Settings

class Portfolio:
    def __init__(self, file_path=None):
        """Initialize Portfolio with ChromaDB"""
        # Handle file path
        if file_path is None:
            possible_paths = [
                "portfolio.csv",
                "data/portfolio.csv",
                os.path.join(os.getcwd(), "portfolio.csv")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.file_path = path
                    break
            else:
                self.file_path = None
                logging.warning("No portfolio CSV found. Creating default portfolio.")
        else:
            self.file_path = file_path
        
        # Load portfolio data
        self.data = self._load_portfolio_data()
        
        # Initialize ChromaDB with proper settings
        try:
            self.chroma_client = chromadb.Client(
                Settings(
                    chroma_api_impl="chromadb.api.ephemeral.EphemeralAPI",
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self.collection = self.chroma_client.get_or_create_collection(
                name="portfolio",
                metadata={"description": "Portfolio projects and skills"}
            )
            
            logging.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB: {e}")
            # Fallback to simple in-memory storage
            self.use_fallback = True
            self.fallback_data = []
    
    def _load_portfolio_data(self) -> pd.DataFrame:
        """Load portfolio data from CSV or create default data"""
        if self.file_path and os.path.exists(self.file_path):
            try:
                data = pd.read_csv(self.file_path)
                logging.info(f"Portfolio data loaded from {self.file_path}")
                return data
            except Exception as e:
                logging.error(f"Error loading portfolio CSV: {e}")
                return self._create_default_portfolio()
        else:
            return self._create_default_portfolio()
    
    def _create_default_portfolio(self) -> pd.DataFrame:
        """Create a default portfolio with sample data"""
        default_data = {
            'Techstack': [
                'Python, Django, PostgreSQL, AWS, Docker',
                'React, Node.js, MongoDB, Express.js, JavaScript',
                'Machine Learning, TensorFlow, Python, Data Analysis',
                'Java, Spring Boot, MySQL, Microservices, Kubernetes',
                'Vue.js, PHP, Laravel, Redis, API Development',
                'Python, FastAPI, SQLAlchemy, PostgreSQL, REST APIs',
                'React Native, Mobile Development, Firebase, iOS, Android',
                'DevOps, CI/CD, Jenkins, AWS, Terraform, Monitoring'
            ],
            'Links': [
                'https://github.com/example/django-ecommerce',
                'https://github.com/example/react-dashboard',
                'https://github.com/example/ml-prediction-model',
                'https://github.com/example/spring-microservices',
                'https://github.com/example/vue-portfolio',
                'https://github.com/example/fastapi-backend',
                'https://github.com/example/mobile-app',
                'https://github.com/example/devops-pipeline'
            ],
            'Title': [
                'E-commerce Platform',
                'Admin Dashboard',
                'ML Prediction System',
                'Microservices Architecture',
                'Portfolio Website',
                'API Backend Service',
                'Mobile Application',
                'DevOps Pipeline'
            ],
            'Description': [
                'Full-stack e-commerce platform with payment integration',
                'Real-time analytics dashboard with interactive charts',
                'Machine learning model for predictive analytics',
                'Scalable microservices with containerization',
                'Responsive portfolio website with modern UI',
                'High-performance API backend with authentication',
                'Cross-platform mobile app with offline capability',
                'Automated CI/CD pipeline with monitoring'
            ]
        }
        
        logging.info("Created default portfolio data")
        return pd.DataFrame(default_data)
    
    def load_portfolio(self):
        """Load the portfolio data into the vector database"""
        try:
            if hasattr(self, 'use_fallback') and self.use_fallback:
                # Use fallback storage
                self.fallback_data = []
                for _, row in self.data.iterrows():
                    self.fallback_data.append({
                        'title': str(row.get("Title", "")),
                        'techstack': str(row.get("Techstack", "")),
                        'link': str(row.get("Links", "")),
                        'description': str(row.get("Description", ""))
                    })
                logging.info(f"Loaded {len(self.fallback_data)} items using fallback storage")
                return
            
            if not self.collection.count():
                documents = []
                metadatas = []
                ids = []
                
                for _, row in self.data.iterrows():
                    tech_stack = str(row.get("Techstack", ""))
                    title = str(row.get("Title", ""))
                    description = str(row.get("Description", ""))
                    
                    document = f"{title} {tech_stack} {description}".strip()
                    
                    metadata = {
                        "link": str(row.get("Links", "")),
                        "title": title,
                        "description": description,
                        "techstack": tech_stack
                    }
                    
                    documents.append(document)
                    metadatas.append(metadata)
                    ids.append(str(uuid.uuid4()))
                
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logging.info(f"Loaded {len(documents)} portfolio items into ChromaDB")
            else:
                logging.info("Portfolio already loaded in ChromaDB")
                
        except Exception as e:
            logging.error(f"Error loading portfolio: {e}")
            # Fall back to simple storage
            self.use_fallback = True
            self.load_portfolio()
    
    def query_links(self, skills: List[str], n_results: int = 3) -> List[Dict[str, Any]]:
        """Query the most relevant portfolio links"""
        if not skills:
            return []
        
        try:
            # Use fallback if ChromaDB failed
            if hasattr(self, 'use_fallback') and self.use_fallback:
                return self._fallback_query(skills, n_results)
            
            query_text = " ".join(skills)
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, self.collection.count())
            )
            
            portfolio_links = []
            metadatas = results.get('metadatas', [[]])
            
            if metadatas and metadatas[0]:
                for metadata in metadatas[0]:
                    portfolio_links.append({
                        'title': metadata.get('title', 'Project'),
                        'link': metadata.get('link', ''),
                        'description': metadata.get('description', ''),
                        'techstack': metadata.get('techstack', '')
                    })
            
            logging.info(f"Found {len(portfolio_links)} relevant portfolio projects")
            return portfolio_links
            
        except Exception as e:
            logging.error(f"Error querying portfolio links: {e}")
            return self._fallback_query(skills, n_results)
    
    def _fallback_query(self, skills: List[str], n_results: int = 3) -> List[Dict[str, Any]]:
        """Fallback query method using simple string matching"""
        if not hasattr(self, 'fallback_data'):
            self.load_portfolio()
        
        scored_projects = []
        skills_lower = [skill.lower() for skill in skills]
        
        for project in self.fallback_data:
            score = 0
            project_text = f"{project['title']} {project['techstack']} {project['description']}".lower()
            
            for skill in skills_lower:
                if skill in project_text:
                    score += 1
            
            if score > 0:
                scored_projects.append((score, project))
        
        # Sort by score and return top results
        scored_projects.sort(key=lambda x: x[0], reverse=True)
        return [project for _, project in scored_projects[:n_results]]
       
