# # import requests
# # from bs4 import BeautifulSoup
# # from datetime import datetime
# # import pytz
# # from typing import List, Dict, Optional
# # import logging
# # import json

# # class DevFestSession:
# #     def __init__(self, title: str, speaker: str, time: str, track: str, 
# #                  description: str, difficulty: str, tags: List[str]):
# #         self.title = title
# #         self.speaker = speaker
# #         self.time = time
# #         self.track = track
# #         self.description = description
# #         self.difficulty = difficulty
# #         self.tags = tags

# #     def to_dict(self) -> Dict:
# #         return {
# #             'title': self.title,
# #             'speaker': self.speaker,
# #             'time': self.time,
# #             'track': self.track,
# #             'description': self.description,
# #             'difficulty': difficulty,
# #             'tags': self.tags
# #         }

# # class DevFestScraper:
# #     def __init__(self, base_url: str = "https://devfestlagos.com"):
# #         self.base_url = base_url
# #         self.schedule_url = f"{base_url}/schedule"
# #         self.logger = self._setup_logger()
# #         self.lagos_tz = pytz.timezone('Africa/Lagos')

# #     def _setup_logger(self) -> logging.Logger:
# #         logger = logging.getLogger('DevFestScraper')
# #         logger.setLevel(logging.INFO)
# #         handler = logging.StreamHandler()
# #         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# #         handler.setFormatter(formatter)
# #         logger.addHandler(handler)
# #         return logger

# #     def _make_request(self, url: str) -> Optional[str]:
# #         """Make HTTP request with error handling and retries"""
# #         try:
# #             headers = {
# #                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# #             }
# #             response = requests.get(url, headers=headers, timeout=10)
# #             response.raise_for_status()
# #             return response.text
# #         except requests.RequestException as e:
# #             self.logger.error(f"Error fetching URL {url}: {str(e)}")
# #             return None

# #     def _parse_session_time(self, time_str: str) -> str:
# #         """Parse and standardize session time"""
# #         try:
# #             # Assuming time format from the website, adjust as needed
# #             parsed_time = datetime.strptime(time_str.strip(), "%I:%M %p")
# #             return parsed_time.strftime("%H:%M")
# #         except ValueError as e:
# #             self.logger.warning(f"Error parsing time {time_str}: {str(e)}")
# #             return time_str

# #     def _extract_session_data(self, session_element) -> Optional[DevFestSession]:
# #         """Extract data from a single session element"""
# #         try:
# #             title = session_element.select_one('.session-title').text.strip()
# #             speaker = session_element.select_one('.speaker-name').text.strip()
# #             time = self._parse_session_time(session_element.select_one('.session-time').text.strip())
# #             track = session_element.select_one('.track-name').text.strip()
# #             description = session_element.select_one('.session-description').text.strip()
# #             difficulty = session_element.select_one('.difficulty-level').text.strip()
# #             tags = [tag.text.strip() for tag in session_element.select('.session-tags .tag')]

# #             return DevFestSession(
# #                 title=title,
# #                 speaker=speaker,
# #                 time=time,
# #                 track=track,
# #                 description=description,
# #                 difficulty=difficulty,
# #                 tags=tags
# #             )
# #         except AttributeError as e:
# #             self.logger.error(f"Error extracting session data: {str(e)}")
# #             return None

# #     def scrape_schedule(self) -> List[Dict]:
# #         """
# #         Main function to scrape the DevFest Lagos schedule
        
# #         Returns:
# #             List[Dict]: List of session dictionaries containing event information
# #         """
# #         self.logger.info("Starting schedule scraping")
# #         sessions = []
        
# #         html_content = self._make_request(self.schedule_url)
# #         if not html_content:
# #             self.logger.error("Failed to fetch schedule page")
# #             return sessions

# #         soup = BeautifulSoup(html_content, 'html.parser')
# #         session_elements = soup.select('.session-card')  # Adjust selector based on actual HTML structure

# #         for element in session_elements:
# #             session = self._extract_session_data(element)
# #             if session:
# #                 sessions.append(session.to_dict())

# #         self.logger.info(f"Successfully scraped {len(sessions)} sessions")
# #         return sessions

# #     def save_to_json(self, sessions: List[Dict], filename: str = "devfest_schedule.json"):
# #         """Save scraped data to JSON file"""
# #         try:
# #             with open(filename, 'w', encoding='utf-8') as f:
# #                 json.dump(sessions, f, ensure_ascii=False, indent=2)
# #             self.logger.info(f"Successfully saved schedule to {filename}")
# #         except IOError as e:
# #             self.logger.error(f"Error saving to JSON: {str(e)}")

# # def get_devfest_schedule() -> List[Dict]:
# #     """
# #     Convenience function to get DevFest schedule data
    
# #     Returns:
# #         List[Dict]: List of session dictionaries containing event information
    
# #     Example:
# #         >>> schedule = get_devfest_schedule()
# #         >>> for session in schedule:
# #         ...     print(f"{session['time']} - {session['title']}")
# #     """
# #     scraper = DevFestScraper()
# #     return scraper.scrape_schedule()

# # if __name__ == "__main__":
# #     # Create scraper instance
# #     scraper = DevFestScraper()
    
# #     # Scrape the schedule
# #     print("Scraping DevFest Lagos schedule...")
# #     sessions = scraper.scrape_schedule()
    
# #     # Display results
# #     if sessions:
# #         print(f"\nSuccessfully scraped {len(sessions)} sessions!")
# #         print("\nSample of scraped data:")
# #         for session in sessions[:3]:  # Show first 3 sessions
# #             print(f"\nTitle: {session['title']}")
# #             print(f"Speaker: {session['speaker']}")
# #             print(f"Time: {session['time']}")
# #             print(f"Track: {session['track']}")
# #             print("-" * 50)
        
# #         # Save to JSON
# #         scraper.save_to_json(sessions)
# #         print(f"\nFull schedule has been saved to 'devfest_schedule.json'")
# #     else:
# #         print("No sessions were found. Please check the HTML structure.")



# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# import pytz
# from typing import List, Dict, Optional
# import logging
# import json

# class DevFestSession:
#     def __init__(self, title: str, speaker: str, time: str, track: str, 
#                  description: str, difficulty: str, tags: List[str]):
#         self.title = title
#         self.speaker = speaker
#         self.time = time
#         self.track = track
#         self.description = description
#         self.difficulty = difficulty
#         self.tags = tags

#     def to_dict(self) -> Dict:
#         return {
#             'title': self.title,
#             'speaker': self.speaker,
#             'time': self.time,
#             'track': self.track,
#             'description': self.description,
#             'difficulty': self.difficulty,  # Fixed: was using undefined variable
#             'tags': self.tags
#         }

# class DevFestScraper:
#     def __init__(self, base_url: str = "https://devfestlagos.com"):
#         self.base_url = base_url
#         self.schedule_url = f"{base_url}/schedule"
#         self.logger = self._setup_logger()
#         self.lagos_tz = pytz.timezone('Africa/Lagos')

#     def _setup_logger(self) -> logging.Logger:
#         logger = logging.getLogger('DevFestScraper')
#         logger.setLevel(logging.INFO)
#         handler = logging.StreamHandler()
#         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#         return logger

#     def _make_request(self, url: str) -> Optional[str]:
#         try:
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#             }
#             response = requests.get(url, headers=headers, timeout=10)
#             response.raise_for_status()
#             return response.text
#         except requests.RequestException as e:
#             self.logger.error(f"Error fetching URL {url}: {str(e)}")
#             return None

#     def _parse_session_time(self, time_str: str) -> str:
#         try:
#             parsed_time = datetime.strptime(time_str.strip(), "%I:%M %p")
#             return parsed_time.strftime("%H:%M")
#         except ValueError as e:
#             self.logger.warning(f"Error parsing time {time_str}: {str(e)}")
#             return time_str

#     def _extract_session_data(self, session_element) -> Optional[DevFestSession]:
#         try:
#             # Debug print to see the HTML structure
#             print("Session element HTML:", session_element.prettify())
            
#             # Updated selectors based on actual HTML structure
#             title = session_element.find('h3', class_='text-lg').text.strip() if session_element.find('h3', class_='text-lg') else "N/A"
#             speaker = session_element.find('p', class_='speaker').text.strip() if session_element.find('p', class_='speaker') else "N/A"
#             time_element = session_element.find('span', class_='time')
#             time = self._parse_session_time(time_element.text.strip()) if time_element else "N/A"
#             track = session_element.find('div', class_='track').text.strip() if session_element.find('div', class_='track') else "N/A"
#             description = session_element.find('p', class_='description').text.strip() if session_element.find('p', class_='description') else "N/A"
#             difficulty = session_element.find('span', class_='difficulty').text.strip() if session_element.find('span', class_='difficulty') else "N/A"
            
#             # Find tags container and extract tags
#             tags_container = session_element.find('div', class_='tags')
#             tags = [tag.text.strip() for tag in tags_container.find_all('span')] if tags_container else []

#             return DevFestSession(
#                 title=title,
#                 speaker=speaker,
#                 time=time,
#                 track=track,
#                 description=description,
#                 difficulty=difficulty,
#                 tags=tags
#             )
#         except AttributeError as e:
#             self.logger.error(f"Error extracting session data: {str(e)}")
#             return None

#     def scrape_schedule(self) -> List[Dict]:
#         self.logger.info("Starting schedule scraping")
#         sessions = []
        
#         html_content = self._make_request(self.schedule_url)
#         if not html_content:
#             self.logger.error("Failed to fetch schedule page")
#             return sessions

#         soup = BeautifulSoup(html_content, 'html.parser')
        
#         # Debug print to see the full HTML
#         print("Full HTML content:")
#         print(soup.prettify()[:1000])  # Print first 1000 characters
        
#         # Try different potential selectors for session cards
#         session_elements = (
#             soup.find_all('div', class_='schedule-item') or
#             soup.find_all('div', class_='session') or
#             soup.find_all('div', class_='event-session') or
#             soup.select('.schedule-card, .session-card, .event-card')
#         )
        
#         print(f"Found {len(session_elements)} potential session elements")

#         for element in session_elements:
#             session = self._extract_session_data(element)
#             if session:
#                 sessions.append(session.to_dict())

#         self.logger.info(f"Successfully scraped {len(sessions)} sessions")
#         return sessions

#     def save_to_json(self, sessions: List[Dict], filename: str = "devfest_schedule.json"):
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(sessions, f, ensure_ascii=False, indent=2)
#             self.logger.info(f"Successfully saved schedule to {filename}")
#         except IOError as e:
#             self.logger.error(f"Error saving to JSON: {str(e)}")

# def get_devfest_schedule() -> List[Dict]:
#     scraper = DevFestScraper()
#     return scraper.scrape_schedule()

# if __name__ == "__main__":
#     # Enable more detailed logging
#     logging.basicConfig(level=logging.DEBUG)
    
#     # Create scraper instance
#     scraper = DevFestScraper()
    
#     # Scrape the schedule
#     print("Scraping DevFest Lagos schedule...")
#     print(f"Accessing URL: {scraper.schedule_url}")
    
#     sessions = scraper.scrape_schedule()
    
#     # Display results
#     if sessions:
#         print(f"\nSuccessfully scraped {len(sessions)} sessions!")
#         print("\nSample of scraped data:")
#         for session in sessions[:3]:
#             print(f"\nTitle: {session['title']}")
#             print(f"Speaker: {session['speaker']}")
#             print(f"Time: {session['time']}")
#             print(f"Track: {session['track']}")
#             print("-" * 50)
        
#         # Save to JSON
#         scraper.save_to_json(sessions)
#         print(f"\nFull schedule has been saved to 'devfest_schedule.json'")
#     else:
#         print("No sessions were found. Debugging information:")
#         html_content = scraper._make_request(scraper.schedule_url)
#         if html_content:
#             soup = BeautifulSoup(html_content, 'html.parser')
#             print("\nAvailable classes in HTML:")
#             classes = set()
#             for tag in soup.find_all(class_=True):
#                 classes.update(tag.get('class', []))
#             print("\n".join(sorted(classes)))




import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from typing import List, Dict, Optional
import logging
import json

class DevFestSession:
    def __init__(self, title: str, speaker: str, time: str, track: str, 
                 description: str = "Not provided", difficulty: str = "Not specified", 
                 tags: List[str] = None):
        self.title = title
        self.speaker = speaker
        self.time = time
        self.track = track
        self.description = description
        self.difficulty = difficulty
        self.tags = tags or []

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'speaker': self.speaker,
            'time': self.time,
            'track': self.track,
            'description': self.description,
            'difficulty': self.difficulty,
            'tags': self.tags
        }

class DevFestScraper:
    def __init__(self, base_url: str = "https://devfestlagos.com"):
        self.base_url = base_url
        self.schedule_url = f"{base_url}/schedule"
        self.logger = self._setup_logger()
        self.lagos_tz = pytz.timezone('Africa/Lagos')

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('DevFestScraper')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _make_request(self, url: str) -> Optional[str]:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching URL {url}: {str(e)}")
            return None

    def _parse_session_time(self, time_str: str) -> str:
        try:
            # Extract time range from string like "1:00 PM - 1:45 PM"
            return time_str.strip()
        except ValueError as e:
            self.logger.warning(f"Error parsing time {time_str}: {str(e)}")
            return time_str

    def _extract_session_data(self, event_block) -> Optional[DevFestSession]:
        try:
            # Extract title from the correct class
            title = event_block.find('h3', class_='EventCategory_eventSchedule__event-title__F2air')
            title_text = title.text.strip() if title else event_block.find('h3').text.strip()

            # Extract speaker name
            speaker_element = event_block.find('p', class_='EventCategory_eventSchedule__event-facilitator__nWvuU')
            speaker = speaker_element.text.strip() if speaker_element else "Not specified"

            # Extract time
            time_element = event_block.find('span', class_='text-sm')
            if not time_element:
                time_element = event_block.find('div', class_='EventBlock_time__RQGQz')
            time = time_element.text.strip() if time_element else "Time not specified"

            # Determine track/venue
            track = "General"
            venue_element = event_block.find('div', class_='EventBlock_venue__wjpVu')
            if venue_element:
                track = venue_element.find('span').text.strip().title()
            
            return DevFestSession(
                title=title_text,
                speaker=speaker,
                time=time,
                track=track
            )
        except AttributeError as e:
            self.logger.error(f"Error extracting session data: {str(e)}")
            return None

    def scrape_schedule(self) -> List[Dict]:
        self.logger.info("Starting schedule scraping")
        sessions = []
        
        html_content = self._make_request(self.schedule_url)
        if not html_content:
            self.logger.error("Failed to fetch schedule page")
            return sessions

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get general sessions
        general_events = soup.find_all('div', class_='EventBlock_event__UsJua')
        for event in general_events:
            session = self._extract_session_data(event)
            if session:
                sessions.append(session.to_dict())

        # Get breakout sessions
        breakout_events = soup.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
        for event in breakout_events:
            session = self._extract_session_data(event)
            if session:
                sessions.append(session.to_dict())

        self.logger.info(f"Successfully scraped {len(sessions)} sessions")
        return sessions

    def save_to_json(self, sessions: List[Dict], filename: str = "devfest_schedule.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Successfully saved schedule to {filename}")
        except IOError as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")

if __name__ == "__main__":
    # Enable debug logging
    logging.basicConfig(level=logging.INFO)
    
    # Create scraper instance
    scraper = DevFestScraper()
    
    # Scrape the schedule
    print("Scraping DevFest Lagos schedule...")
    sessions = scraper.scrape_schedule()
    
    # Display results
    if sessions:
        print(f"\nSuccessfully scraped {len(sessions)} sessions!")
        print("\nSample of scraped data:")
        for session in sessions[:5]:  # Show first 5 sessions
            print(f"\nTitle: {session['title']}")
            print(f"Speaker: {session['speaker']}")
            print(f"Time: {session['time']}")
            print(f"Track: {session['track']}")
            print("-" * 50)
        
        # Save to JSON
        scraper.save_to_json(sessions)
        print(f"\nFull schedule has been saved to 'devfest_schedule.json'")
    else:
        print("No sessions were found.")