import os
import pandas as pd
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
COLLECTION_NAME: str = "drugs_knowledge_base"
DB_PATH: str = "qdrant_db"
DATASET_PATH: str = "drugs_dataset.csv"

def index_data(limit: Optional[int] = None) -> None:
    print("--- ⚙️ Initializing Embedding Model ---")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"--- 🔌 Connecting to Qdrant Local ({DB_PATH}) ---")
    client = QdrantClient(path=DB_PATH)
    
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"❌ Error: '{DATASET_PATH}' not found. Please move the CSV to the root folder.")

    df = pd.read_csv(DATASET_PATH).fillna("Unknown")
    print(f"--- 📂 Loaded {len(df)} records. Indexing... ---")

    points: List[PointStruct] = []
    batch_size: int = 100
    
    data_iterator = df.head(limit) if limit else df

    for index, row in data_iterator.iterrows():
        semantic_text = (
            f"Drug Name: {row.get('drug_name', 'Unknown')}. "
            f"Condition: {row.get('medical_condition', 'Unknown')}. "
            f"Side Effects: {row.get('side_effects', '')}."
        )
        
        embedding = model.encode(semantic_text).tolist()
        
        payload: Dict[str, Any] = {
            "drug_name": row.get('drug_name', 'Unknown'),
            "condition": row.get('medical_condition', 'Unknown'),
            "rx_otc": row.get('rx_otc', 'Rx'),
            "pregnancy_category": str(row.get('pregnancy_category', 'N')), 
            "side_effects": str(row.get('side_effects', 'Unknown'))[:500] 
        }
        
        points.append(PointStruct(id=index, vector=embedding, payload=payload))
        
        if len(points) >= batch_size:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            points = []

    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
    
    print(f"--- ✅ SUCCESS: Knowledge Base built at '{DB_PATH}' ---")

if __name__ == "__main__":
    index_data()