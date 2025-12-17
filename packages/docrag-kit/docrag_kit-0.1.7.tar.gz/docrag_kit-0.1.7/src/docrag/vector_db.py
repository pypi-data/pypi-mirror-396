"""Vector database management for DocRAG Kit."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import shutil
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv


class VectorDBManager:
    """Manages ChromaDB vector database operations."""

    def __init__(self, config: Dict[str, Any], project_root: Optional[Path] = None):
        """
        Initialize vector database manager.
        
        Args:
            config: Configuration dictionary containing LLM and retrieval settings.
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.config = config
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.db_path = self.project_root / ".docrag" / "vectordb"
        
        # Load environment variables
        load_dotenv(self.project_root / ".env")
        
        # Initialize embeddings
        self.embeddings = self._init_embeddings()
        
        # Store previous provider for change detection
        self._previous_provider = None

    def _init_embeddings(self):
        """
        Initialize embeddings based on configured provider.
        
        Returns:
            Embeddings instance (OpenAIEmbeddings or GoogleGenerativeAIEmbeddings).
        
        Raises:
            ValueError: If provider is not supported or API key is missing.
        """
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider', 'openai')
        embedding_model = llm_config.get('embedding_model')
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "ERROR: OpenAI API key not found.\n"
                    "   Add OPENAI_API_KEY to your .env file.\n"
                    "   Get your API key from: https://platform.openai.com/api-keys"
                )
            
            return OpenAIEmbeddings(
                model=embedding_model or 'text-embedding-3-small',
                openai_api_key=api_key
            )
        
        elif provider == 'gemini':
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError(
                    "ERROR: Google API key not found.\n"
                    "   Add GOOGLE_API_KEY to your .env file.\n"
                    "   Get your API key from: https://makersuite.google.com/app/apikey"
                )
            
            return GoogleGenerativeAIEmbeddings(
                model=embedding_model or 'models/embedding-001',
                google_api_key=api_key
            )
        
        else:
            raise ValueError(
                f"ERROR: Unsupported provider: {provider}\n"
                f"   Supported providers: openai, gemini"
            )

    def create_database(self, chunks: List[Document], show_progress: bool = True) -> None:
        """
        Create new vector database from chunks.
        
        Args:
            chunks: List of Document chunks to index.
            show_progress: Whether to display progress information.
        
        Raises:
            Exception: If database creation fails.
        """
        if not chunks:
            raise ValueError("ERROR: No chunks provided for indexing")
        
        # Ensure .docrag directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Delete existing database if it exists
        if self.db_path.exists():
            self.delete_database()
        
        if show_progress:
            print(f"📊 Creating embeddings for {len(chunks)} chunks...")
        
        try:
            # Create ChromaDB vector store
            # Chroma will automatically create embeddings for all chunks
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.db_path)
            )
            
            if show_progress:
                print(f"SUCCESS: Vector database created successfully at {self.db_path}")
        
        except Exception as e:
            raise Exception(f"ERROR: Failed to create vector database: {e}")

    def delete_database(self) -> None:
        """
        Delete existing vector database.
        
        This removes the .docrag/vectordb/ directory and all its contents.
        """
        if self.db_path.exists():
            try:
                shutil.rmtree(self.db_path)
            except Exception as e:
                print(f"WARNING:  Warning: Failed to delete database: {e}")

    def get_retriever(self, top_k: Optional[int] = None):
        """
        Get retriever for querying the vector database.
        
        Args:
            top_k: Number of top results to retrieve. If None, uses config value.
        
        Returns:
            VectorStoreRetriever instance.
        
        Raises:
            ValueError: If database doesn't exist.
        """
        if not self.db_path.exists():
            raise ValueError(
                "ERROR: Vector database not found.\n"
                "   Run 'docrag index' to create the database first."
            )
        
        # Use provided top_k or fall back to config
        if top_k is None:
            retrieval_config = self.config.get('retrieval', {})
            top_k = retrieval_config.get('top_k', 5)
        
        # Load existing vector store
        vectorstore = Chroma(
            persist_directory=str(self.db_path),
            embedding_function=self.embeddings
        )
        
        # Create and return retriever
        return vectorstore.as_retriever(
            search_kwargs={"k": top_k}
        )

    def list_documents(self) -> List[str]:
        """
        List all unique source files in the database.
        
        Returns:
            Sorted list of unique source file names.
        
        Raises:
            ValueError: If database doesn't exist.
        """
        if not self.db_path.exists():
            raise ValueError(
                "ERROR: Vector database not found.\n"
                "   Run 'docrag index' to create the database first."
            )
        
        # Load existing vector store
        vectorstore = Chroma(
            persist_directory=str(self.db_path),
            embedding_function=self.embeddings
        )
        
        # Get all documents
        # We need to query with a dummy search to get all documents
        # ChromaDB doesn't have a direct "get all" method, so we use get()
        collection = vectorstore._collection
        results = collection.get()
        
        # Extract unique source files from metadata
        source_files = set()
        if results and 'metadatas' in results:
            for metadata in results['metadatas']:
                if metadata and 'source_file' in metadata:
                    source_files.add(metadata['source_file'])
                elif metadata and 'source' in metadata:
                    # Fallback to extracting filename from full path
                    source_path = Path(metadata['source'])
                    source_files.add(source_path.name)
        
        # Return sorted list
        return sorted(list(source_files))

    def detect_provider_change(self, previous_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Detect if LLM provider has changed from previous configuration.
        
        Args:
            previous_config: Previous configuration dictionary. If None, loads from file.
        
        Returns:
            True if provider has changed, False otherwise.
        """
        if previous_config is None:
            # Try to load previous config from a stored file
            config_path = self.project_root / ".docrag" / "config.yaml"
            if not config_path.exists():
                return False
            
            import yaml
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    previous_config = yaml.safe_load(f)
            except Exception:
                return False
        
        # Get current and previous providers
        current_provider = self.config.get('llm', {}).get('provider')
        previous_provider = previous_config.get('llm', {}).get('provider')
        
        # Check if provider changed
        if previous_provider and current_provider != previous_provider:
            return True
        
        return False
    
    def check_reindex_required(self) -> Optional[str]:
        """
        Check if reindexing is required due to configuration changes.
        
        Returns:
            Warning message if reindexing is required, None otherwise.
        """
        if self.detect_provider_change():
            return (
                "WARNING:  WARNING: LLM provider has changed!\n"
                "   Different providers use different embedding dimensions.\n"
                "   You must run 'docrag reindex' to rebuild the vector database."
            )
        
        return None
