import logging
from typing import List, Tuple
import vertexai
from llama_index.core import (
    QueryEngine,
    StorageContext,
    VectorStoreIndex
)
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class MwongozoQueryEngine:
    """Query engine for DevFest events using ReAct agents"""
    
    def __init__(
        self,
        project_id: str = "your-project-id",
        location: str = "us-central1"
    ):
        self.project_id = project_id
        self.location = location
        self.logger = logging.getLogger(__name__)
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Set up models
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        self.llm = Vertex("gemini-pro")
        
        self.query_tools = {}
        self.agent = None
        
    def load_event_index(self, event_name: str, persist_dir: str) -> QueryEngine:
        """Load vector index for an event"""
        try:
            event_dir = f"{persist_dir}/{event_name.lower()}"
            storage_context = StorageContext.from_defaults(persist_dir=event_dir)
            index = VectorStoreIndex.load_from_storage(storage_context)
            return index.as_query_engine(
                similarity_top_k=3,
                response_mode="tree_summarize"
            )
        except Exception as e:
            self.logger.error(f"Error loading index for {event_name}: {str(e)}")
            raise
            
    def setup_tools(self, persist_dir: str, events: List[str]):
        """Set up query tools for multiple events"""
        for event in events:
            query_engine = self.load_event_index(event, persist_dir)
            
            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=f"devfest_{event.lower()}",
                    description=f"""
                    Provides information about DevFest {event} sessions, 
                    speakers, schedules, and tracks. Use this tool for queries 
                    specific to DevFest {event}.
                    """
                )
            )
            
            self.query_tools[event.lower()] = tool
            
        # Create ReAct agent with all tools
        self.agent = ReActAgent.from_tools(
            list(self.query_tools.values()),
            llm=self.llm,
            verbose=True,
            system_prompt=self.get_system_prompt()
        )
        
    def get_system_prompt(self) -> str:
        """Get system prompt for the ReAct agent"""
        return """You are Mwongozo, a specialized AI assistant for DevFest events.
        Your purpose is to help attendees navigate event schedules and find relevant sessions.
        
        When answering queries:
        1. Always use the provided tools to fetch accurate information
        2. Compare information across events when relevant
        3. Provide clear, structured responses with specific details
        4. Include session times, rooms, and speaker information when available
        5. Make personalized recommendations based on user interests
        6. Highlight any unique aspects or special sessions
        
        Remember to:
        - Be concise but informative
        - Highlight technical sessions appropriately
        - Suggest related sessions when relevant
        - Mention any schedule conflicts or overlaps
        - Provide practical navigation tips
        
        Always verify information using the tools rather than relying on prior knowledge."""
        
    def query(self, query_text: str) -> Tuple[str, str]:
        """Execute a query and return response with explanation"""
        try:
            if not self.agent:
                raise ValueError("Query tools not initialized. Call setup_tools first.")
                
            response = self.agent.chat(query_text)
            return str(response), self.agent.last_observation
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    engine = MwongozoQueryEngine()
    engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
    
    # Test query
    response, explanation = engine.query(
        "Find me all AI and Machine Learning sessions in both DevFest events"
    )
    print("\nResponse:", response)
    print("\nExplanation:", explanation)