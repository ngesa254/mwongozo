import requests
import json
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import pytz
from enum import Enum

class SessionType(Enum):
    GENERAL = "General"
    BREAKOUT = "Breakout"
    WORKSHOP = "Workshop"
    KEYNOTE = "Keynote"

@dataclass
class DevFestSession:
    """Data structure for DevFest session information"""
    title: str
    speaker: str
    time: str
    track: str
    day: str
    room: str
    session_type: str
    description: str = "Not provided"
    tags: List[str] = None
    keywords: List[str] = None  # For better recommendation matching
    
    def __post_init__(self):
        self.tags = self.tags or []
        self.keywords = self.keywords or self._extract_keywords()
    
    def _extract_keywords(self) -> List[str]:
        """Extract keywords from title and description for matching"""
        keywords = []
        for text in [self.title, self.description]:
            words = text.lower().split()
            keywords.extend([word for word in words if len(word) > 3])
        return list(set(keywords))

    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if not k.startswith('_')}

    def relevance_score(self, interests: List[str]) -> float:
        """Calculate relevance score based on user interests"""
        if not interests:
            return 0.0
        
        interests_lower = [i.lower() for i in interests]
        matches = sum(1 for k in self.keywords if any(i in k or k in i for i in interests_lower))
        return matches / len(self.keywords) if self.keywords else 0.0

class MwongozoScheduleTool:
    """Tool for accessing and filtering DevFest Lagos schedule"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.base_url = "https://devfestlagos.com"
        self.schedule_url = f"{self.base_url}/schedule"
        self.session = self._setup_session()
        self.schedule_cache = None
        self.last_fetch_time = None
        self.cache_duration = 3600  # 1 hour cache

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('MwongozoScheduleTool')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mwongozo/1.0 - DevFest Lagos Conference Assistant',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        return session

    def _should_refresh_cache(self) -> bool:
        """Determine if cache should be refreshed"""
        if not self.schedule_cache or not self.last_fetch_time:
            return True
        elapsed = (datetime.now() - self.last_fetch_time).total_seconds()
        return elapsed > self.cache_duration

    async def get_schedule(self, refresh: bool = False) -> Dict[str, List[Dict]]:
        """Get complete schedule with caching"""
        if refresh or self._should_refresh_cache():
            self.schedule_cache = await self._fetch_schedule()
            self.last_fetch_time = datetime.now()
        return self.schedule_cache

    async def search_sessions(self, 
                            query: str = None, 
                            day: str = None,
                            track: str = None,
                            speaker: str = None) -> List[Dict]:
        """Search sessions based on criteria"""
        schedule = await self.get_schedule()
        results = []
        
        for day_sessions in schedule.values():
            for session in day_sessions:
                if self._matches_criteria(session, query, day, track, speaker):
                    results.append(session)
        
        return results

    async def get_recommendations(self, 
                                interests: List[str], 
                                day: str = None,
                                limit: int = 5) -> List[Dict]:
        """Get personalized session recommendations"""
        schedule = await self.get_schedule()
        all_sessions = []
        
        for day_key, day_sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
            all_sessions.extend(day_sessions)
        
        # Convert to DevFestSession objects for scoring
        session_objects = [DevFestSession(**s) for s in all_sessions]
        
        # Score and sort sessions
        scored_sessions = [
            (session, session.relevance_score(interests))
            for session in session_objects
        ]
        scored_sessions.sort(key=lambda x: x[1], reverse=True)
        
        # Return top recommendations
        return [
            {**session.to_dict(), 'relevance_score': score}
            for session, score in scored_sessions[:limit]
        ]

    def _matches_criteria(self, 
                         session: Dict, 
                         query: str = None, 
                         day: str = None,
                         track: str = None,
                         speaker: str = None) -> bool:
        """Check if session matches search criteria"""
        if query and query.lower() not in session['title'].lower():
            return False
        if day and day.lower() not in session['day'].lower():
            return False
        if track and track.lower() not in session['track'].lower():
            return False
        if speaker and speaker.lower() not in session['speaker'].lower():
            return False
        return True

    # ... [Previous scraping methods remain the same]

def get_tool_spec() -> Dict:
    """Get the tool specification for Gemini function calling"""
    return {
        "name": "mwongozo_schedule_tool",
        "description": "DevFest Lagos schedule assistant tool for searching sessions and getting recommendations",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search_sessions", "get_recommendations", "get_schedule"],
                    "description": "The action to perform"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for finding sessions"
                },
                "day": {
                    "type": "string",
                    "enum": ["Day 1", "Day 2"],
                    "description": "Specific day to search"
                },
                "track": {
                    "type": "string",
                    "description": "Specific track to search"
                },
                "speaker": {
                    "type": "string",
                    "description": "Speaker name to search for"
                },
                "interests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user interests for recommendations"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return"
                }
            },
            "required": ["action"]
        }
    }

# Example usage in main app
async def process_schedule_query(query: str, tool: MwongozoScheduleTool) -> Dict:
    """Process a natural language query about the schedule"""
    # This would be integrated with Gemini's function calling
    try:
        if "recommend" in query.lower():
            interests = ["AI", "Machine Learning"]  # Extract from query
            return await tool.get_recommendations(interests)
        elif "search" in query.lower():
            return await tool.search_sessions(query=query)
        else:
            return await tool.get_schedule()
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return {"error": str(e)}
