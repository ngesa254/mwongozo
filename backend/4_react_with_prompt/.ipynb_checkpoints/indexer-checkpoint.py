# # indexer.py

# import os
# import logging
# from typing import Dict, List
# import vertexai
# from google.cloud import aiplatform
# from llama_index.core import (
#     Document,
#     Settings,
#     StorageContext,
#     VectorStoreIndex
# )
# from llama_index.embeddings.vertex import VertexTextEmbedding
# from llama_index.llms.vertex import Vertex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# class DevFestIndexer:
#     """Indexes DevFest event data for efficient querying"""
    
#     def __init__(
#         self,
#         project_id: str = "your-project-id",
#         location: str = "us-central1",
#         persist_dir: str = "./storage/devfest"
#     ):
#         self.project_id = project_id
#         self.location = location
#         self.persist_dir = persist_dir
#         self.logger = logging.getLogger(__name__)
        
#         # Initialize Vertex AI
#         vertexai.init(project=project_id, location=location)
        
#         # Set up embedding model
#         self.embed_model = HuggingFaceEmbedding(
#             model_name="BAAI/bge-small-en-v1.5"
#         )
        
#         # Set up LLM
#         self.llm = Vertex("gemini-pro")
        
#         # Configure global settings
#         Settings.embed_model = self.embed_model
#         Settings.llm = self.llm
        
#         # Initialize storage for different events
#         self.indices = {}
        
#     def convert_to_documents(self, schedule_data: Dict, event_name: str) -> List[Document]:
#         """Convert schedule data to LlamaIndex documents"""
#         documents = []
        
#         for day, sessions in schedule_data.items():
#             for session in sessions:
#                 # Create rich formatted content
#                 content = f"""
#                 Event: DevFest {event_name}
#                 Title: {session['title']}
#                 Speaker: {session.get('speaker', 'Not specified')}
#                 Time: {session.get('time', 'Not specified')}
#                 Track: {session.get('track', 'General')}
#                 Room: {session.get('room', 'Main Hall')}
#                 Session Type: {session.get('session_type', 'General')}
#                 Day: {day.replace('day', 'Day ')}
#                 Description: {session.get('description', '')}
#                 """
                
#                 # Create metadata for enhanced querying
#                 metadata = {
#                     "event": f"DevFest {event_name}",
#                     "title": session['title'],
#                     "speaker": session.get('speaker', 'Not specified'),
#                     "time": session.get('time', 'Not specified'),
#                     "track": session.get('track', 'General'),
#                     "room": session.get('room', 'Main Hall'),
#                     "session_type": session.get('session_type', 'General'),
#                     "day": day.replace('day', 'Day '),
#                     "description": session.get('description', '')
#                 }
                
#                 doc = Document(text=content, metadata=metadata)
#                 documents.append(doc)
                
#         return documents
    
#     def index_event(self, schedule_data: Dict, event_name: str) -> VectorStoreIndex:
#         """Create or load index for an event"""
#         event_dir = f"{self.persist_dir}/{event_name.lower()}"
        
#         try:
#             if not os.path.exists(event_dir):
#                 self.logger.info(f"Creating new index for DevFest {event_name}")
#                 documents = self.convert_to_documents(schedule_data, event_name)
#                 index = VectorStoreIndex.from_documents(
#                     documents,
#                     show_progress=True
#                 )
#                 # Persist index
#                 index.storage_context.persist(persist_dir=event_dir)
#             else:
#                 self.logger.info(f"Loading existing index for DevFest {event_name}")
#                 storage_context = StorageContext.from_defaults(persist_dir=event_dir)
#                 index = VectorStoreIndex.load_from_storage(storage_context)
                
#             self.indices[event_name.lower()] = index
#             return index
            
#         except Exception as e:
#             self.logger.error(f"Error indexing DevFest {event_name}: {str(e)}")
#             raise
            
#     def get_index(self, event_name: str) -> VectorStoreIndex:
#         """Retrieve index for an event"""
#         return self.indices.get(event_name.lower())

# if __name__ == "__main__":
#     # Configure logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
    
#     # Example usage
#     indexer = DevFestIndexer()
    
#     # Sample schedule data
#     sample_schedule = {
#         "day1": [
#             {
#                 "title": "Keynote: Future of AI",
#                 "speaker": "Jane Doe",
#                 "time": "9:00 AM",
#                 "track": "AI/ML",
#                 "room": "Main Hall",
#                 "session_type": "Keynote"
#             }
#         ]
#     }
    
#     # Index sample data
#     index = indexer.index_event(sample_schedule, "Lagos")
#     print("Index created successfully!")





import os
import logging
import re
import json
import requests
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass
import vertexai
from google.cloud import aiplatform
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex
)
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

@dataclass
class DevFestSession:
    """Data class for storing session information"""
    title: str
    speaker: str
    time: str
    track: str
    day: str
    room: str
    session_type: str
    description: Optional[str] = ""

class DevFestScraper:
    """Handles scraping for different DevFest events"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

    def scrape_lagos_schedule(self) -> Dict[str, List[Dict]]:
        """Scrape DevFest Lagos schedule"""
        schedule = {
            'day1': [],
            'day2': []
        }
        
        try:
            response = self.session.get("https://devfestlagos.com/schedule")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            schedule_container = soup.find('div', class_='schedule_scheduleItemsContainer__wkWNt')
            
            if schedule_container:
                # Extract general sessions
                general_events = schedule_container.find_all('div', class_='EventBlock_event__UsJua')
                for event in general_events:
                    session_data = {
                        'title': event.find('h3').text.strip(),
                        'time': event.find('div', class_='EventBlock_time__RQGQz').text.strip() if event.find('div', class_='EventBlock_time__RQGQz') else "Time not specified",
                        'room': event.find('div', class_='EventBlock_venue__wjpVu').find('span').text.strip() if event.find('div', class_='EventBlock_venue__wjpVu') and event.find('div', class_='EventBlock_venue__wjpVu').find('span') else "Main Hall",
                        'speaker': "N/A",
                        'track': "General",
                        'session_type': "General",
                        'day': "Day 1",
                        'description': ""
                    }
                    schedule['day1'].append(session_data)
                
                # Extract breakout sessions
                breakout_container = schedule_container.find('div', class_='EventCategory_eventSchedule__events__cCu22')
                if breakout_container:
                    breakout_events = breakout_container.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
                    for event in breakout_events:
                        session_data = {
                            'title': event.find('h3', class_='EventCategory_eventSchedule__event-title__F2air').text.strip() if event.find('h3', class_='EventCategory_eventSchedule__event-title__F2air') else "No Title",
                            'speaker': event.find('p', class_='EventCategory_eventSchedule__event-facilitator__nWvuU').text.strip() if event.find('p', class_='EventCategory_eventSchedule__event-facilitator__nWvuU') else "Not specified",
                            'time': event.find('div', class_='EventCategory_eventSchedule__event-time__f_zfq').find('span', class_='text-sm').text.strip() if event.find('div', class_='EventCategory_eventSchedule__event-time__f_zfq') else "Time not specified",
                            'room': "Breakout Room",
                            'track': "Breakout",
                            'session_type': "Breakout",
                            'day': "Day 1",
                            'description': ""
                        }
                        schedule['day1'].append(session_data)
        
        except Exception as e:
            self.logger.error(f"Error scraping Lagos schedule: {str(e)}")
            
        return schedule

    def extract_agenda_data(self, html_content: str) -> Dict:
        """Extract and parse agenda data from Nairobi page source"""
        try:
            pattern = r'Globals\.eventInfo\s*=\s*({[^;]*});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                self.logger.error("Could not find eventInfo in Nairobi page")
                return {}
                
            event_info_str = match.group(1)
            agenda_pattern = r'"agenda":\s*({[^}]*})'
            agenda_match = re.search(agenda_pattern, event_info_str, re.DOTALL)
            
            if not agenda_match:
                self.logger.error("Could not find agenda data")
                return {}
                
            agenda_str = agenda_match.group(1)
            agenda_str = (
                agenda_str
                .replace("'", '"')
                .replace('multiday', '"multiday"')
                .replace('any_descriptions', '"any_descriptions"')
                .replace('empty', '"empty"')
                .replace('days', '"days"')
                .replace('title', '"title"')
                .replace('agenda', '"agenda"')
                .replace('time', '"time"')
                .replace('activity', '"activity"')
                .replace('description', '"description"')
                .replace('audience_type', '"audience_type"')
            )
            
            agenda_str = re.sub(r':\s*([^",\{\[\d][^,\}\]]*?)(?=,|\}|\])', r': "\1"', agenda_str)
            agenda_str = agenda_str.replace('"true"', 'true').replace('"false"', 'false')
            
            try:
                agenda_data = json.loads(agenda_str)
                self.logger.info("Successfully parsed Nairobi agenda data")
                return agenda_data
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing error: {e}")
                with open('debug_agenda.json', 'w') as f:
                    f.write(agenda_str)
                return {}
                
        except Exception as e:
            self.logger.error(f"Error extracting Nairobi agenda data: {e}")
            return {}

    def scrape_nairobi_schedule(self) -> Dict[str, List[Dict]]:
        """Scrape DevFest Nairobi schedule"""
        schedule = {
            'day1': []
        }
        
        try:
            url = "https://gdg.community.dev/events/details/google-gdg-nairobi-presents-devfest-nairobi-2024-1/"
            response = self.session.get(url)
            response.raise_for_status()
            
            # Extract the JavaScript object containing the schedule
            js_pattern = r'Globals\.eventInfo\s*=\s*({.*?});'
            js_match = re.search(js_pattern, response.text, re.DOTALL)
            
            if not js_match:
                self.logger.error("Could not find eventInfo object")
                return schedule
                
            event_info_str = js_match.group(1)
            
            # Convert JavaScript object to Python dict
            import ast
            try:
                event_info_str = event_info_str.replace('false', 'False').replace('true', 'True')
                event_info = ast.literal_eval(event_info_str)
                
                agenda_data = event_info.get('agenda', {})
                days_data = agenda_data.get('days', [])
                
                if not days_data:
                    self.logger.error("No days data found")
                    return schedule
                    
                # Process the first day
                day_data = days_data[0]
                day_agenda = day_data.get('agenda', [])
                
                for session in day_agenda:
                    activity = session.get('activity', '')
                    room = ""
                    title = activity
                    
                    if '[' in activity and ']' in activity:
                        match = re.match(r'\[(.*?)\](.*)', activity)
                        if match:
                            room = match.group(1).strip()
                            title = match.group(2).strip()
                    
                    session_data = {
                        'title': title,
                        'time': session.get('time', ''),
                        'description': session.get('description', ''),
                        'room': room,
                        'audience_type': session.get('audience_type', 'IN_PERSON'),
                        'track': 'General',
                        'session_type': 'Session',
                        'speaker': session.get('description', ''),
                        'day': 'Day 1'
                    }
                    
                    schedule['day1'].append(session_data)
                    
            except Exception as e:
                self.logger.error(f"Error parsing Nairobi event info: {e}")
                
        except Exception as e:
            self.logger.error(f"Error processing Nairobi schedule: {e}")
            
        return schedule

class DevFestIndexer:
    """Indexes DevFest event data for efficient querying"""
    
    def __init__(
        self,
        project_id: str = "your-project-id",
        location: str = "us-central1",
        persist_dir: str = "./storage/devfest"
    ):
        self.project_id = project_id
        self.location = location
        self.persist_dir = persist_dir
        self.logger = logging.getLogger(__name__)
        self.scraper = DevFestScraper()
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Set up embedding model
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        # Set up LLM
        self.llm = Vertex("gemini-pro")
        
        # Configure global settings
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
        
        # Initialize storage for different events
        self.indices = {}
        
    def scrape_schedule(self, event_name: str) -> Dict[str, List[Dict]]:
        """Scrape schedule based on event name"""
        if event_name.lower() == 'lagos':
            return self.scraper.scrape_lagos_schedule()
        elif event_name.lower() == 'nairobi':
            return self.scraper.scrape_nairobi_schedule()
        else:
            raise ValueError(f"Unsupported event: {event_name}")

    def convert_to_documents(self, schedule_data: Dict, event_name: str) -> List[Document]:
        """Convert schedule data to LlamaIndex documents"""
        documents = []
        
        for day, sessions in schedule_data.items():
            for session in sessions:
                # Create rich formatted content
                content = f"""
                Event: DevFest {event_name}
                Title: {session['title']}
                Speaker: {session.get('speaker', 'Not specified')}
                Time: {session.get('time', 'Not specified')}
                Track: {session.get('track', 'General')}
                Room: {session.get('room', 'Main Hall')}
                Session Type: {session.get('session_type', 'General')}
                Day: {day.replace('day', 'Day ')}
                Description: {session.get('description', '')}
                """
                
                # Create metadata for enhanced querying
                metadata = {
                    "event": f"DevFest {event_name}",
                    "title": session['title'],
                    "speaker": session.get('speaker', 'Not specified'),
                    "time": session.get('time', 'Not specified'),
                    "track": session.get('track', 'General'),
                    "room": session.get('room', 'Main Hall'),
                    "session_type": session.get('session_type', 'General'),
                    "day": day.replace('day', 'Day '),
                    "description": session.get('description', '')
                }
                
                doc = Document(text=content, metadata=metadata)
                documents.append(doc)
                
        return documents
        
    def index_event(self, event_name: str, force_refresh: bool = False) -> VectorStoreIndex:
        """Create or load index for an event"""
        event_dir = f"{self.persist_dir}/{event_name.lower()}"
        
        try:
            if not os.path.exists(event_dir) or force_refresh:
                self.logger.info(f"Creating new index for DevFest {event_name}")
                schedule_data = self.scrape_schedule(event_name)
                
                # Save raw schedule data
                os.makedirs(event_dir, exist_ok=True)
                with open(f"{event_dir}/schedule.json", 'w') as f:
                    json.dump(schedule_data, f, indent=2)
                
                documents = self.convert_to_documents(schedule_data, event_name)
                index = VectorStoreIndex.from_documents(
                    documents,
                    show_progress=True
                )
                # Persist index
                index.storage_context.persist(persist_dir=event_dir)
            else:
                self.logger.info(f"Loading existing index for DevFest {event_name}")
                storage_context = StorageContext.from_defaults(persist_dir=event_dir)
                index = VectorStoreIndex.load_from_storage(storage_context)
                
            self.indices[event_name.lower()] = index
            return index
            
        except Exception as e:
            self.logger.error(f"Error indexing DevFest {event_name}: {str(e)}")
            raise
            
    def get_index(self, event_name: str) -> VectorStoreIndex:
        """Retrieve index for an event"""
        return self.indices.get(event_name.lower())

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    indexer = DevFestIndexer()
    
    # Index both events
    lagos_index = indexer.index_event("Lagos", force_refresh=True)
    nairobi_index = indexer.index_event("Nairobi", force_refresh=True)
    
    print("Indices created successfully!")