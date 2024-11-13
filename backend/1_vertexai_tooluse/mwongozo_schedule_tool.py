import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from DevFestScraper import DevFestScraper

class MwongozoScheduleTool:
    """Tool for managing DevFest Lagos schedule data"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.scraper = DevFestScraper()
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

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed"""
        if not self._last_fetch:
            return True
        elapsed = (datetime.now() - self._last_fetch).total_seconds()
        return elapsed > self.cache_duration

    async def get_schedule(self, refresh: bool = False) -> Dict[str, List[Dict]]:
        """Get the complete schedule with caching"""
        if not self._schedule_cache or refresh or self._should_refresh_cache():
            # Use the DevFestScraper to get schedule
            self._schedule_cache = self.scraper.scrape_schedule()
            self._last_fetch = datetime.now()
        return self._schedule_cache

    async def search_sessions(self, 
                            query: str = None, 
                            day: str = None,
                            track: str = None,
                            speaker: str = None) -> List[Dict]:
        """Search for specific sessions"""
        schedule = await self.get_schedule()
        results = []
        
        for day_key, sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
            
            for session in sessions:
                if self._matches_criteria(session, query, track, speaker):
                    results.append(session)
        
        return results

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

    async def get_recommendations(self, 
                                interests: List[str], 
                                day: str = None,
                                limit: int = 5) -> List[Dict]:
        """Get personalized recommendations"""
        schedule = await self.get_schedule()
        all_sessions = []
        
        for day_key, sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
            all_sessions.extend(sessions)
        
        # Score sessions based on interests
        scored_sessions = [
            (session, self._calculate_relevance(session, interests))
            for session in all_sessions
        ]
        
        # Sort by score and return top recommendations
        scored_sessions.sort(key=lambda x: x[1], reverse=True)
        return [
            {**session, 'relevance_score': score}
            for session, score in scored_sessions[:limit]
        ]

    def _calculate_relevance(self, session: Dict, interests: List[str]) -> float:
        """Calculate relevance score for a session"""
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
