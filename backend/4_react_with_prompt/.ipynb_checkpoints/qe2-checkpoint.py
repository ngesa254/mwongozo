# query_engine.py

import logging
import os
import yaml
from typing import List, Tuple, Dict, Optional
import vertexai
from llama_index.core import (
    QueryEngine,
    StorageContext,
    VectorStoreIndex,
    PromptTemplate
)
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class PromptTemplateLoader:
    """Loads and manages prompt templates from markdown file"""
    
    @staticmethod
    def load_prompts(prompt_file_path: str) -> Dict[str, str]:
        """Load prompt templates from markdown file"""
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse sections from markdown
            sections = {}
            current_section = None
            current_content = []
            
            for line in content.split('\n'):
                if line.startswith('##'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = line.strip('# ').lower().replace(' ', '_')
                    current_content = []
                else:
                    current_content.append(line)
                    
            # Add last section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
                
            # Extract templates from code blocks
            templates = {}
            for section, content in sections.items():
                code_blocks = content.split('```')
                if len(code_blocks) > 1:
                    # Get content between ``` marks
                    template = code_blocks[1].strip()
                    templates[section] = template
                    
            return templates
            
        except Exception as e:
            logging.error(f"Error loading prompt templates: {str(e)}")
            raise

class MwongozoQueryEngine:
    """Enhanced query engine for DevFest events using ReAct agents with structured prompts"""
    
    def __init__(
        self,
        project_id: str = "your-project-id",
        location: str = "us-central1",
        prompt_file: str = "prompt.md"
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
        
        # Load prompt templates
        self.prompts = PromptTemplateLoader.load_prompts(prompt_file)
        
        self.query_tools = {}
        self.agent = None
        self.user_context = {}
        
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

    def update_user_context(self, interests: Optional[List[str]] = None, 
                          experience_level: Optional[str] = None,
                          preferences: Optional[Dict] = None):
        """Update user context for personalized recommendations"""
        if interests:
            self.user_context['interests'] = interests
        if experience_level:
            self.user_context['experience_level'] = experience_level
        if preferences:
            self.user_context['preferences'] = preferences

    def setup_tools(self, persist_dir: str, events: List[str]):
        """Set up query tools for multiple events with loaded prompts"""
        for event in events:
            query_engine = self.load_event_index(event, persist_dir)
            
            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=f"devfest_{event.lower()}",
                    description=f"""
                    Expert tool for DevFest {event} sessions. 
                    Provides detailed information about:
                    - Technical sessions and workshops
                    - Speaker details and expertise
                    - Schedule and room information
                    - Session prerequisites and descriptions
                    Use for queries specific to DevFest {event}.
                    """
                )
            )
            
            self.query_tools[event.lower()] = tool
            
        # Get system prompt from loaded templates
        system_prompt = self.prompts.get('system_context', '')
        
        # Create ReAct agent with loaded prompt
        self.agent = ReActAgent.from_tools(
            list(self.query_tools.values()),
            llm=self.llm,
            verbose=True,
            system_prompt=system_prompt
        )

    def query(self, query_text: str) -> Tuple[str, str]:
        """Execute query using loaded prompts"""
        try:
            if not self.agent:
                raise ValueError("Query tools not initialized. Call setup_tools first.")
                
            # Determine query type and get appropriate template
            template = self._select_prompt_template(query_text)
            
            # Format template with context
            formatted_prompt = template.format(
                event_names=list(self.query_tools.keys()),
                user_interests=self.user_context.get('interests', []),
                search_context=self.user_context.get('preferences', {}),
                user_context=self.user_context,
                query=query_text
            )
            
            # Execute query
            response = self.agent.chat(formatted_prompt)
            return str(response), self.agent.last_observation
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise

    def _select_prompt_template(self, query_text: str) -> str:
        """Select appropriate prompt template based on query type"""
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ['schedule', 'plan', 'timing', 'conflict']):
            return self.prompts.get('schedule_optimization', self.prompts['session_discovery'])
        elif any(word in query_lower for word in ['compare', 'difference', 'between']):
            return self.prompts.get('cross_event_comparison', self.prompts['session_discovery'])
        else:
            return self.prompts.get('session_discovery', '')

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    engine = MwongozoQueryEngine(prompt_file="prompt.md")
    
    # Update user context
    engine.update_user_context(
        interests=['AI', 'Machine Learning', 'Cloud Computing'],
        experience_level='intermediate',
        preferences={'preferred_times': 'morning', 'session_type': 'workshop'}
    )
    
    # Setup tools
    engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
    
    # Test queries
    queries = [
        "Find me AI and ML sessions in both events",
        "Help me plan my schedule for cloud computing sessions",
        "Compare the AI workshops between Lagos and Nairobi"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response, explanation = engine.query(query)
        print("Response:", response)
        print("Explanation:", explanation)