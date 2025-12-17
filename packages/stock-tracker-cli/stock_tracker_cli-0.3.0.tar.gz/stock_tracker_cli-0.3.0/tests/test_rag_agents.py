import os
import sys
import logging
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing modules that use them
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()
sys.modules['chromadb.errors'] = MagicMock()
sys.modules['tavily'] = MagicMock()

from src.rag.embeddings import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.processor import DocumentProcessor
from src.agents.orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_flow():
    logger.info("Testing RAG Flow...")
    
    # 1. Test Embeddings
    with patch('src.rag.embeddings.SentenceTransformer') as mock_model_cls:
        mock_model = MagicMock()
        mock_model.encode.return_value = MagicMock(tolist=lambda: [[0.1] * 384])
        mock_model_cls.return_value = mock_model
        
        embedding_service = EmbeddingService()
        embeddings = embedding_service.generate_embeddings(["Hello world"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 384
        logger.info("✅ Embeddings generated successfully (Mocked)")
    
    # 2. Test Processor
    text = "This is a test document. It has multiple sentences."
    chunks = DocumentProcessor.chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    logger.info("✅ Text chunking successful")
    
    # 3. Test Vector Store
    vector_store = VectorStore(persist_directory="/tmp/test_rag", embedding_service=embedding_service)
    
    mock_client = vector_store.client
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    
    vector_store.add_documents(["test"], [{"source": "test"}], ["id1"])
    
    mock_collection.add.assert_called_once()
    logger.info("✅ Vector Store add_documents verified (Mocked)")

def test_agent_orchestrator():
    logger.info("Testing Agent Orchestrator...")
    
    # Mock Groq client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"plan": [{"step_id": 1, "description": "Test step", "tool": "search_web", "query": "test"}]}'
    mock_client.chat.completions.create.return_value = mock_response
    
    orchestrator = AgentOrchestrator(model_client=mock_client)
    
    assert orchestrator.planner is not None
    assert orchestrator.researcher is not None
    assert orchestrator.analyst is not None
    assert orchestrator.decision_maker is not None
    
    logger.info("✅ Agent Orchestrator initialized successfully")

if __name__ == "__main__":
    try:
        test_rag_flow()
        test_agent_orchestrator()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        sys.exit(1)
