# ```python
# import asyncio
# import logging
# from typing import Dict, List, Optional
# from datetime import datetime
# from dataclasses import dataclass, asdict
# import requests
# from bs4 import BeautifulSoup
# from rich.console import Console

# @dataclass
# class DevFestSession:
#     """Data class for storing session information"""
#     title: str
#     speaker: str
#     time: str
#     track: str
#     day: str
#     room: str
#     session_type: str
#     description: str = "Not provided"
#     tags: List[str] = None

#     def __post_init__(self):
#         self.tags = self.tags or []
#         # Extract keywords from title and description
#         self.keywords = self._extract_keywords()

#     def _extract_keywords(self) -> List[str]:
#         """Extract keywords from title and description"""
#         keywords = []
#         for text in [self.title, self.description]:
#             words = text.lower().split()
#             keywords.extend([word for word in words if len(word) > 3])
#         return list(set(keywords))

#     def to_dict(self) -> Dict:
#         return {k: v for k, v in asdict(self).items() if not k.startswith('_')}

# class MwongozoScheduleTool:
#     def __init__(self):
#         self.console = Console()
#         self.logger = self._setup_logger()
#         self.base_url = "https://devfestlagos.com"
#         self.schedule_url = f"{self.base_url}/schedule"
#         self.session = self._setup_session()
#         self._schedule_cache = None
#         self._last_fetch = None
#         self.cache_duration = 3600  # 1 hour

#     def _setup_logger(self) -> logging.Logger:
#         logger = logging.getLogger('MwongozoScheduleTool')
#         logger.setLevel(logging.INFO)
#         handler = logging.StreamHandler()
#         formatter = logging.Formatter(
#             '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#         )
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#         return logger

#     def _setup_session(self) -> requests.Session:
#         session = requests.Session()
#         session.headers.update({
#             'User-Agent': 'Mwongozo/1.0 - DevFest Lagos Conference Assistant',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         })
#         return session

#     async def get_schedule(self, refresh: bool = False) -> Dict[str, List[Dict]]:
#         """Get the complete schedule with caching"""
#         if not self._schedule_cache or refresh or self._should_refresh_cache():
#             self._schedule_cache = await self._fetch_schedule()
#             self._last_fetch = datetime.now()
#         return self._schedule_cache

#     def _should_refresh_cache(self) -> bool:
#         """Check if cache should be refreshed"""
#         if not self._last_fetch:
#             return True
#         elapsed = (datetime.now() - self._last_fetch).total_seconds()
#         return elapsed > self.cache_duration

#     async def _fetch_schedule(self) -> Dict[str, List[Dict]]:
#         """Fetch and process the schedule"""
#         try:
#             html_content = await self._get_html_content()
#             if not html_content:
#                 return {'day1': [], 'day2': []}

#             soup = BeautifulSoup(html_content, 'html.parser')
            
#             schedule = {
#                 'day1': await self._process_day_content(soup, "Day 1"),
#                 'day2': await self._process_day_content(soup, "Day 2")
#             }
            
#             self.logger.info(f"Fetched schedule: {len(schedule['day1'])} Day 1 sessions, {len(schedule['day2'])} Day 2 sessions")
#             return schedule
            
#         except Exception as e:
#             self.logger.error(f"Error fetching schedule: {e}")
#             return {'day1': [], 'day2': []}

#     async def _get_html_content(self) -> Optional[str]:
#         """Get HTML content with error handling"""
#         try:
#             response = await asyncio.to_thread(
#                 self.session.get, 
#                 self.schedule_url
#             )
#             response.raise_for_status()
#             return response.text
#         except Exception as e:
#             self.logger.error(f"Error fetching HTML: {e}")
#             return None

#     async def search_sessions(self, 
#                             query: str = None, 
#                             day: str = None,
#                             track: str = None,
#                             speaker: str = None) -> List[Dict]:
#         """Search sessions based on criteria"""
#         schedule = await self.get_schedule()
#         results = []
        
#         for day_key, day_sessions in schedule.items():
#             if day and day.lower() not in day_key.lower():
#                 continue
                
#             for session in day_sessions:
#                 if self._matches_criteria(session, query, track, speaker):
#                     results.append(session)
        
#         return results

#     async def get_recommendations(self, 
#                                 interests: List[str], 
#                                 day: str = None,
#                                 limit: int = 5) -> List[Dict]:
#         """Get personalized recommendations"""
#         schedule = await self.get_schedule()
#         all_sessions = []
        
#         for day_key, day_sessions in schedule.items():
#             if day and day.lower() not in day_key.lower():
#                 continue
#             all_sessions.extend(day_sessions)
        
#         # Score sessions based on interests
#         scored_sessions = [
#             (session, self._calculate_relevance(session, interests))
#             for session in all_sessions
#         ]
        
#         # Sort by score and return top recommendations
#         scored_sessions.sort(key=lambda x: x[1], reverse=True)
#         recommendations = [
#             {**session, 'relevance_score': score}
#             for session, score in scored_sessions[:limit]
#         ]
        
#         return recommendations

#     def _matches_criteria(self, 
#                          session: Dict, 
#                          query: str = None, 
#                          track: str = None,
#                          speaker: str = None) -> bool:
#         """Check if session matches search criteria"""
#         if query:
#             query = query.lower()
#             if query not in session['title'].lower() and query not in session.get('description', '').lower():
#                 return False
                
#         if track and track.lower() not in session['track'].lower():
#             return False
            
#         if speaker and speaker.lower() not in session['speaker'].lower():
#             return False
            
#         return True

#     def _calculate_relevance(self, session: Dict, interests: List[str]) -> float:
#         """Calculate session relevance score"""
#         score = 0.0
#         session_text = f"{session['title']} {session['track']} {session.get('description', '')}"
#         session_text = session_text.lower()
        
#         for interest in interests:
#             interest = interest.lower()
#             if interest in session_text:
#                 score += 1.0
#                 # Bonus for title matches
#                 if interest in session['title'].lower():
#                     score += 0.5
        
#         return score

#     async def _process_day_content(self, soup: BeautifulSoup, day: str



import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
from rich.console import Console

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
    description: str = "Not provided"
    tags: List[str] = None

    def __post_init__(self):
        self.tags = self.tags or []
        # Extract keywords from title and description
        self.keywords = self._extract_keywords()

    def _extract_keywords(self) -> List[str]:
        """Extract keywords from title and description"""
        keywords = []
        for text in [self.title, self.description]:
            words = text.lower().split()
            keywords.extend([word for word in words if len(word) > 3])
        return list(set(keywords))

    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if not k.startswith('_')}

class MwongozoScheduleTool:
    def __init__(self):
        self.console = Console()
        self.logger = self._setup_logger()
        self.base_url = "https://devfestlagos.com"
        self.schedule_url = f"{self.base_url}/schedule"
        self.session = self._setup_session()
        self._schedule_cache = None
        self._last_fetch = None
        self.cache_duration = 3600  # 1 hour

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

    async def get_schedule(self, refresh: bool = False) -> Dict[str, List[Dict]]:
        """Get the complete schedule with caching"""
        if not self._schedule_cache or refresh or self._should_refresh_cache():
            self._schedule_cache = await self._fetch_schedule()
            self._last_fetch = datetime.now()
        return self._schedule_cache

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed"""
        if not self._last_fetch:
            return True
        elapsed = (datetime.now() - self._last_fetch).total_seconds()
        return elapsed > self.cache_duration

    async def _fetch_schedule(self) -> Dict[str, List[Dict]]:
        """Fetch and process the schedule"""
        try:
            html_content = await self._get_html_content()
            if not html_content:
                return {'day1': [], 'day2': []}

            soup = BeautifulSoup(html_content, 'html.parser')
            
            schedule = {
                'day1': await self._process_day_content(soup, "Day 1"),
                'day2': await self._process_day_content(soup, "Day 2")
            }
            
            self.logger.info(f"Fetched schedule: {len(schedule['day1'])} Day 1 sessions, {len(schedule['day2'])} Day 2 sessions")
            return schedule
            
        except Exception as e:
            self.logger.error(f"Error fetching schedule: {e}")
            return {'day1': [], 'day2': []}

    async def _get_html_content(self) -> Optional[str]:
        """Get HTML content with error handling"""
        try:
            response = await asyncio.to_thread(
                self.session.get, 
                self.schedule_url
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching HTML: {e}")
            return None

    async def _process_day_content(self, soup: BeautifulSoup, day: str) -> List[Dict]:
        """Process content for a specific day"""
        sessions = []
        
        try:
            # Process general sessions
            day_selector = f"div[data-day='{day.split()[-1]}']" if day == "Day 2" else "div"
            day_content = soup.select_one(day_selector)
            
            if day_content:
                # Get general sessions
                general_events = day_content.find_all('div', class_='EventBlock_event__UsJua')
                for event in general_events:
                    session = await self._extract_session_data(event, day, "General")
                    if session:
                        sessions.append(session.to_dict())

                # Get breakout sessions
                breakout_container = day_content.find('div', class_='EventCategory_eventSchedule__events__cCu22')
                if breakout_container:
                    breakout_events = breakout_container.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
                    for event in breakout_events:
                        session = await self._extract_session_data(event, day, "Breakout")
                        if session:
                            sessions.append(session.to_dict())
            
            self.logger.info(f"Processed {len(sessions)} sessions for {day}")
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error processing {day} content: {e}")
            return []

    async def _extract_session_data(self, event_element, day: str, session_type: str = "General") -> Optional[DevFestSession]:
        """Extract session data from HTML element"""
        try:
            if session_type == "General":
                title = event_element.find('h3').text.strip()
                time_elem = event_element.find('div', class_='EventBlock_time__RQGQz')
                time = time_elem.text.strip() if time_elem else "Time not specified"
                venue_elem = event_element.find('div', class_='EventBlock_venue__wjpVu')
                room = venue_elem.find('span').text.strip() if venue_elem and venue_elem.find('span') else "Main Hall"
                speaker = "N/A"
            else:
                title_elem = event_element.find('div', class_='EventCategory_eventSchedule__event-title__F2air')
                title = title_elem.text.strip() if title_elem else "No Title"
                speaker_elem = event_element.find('p', class_='EventCategory_eventSchedule__event-facilitator__nWvuU')
                speaker = speaker_elem.text.strip() if speaker_elem else "Not specified"
                time_elem = event_element.find('div', class_='EventCategory_eventSchedule__event-time__f_zfq')
                time = time_elem.find('span', class_='text-sm').text.strip() if time_elem else "Time not specified"
                room = "Breakout Room"

            track = "General" if session_type == "General" else room

            # Create session object
            session = DevFestSession(
                title=title,
                speaker=speaker,
                time=time,
                track=track,
                day=day,
                room=room,
                session_type=session_type
            )

            return session

        except Exception as e:
            self.logger.error(f"Error extracting session data: {e}")
            return None

    async def search_sessions(self, 
                            query: str = None, 
                            day: str = None,
                            track: str = None,
                            speaker: str = None) -> List[Dict]:
        """Search sessions based on criteria"""
        schedule = await self.get_schedule()
        results = []
        
        for day_key, day_sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
                
            for session in day_sessions:
                if self._matches_criteria(session, query, track, speaker):
                    results.append(session)
        
        return results

    async def get_recommendations(self, 
                                interests: List[str], 
                                day: str = None,
                                limit: int = 5) -> List[Dict]:
        """Get personalized recommendations"""
        schedule = await self.get_schedule()
        all_sessions = []
        
        for day_key, day_sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
            all_sessions.extend(day_sessions)
        
        # Score sessions based on interests
        scored_sessions = [
            (session, self._calculate_relevance(session, interests))
            for session in all_sessions
        ]
        
        # Sort by score and return top recommendations
        scored_sessions.sort(key=lambda x: x[1], reverse=True)
        recommendations = [
            {**session, 'relevance_score': score}
            for session, score in scored_sessions[:limit]
        ]
        
        return recommendations

    def _matches_criteria(self, 
                         session: Dict, 
                         query: str = None, 
                         track: str = None,
                         speaker: str = None) -> bool:
        """Check if session matches search criteria"""
        if query:
            query = query.lower()
            if query not in session['title'].lower() and query not in session.get('description', '').lower():
                return False
                
        if track and track.lower() not in session['track'].lower():
            return False
            
        if speaker and speaker.lower() not in session['speaker'].lower():
            return False
            
        return True

    def _calculate_relevance(self, session: Dict, interests: List[str]) -> float:
        """Calculate session relevance score"""
        score = 0.0
        session_text = f"{session['title']} {session['track']} {session.get('description', '')}"
        session_text = session_text.lower()
        
        for interest in interests:
            interest = interest.lower()
            if interest in session_text:
                score += 1.0
                # Bonus for title matches
                if interest in session['title'].lower():
                    score += 0.5
        
        return score
