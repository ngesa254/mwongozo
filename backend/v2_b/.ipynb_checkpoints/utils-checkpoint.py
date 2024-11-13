import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
from rich.table import Table
from rich.markdown import Markdown
from rich.style import Style
from rich.text import Text

def setup_logging() -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger('Mwongozo')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

class MwongozoTerminal:
    def __init__(self):
        self.console = Console()

    def display_welcome(self):
        """Display welcome message"""
        self.console.print(Panel.fit(
            "[bold green]Welcome to Mwongozo - DevFest Lagos Conference Assistant![/]\n"
            "Ask me about sessions, schedules, or get personalized recommendations.\n"
            "Type 'exit' to end the conversation.",
            title="🎯 Mwongozo"
        ))

    def display_goodbye(self):
        """Display goodbye message"""
        self.console.print("\n[bold green]Goodbye! Enjoy DevFest Lagos! 👋[/]")

    def display_error(self, message: str):
        """Display error message"""
        self.console.print(
            Panel.fit(
                f"[bold red]{message}[/]",
                title="Error"
            )
        )

    def get_input(self) -> str:
        """Get user input"""
        return Prompt.ask("\n[bold blue]You")

    def display_response(self, response: str):
        """Display assistant response"""
        self.console.print("\n[bold green]Mwongozo:", style="bold green")
        self.console.print(Markdown(response))

    def progress_indicator(self):
        """Create progress indicator"""
        return Progress(
            "⚡ Processing",
            "⚙️ Analyzing",
            "🔍 Finding matches",
            "📝 Formatting response"
        )

class SessionAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._schedule_cache = None
        self._last_fetch = None
        self.cache_duration = 3600  # 1 hour

    async def get_schedule(self, day: Optional[str] = None, track: Optional[str] = None) -> Dict:
        """Get conference schedule with optional filtering"""
        schedule = await self._fetch_schedule()
        
        if day:
            schedule = {day.lower().replace(" ", ""): schedule[day.lower().replace(" ", "")]}
        if track:
            for day_sessions in schedule.values():
                day_sessions[:] = [s for s in day_sessions if track.lower() in s['track'].lower()]
        
        return schedule

    async def search_sessions(
        self,
        query: Optional[str] = None,
        day: Optional[str] = None,
        track: Optional[str] = None,
        speaker: Optional[str] = None
    ) -> List[Dict]:
        """Search for sessions based on criteria"""
        schedule = await self._fetch_schedule()
        results = []
        
        for day_key, sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
                
            for session in sessions:
                if self._matches_criteria(session, query, track, speaker):
                    results.append(session)
        
        return results

    async def get_recommendations(
        self,
        interests: List[str],
        expertise_level: str = "intermediate",
        preferred_formats: List[str] = None,
        day: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Get personalized session recommendations"""
        schedule = await self._fetch_schedule()
        scored_sessions = []
        
        for day_key, sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
                
            for session in sessions:
                score = self._calculate_session_score(
                    session,
                    interests,
                    expertise_level,
                    preferred_formats
                )
                if score > 0:
                    scored_sessions.append((session, score))
        
        # Sort by score and return top recommendations
        scored_sessions.sort(key=lambda x: x[1], reverse=True)
        return [
            self._enhance_recommendation(session, score)
            for session, score in scored_sessions[:limit]
        ]

    def _matches_criteria(
        self,
        session: Dict,
        query: Optional[str] = None,
        track: Optional[str] = None,
        speaker: Optional[str] = None
    ) -> bool:
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

    def _calculate_session_score(
        self,
        session: Dict,
        interests: List[str],
        expertise_level: str,
        preferred_formats: List[str]
    ) -> float:
        """Calculate session relevance score"""
        score = 0.0
        
        # Interest matching
        for interest in interests:
            if interest.lower() in session['title'].lower():
                score += 0.4
            if interest.lower() in session['track'].lower():
                score += 0.3
            if interest.lower() in session.get('description', '').lower():
                score += 0.2
        
        # Format preference
        if preferred_formats:
            session_format = session.get('format', '').lower()
            if session_format in [f.lower() for f in preferred_formats]:
                score += 0.2
        
        # Expertise level match
        if session.get('level', '').lower() == expertise_level.lower():
            score += 0.3
        
        return min(score, 1.0)

    def _enhance_recommendation(self, session: Dict, score: float) -> Dict:
        """Enhance recommendation with additional context"""
        return {
            **session,
            'relevance_score': score,
            'why_recommended': self._generate_recommendation_reason(session, score),
            'prerequisites': self._identify_prerequisites(session),
            'related_sessions': []  # Would be populated with actual related sessions
        }

    def _generate_recommendation_reason(self, session: Dict, score: float) -> str:
        """Generate explanation for recommendation"""
        reasons = []
        
        if score > 0.8:
            reasons.append("Strong match with your interests")
        elif score > 0.6:
            reasons.append("Good alignment with your goals")
        
        if 'level' in session:
            reasons.append(f"Appropriate for {session['level']} skill level")
        
        if 'format' in session:
            reasons.append(f"Matches preferred {session['format']} format")
        
        return " • ".join(reasons)

    def _identify_prerequisites(self, session: Dict) -> List[str]:
        """Identify session prerequisites"""
        # This would implement actual prerequisite analysis
        return session.get('prerequisites', [])  
        
           
    
    async def _fetch_schedule(self) -> Dict:
        """Fetch and cache schedule data"""
        if not self._should_refresh_cache():
            return self._schedule_cache
            
        # This would be replaced with actual API/database fetch
        # For now, using sample data
        self._schedule_cache = {
            "day1": [
                {
                    "title": "Keynote: Future of Tech in Africa",
                    "speaker": "Ada Nduka",
                    "time": "9:00 AM",
                    "track": "General",
                    "room": "Main Hall",
                    "format": "keynote",
                    "level": "all",
                    "description": "Opening keynote discussing tech trends and opportunities"
                },
                {
                    "title": "Building ML Models with TensorFlow",
                    "speaker": "Dr. Chidi Okonkwo",
                    "time": "10:30 AM",
                    "track": "AI/ML",
                    "room": "Tech Hub 1",
                    "format": "workshop",
                    "level": "intermediate",
                    "description": "Hands-on workshop on building and deploying ML models"
                }
                # Additional sessions would be added here
            ],
            "day2": [
                {
                    "title": "Web3 Development Fundamentals",
                    "speaker": "Yewande Oyebo",
                    "time": "9:00 AM",
                    "track": "Web",
                    "room": "Tech Hub 2",
                    "format": "technical",
                    "level": "beginner",
                    "description": "Introduction to Web3 development concepts"
                },
                {
                    "title": "Cloud Native Architecture Patterns",
                    "speaker": "Ibrahim Suleiman",
                    "time": "10:30 AM",
                    "track": "Cloud",
                    "room": "Tech Hub 1",
                    "format": "technical",
                    "level": "advanced",
                    "description": "Deep dive into cloud-native architecture patterns"
                }
                # Additional sessions would be added here
            ]
        }
        
        self._last_fetch = datetime.now()
        return self._schedule_cache

    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed"""
        if not self._last_fetch:
            return True
        elapsed = (datetime.now() - self._last_fetch).total_seconds()
        return elapsed > self.cache_duration

def format_response(response_type: str, data: Dict) -> str:
    """Format different types of responses"""
    if response_type == "schedule":
        return _format_schedule(data)
    elif response_type == "search":
        return _format_search_results(data)
    elif response_type == "recommendations":
        return _format_recommendations(data)
    return str(data)

def _format_schedule(schedule: Dict) -> str:
    """Format schedule data into markdown"""
    output = []
    for day, sessions in schedule.items():
        output.append(f"\n## {day.upper()} SCHEDULE\n")
        for session in sorted(sessions, key=lambda x: x['time']):
            output.append(
                f"### {session['time']} - {session['title']}\n"
                f"**Speaker:** {session['speaker']}\n"
                f"**Track:** {session['track']}\n"
                f"**Room:** {session['room']}\n"
                f"**Format:** {session['format'].title()}\n"
                f"**Level:** {session['level'].title()}\n"
                f"{session.get('description', '')}\n"
            )
    return "\n".join(output)

def _format_search_results(sessions: List[Dict]) -> str:
    """Format search results into markdown"""
    if not sessions:
        return "No sessions found matching your criteria."
    
    output = ["\n## MATCHING SESSIONS\n"]
    for session in sessions:
        output.append(
            f"### {session['title']}\n"
            f"**Time:** {session['time']}\n"
            f"**Speaker:** {session['speaker']}\n"
            f"**Track:** {session['track']}\n"
            f"**Room:** {session['room']}\n"
        )
    return "\n".join(output)

def _format_recommendations(recommendations: List[Dict]) -> str:
    """Format recommendations into markdown"""
    if not recommendations:
        return "No recommendations found matching your interests."
    
    output = ["\n## RECOMMENDED SESSIONS\n"]
    for rec in recommendations:
        relevance = "⭐" * int(rec['relevance_score'] * 5)
        output.append(
            f"### {rec['title']}\n"
            f"**Relevance:** {relevance}\n"
            f"**Time:** {rec['time']}\n"
            f"**Speaker:** {rec['speaker']}\n"
            f"**Track:** {rec['track']}\n"
            f"**Format:** {rec['format'].title()}\n"
            f"**Why Recommended:** {rec['why_recommended']}\n"
        )
        
        if rec['prerequisites']:
            output.append(
                "\n**Prerequisites:**\n" +
                "\n".join(f"- {prereq}" for prereq in rec['prerequisites'])
            )
            
        output.append("\n---\n")
    
    return "\n".join(output)
