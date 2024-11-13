!pip install -qU \
    google-cloud-aiplatform \
    google-cloud-storage \
    llama-index \
    llama-index-embeddings-vertex \
    llama-index-llms-vertex \
    llama-index-vector_stores-vertexaivectorsearch \
    llama-index-llms-fireworks \
    llama-index-embeddings-huggingface


# Imports
import os
import logging
import re 

from google.cloud import aiplatform, storage
from llama_index.core import (
    Document,
    PromptTemplate,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
)
from llama_index.core.agent import ReActAgent
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.objects import ObjectIndex
from llama_index.core.prompts import LangchainPromptTemplate
from llama_index.core.prompts.base import BasePromptTemplate
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.llms.vertex import Vertex
from llama_index.vector_stores.vertexaivectorsearch import VertexAIVectorStore

from llama_index.llms.vertex import Vertex

PROJECT_ID = "angelic-bee-193823"  
LOCATION = "us-central1"  

import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION)


from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")


llm = Vertex("gemini-pro")

Settings.embed_model = embed_model
Settings.llm = llm


from typing import Dict, List
from llama_index.core.tools import FunctionTool
from llama_index.core.schema import Document
import requests
import json
from bs4 import BeautifulSoup
from dataclasses import dataclass
from IPython.display import JSON, display

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

def get_devfest_schedule() -> Dict[str, List[Dict]]:
    """
    Scrape and return the DevFest Lagos schedule as JSON data.
    Returns a dictionary with days as keys and lists of session information as values.
    """
    # Initialize schedule structure
    schedule = {
        'day1': [],
        'day2': []
    }
    
    try:
        # Set up session and get page content
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        
        # Get HTML content
        response = session.get("https://devfestlagos.com/schedule")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find schedule container
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
                    'day': "Day 1"
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
                        'day': "Day 1"
                    }
                    schedule['day1'].append(session_data)
    
    except Exception as e:
        print(f"Error scraping schedule: {str(e)}")
        
    return schedule

def convert_to_documents(schedule_data: Dict[str, List[Dict]]) -> List[Document]:
    """
    Convert schedule data into LlamaIndex Document objects
    """
    documents = []
    
    for day, sessions in schedule_data.items():
        for session in sessions:
            # Create formatted content
            content = f"""
            Title: {session['title']}
            Speaker: {session['speaker']}
            Time: {session['time']}
            Track: {session['track']}
            Room: {session['room']}
            Session Type: {session['session_type']}
            Day: {session['day']}
            """
            
            # Create metadata for better querying
            metadata = {
                "day": session['day'],
                "track": session['track'],
                "session_type": session['session_type'],
                "speaker": session['speaker'],
                "time": session['time'],
                "room": session['room']
            }
            
            # Create Document object
            doc = Document(
                text=content,
                metadata=metadata
            )
            documents.append(doc)
    
    return documents

class DevFestScheduleTool:
    """Tool for handling DevFest schedule data"""
    
    def __init__(self):
        self.schedule_data = None
        self.documents = None
    
    def get_schedule(self) -> Dict[str, List[Dict]]:
        """Get schedule data"""
        if not self.schedule_data:
            self.schedule_data = get_devfest_schedule()
        return self.schedule_data
    
    def get_documents(self) -> List[Document]:
        """Get schedule as Document objects"""
        if not self.documents:
            schedule_data = self.get_schedule()
            self.documents = convert_to_documents(schedule_data)
        return self.documents
    
    def save_schedule(self, filename: str = 'devfest_schedule.json'):
        """Save schedule to JSON file"""
        schedule_data = self.get_schedule()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
    
    def display_schedule(self):
        """Display schedule in notebook"""
        schedule_data = self.get_schedule()
        display(JSON(schedule_data))

# Create the Llama Index Function Tool
devfest_schedule_tool = FunctionTool.from_defaults(
    fn=get_devfest_schedule,
    name="get_devfest_schedule",
    description="Get the complete DevFest Lagos schedule as JSON data and convert to Document objects for indexing"
)

# Example usage in Jupyter notebook
if __name__ == "__main__":
    # Create tool instance
    tool = DevFestScheduleTool()
    
    # Get and display schedule
    print("Fetching DevFest schedule...")
    tool.display_schedule()
    
    # Get documents
    print("\nConverting to Documents...")
    documents = tool.get_documents()
    print(f"Created {len(documents)} Document objects")
    
    # Save schedule
    tool.save_schedule()
    print("\nSchedule saved to devfest_schedule.json")
    
    # Example of document content
    if documents:
        print("\nExample Document content:")
        print(documents[0].text)
        print("\nExample Document metadata:")
        print(documents[0].metadata)
        
        
        
        # Basic usage
tool = DevFestScheduleTool()

# Get JSON data
schedule_data = tool.get_schedule()
tool.display_schedule()

# Get Document objects
documents = tool.get_documents()

# Save to file
tool.save_schedule()

# Access individual documents
print(f"First session: {documents[0].text}")


# Get documents
tool = DevFestScheduleTool()
lagos_documents = tool.get_documents()

# Create index
index = VectorStoreIndex.from_documents(lagos_documents)

# Create query engine
query_engine = index.as_query_engine()

# Query the schedule
response = query_engine.query("What sessions are about web development?")
print(response)



# > What sessions are available tomorrow?
# > Find me sessions about AI and machine learning
# > Who is speaking about web development?
# > Recommend sessions for someone interested in cloud computing


#   "Show me all AI sessions on Day 1",
#     "Who are the keynote speakers?",
#     "Recommend sessions for a web developer",
#     "What's happening in Room 1 tomorrow?",
#     "Is there a workshop about cloud computing?"

# Query the schedule
response = query_engine.query("Find me sessions about AI and machine learning")
print(response)



def extract_agenda_data(html_content: str) -> Dict:
    """Extract and parse agenda data from the page source"""
    try:
        # Look for the eventInfo object
        pattern = r'Globals\.eventInfo\s*=\s*({[^;]*});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            logger.error("Could not find eventInfo in page")
            return {}
            
        # Get the raw eventInfo string
        event_info_str = match.group(1)
        
        # Extract the agenda portion
        agenda_pattern = r'"agenda":\s*({[^}]*})'
        agenda_match = re.search(agenda_pattern, event_info_str, re.DOTALL)
        
        if not agenda_match:
            logger.error("Could not find agenda data")
            return {}
            
        # Get the raw agenda string and clean it up
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
        
        # Add quotes around string values
        agenda_str = re.sub(r':\s*([^",\{\[\d][^,\}\]]*?)(?=,|\}|\])', r': "\1"', agenda_str)
        
        # Fix booleans
        agenda_str = agenda_str.replace('"true"', 'true').replace('"false"', 'false')
        
        try:
            # Parse the cleaned JSON
            agenda_data = json.loads(agenda_str)
            logger.info("Successfully parsed agenda data")
            return agenda_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            # Save problematic string for debugging
            with open('debug_agenda.json', 'w') as f:
                f.write(agenda_str)
            return {}
            
    except Exception as e:
        logger.error(f"Error extracting agenda data: {e}")
        return {}

def get_devfest_schedule() -> Dict[str, List[Dict]]:
    """Fetch and parse the DevFest schedule"""
    schedule = {
        'day1': []
    }
    
    try:
        url = "https://gdg.community.dev/events/details/google-gdg-nairobi-presents-devfest-nairobi-2024-1/"
        logger.info(f"Fetching schedule from: {url}")
        
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        response.raise_for_status()
        
        # Save the HTML for debugging if needed
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        # Extract the JavaScript object containing the schedule
        js_pattern = r'Globals\.eventInfo\s*=\s*({.*?});'
        js_match = re.search(js_pattern, response.text, re.DOTALL)
        
        if not js_match:
            logger.error("Could not find eventInfo object")
            return schedule
            
        # Get the raw eventInfo string
        event_info_str = js_match.group(1)
        
        # Extract the schedule data using eval (since it's a JavaScript object)
        import ast
        try:
            # Convert JavaScript object to Python dict
            event_info_str = event_info_str.replace('false', 'False').replace('true', 'True')
            event_info = ast.literal_eval(event_info_str)
            
            # Get the agenda data
            agenda_data = event_info.get('agenda', {})
            days_data = agenda_data.get('days', [])
            
            if not days_data:
                logger.error("No days data found")
                return schedule
                
            # Process the first day
            day_data = days_data[0]
            day_agenda = day_data.get('agenda', [])
            
            for session in day_agenda:
                # Extract room and title
                activity = session.get('activity', '')
                room = ""
                title = activity
                
                # Check for room in brackets
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
                    'track': 'General',  # Will be determined later
                    'session_type': 'Session',  # Will be determined later
                    'speaker': ''  # Will be extracted from description
                }
                
                # Extract speaker if in description
                if session_data['description']:
                    session_data['speaker'] = session_data['description']
                
                schedule['day1'].append(session_data)
                
            logger.info(f"Successfully processed {len(schedule['day1'])} sessions")
            
        except Exception as e:
            logger.error(f"Error parsing event info: {e}")
            
    except Exception as e:
        logger.error(f"Error processing schedule: {e}")
        
    return schedule

# Update display function to handle empty schedules
def display_schedule(schedule_data: Dict[str, List[Dict]], show_details: bool = True):
    """Display the schedule in a readable format"""
    if not schedule_data or not schedule_data.get('day1'):
        print("\nNo schedule data available. Please check the logs for errors.")
        return
        
    sessions = schedule_data['day1']
    if not sessions:
        print("\nNo sessions found in the schedule.")
        return
        
    print("\n=== DevFest Nairobi 2024 Schedule ===\n")
    
    # Sort sessions by time
    for session in sorted(sessions, key=lambda x: x.get('time', '')):
        print(f"Time: {session['time']}")
        print(f"Title: {session['title']}")
        if session['room']:
            print(f"Room: {session['room']}")
        if session['speaker']:
            print(f"Speaker: {session['speaker']}")
        if show_details and session['description']:
            print(f"Description: {session['description']}")
        print("-" * 50)



# Test the scraper
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get the schedule
    print("Fetching DevFest schedule...")
    schedule = get_devfest_schedule()
    
    # Display the schedule
    display_schedule(schedule)
    
    # Save to file for debugging
    with open('schedule_data.json', 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)

        
        
def convert_to_documents(schedule_data: Dict[str, List[Dict]]) -> List[Document]:
    """
    Convert schedule data into LlamaIndex Document objects
    """
    documents = []
    
    for day, sessions in schedule_data.items():
        for session in sessions:
            # Create formatted content with safe access to fields
            content = f"""
            Title: {session['title']}
            Time: {session['time']}
            Room: {session.get('room', 'Not specified')}
            Speaker: {session.get('speaker', 'Not specified')}
            Track: {session.get('track', 'General')}
            Session Type: {session.get('session_type', 'Session')}
            Description: {session.get('description', '')}
            Audience Type: {session.get('audience_type', 'IN_PERSON')}
            Day: {day.replace('day', 'Day ')}
            """
            
            # Create metadata for better querying
            metadata = {
                "title": session['title'],
                "time": session['time'],
                "room": session.get('room', 'Not specified'),
                "speaker": session.get('speaker', 'Not specified'),
                "track": session.get('track', 'General'),
                "session_type": session.get('session_type', 'Session'),
                "description": session.get('description', ''),
                "audience_type": session.get('audience_type', 'IN_PERSON'),
                "day": day.replace('day', 'Day '),
                "event": "DevFest Nairobi 2024"
            }
            
            # Create Document object
            doc = Document(
                text=content,
                metadata=metadata
            )
            documents.append(doc)
    
    return documents

class DevFestScheduleTool:
    """Tool for handling DevFest schedule data"""
    
    def __init__(self):
        self.schedule_data = None
        self.documents = None
    
    def get_schedule(self) -> Dict[str, List[Dict]]:
        """Get schedule data"""
        if not self.schedule_data:
            self.schedule_data = get_devfest_schedule()
        return self.schedule_data
    
    def get_documents(self) -> List[Document]:
        """Get schedule as Document objects"""
        if not self.documents:
            schedule_data = self.get_schedule()
            self.documents = convert_to_documents(schedule_data)
            logger.info(f"Created {len(self.documents)} documents")
        return self.documents
    
    def save_schedule(self, filename: str = 'devfest_nairobi_schedule.json'):
        """Save schedule to JSON file"""
        schedule_data = self.get_schedule()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
    
    def display_schedule(self, show_details: bool = False):
        """Display schedule in notebook"""
        if show_details:
            documents = self.get_documents()
            for doc in documents:
                print("\n" + "="*50)
                print(doc.text)
        else:
            schedule_data = self.get_schedule()
            display(JSON(schedule_data))

# Create the Llama Index Function Tool
devfest_schedule_tool = FunctionTool.from_defaults(
    fn=get_devfest_schedule,
    name="get_devfest_schedule",
    description="Get the complete DevFest Nairobi 2024 schedule as JSON data and convert to Document objects for indexing"
)




# Create tool instance
tool = DevFestScheduleTool()

# Get documents
nairobi_documents = tool.get_documents()

# Build index
index = VectorStoreIndex.from_documents(nairobi_documents)

# Create query engine
query_engine = index.as_query_engine()

# Test query
response = query_engine.query("What sessions are available in the afternoon?")
print(response)



# Query the schedule
response = query_engine.query("Find me sessions about AI and machine learning")
print(response)



## ReACT

# build index
dv_lagos_index = VectorStoreIndex.from_documents(lagos_documents)
dv_nairobi_index = VectorStoreIndex.from_documents(nairobi_documents)
    

# persist index
dv_lagos_index.storage_context.persist(persist_dir="./storage/devfest_lagos")
dv_nairobi_index.storage_context.persist(persist_dir="./storage/devfest_nairobi")


dv_lagos_engine = dv_lagos_index.as_query_engine(similarity_top_k=3)
dv_nairobi_engine = dv_nairobi_index.as_query_engine(similarity_top_k=3)




query_engine_tools = [
    QueryEngineTool(
        query_engine=dv_nairobi_engine,
        metadata=ToolMetadata(
            name="devfest_nairobi",
            description=(
                "Provides information about DevFest Nairobi 2024 schedule, "
                "including sessions, speakers, tracks, and timings. "
                "Use for queries specifically about the Nairobi event."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=dv_lagos_engine,
        metadata=ToolMetadata(
            name="devfest_lagos",
            description=(
                "Provides information about DevFest Lagos 2024 schedule, "
                "including sessions, speakers, tracks, and timings. "
                "Use for queries specifically about the Lagos event."
            ),
        ),
    ),
]




agent = ReActAgent.from_tools(
    query_engine_tools,
    llm=llm,
    verbose=True,
    # context=context
)




response = agent.chat("Find me sessions about AI and machine learning in DevFest Nairobi")
print(str(response))



response = agent.chat(
    "Compare and contrast DevFest Nairobi and DevFest Lagos Schedules, then"
    " give an analysis"
)
print(str(response))