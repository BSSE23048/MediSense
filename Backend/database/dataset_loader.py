"""
Dataset Loader - Initialize medical knowledge base for RAG
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import RAGService
from config import Config

def load_medical_dataset():
    """
    Load medical dataset into vector store
    This is a placeholder - implement with actual medical data sources
    """
    print("Initializing medical knowledge base...")
    
    rag_service = RAGService()
    
    # Example medical knowledge entries
    # In production, load from WHO/NIH datasets
    sample_entries = [
        {
            "text": "Influenza (Flu) is a viral infection that affects the respiratory system. Common symptoms include fever, cough, sore throat, body aches, and fatigue. It typically resolves within 1-2 weeks with rest and hydration.",
            "metadata": {"source": "WHO", "category": "infectious_disease"}
        },
        {
            "text": "Type 2 Diabetes is a chronic condition characterized by high blood sugar levels. Symptoms include increased thirst, frequent urination, fatigue, and blurred vision. Management involves diet, exercise, and medication.",
            "metadata": {"source": "NIH", "category": "chronic_disease"}
        },
        {
            "text": "Migraine is a neurological condition causing severe headaches, often accompanied by sensitivity to light, nausea, and vomiting. Triggers include stress, certain foods, and hormonal changes.",
            "metadata": {"source": "NIH", "category": "neurological"}
        }
    ]
    
    print(f"Loading {len(sample_entries)} medical knowledge entries...")
    
    for entry in sample_entries:
        success = rag_service.add_medical_document(
            entry["text"],
            entry.get("metadata", {})
        )
        if success:
            print(f"✓ Loaded: {entry['metadata'].get('category', 'unknown')}")
        else:
            print(f"✗ Failed to load entry")
    
    print("Medical knowledge base initialization complete!")
    print(f"Vector store location: {Config.CHROMA_DB_PATH}")

if __name__ == '__main__':
    load_medical_dataset()

