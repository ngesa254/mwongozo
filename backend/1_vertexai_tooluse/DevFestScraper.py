import requests
import json
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

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

    def to_dict(self) -> Dict:
        return asdict(self)

class DevFestScraper:
    def __init__(self):
        self.logger = self._setup_logger()
        self.base_url = "https://devfestlagos.com"
        self.schedule_url = f"{self.base_url}/schedule"
        self.session = self._setup_session()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('DevFestScraper')
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        return session

    def _get_html_content(self) -> Optional[str]:
        try:
            response = self.session.get(self.schedule_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching schedule page: {str(e)}")
            return None

    def _extract_session_data(self, event_element, day: str, session_type: str = "General") -> Optional[DevFestSession]:
        try:
            # Extract title
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

            return DevFestSession(
                title=title,
                speaker=speaker,
                time=time,
                track=track,
                day=day,
                room=room,
                session_type=session_type
            )
        except Exception as e:
            self.logger.error(f"Error extracting session data: {str(e)}")
            return None

    def scrape_schedule(self) -> Dict[str, List[Dict]]:
        """Main method to scrape the schedule"""
        schedule = {
            'day1': [],
            'day2': []
        }

        html_content = self._get_html_content()
        if not html_content:
            return schedule

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Process Day 1
        schedule_container = soup.find('div', class_='schedule_scheduleItemsContainer__wkWNt')
        if schedule_container:
            # Get general sessions
            general_events = schedule_container.find_all('div', class_='EventBlock_event__UsJua')
            for event in general_events:
                session = self._extract_session_data(event, "Day 1", "General")
                if session:
                    schedule['day1'].append(session.to_dict())

            # Get breakout sessions
            breakout_container = schedule_container.find('div', class_='EventCategory_eventSchedule__events__cCu22')
            if breakout_container:
                breakout_events = breakout_container.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
                for event in breakout_events:
                    session = self._extract_session_data(event, "Day 1", "Breakout")
                    if session:
                        schedule['day1'].append(session.to_dict())

        # Process Day 2 (needs to click the Day 2 tab first)
        day2_container = soup.find('div', {'data-day': '2'})
        if day2_container:
            # Get general sessions for Day 2
            general_events = day2_container.find_all('div', class_='EventBlock_event__UsJua')
            for event in general_events:
                session = self._extract_session_data(event, "Day 2", "General")
                if session:
                    schedule['day2'].append(session.to_dict())

            # Get breakout sessions for Day 2
            breakout_container = day2_container.find('div', class_='EventCategory_eventSchedule__events__cCu22')
            if breakout_container:
                breakout_events = breakout_container.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
                for event in breakout_events:
                    session = self._extract_session_data(event, "Day 2", "Breakout")
                    if session:
                        schedule['day2'].append(session.to_dict())

        self.logger.info(f"Successfully scraped {len(schedule['day1'])} Day 1 sessions")
        self.logger.info(f"Successfully scraped {len(schedule['day2'])} Day 2 sessions")
        
        return schedule

    def save_to_json(self, schedule: Dict[str, List[Dict]], filename: str = "devfest_schedule.json"):
        """Save schedule to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Successfully saved schedule to {filename}")
        except IOError as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")

# For standalone testing
if __name__ == "__main__":
    # Create scraper instance
    scraper = DevFestScraper()
    
    # Scrape schedule
    print("Scraping DevFest Lagos schedule...")
    schedule = scraper.scrape_schedule()
    
    # Save to JSON
    scraper.save_to_json(schedule)
    
    # Print summary
    total_sessions = len(schedule['day1']) + len(schedule['day2'])
    print(f"\nSummary:")
    print(f"Total sessions scraped: {total_sessions}")
    print(f"Day 1 sessions: {len(schedule['day1'])}")
    print(f"Day 2 sessions: {len(schedule['day2'])}")
    print("\nFull schedule has been saved to 'devfest_schedule.json'")
