import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from DevFestScraper import DevFestScraper

@dataclass
class SessionRecommendation:
    """Enhanced session recommendation with metadata"""
    session: Dict
    relevance_score: float
    match_reasons: List[str]
    complementary_sessions: List[Dict]
    expertise_level: str
    prerequisites: List[str]

class MwongozoScheduleTool:
    """Enhanced tool for managing DevFest schedule and recommendations"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.scraper = DevFestScraper()
        self._schedule_cache = None
        self._last_fetch = None
        self.cache_duration = 3600  # 1 hour cache

        # Define track keywords for better matching
        self.track_keywords = {
            "AI/ML": [
                "artificial intelligence", "machine learning", "deep learning", 
                "neural networks", "ai", "ml", "data science", "nlp", 
                "computer vision", "tensorflow", "pytorch"
            ],
            "Web": [
                "web development", "javascript", "frontend", "backend", 
                "fullstack", "react", "angular", "vue", "node.js", "api",
                "html", "css", "web3", "typescript"
            ],
            "Mobile": [
                "android", "ios", "flutter", "react native", "mobile development",
                "kotlin", "swift", "mobile apps", "pwa", "cross-platform"
            ],
            "Cloud": [
                "aws", "azure", "gcp", "kubernetes", "docker", "cloud native",
                "serverless", "microservices", "containers", "devops",
                "cloud computing", "iaas", "paas", "saas"
            ],
            "DevOps": [
                "ci/cd", "automation", "deployment", "monitoring", "infrastructure",
                "jenkins", "github actions", "gitlab", "ansible", "terraform"
            ],
            "Security": [
                "cybersecurity", "encryption", "authentication", "security",
                "oauth", "jwt", "pentesting", "devsecops", "zero trust"
            ],
            "Emerging Tech": [
                "blockchain", "vr", "ar", "iot", "5g", "quantum computing",
                "edge computing", "web3", "metaverse", "cryptocurrency"
            ]
        }

        # Session format types
        self.session_formats = {
            "workshop": ["hands-on", "workshop", "lab", "practical"],
            "talk": ["session", "presentation", "talk", "lecture"],
            "panel": ["panel", "discussion", "qa", "forum"],
            "keynote": ["keynote", "plenary", "featured"]
        }

        # Expertise level indicators
        self.expertise_indicators = {
            "beginner": ["introduction", "basic", "fundamental", "getting started", "101", "beginner"],
            "intermediate": ["intermediate", "practical", "applied", "real-world"],
            "advanced": ["advanced", "expert", "deep dive", "architecture", "internals"]
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
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
            self._schedule_cache = self.scraper.scrape_schedule()
            self._last_fetch = datetime.now()
            self.logger.info("Schedule cache refreshed")
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

    async def get_recommendations(self, 
                                interests: List[str], 
                                expertise_level: str = "intermediate",
                                preferred_formats: List[str] = None,
                                day: str = None,
                                limit: int = 5) -> List[SessionRecommendation]:
        """Get personalized session recommendations"""
        schedule = await self.get_schedule()
        all_sessions = []
        
        # Gather relevant sessions
        for day_key, sessions in schedule.items():
            if day and day.lower() not in day_key.lower():
                continue
            all_sessions.extend(sessions)

        # Score and analyze sessions
        recommendations = []
        for session in all_sessions:
            score, reasons = self._calculate_relevance_detailed(
                session, 
                interests, 
                expertise_level,
                preferred_formats
            )
            
            if score > 0:
                complementary = self._find_complementary_sessions(
                    session, 
                    all_sessions, 
                    interests
                )
                
                session_level, prereqs = self._analyze_session_requirements(session)
                
                recommendation = SessionRecommendation(
                    session=session,
                    relevance_score=score,
                    match_reasons=reasons,
                    complementary_sessions=complementary[:2],
                    expertise_level=session_level,
                    prerequisites=prereqs
                )
                recommendations.append(recommendation)

        # Sort by relevance score
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:limit]

    def _calculate_relevance_detailed(self, 
                                    session: Dict, 
                                    interests: List[str],
                                    expertise_level: str,
                                    preferred_formats: List[str]) -> Tuple[float, List[str]]:
        """Calculate detailed relevance score with reasons"""
        score = 0.0
        reasons = []
        
        session_text = f"{session['title']} {session['track']} {session.get('description', '')}"
        session_text = session_text.lower()
        
        # Match interests and track keywords
        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in session_text:
                score += 1.0
                if interest_lower in session['title'].lower():
                    score += 0.5
                    reasons.append(f"Directly addresses {interest}")
            
            # Track keyword matches
            for track, keywords in self.track_keywords.items():
                if any(keyword in interest_lower for keyword in keywords):
                    if session['track'].lower() == track.lower():
                        score += 0.8
                        reasons.append(f"Matches {track} track interest")

        # Format preference matching
        session_format = self._detect_session_format(session)
        if preferred_formats and session_format in preferred_formats:
            score += 0.3
            reasons.append(f"Preferred session format: {session_format}")

        # Expertise level matching
        session_level = self._determine_session_level(session)
        if session_level == expertise_level:
            score += 0.4
            reasons.append(f"Matches expertise level: {expertise_level}")

        return score, reasons

    def _detect_session_format(self, session: Dict) -> str:
        """Detect the format of a session"""
        text = f"{session['title']} {session.get('description', '')}".lower()
        
        for format_type, indicators in self.session_formats.items():
            if any(indicator in text for indicator in indicators):
                return format_type
        
        return "talk"  # default format

    def _find_complementary_sessions(self, 
                                   current_session: Dict,
                                   all_sessions: List[Dict],
                                   interests: List[str]) -> List[Dict]:
        """Find complementary sessions"""
        complementary = []
        current_topics = set(self._extract_topics(current_session))
        
        for session in all_sessions:
            if session == current_session:
                continue
                
            session_topics = set(self._extract_topics(session))
            common_topics = current_topics & session_topics
            
            if common_topics and len(common_topics) < len(current_topics):
                relevance = self._calculate_complementary_relevance(
                    session, 
                    current_session,
                    interests
                )
                if relevance > 0.5:
                    complementary.append((session, relevance))
        
        complementary.sort(key=lambda x: x[1], reverse=True)
        return [session for session, _ in complementary[:3]]

    def _calculate_complementary_relevance(self,
                                         session: Dict,
                                         current_session: Dict,
                                         interests: List[str]) -> float:
        """Calculate relevance score for complementary session"""
        score = 0.0
        
        # Topic overlap
        current_topics = set(self._extract_topics(current_session))
        session_topics = set(self._extract_topics(session))
        common_topics = current_topics & session_topics
        
        score += len(common_topics) * 0.3
        
        # Interest matching
        session_text = f"{session['title']} {session['track']} {session.get('description', '')}"
        session_text = session_text.lower()
        
        for interest in interests:
            if interest.lower() in session_text:
                score += 0.2
        
        return min(score, 1.0)

    def _extract_topics(self, session: Dict) -> List[str]:
        """Extract topics from session"""
        topics = []
        text = f"{session['title']} {session.get('description', '')}"
        
        for track, keywords in self.track_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                topics.append(track)
                
        return topics

    def _determine_session_level(self, session: Dict) -> str:
        """Determine session expertise level"""
        text = f"{session['title']} {session.get('description', '')}".lower()
        
        for level, indicators in self.expertise_indicators.items():
            if any(indicator in text for indicator in indicators):
                return level
        
        return "intermediate"  # default level

    def _analyze_session_requirements(self, session: Dict) -> Tuple[str, List[str]]:
        """Analyze session requirements"""
        text = f"{session['title']} {session.get('description', '')}".lower()
        prerequisites = []
        
        prereq_indicators = [
            "required", "prerequisite", "familiarity with", "knowledge of",
            "should know", "should be familiar with", "experience with"
        ]
        
        for indicator in prereq_indicators:
            if indicator in text:
                idx = text.find(indicator)
                if idx != -1:
                    phrase = text[idx:idx+50].split(".")[0].strip()
                    prerequisites.append(phrase)
        
        return self._determine_session_level(session), prerequisites

    def _matches_criteria(self, 
                         session: Dict, 
                         query: str = None, 
                         track: str = None,
                         speaker: str = None) -> bool:
        """Check if session matches search criteria"""
        if query:
            query = query.lower()
            session_text = f"{session['title']} {session.get('description', '')}".lower()
            if query not in session_text:
                return False
        
        if track and track.lower() not in session['track'].lower():
            return False
        
        if speaker and speaker.lower() not in session['speaker'].lower():
            return False
        
        return True
