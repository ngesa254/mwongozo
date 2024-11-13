# # query_engine.py

# import logging
# import os
# import io
# import json
# import contextlib
# from datetime import datetime
# from typing import List, Tuple, Dict, Optional
# import vertexai
# from llama_index.core import (
#     StorageContext, 
#     load_index_from_storage,
#     VectorStoreIndex,
#     Settings
# )
# from llama_index.core.agent import ReActAgent
# from llama_index.core.tools import QueryEngineTool, ToolMetadata
# from llama_index.llms.vertex import Vertex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('mwongozo.log')
#     ]
# )
# logger = logging.getLogger(__name__)

# # Global configuration
# PROJECT_ID = "angelic-bee-193823"
# LOCATION = "us-central1"

# # Initialize Vertex AI globally
# vertexai.init(project=PROJECT_ID, location=LOCATION)

# # Set up models globally
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
# llm = Vertex("gemini-pro")
# Settings.embed_model = embed_model
# Settings.llm = llm

# class MwongozoQueryEngine:
#     """Query engine for DevFest events using ReAct agents"""
    
#     def __init__(
#         self,
#         prompt_file: str = "prompt.md",
#         storage_dir: str = "./storage/devfest"
#     ):
#         self.storage_dir = storage_dir
#         self.logger = logging.getLogger(__name__)
        
#         try:
#             # Load prompt templates
#             self.prompts = self._load_prompts(prompt_file)
            
#             # Initialize tools and storage
#             self.tools = []
#             self.user_context = {}
#             self.agent = None
        
#         except Exception as e:
#             self.logger.error(f"Error initializing query engine: {str(e)}")
#             raise

#     def _load_prompts(self, prompt_file_path: str) -> Dict[str, str]:
#         """Load prompt templates from markdown file"""
#         try:
#             if not os.path.exists(prompt_file_path):
#                 raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
                
#             with open(prompt_file_path, 'r', encoding='utf-8') as f:
#                 content = f.read()
                
#             # Parse sections from markdown
#             sections = {}
#             current_section = None
#             current_content = []
            
#             for line in content.split('\n'):
#                 if line.startswith('##'):
#                     if current_section and current_content:
#                         sections[current_section] = '\n'.join(current_content).strip()
#                     current_section = line.strip('# ').lower().replace(' ', '_')
#                     current_content = []
#                 else:
#                     current_content.append(line)
                    
#             # Add last section
#             if current_section and current_content:
#                 sections[current_section] = '\n'.join(current_content).strip()
                
#             # Extract templates from code blocks
#             templates = {}
#             for section, content in sections.items():
#                 code_blocks = content.split('```')
#                 if len(code_blocks) > 1:
#                     template = code_blocks[1].strip()
#                     templates[section] = template
                    
#             return templates
            
#         except Exception as e:
#             self.logger.error(f"Error loading prompt templates: {str(e)}")
#             raise
            
#     def setup_tools(self, persist_dir: str, events: List[str]):
#         """Set up query tools for multiple events"""
#         try:
#             for event in events:
#                 # Load event index
#                 event_dir = os.path.join(persist_dir, event.lower())
#                 if not os.path.exists(event_dir):
#                     raise FileNotFoundError(f"Event index not found: {event_dir}")
                
#                 storage_context = StorageContext.from_defaults(persist_dir=event_dir)
#                 index = load_index_from_storage(storage_context)
#                 query_engine = index.as_query_engine(
#                     similarity_top_k=3,
#                     response_mode="tree_summarize"
#                 )
                
#                 # Create tool
#                 tool = QueryEngineTool(
#                     query_engine=query_engine,
#                     metadata=ToolMetadata(
#                         name=f"devfest_{event.lower()}",
#                         description=f"Provides information about DevFest {event} 2024 schedule, sessions, speakers, and tracks."
#                     )
#                 )
                
#                 self.tools.append(tool)
            
#             # Create ReAct agent
#             system_prompt = self.prompts.get('system_context', '')
#             self.agent = ReActAgent.from_tools(
#                 self.tools,
#                 llm=llm,
#                 verbose=True,
#                 system_prompt=system_prompt
#             )
            
#             self.logger.info(f"Successfully set up tools for events: {events}")
            
#         except Exception as e:
#             self.logger.error(f"Error setting up tools: {str(e)}")
#             raise
    
#     def update_user_context(self, interests: Optional[List[str]] = None, 
#                           experience_level: Optional[str] = None,
#                           preferences: Optional[Dict] = None):
#         """Update user preferences and context"""
#         try:
#             if interests:
#                 self.user_context['interests'] = interests
#             if experience_level:
#                 self.user_context['experience_level'] = experience_level
#             if preferences:
#                 self.user_context['preferences'] = preferences
                
#             self.logger.info(f"Updated user context: {self.user_context}")
            
#         except Exception as e:
#             self.logger.error(f"Error updating user context: {str(e)}")
#             raise

#     def _select_prompt_template(self, query_text: str) -> str:
#         """Select appropriate prompt template"""
#         query_lower = query_text.lower()
#         default_template = self._get_default_template()
        
#         if any(word in query_lower for word in ['schedule', 'plan', 'timing', 'conflict']):
#             return self.prompts.get('schedule_optimization', default_template)
#         elif any(word in query_lower for word in ['compare', 'difference', 'between']):
#             return self.prompts.get('cross_event_comparison', default_template)
#         return self.prompts.get('session_discovery', default_template)

#     def _get_default_template(self) -> str:
#         """Get default template for fallback"""
#         return """
#         I am Mwongozo, your DevFest events assistant.
#         Available Tools: {TOOLS}
        
#         Context:
#         - Events: {EVENT_NAMES}
#         - Your Interests: {USER_INTERESTS}
#         - Experience Level: {EXPERIENCE_LEVEL}
        
#         Query: {QUERY}
        
#         I'll search through event sessions to find relevant information.
#         """

#     def query(self, query_text: str) -> Tuple[str, str]:
#         """Execute query using ReAct agent"""
#         try:
#             if not self.agent:
#                 raise ValueError("Tools not initialized. Call setup_tools first.")
            
#             # Prepare prompt variables
#             template_vars = {
#                 'EVENT_NAMES': [tool.metadata.name.replace('devfest_', '') for tool in self.tools],
#                 'USER_INTERESTS': self.user_context.get('interests', []),
#                 'SEARCH_CONTEXT': self.user_context.get('preferences', {}),
#                 'EXPERIENCE_LEVEL': self.user_context.get('experience_level', 'intermediate'),
#                 'QUERY': query_text,
#                 'TOOLS': [tool.metadata.name for tool in self.tools]
#             }
            
#             # Get and format template
#             try:
#                 template = self._select_prompt_template(query_text)
#                 formatted_prompt = template.format(**template_vars)
#             except KeyError as e:
#                 logger.warning(f"Template key error: {e}. Using default template.")
#                 formatted_prompt = self._get_default_template().format(**template_vars)
            
#             # Execute query
#             with io.StringIO() as buf, contextlib.redirect_stdout(buf):
#                 response = self.agent.chat(formatted_prompt)
#                 verbose_output = buf.getvalue()
            
#             # Save query log
#             self._save_query_log(query_text, str(response), verbose_output)
            
#             return str(response), verbose_output
            
#         except Exception as e:
#             self.logger.error(f"Error processing query: {str(e)}")
#             raise

#     def _save_query_log(self, query: str, response: str, explanation: str):
#         """Save query and response to log file"""
#         try:
#             log_entry = {
#                 "timestamp": datetime.now().isoformat(),
#                 "query": query,
#                 "response": response,
#                 "explanation": explanation,
#                 "user_context": self.user_context
#             }
            
#             log_file = os.path.join(self.storage_dir, "query_log.jsonl")
#             os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
#             with open(log_file, "a") as f:
#                 f.write(json.dumps(log_entry) + "\n")
                
#         except Exception as e:
#             self.logger.warning(f"Error saving query log: {str(e)}")

# def main():
#     """Main function for testing"""
#     try:
#         # Initialize query engine
#         engine = MwongozoQueryEngine()
        
#         # Update user context
#         engine.update_user_context(
#             interests=['AI', 'Machine Learning', 'Cloud Computing'],
#             experience_level='intermediate',
#             preferences={'preferred_times': 'morning', 'session_type': 'workshop'}
#         )
        
#         # Setup tools
#         engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
        
#         # Test queries
#         test_queries = [
#             "Find AI and ML sessions in both events",
#             "Help me plan my schedule for cloud computing sessions",
#             "Compare the AI workshops between Lagos and Nairobi"
#         ]
        
#         for query in test_queries:
#             print(f"\nQuery: {query}")
#             response, explanation = engine.query(query)
#             print(f"Response: {response}")
#             print(f"Explanation: {explanation}")
            
#     except Exception as e:
#         logger.error(f"Error in main: {str(e)}")
#         raise

# if __name__ == "__main__":
#     main()




# # query_engine.py

# import logging
# import os
# import io
# import json
# import contextlib
# from datetime import datetime
# from typing import List, Tuple, Dict, Optional
# import vertexai
# from llama_index.core import (
#     StorageContext, 
#     load_index_from_storage,
#     VectorStoreIndex,
#     Settings
# )
# from llama_index.core.agent import ReActAgent
# from llama_index.core.tools import QueryEngineTool, ToolMetadata
# from llama_index.llms.vertex import Vertex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('mwongozo.log')
#     ]
# )
# logger = logging.getLogger(__name__)

# # Global configuration
# PROJECT_ID = "angelic-bee-193823"
# LOCATION = "us-central1"

# # Initialize Vertex AI globally
# vertexai.init(project=PROJECT_ID, location=LOCATION)

# # Set up models globally
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
# llm = Vertex(
#     model="gemini-pro",
#     model_kwargs={
#         "temperature": 0.7,
#         "max_output_tokens": 2048,
#         "top_p": 0.8,
#         "top_k": 40
#     },
#     vertexai_kwargs={
#         "project": PROJECT_ID,
#         "location": LOCATION,
#         "response_validation": False
#     }
# )

# Settings.embed_model = embed_model
# Settings.llm = llm

# class MwongozoQueryEngine:
#     """Query engine for DevFest events using ReAct agents"""
    
#     def __init__(
#         self,
#         prompt_file: str = "prompt.md",
#         storage_dir: str = "./storage/devfest"
#     ):
#         self.storage_dir = storage_dir
#         self.logger = logging.getLogger(__name__)
        
#         try:
#             # Load prompt templates
#             self.prompts = self._load_prompts(prompt_file)
            
#             # Initialize tools and storage
#             self.tools = []
#             self.user_context = {}
#             self.agent = None
        
#         except Exception as e:
#             self.logger.error(f"Error initializing query engine: {str(e)}")
#             raise

#     def _load_prompts(self, prompt_file_path: str) -> Dict[str, str]:
#         """Load prompt templates from markdown file"""
#         try:
#             if not os.path.exists(prompt_file_path):
#                 raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
                
#             with open(prompt_file_path, 'r', encoding='utf-8') as f:
#                 content = f.read()
                
#             # Parse sections from markdown
#             sections = {}
#             current_section = None
#             current_content = []
            
#             for line in content.split('\n'):
#                 if line.startswith('##'):
#                     if current_section and current_content:
#                         sections[current_section] = '\n'.join(current_content).strip()
#                     current_section = line.strip('# ').lower().replace(' ', '_')
#                     current_content = []
#                 else:
#                     current_content.append(line)
                    
#             # Add last section
#             if current_section and current_content:
#                 sections[current_section] = '\n'.join(current_content).strip()
                
#             # Extract templates from code blocks
#             templates = {}
#             for section, content in sections.items():
#                 code_blocks = content.split('```')
#                 if len(code_blocks) > 1:
#                     template = code_blocks[1].strip()
#                     templates[section] = template
                    
#             return templates
            
#         except Exception as e:
#             self.logger.error(f"Error loading prompt templates: {str(e)}")
#             raise
            
#     def setup_tools(self, persist_dir: str, events: List[str]):
#         """Set up query tools for multiple events"""
#         try:
#             for event in events:
#                 # Load event index
#                 event_dir = os.path.join(persist_dir, event.lower())
#                 if not os.path.exists(event_dir):
#                     raise FileNotFoundError(f"Event index not found: {event_dir}")
                
#                 storage_context = StorageContext.from_defaults(persist_dir=event_dir)
#                 index = load_index_from_storage(storage_context)
#                 query_engine = index.as_query_engine(
#                     similarity_top_k=3,
#                     response_mode="tree_summarize"
#                 )
                
#                 # Create tool
#                 tool = QueryEngineTool(
#                     query_engine=query_engine,
#                     metadata=ToolMetadata(
#                         name=f"devfest_{event.lower()}",
#                         description=f"""
#                         Expert tool for DevFest {event} 2024 schedule. 
#                         Provides information about sessions, speakers, tracks, timings.
#                         Use for specific queries about DevFest {event} event.
#                         """
#                     )
#                 )
                
#                 self.tools.append(tool)
            
#             # Create ReAct agent
#             system_prompt = self.prompts.get('system_context', '')
#             self.agent = ReActAgent.from_tools(
#                 self.tools,
#                 llm=llm,
#                 verbose=True,
#                 system_prompt=system_prompt
#             )
            
#             self.logger.info(f"Successfully set up tools for events: {events}")
            
#         except Exception as e:
#             self.logger.error(f"Error setting up tools: {str(e)}")
#             raise
    
#     def update_user_context(self, interests: Optional[List[str]] = None, 
#                           experience_level: Optional[str] = None,
#                           preferences: Optional[Dict] = None):
#         """Update user preferences and context"""
#         try:
#             if interests:
#                 self.user_context['interests'] = interests
#             if experience_level:
#                 self.user_context['experience_level'] = experience_level
#             if preferences:
#                 self.user_context['preferences'] = preferences
                
#             self.logger.info(f"Updated user context: {self.user_context}")
            
#         except Exception as e:
#             self.logger.error(f"Error updating user context: {str(e)}")
#             raise

#     def _select_prompt_template(self, query_text: str) -> str:
#         """Select appropriate prompt template"""
#         query_lower = query_text.lower()
#         default_template = self._get_default_template()
        
#         if any(word in query_lower for word in ['schedule', 'plan', 'timing', 'conflict']):
#             return self.prompts.get('schedule_optimization', default_template)
#         elif any(word in query_lower for word in ['compare', 'difference', 'between']):
#             return self.prompts.get('cross_event_comparison', default_template)
#         return self.prompts.get('session_discovery', default_template)

#     def _get_default_template(self) -> str:
#         """Get default template for fallback"""
#         return """
#         I am Mwongozo, your DevFest events assistant.
#         Available Tools: {TOOLS}
        
#         Context:
#         - Events: {EVENT_NAMES}
#         - Your Interests: {USER_INTERESTS}
#         - Experience Level: {EXPERIENCE_LEVEL}
        
#         Query: {QUERY}
        
#         I'll search through event sessions to find relevant information.
#         """

#     def query(self, query_text: str) -> Tuple[str, str]:
#         """Execute query using ReAct agent"""
#         try:
#             if not self.agent:
#                 raise ValueError("Tools not initialized. Call setup_tools first.")
            
#             # Prepare prompt variables
#             template_vars = {
#                 'EVENT_NAMES': [tool.metadata.name.replace('devfest_', '') for tool in self.tools],
#                 'USER_INTERESTS': self.user_context.get('interests', []),
#                 'SEARCH_CONTEXT': self.user_context.get('preferences', {}),
#                 'EXPERIENCE_LEVEL': self.user_context.get('experience_level', 'intermediate'),
#                 'QUERY': query_text,
#                 'TOOLS': [tool.metadata.name for tool in self.tools]
#             }
            
#             # Get and format template
#             try:
#                 template = self._select_prompt_template(query_text)
#                 formatted_prompt = template.format(**template_vars)
#             except KeyError as e:
#                 self.logger.warning(f"Template key error: {e}. Using default template.")
#                 formatted_prompt = self._get_default_template().format(**template_vars)
            
#             # Execute query
#             with io.StringIO() as buf, contextlib.redirect_stdout(buf):
#                 response = self.agent.chat(formatted_prompt)
#                 verbose_output = buf.getvalue()
            
#             # Save query log
#             self._save_query_log(query_text, str(response), verbose_output)
            
#             return str(response), verbose_output
            
#         except Exception as e:
#             self.logger.error(f"Error processing query: {str(e)}")
#             raise

#     def _save_query_log(self, query: str, response: str, explanation: str):
#         """Save query and response to log file"""
#         try:
#             log_entry = {
#                 "timestamp": datetime.now().isoformat(),
#                 "query": query,
#                 "response": response,
#                 "explanation": explanation,
#                 "user_context": self.user_context
#             }
            
#             log_file = os.path.join(self.storage_dir, "query_log.jsonl")
#             os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
#             with open(log_file, "a") as f:
#                 f.write(json.dumps(log_entry) + "\n")
                
#         except Exception as e:
#             self.logger.warning(f"Error saving query log: {str(e)}")

# def main():
#     """Main function for testing"""
#     try:
#         # Initialize query engine
#         engine = MwongozoQueryEngine()
        
#         # Update user context
#         engine.update_user_context(
#             interests=['AI', 'Machine Learning', 'Cloud Computing'],
#             experience_level='intermediate',
#             preferences={'preferred_times': 'morning', 'session_type': 'workshop'}
#         )
        
#         # Setup tools
#         engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
        
#         # Test queries
#         test_queries = [
#             "Find AI and ML sessions in both events",
#             "Help me plan my schedule for cloud computing sessions",
#             "Compare the AI workshops between Lagos and Nairobi"
#         ]
        
#         for query in test_queries:
#             print(f"\nQuery: {query}")
#             try:
#                 response, explanation = engine.query(query)
#                 print(f"Response: {response}")
#                 print(f"Explanation: {explanation}")
#             except Exception as e:
#                 print(f"Error processing query: {str(e)}")
#                 continue
            
#     except Exception as e:
#         logger.error(f"Error in main: {str(e)}")
#         raise

# if __name__ == "__main__":
#     main()




# # query_engine.py

# import logging
# import os
# import io
# import json
# import contextlib
# from datetime import datetime
# from typing import List, Tuple, Dict, Optional
# import vertexai
# from llama_index.core import (
#     StorageContext, 
#     load_index_from_storage,
#     VectorStoreIndex,
#     Settings
# )
# from llama_index.core.agent import ReActAgent
# from llama_index.core.tools import QueryEngineTool, ToolMetadata
# from llama_index.llms.vertex import Vertex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('mwongozo.log')
#     ]
# )
# logger = logging.getLogger(__name__)

# # Global configuration
# PROJECT_ID = "angelic-bee-193823"
# LOCATION = "us-central1"

# # Initialize Vertex AI globally
# vertexai.init(project=PROJECT_ID, location=LOCATION)

# # Set up models globally
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
# llm = Vertex(
#     model_name="gemini-pro",
#     temperature=0.7,
#     max_tokens=2048,
#     top_p=0.8,
#     top_k=40,
#     project=PROJECT_ID,
#     location=LOCATION
# )

# Settings.embed_model = embed_model
# Settings.llm = llm

# class MwongozoQueryEngine:
#     """Query engine for DevFest events using ReAct agents"""
    
#     def __init__(
#         self,
#         prompt_file: str = "prompt.md",
#         storage_dir: str = "./storage/devfest"
#     ):
#         self.storage_dir = storage_dir
#         self.logger = logging.getLogger(__name__)
        
#         try:
#             # Load prompt templates
#             self.prompts = self._load_prompts(prompt_file)
            
#             # Initialize tools and storage
#             self.tools = []
#             self.user_context = {}
#             self.agent = None
        
#         except Exception as e:
#             self.logger.error(f"Error initializing query engine: {str(e)}")
#             raise

#     def _load_prompts(self, prompt_file_path: str) -> Dict[str, str]:
#         """Load prompt templates from markdown file"""
#         try:
#             if not os.path.exists(prompt_file_path):
#                 raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
                
#             with open(prompt_file_path, 'r', encoding='utf-8') as f:
#                 content = f.read()
                
#             # Parse sections from markdown
#             sections = {}
#             current_section = None
#             current_content = []
            
#             for line in content.split('\n'):
#                 if line.startswith('##'):
#                     if current_section and current_content:
#                         sections[current_section] = '\n'.join(current_content).strip()
#                     current_section = line.strip('# ').lower().replace(' ', '_')
#                     current_content = []
#                 else:
#                     current_content.append(line)
                    
#             # Add last section
#             if current_section and current_content:
#                 sections[current_section] = '\n'.join(current_content).strip()
                
#             # Extract templates from code blocks
#             templates = {}
#             for section, content in sections.items():
#                 code_blocks = content.split('```')
#                 if len(code_blocks) > 1:
#                     template = code_blocks[1].strip()
#                     templates[section] = template
                    
#             return templates
            
#         except Exception as e:
#             self.logger.error(f"Error loading prompt templates: {str(e)}")
#             raise
            
#     def setup_tools(self, persist_dir: str, events: List[str]):
#         """Set up query tools for multiple events"""
#         try:
#             for event in events:
#                 # Load event index
#                 event_dir = os.path.join(persist_dir, event.lower())
#                 if not os.path.exists(event_dir):
#                     raise FileNotFoundError(f"Event index not found: {event_dir}")
                
#                 storage_context = StorageContext.from_defaults(persist_dir=event_dir)
#                 index = load_index_from_storage(storage_context)
#                 query_engine = index.as_query_engine(
#                     similarity_top_k=3,
#                     response_mode="tree_summarize"
#                 )
                
#                 # Create tool
#                 tool = QueryEngineTool(
#                     query_engine=query_engine,
#                     metadata=ToolMetadata(
#                         name=f"devfest_{event.lower()}",
#                         description=f"""
#                         Expert tool for DevFest {event} 2024 schedule. 
#                         Provides information about sessions, speakers, tracks, timings.
#                         Use for specific queries about DevFest {event} event.
#                         """
#                     )
#                 )
                
#                 self.tools.append(tool)
            
#             # Create ReAct agent
#             system_prompt = self.prompts.get('system_context', '')
#             self.agent = ReActAgent.from_tools(
#                 self.tools,
#                 llm=llm,
#                 verbose=True,
#                 system_prompt=system_prompt
#             )
            
#             self.logger.info(f"Successfully set up tools for events: {events}")
            
#         except Exception as e:
#             self.logger.error(f"Error setting up tools: {str(e)}")
#             raise
    
#     def update_user_context(self, interests: Optional[List[str]] = None, 
#                           experience_level: Optional[str] = None,
#                           preferences: Optional[Dict] = None):
#         """Update user preferences and context"""
#         try:
#             if interests:
#                 self.user_context['interests'] = interests
#             if experience_level:
#                 self.user_context['experience_level'] = experience_level
#             if preferences:
#                 self.user_context['preferences'] = preferences
                
#             self.logger.info(f"Updated user context: {self.user_context}")
            
#         except Exception as e:
#             self.logger.error(f"Error updating user context: {str(e)}")
#             raise

#     def _select_prompt_template(self, query_text: str) -> str:
#         """Select appropriate prompt template"""
#         query_lower = query_text.lower()
#         default_template = self._get_default_template()
        
#         if any(word in query_lower for word in ['schedule', 'plan', 'timing', 'conflict']):
#             return self.prompts.get('schedule_optimization', default_template)
#         elif any(word in query_lower for word in ['compare', 'difference', 'between']):
#             return self.prompts.get('cross_event_comparison', default_template)
#         return self.prompts.get('session_discovery', default_template)

#     def _get_default_template(self) -> str:
#         """Get default template for fallback"""
#         return """
#         I am Mwongozo, your DevFest events assistant.
#         Available Tools: {TOOLS}
        
#         Context:
#         - Events: {EVENT_NAMES}
#         - Your Interests: {USER_INTERESTS}
#         - Experience Level: {EXPERIENCE_LEVEL}
        
#         Query: {QUERY}
        
#         I'll search through event sessions to find relevant information.
#         """

#     def query(self, query_text: str) -> Tuple[str, str]:
#         """Execute query using ReAct agent"""
#         try:
#             if not self.agent:
#                 raise ValueError("Tools not initialized. Call setup_tools first.")
            
#             # Prepare prompt variables
#             template_vars = {
#                 'EVENT_NAMES': [tool.metadata.name.replace('devfest_', '') for tool in self.tools],
#                 'USER_INTERESTS': self.user_context.get('interests', []),
#                 'SEARCH_CONTEXT': self.user_context.get('preferences', {}),
#                 'EXPERIENCE_LEVEL': self.user_context.get('experience_level', 'intermediate'),
#                 'QUERY': query_text,
#                 'TOOLS': [tool.metadata.name for tool in self.tools]
#             }
            
#             # Get and format template
#             try:
#                 template = self._select_prompt_template(query_text)
#                 formatted_prompt = template.format(**template_vars)
#             except KeyError as e:
#                 self.logger.warning(f"Template key error: {e}. Using default template.")
#                 formatted_prompt = self._get_default_template().format(**template_vars)
            
#             # Execute query
#             with io.StringIO() as buf, contextlib.redirect_stdout(buf):
#                 response = self.agent.chat(formatted_prompt)
#                 verbose_output = buf.getvalue()
            
#             # Save query log
#             self._save_query_log(query_text, str(response), verbose_output)
            
#             return str(response), verbose_output
            
#         except Exception as e:
#             self.logger.error(f"Error processing query: {str(e)}")
#             raise

#     def _save_query_log(self, query: str, response: str, explanation: str):
#         """Save query and response to log file"""
#         try:
#             log_entry = {
#                 "timestamp": datetime.now().isoformat(),
#                 "query": query,
#                 "response": response,
#                 "explanation": explanation,
#                 "user_context": self.user_context
#             }
            
#             log_file = os.path.join(self.storage_dir, "query_log.jsonl")
#             os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
#             with open(log_file, "a") as f:
#                 f.write(json.dumps(log_entry) + "\n")
                
#         except Exception as e:
#             self.logger.warning(f"Error saving query log: {str(e)}")

# def main():
#     """Main function for testing"""
#     try:
#         # Initialize query engine
#         engine = MwongozoQueryEngine()
        
#         # Update user context
#         engine.update_user_context(
#             interests=['AI', 'Machine Learning', 'Cloud Computing'],
#             experience_level='intermediate',
#             preferences={'preferred_times': 'morning', 'session_type': 'workshop'}
#         )
        
#         # Setup tools
#         engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
        
#         # Test queries
#         test_queries = [
#             "Find AI and ML sessions in both events",
#             "Help me plan my schedule for cloud computing sessions",
#             "Compare the AI workshops between Lagos and Nairobi"
#         ]
        
#         for query in test_queries:
#             print(f"\nQuery: {query}")
#             try:
#                 response, explanation = engine.query(query)
#                 print(f"Response: {response}")
#                 print(f"Explanation: {explanation}")
#             except Exception as e:
#                 print(f"Error processing query: {str(e)}")
#                 continue
            
#     except Exception as e:
#         logger.error(f"Error in main: {str(e)}")
#         raise

# if __name__ == "__main__":
#     main()



# # query_engine.py

# import logging
# import os
# import io
# import json
# import contextlib
# from datetime import datetime
# from typing import List, Tuple, Dict, Optional
# import vertexai
# from llama_index.core import (
#     StorageContext, 
#     load_index_from_storage,
#     VectorStoreIndex,
#     Settings
# )
# from llama_index.core.agent import ReActAgent
# from llama_index.core.tools import QueryEngineTool, ToolMetadata
# from llama_index.llms.vertex import Vertex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('mwongozo.log')
#     ]
# )
# logger = logging.getLogger(__name__)

# # Global configuration
# PROJECT_ID = "angelic-bee-193823"
# LOCATION = "us-central1"

# # Initialize Vertex AI globally
# vertexai.init(project=PROJECT_ID, location=LOCATION)

# # Set up models globally
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
# llm = Vertex(
#     model_name="gemini-pro",
#     temperature=0.7,
#     max_tokens=2048,
#     top_p=0.8,
#     top_k=40,
#     project=PROJECT_ID,
#     location=LOCATION
# )

# Settings.embed_model = embed_model
# Settings.llm = llm

# class MwongozoQueryEngine:
#     """Query engine for DevFest events using ReAct agents"""
    
#     def __init__(
#         self,
#         prompt_file: str = "prompt.md",
#         storage_dir: str = "./storage/devfest"
#     ):
#         self.storage_dir = storage_dir
#         self.logger = logging.getLogger(__name__)
        
#         try:
#             # Load prompt templates
#             self.prompts = self._load_prompts(prompt_file)
            
#             # Initialize tools and storage
#             self.tools = []
#             self.user_context = {}
#             self.agent = None
        
#         except Exception as e:
#             self.logger.error(f"Error initializing query engine: {str(e)}")
#             raise

#     def _load_prompts(self, prompt_file_path: str) -> Dict[str, str]:
#         """Load prompt templates from markdown file"""
#         try:
#             if not os.path.exists(prompt_file_path):
#                 raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
                
#             with open(prompt_file_path, 'r', encoding='utf-8') as f:
#                 content = f.read()
                
#             # Parse sections from markdown
#             sections = {}
#             current_section = None
#             current_content = []
            
#             for line in content.split('\n'):
#                 if line.startswith('##'):
#                     if current_section and current_content:
#                         sections[current_section] = '\n'.join(current_content).strip()
#                     current_section = line.strip('# ').lower().replace(' ', '_')
#                     current_content = []
#                 else:
#                     current_content.append(line)
                    
#             # Add last section
#             if current_section and current_content:
#                 sections[current_section] = '\n'.join(current_content).strip()
                
#             # Extract templates from code blocks
#             templates = {}
#             for section, content in sections.items():
#                 code_blocks = content.split('```')
#                 if len(code_blocks) > 1:
#                     template = code_blocks[1].strip()
#                     templates[section] = template
                    
#             return templates
            
#         except Exception as e:
#             self.logger.error(f"Error loading prompt templates: {str(e)}")
#             raise
            
#     def setup_tools(self, persist_dir: str, events: List[str]):
#         """Set up query tools for multiple events"""
#         try:
#             for event in events:
#                 # Load event index
#                 event_dir = os.path.join(persist_dir, event.lower())
#                 if not os.path.exists(event_dir):
#                     raise FileNotFoundError(f"Event index not found: {event_dir}")
                
#                 storage_context = StorageContext.from_defaults(persist_dir=event_dir)
#                 index = load_index_from_storage(storage_context)
#                 query_engine = index.as_query_engine(
#                     similarity_top_k=3,
#                     response_mode="tree_summarize"
#                 )
                
#                 # Create tool
#                 tool = QueryEngineTool(
#                     query_engine=query_engine,
#                     metadata=ToolMetadata(
#                         name=f"devfest_{event.lower()}",
#                         description=f"""
#                         Expert tool for DevFest {event} 2024 schedule. 
#                         Provides information about sessions, speakers, tracks, timings.
#                         Use for specific queries about DevFest {event} event.
#                         """
#                     )
#                 )
                
#                 self.tools.append(tool)
            
#             # Create ReAct agent
#             system_prompt = self.prompts.get('system_context', '')
#             self.agent = ReActAgent.from_tools(
#                 self.tools,
#                 llm=llm,
#                 verbose=True,
#                 system_prompt=system_prompt
#             )
            
#             self.logger.info(f"Successfully set up tools for events: {events}")
            
#         except Exception as e:
#             self.logger.error(f"Error setting up tools: {str(e)}")
#             raise
    
#     def update_user_context(self, interests: Optional[List[str]] = None, 
#                           experience_level: Optional[str] = None,
#                           preferences: Optional[Dict] = None):
#         """Update user preferences and context"""
#         try:
#             if interests:
#                 self.user_context['interests'] = interests
#             if experience_level:
#                 self.user_context['experience_level'] = experience_level
#             if preferences:
#                 self.user_context['preferences'] = preferences
                
#             self.logger.info(f"Updated user context: {self.user_context}")
            
#         except Exception as e:
#             self.logger.error(f"Error updating user context: {str(e)}")
#             raise

#     def _select_prompt_template(self, query_text: str) -> str:
#         """Select appropriate prompt template"""
#         query_lower = query_text.lower()
#         default_template = self._get_default_template()
        
#         if any(word in query_lower for word in ['schedule', 'plan', 'timing', 'conflict']):
#             return self.prompts.get('schedule_optimization', default_template)
#         elif any(word in query_lower for word in ['compare', 'difference', 'between']):
#             return self.prompts.get('cross_event_comparison', default_template)
#         return self.prompts.get('session_discovery', default_template)

#     def _get_default_template(self) -> str:
#         """Get default template for fallback"""
#         return """
#         I am Mwongozo, your DevFest events assistant.
#         Available Tools: {TOOLS}
        
#         Context:
#         - Events: {EVENT_NAMES}
#         - Your Interests: {USER_INTERESTS}
#         - Experience Level: {EXPERIENCE_LEVEL}
        
#         Query: {QUERY}
        
#         I'll search through event sessions to find relevant information.
#         """

#     def query(self, query_text: str) -> Tuple[str, str]:
#         """Execute query using ReAct agent"""
#         try:
#             if not self.agent:
#                 raise ValueError("Tools not initialized. Call setup_tools first.")
            
#             # Prepare prompt variables
#             template_vars = {
#                 'EVENT_NAMES': [tool.metadata.name.replace('devfest_', '') for tool in self.tools],
#                 'USER_INTERESTS': self.user_context.get('interests', []),
#                 'SEARCH_CONTEXT': self.user_context.get('preferences', {}),
#                 'EXPERIENCE_LEVEL': self.user_context.get('experience_level', 'intermediate'),
#                 'QUERY': query_text,
#                 'TOOLS': [tool.metadata.name for tool in self.tools]
#             }
            
#             # Get and format template
#             try:
#                 template = self._select_prompt_template(query_text)
#                 formatted_prompt = template.format(**template_vars)
#             except KeyError as e:
#                 self.logger.warning(f"Template key error: {e}. Using default template.")
#                 formatted_prompt = self._get_default_template().format(**template_vars)
            
#             # Execute query
#             with io.StringIO() as buf, contextlib.redirect_stdout(buf):
#                 response = self.agent.chat(formatted_prompt)
#                 verbose_output = buf.getvalue()
            
#             # Save query log
#             self._save_query_log(query_text, str(response), verbose_output)
            
#             return str(response), verbose_output
            
#         except Exception as e:
#             self.logger.error(f"Error processing query: {str(e)}")
#             raise

#     def _save_query_log(self, query: str, response: str, explanation: str):
#         """Save query and response to log file"""
#         try:
#             log_entry = {
#                 "timestamp": datetime.now().isoformat(),
#                 "query": query,
#                 "response": response,
#                 "explanation": explanation,
#                 "user_context": self.user_context
#             }
            
#             log_file = os.path.join(self.storage_dir, "query_log.jsonl")
#             os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
#             with open(log_file, "a") as f:
#                 f.write(json.dumps(log_entry) + "\n")
                
#         except Exception as e:
#             self.logger.warning(f"Error saving query log: {str(e)}")

# def main():
#     """Main function for testing"""
#     try:
#         # Initialize query engine
#         engine = MwongozoQueryEngine()
        
#         # Update user context
#         engine.update_user_context(
#             interests=['AI', 'Machine Learning', 'Cloud Computing'],
#             experience_level='intermediate',
#             preferences={'preferred_times': 'morning', 'session_type': 'workshop'}
#         )
        
#         # Setup tools
#         engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
        
#         # Test queries
#         test_queries = [
#             "Find AI and ML sessions in both events",
#             "Help me plan my schedule for cloud computing sessions",
#             "Compare the AI workshops between Lagos and Nairobi"
#         ]
        
#         for query in test_queries:
#             print(f"\nQuery: {query}")
#             try:
#                 response, explanation = engine.query(query)
#                 print(f"Response: {response}")
#                 print(f"Explanation: {explanation}")
#             except Exception as e:
#                 print(f"Error processing query: {str(e)}")
#                 continue
            
#     except Exception as e:
#         logger.error(f"Error in main: {str(e)}")
#         raise

# if __name__ == "__main__":
#     main()



# query_engine.py

import logging
import os
import io
import json
import contextlib
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import vertexai
from llama_index.core import (
    StorageContext, 
    load_index_from_storage,
    VectorStoreIndex,
    Settings
)
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mwongozo.log')
    ]
)
logger = logging.getLogger(__name__)

# Global configuration
PROJECT_ID = "angelic-bee-193823"
LOCATION = "us-central1"

# Initialize Vertex AI globally
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Set up models globally - using exact working configuration
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Vertex("gemini-pro")
Settings.embed_model = embed_model
Settings.llm = llm

class MwongozoQueryEngine:
    """Query engine for DevFest events using ReAct agents"""
    
    def __init__(
        self,
        prompt_file: str = "prompt.md",
        storage_dir: str = "./storage/devfest"
    ):
        self.storage_dir = storage_dir
        self.logger = logging.getLogger(__name__)
        
        try:
            # Load prompt templates
            self.prompts = self._load_prompts(prompt_file)
            
            # Initialize tools and storage
            self.tools = []
            self.user_context = {}
            self.agent = None
        
        except Exception as e:
            self.logger.error(f"Error initializing query engine: {str(e)}")
            raise

    def _load_prompts(self, prompt_file_path: str) -> Dict[str, str]:
        """Load prompt templates from markdown file"""
        try:
            if not os.path.exists(prompt_file_path):
                raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
                
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
                    template = code_blocks[1].strip()
                    templates[section] = template
                    
            return templates
            
        except Exception as e:
            self.logger.error(f"Error loading prompt templates: {str(e)}")
            raise
            
    def setup_tools(self, persist_dir: str, events: List[str]):
        """Set up query tools for multiple events"""
        try:
            for event in events:
                # Load event index
                event_dir = os.path.join(persist_dir, event.lower())
                if not os.path.exists(event_dir):
                    raise FileNotFoundError(f"Event index not found: {event_dir}")
                
                storage_context = StorageContext.from_defaults(persist_dir=event_dir)
                index = load_index_from_storage(storage_context)
                query_engine = index.as_query_engine(
                    similarity_top_k=3,
                    response_mode="tree_summarize"
                )
                
                # Create tool
                tool = QueryEngineTool(
                    query_engine=query_engine,
                    metadata=ToolMetadata(
                        name=f"devfest_{event.lower()}",
                        description=f"Provides information about DevFest {event} 2024 schedule, sessions, speakers, and tracks."
                    )
                )
                
                self.tools.append(tool)
            
            # Create ReAct agent
            system_prompt = self.prompts.get('system_context', '')
            self.agent = ReActAgent.from_tools(
                self.tools,
                llm=llm,
                verbose=True,
                system_prompt=system_prompt
            )
            
            self.logger.info(f"Successfully set up tools for events: {events}")
            
        except Exception as e:
            self.logger.error(f"Error setting up tools: {str(e)}")
            raise
    
    def update_user_context(self, interests: Optional[List[str]] = None, 
                          experience_level: Optional[str] = None,
                          preferences: Optional[Dict] = None):
        """Update user preferences and context"""
        try:
            if interests:
                self.user_context['interests'] = interests
            if experience_level:
                self.user_context['experience_level'] = experience_level
            if preferences:
                self.user_context['preferences'] = preferences
                
            self.logger.info(f"Updated user context: {self.user_context}")
            
        except Exception as e:
            self.logger.error(f"Error updating user context: {str(e)}")
            raise

    def _select_prompt_template(self, query_text: str) -> str:
        """Select appropriate prompt template"""
        query_lower = query_text.lower()
        default_template = self._get_default_template()
        
        if any(word in query_lower for word in ['schedule', 'plan', 'timing', 'conflict']):
            return self.prompts.get('schedule_optimization', default_template)
        elif any(word in query_lower for word in ['compare', 'difference', 'between']):
            return self.prompts.get('cross_event_comparison', default_template)
        return self.prompts.get('session_discovery', default_template)

    def _get_default_template(self) -> str:
        """Get default template for fallback"""
        return """
        I am Mwongozo, your DevFest events assistant.
        Available Tools: {TOOLS}
        
        Context:
        - Events: {EVENT_NAMES}
        - Your Interests: {USER_INTERESTS}
        - Experience Level: {EXPERIENCE_LEVEL}
        
        Query: {QUERY}
        
        I'll search through event sessions to find relevant information.
        """

    def query(self, query_text: str) -> Tuple[str, str]:
        """Execute query using ReAct agent"""
        try:
            if not self.agent:
                raise ValueError("Tools not initialized. Call setup_tools first.")
            
            # Prepare prompt variables
            template_vars = {
                'EVENT_NAMES': [tool.metadata.name.replace('devfest_', '') for tool in self.tools],
                'USER_INTERESTS': self.user_context.get('interests', []),
                'SEARCH_CONTEXT': self.user_context.get('preferences', {}),
                'EXPERIENCE_LEVEL': self.user_context.get('experience_level', 'intermediate'),
                'QUERY': query_text,
                'TOOLS': [tool.metadata.name for tool in self.tools]
            }
            
            # Get and format template
            try:
                template = self._select_prompt_template(query_text)
                formatted_prompt = template.format(**template_vars)
            except KeyError as e:
                self.logger.warning(f"Template key error: {e}. Using default template.")
                formatted_prompt = self._get_default_template().format(**template_vars)
            
            # Execute query
            with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                response = self.agent.chat(formatted_prompt)
                verbose_output = buf.getvalue()
            
            # Save query log
            self._save_query_log(query_text, str(response), verbose_output)
            
            return str(response), verbose_output
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise

    def _save_query_log(self, query: str, response: str, explanation: str):
        """Save query and response to log file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "explanation": explanation,
                "user_context": self.user_context
            }
            
            log_file = os.path.join(self.storage_dir, "query_log.jsonl")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            self.logger.warning(f"Error saving query log: {str(e)}")

# def main():
#     """Main function for testing"""
#     try:
#         # Initialize query engine
#         engine = MwongozoQueryEngine()
        
#         # Update user context
#         engine.update_user_context(
#             interests=['AI', 'Machine Learning', 'Cloud Computing'],
#             experience_level='intermediate',
#             preferences={'preferred_times': 'morning', 'session_type': 'workshop'}
#         )
        
#         # Setup tools
#         engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
        
#         # Test queries
#         test_queries = [
#             "Find AI and ML sessions in both events",
#             "Help me plan my schedule for cloud computing sessions",
#             "Compare the AI workshops between Lagos and Nairobi"
#         ]
        
#         for query in test_queries:
#             print(f"\nQuery: {query}")
#             try:
#                 response, explanation = engine.query(query)
#                 print(f"Response: {response}")
#                 print(f"Explanation: {explanation}")
#             except Exception as e:
#                 print(f"Error processing query: {str(e)}")
#                 continue
            
#     except Exception as e:
#         logger.error(f"Error in main: {str(e)}")
#         raise

# if __name__ == "__main__":
#     main()


def main():
    """Interactive main function for chatting with Mwongozo"""
    try:
        print("\nWelcome to Mwongozo - Your DevFest Events Assistant!")
        print("=" * 50)
        
        # Initialize query engine
        print("\nInitializing Mwongozo...")
        engine = MwongozoQueryEngine()
        
        # Update user context
        print("\nLet me understand your preferences better:")
        interests = input("What are your technical interests? (comma-separated, e.g., AI, Cloud, Web): ").split(',')
        interests = [interest.strip() for interest in interests]
        
        experience_level = input("What's your experience level? (beginner/intermediate/advanced): ").strip()
        
        preferred_times = input("Do you prefer morning or afternoon sessions? ").strip()
        session_type = input("What type of sessions do you prefer? (workshop/talk/any): ").strip()
        
        engine.update_user_context(
            interests=interests,
            experience_level=experience_level,
            preferences={
                'preferred_times': preferred_times, 
                'session_type': session_type
            }
        )
        
        # Setup tools
        print("\nLoading DevFest events data...")
        engine.setup_tools("./storage/devfest", ["Lagos", "Nairobi"])
        
        print("\nMwongozo is ready! You can now ask questions about DevFest Lagos and Nairobi.")
        print("\nExample questions:")
        print("- Find AI and ML sessions in both events")
        print("- What cloud computing talks are available?")
        print("- Compare the workshops between Lagos and Nairobi")
        print("- Help me plan my schedule for web development sessions")
        print("\nType 'exit' to quit.")
        
        # Interactive chat loop
        while True:
            print("\n" + "=" * 50)
            query = input("\nYour question: ")
            
            if query.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you for using Mwongozo. Goodbye!")
                break
                
            try:
                response, explanation = engine.query(query)
                print("\nMwongozo's Response:")
                print(response)
                
                # Ask if user wants more details
                more_info = input("\nWould you like more details about any of these sessions? (yes/no): ")
                if more_info.lower() == 'yes':
                    detail_query = input("Which session would you like to know more about?: ")
                    response, explanation = engine.query(f"Tell me more about the session: {detail_query}")
                    print("\nMwongozo's Response:")
                    print(response)
                
                # Ask for recommendations
                recommend = input("\nWould you like recommendations for related sessions? (yes/no): ")
                if recommend.lower() == 'yes':
                    response, explanation = engine.query(f"Recommend related sessions to: {query}")
                    print("\nRecommended Sessions:")
                    print(response)
                
            except Exception as e:
                print(f"\nError processing query: {str(e)}")
                print("Please try rephrasing your question.")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()

