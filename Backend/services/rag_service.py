"""
RAG Service - Retrieval Augmented Generation for medical knowledge
"""

from config import Config

class RAGService:
    """Service for RAG-based medical knowledge retrieval"""
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings_model = None
        self._init_rag()
    
    def _init_rag(self):
        """Initialize RAG components (vector store and embeddings)"""
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            
            # Initialize embeddings model
            self.embeddings_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection("medical_knowledge")
            except:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection("medical_knowledge")
                # Load initial dataset if available
                self._load_initial_dataset()
                
        except ImportError as e:
            print(f"Warning: RAG components not fully initialized. {str(e)}")
            print("RAG will work in fallback mode. Install: pip install chromadb sentence-transformers")
            self.collection = None
    
    def _load_initial_dataset(self):
        """Load initial medical dataset into vector store"""
        # This will be implemented when dataset is available
        # For now, we'll use a fallback approach
        pass
    
    def retrieve_medical_context(self, query, top_k=None):
        """
        Retrieve relevant medical context for a query
        
        Args:
            query: User query (symptoms, condition, etc.)
            top_k: Number of results to retrieve (default from config)
            
        Returns:
            String with relevant medical context
        """
        if not self.collection or not self.embeddings_model:
            # Fallback: return empty context (LLM will still work)
            return ""
        
        try:
            top_k = top_k or Config.TOP_K_RESULTS
            
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query).tolist()
            
            # Search in vector store
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Combine retrieved documents
            if results['documents'] and len(results['documents'][0]) > 0:
                context = "\n\n".join(results['documents'][0])
                return context
            else:
                return ""
                
        except Exception as e:
            print(f"RAG retrieval error: {str(e)}")
            return ""

    def build_context_bundle(self, query, user_context="", conversation_memory="", top_k=None):
        """
        Build a multi-source context bundle for symptom and follow-up workflows.
        """
        medical_context = self.retrieve_medical_context(query, top_k=top_k)
        sources = []
        merged_parts = []

        if medical_context:
            merged_parts.append(f"Medical Corpus Context:\n{medical_context}")
            sources.append("medical_corpus")
        if user_context:
            merged_parts.append(f"User Report Context:\n{user_context}")
            sources.append("report")
        if conversation_memory:
            merged_parts.append(f"Conversation Memory:\n{conversation_memory}")
            sources.append("conversation_memory")

        return {
            "context": "\n\n".join(merged_parts).strip(),
            "sources": sources,
        }
    
    def add_medical_document(self, text, metadata=None):
        """
        Add a medical document to the knowledge base
        
        Args:
            text: Medical document text
            metadata: Optional metadata dictionary
        """
        if not self.collection or not self.embeddings_model:
            return False
        
        try:
            # Generate embedding
            embedding = self.embeddings_model.encode(text).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}],
                ids=[f"doc_{len(self.collection.get()['ids'])}"]
            )
            
            return True
        except Exception as e:
            print(f"Error adding document to RAG: {str(e)}")
            return False

