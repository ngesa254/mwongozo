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




# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# import pytz
# from typing import List, Dict, Optional
# import logging
# import json

# class DevFestSession:
#     def __init__(self, title: str, speaker: str, time: str, track: str, 
#                  description: str = "Not provided", difficulty: str = "Not specified", 
#                  tags: List[str] = None):
#         self.title = title
#         self.speaker = speaker
#         self.time = time
#         self.track = track
#         self.description = description
#         self.difficulty = difficulty
#         self.tags = tags or []

#     def to_dict(self) -> Dict:
#         return {
#             'title': self.title,
#             'speaker': self.speaker,
#             'time': self.time,
#             'track': self.track,
#             'description': self.description,
#             'difficulty': self.difficulty,
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
#             # Extract time range from string like "1:00 PM - 1:45 PM"
#             return time_str.strip()
#         except ValueError as e:
#             self.logger.warning(f"Error parsing time {time_str}: {str(e)}")
#             return time_str

#     def _extract_session_data(self, event_block) -> Optional[DevFestSession]:
#         try:
#             # Extract title from the correct class
#             title = event_block.find('h3', class_='EventCategory_eventSchedule__event-title__F2air')
#             title_text = title.text.strip() if title else event_block.find('h3').text.strip()

#             # Extract speaker name
#             speaker_element = event_block.find('p', class_='EventCategory_eventSchedule__event-facilitator__nWvuU')
#             speaker = speaker_element.text.strip() if speaker_element else "Not specified"

#             # Extract time
#             time_element = event_block.find('span', class_='text-sm')
#             if not time_element:
#                 time_element = event_block.find('div', class_='EventBlock_time__RQGQz')
#             time = time_element.text.strip() if time_element else "Time not specified"

#             # Determine track/venue
#             track = "General"
#             venue_element = event_block.find('div', class_='EventBlock_venue__wjpVu')
#             if venue_element:
#                 track = venue_element.find('span').text.strip().title()
            
#             return DevFestSession(
#                 title=title_text,
#                 speaker=speaker,
#                 time=time,
#                 track=track
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
        
#         # Get general sessions
#         general_events = soup.find_all('div', class_='EventBlock_event__UsJua')
#         for event in general_events:
#             session = self._extract_session_data(event)
#             if session:
#                 sessions.append(session.to_dict())

#         # Get breakout sessions
#         breakout_events = soup.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
#         for event in breakout_events:
#             session = self._extract_session_data(event)
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

# if __name__ == "__main__":
#     # Enable debug logging
#     logging.basicConfig(level=logging.INFO)
    
#     # Create scraper instance
#     scraper = DevFestScraper()
    
#     # Scrape the schedule
#     print("Scraping DevFest Lagos schedule...")
#     sessions = scraper.scrape_schedule()
    
#     # Display results
#     if sessions:
#         print(f"\nSuccessfully scraped {len(sessions)} sessions!")
#         print("\nSample of scraped data:")
#         for session in sessions[:5]:  # Show first 5 sessions
#             print(f"\nTitle: {session['title']}")
#             print(f"Speaker: {session['speaker']}")
#             print(f"Time: {session['time']}")
#             print(f"Track: {session['track']}")
#             print("-" * 50)
        
#         # Save to JSON
#         scraper.save_to_json(sessions)
#         print(f"\nFull schedule has been saved to 'devfest_schedule.json'")
#     else:
#         print("No sessions were found.")





# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# import pytz
# from typing import List, Dict, Optional
# import logging
# import json

# class DevFestSession:
#     def __init__(self, title: str, speaker: str, time: str, track: str, 
#                  day: str, description: str = "Not provided", 
#                  difficulty: str = "Not specified", tags: List[str] = None):
#         self.title = title
#         self.speaker = speaker
#         self.time = time
#         self.track = track
#         self.day = day
#         self.description = description
#         self.difficulty = difficulty
#         self.tags = tags or []

#     def to_dict(self) -> Dict:
#         return {
#             'title': self.title,
#             'speaker': self.speaker,
#             'time': self.time,
#             'track': self.track,
#             'day': self.day,
#             'description': self.description,
#             'difficulty': self.difficulty,
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
#             return time_str.strip()
#         except ValueError as e:
#             self.logger.warning(f"Error parsing time {time_str}: {str(e)}")
#             return time_str

#     def _extract_session_data(self, event_block, day: str) -> Optional[DevFestSession]:
#         try:
#             # Extract title
#             title = event_block.find('h3', class_='EventCategory_eventSchedule__event-title__F2air')
#             title_text = title.text.strip() if title else event_block.find('h3').text.strip()

#             # Extract speaker name
#             speaker_element = event_block.find('p', class_='EventCategory_eventSchedule__event-facilitator__nWvuU')
#             speaker = speaker_element.text.strip() if speaker_element else "Not specified"

#             # Extract time
#             time_element = event_block.find('span', class_='text-sm')
#             if not time_element:
#                 time_element = event_block.find('div', class_='EventBlock_time__RQGQz')
#             time = time_element.text.strip() if time_element else "Time not specified"

#             # Determine track/venue
#             track = "General"
#             venue_element = event_block.find('div', class_='EventBlock_venue__wjpVu')
#             if venue_element:
#                 track = venue_element.find('span').text.strip().title()
            
#             return DevFestSession(
#                 title=title_text,
#                 speaker=speaker,
#                 time=time,
#                 track=track,
#                 day=day
#             )
#         except AttributeError as e:
#             self.logger.error(f"Error extracting session data: {str(e)}")
#             return None

#     def _scrape_day_schedule(self, soup: BeautifulSoup, day: str) -> List[Dict]:
#         sessions = []
        
#         # Get general sessions
#         general_events = soup.find_all('div', class_='EventBlock_event__UsJua')
#         for event in general_events:
#             session = self._extract_session_data(event, day)
#             if session:
#                 sessions.append(session.to_dict())

#         # Get breakout sessions
#         breakout_events = soup.find_all('div', class_='EventCategory_eventSchedule__event__AhbY3')
#         for event in breakout_events:
#             session = self._extract_session_data(event, day)
#             if session:
#                 sessions.append(session.to_dict())

#         return sessions

#     def scrape_schedule(self) -> Dict[str, List[Dict]]:
#         """
#         Scrape schedule for both days
#         Returns:
#             Dict with 'day1' and 'day2' keys containing lists of session dictionaries
#         """
#         self.logger.info("Starting schedule scraping for both days")
#         schedule = {
#             'day1': [],
#             'day2': []
#         }
        
#         html_content = self._make_request(self.schedule_url)
#         if not html_content:
#             self.logger.error("Failed to fetch schedule page")
#             return schedule

#         soup = BeautifulSoup(html_content, 'html.parser')
        
#         try:
#             # Find day tabs/buttons
#             day_buttons = soup.find_all('button', class_='Button_button__uaOkJ Button_default__fQPmh  schedule_ctaButton__0a9VM')
            
#             if day_buttons:
#                 self.logger.info(f"Found {len(day_buttons)} day buttons")
                
#                 # The site likely uses JavaScript to switch content, but the HTML for both days
#                 # might be present in the initial load
#                 day1_content = soup.find('div', class_='schedule_scheduleItemsContainer__wkWNt')
#                 if day1_content:
#                     self.logger.info("Scraping Day 1 schedule")
#                     schedule['day1'] = self._scrape_day_schedule(day1_content, "Day 1 - Friday")
                
#                 # Try to find Day 2 content
#                 # Note: This might require JavaScript interaction in a real browser
#                 day2_content = soup.find_all('div', class_='schedule_scheduleItemsContainer__wkWNt')
#                 if len(day2_content) > 1:
#                     self.logger.info("Scraping Day 2 schedule")
#                     schedule['day2'] = self._scrape_day_schedule(day2_content[1], "Day 2 - Saturday")
            
#         except Exception as e:
#             self.logger.error(f"Error during schedule scraping: {str(e)}")

#         self.logger.info(f"Successfully scraped {len(schedule['day1'])} sessions for Day 1")
#         self.logger.info(f"Successfully scraped {len(schedule['day2'])} sessions for Day 2")
#         return schedule

#     def save_to_json(self, schedule: Dict[str, List[Dict]], filename: str = "devfest_schedule.json"):
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(schedule, f, ensure_ascii=False, indent=2)
#             self.logger.info(f"Successfully saved schedule to {filename}")
#         except IOError as e:
#             self.logger.error(f"Error saving to JSON: {str(e)}")

# if __name__ == "__main__":
#     # Enable debug logging
#     logging.basicConfig(level=logging.INFO)
    
#     # Create scraper instance
#     scraper = DevFestScraper()
    
#     # Scrape the schedule
#     print("Scraping DevFest Lagos schedule for both days...")
#     schedule = scraper.scrape_schedule()
    
#     # Display results
#     for day, sessions in schedule.items():
#         if sessions:
#             print(f"\n{day.upper()}: {len(sessions)} sessions")
#             print("\nSample of scraped data:")
#             for session in sessions[:3]:  # Show first 3 sessions for each day
#                 print(f"\nTitle: {session['title']}")
#                 print(f"Speaker: {session['speaker']}")
#                 print(f"Time: {session['time']}")
#                 print(f"Track: {session['track']}")
#                 print(f"Day: {session['day']}")
#                 print("-" * 50)
    
#     # Save to JSON
#     scraper.save_to_json(schedule)
#     print(f"\nFull schedule has been saved to 'devfest_schedule.json'")



# NOT W.
# import logging
# from typing import List, Dict, Optional, Tuple
# from datetime import datetime
# import json
# import time
# from dataclasses import dataclass, asdict
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# import pytz
# from bs4 import BeautifulSoup
# from rich.console import Console
# from rich.table import Table
# from rich.progress import Progress, SpinnerColumn, TextColumn

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
#     difficulty: str = "Not specified"
#     tags: List[str] = None

#     def __post_init__(self):
#         self.tags = self.tags or []

#     def to_dict(self) -> Dict:
#         return asdict(self)

# class DevFestScraper:
#     def __init__(self, headless: bool = True):
#         self.logger = self._setup_logger()
#         self.console = Console()
#         self.base_url = "https://devfestlagos.com"
#         self.schedule_url = f"{self.base_url}/schedule"
#         self.headless = headless
#         self.driver = None
#         self.wait = None
#         self.lagos_tz = pytz.timezone('Africa/Lagos')

#     def _setup_logger(self) -> logging.Logger:
#         """Setup detailed logging configuration"""
#         logger = logging.getLogger('DevFestScraper')
#         logger.setLevel(logging.INFO)
#         handler = logging.StreamHandler()
#         formatter = logging.Formatter(
#             '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#         )
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#         return logger

#     def _setup_webdriver(self):
#         """Setup Chrome WebDriver with optimized settings"""
#         chrome_options = Options()
#         if self.headless:
#             chrome_options.add_argument("--headless")
        
#         # Add performance optimizing arguments
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-notifications")
#         chrome_options.add_argument("--disable-infobars")
#         chrome_options.add_argument("--disable-automation")
#         chrome_options.add_argument("--disable-browser-side-navigation")
#         chrome_options.add_argument("--disable-web-security")
#         chrome_options.add_argument("--dns-prefetch-disable")
#         chrome_options.add_argument("--disable-popup-blocking")
        
#         service = Service(ChromeDriverManager().install())
#         self.driver = webdriver.Chrome(service=service, options=chrome_options)
#         self.wait = WebDriverWait(self.driver, 10)
#         self.driver.set_window_size(1920, 1080)

#     def _extract_session_data(self, event_element, day: str, session_type: str) -> Optional[DevFestSession]:
#         """Extract session data from event element with enhanced error handling"""
#         try:
#             # Extract title with fallback options
#             title_element = (
#                 event_element.find_element(By.CSS_SELECTOR, '.EventCategory_eventSchedule__event-title__F2air') or
#                 event_element.find_element(By.TAG_NAME, 'h3')
#             )
#             title = title_element.text.strip()

#             # Extract speaker with multiple selector attempts
#             try:
#                 speaker = event_element.find_element(
#                     By.CSS_SELECTOR, 
#                     '.EventCategory_eventSchedule__event-facilitator__nWvuU'
#                 ).text.strip()
#             except NoSuchElementException:
#                 speaker = "Not specified"

#             # Extract time with fallback
#             try:
#                 time_element = (
#                     event_element.find_element(By.CSS_SELECTOR, '.text-sm') or
#                     event_element.find_element(By.CSS_SELECTOR, '.EventBlock_time__RQGQz')
#                 )
#                 time_str = time_element.text.strip()
#             except NoSuchElementException:
#                 time_str = "Time not specified"

#             # Extract track/room information
#             track = "General"
#             room = "Main Hall"
#             try:
#                 venue_element = event_element.find_element(
#                     By.CSS_SELECTOR, 
#                     '.EventBlock_venue__wjpVu'
#                 )
#                 if venue_element:
#                     venue_text = venue_element.find_element(By.TAG_NAME, 'span').text.strip()
#                     track = venue_text.title()
#                     room = f"Room {venue_text.split()[-1]}" if 'room' in venue_text.lower() else venue_text.title()
#             except NoSuchElementException:
#                 pass

#             return DevFestSession(
#                 title=title,
#                 speaker=speaker,
#                 time=time_str,
#                 track=track,
#                 day=day,
#                 room=room,
#                 session_type=session_type
#             )

#         except Exception as e:
#             self.logger.error(f"Error extracting session data: {str(e)}")
#             return None

#     def _scrape_day_schedule(self, day_button, day_name: str) -> List[Dict]:
#         """Scrape schedule for a specific day"""
#         sessions = []
        
#         try:
#             # Click day button and wait for content to load
#             day_button.click()
#             time.sleep(2)  # Allow time for JavaScript transitions
            
#             # Wait for schedule container to be present
#             schedule_container = self.wait.until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "schedule_scheduleItemsContainer__wkWNt"))
#             )

#             # Get general sessions
#             general_events = self.driver.find_elements(
#                 By.CSS_SELECTOR, 
#                 ".EventBlock_event__UsJua"
#             )
#             for event in general_events:
#                 session = self._extract_session_data(event, day_name, "General")
#                 if session:
#                     sessions.append(session.to_dict())

#             # Get breakout sessions
#             breakout_events = self.driver.find_elements(
#                 By.CSS_SELECTOR, 
#                 ".EventCategory_eventSchedule__event__AhbY3"
#             )
#             for event in breakout_events:
#                 session = self._extract_session_data(event, day_name, "Breakout")
#                 if session:
#                     sessions.append(session.to_dict())

#         except Exception as e:
#             self.logger.error(f"Error scraping {day_name} schedule: {str(e)}")

#         return sessions

#     def scrape_schedule(self) -> Dict[str, List[Dict]]:
#         """Main method to scrape schedule for both days"""
#         schedule = {
#             'day1': [],
#             'day2': []
#         }
        
#         try:
#             with Progress(
#                 SpinnerColumn(),
#                 TextColumn("[progress.description]{task.description}"),
#                 console=self.console
#             ) as progress:
#                 # Setup WebDriver
#                 progress.add_task("Setting up WebDriver...", total=None)
#                 self._setup_webdriver()

#                 # Load schedule page
#                 progress.add_task("Loading schedule page...", total=None)
#                 self.driver.get(self.schedule_url)

#                 # Wait for day buttons to be present
#                 progress.add_task("Locating day buttons...", total=None)
#                 day_buttons = self.wait.until(
#                     EC.presence_of_all_elements_located(
#                         (By.CSS_SELECTOR, ".schedule_ctaButton__0a9VM")
#                     )
#                 )

#                 if len(day_buttons) >= 2:
#                     # Scrape Day 1
#                     progress.add_task("Scraping Day 1 schedule...", total=None)
#                     schedule['day1'] = self._scrape_day_schedule(
#                         day_buttons[0], 
#                         "Day 1 - Friday"
#                     )

#                     # Scrape Day 2
#                     progress.add_task("Scraping Day 2 schedule...", total=None)
#                     schedule['day2'] = self._scrape_day_schedule(
#                         day_buttons[1], 
#                         "Day 2 - Saturday"
#                     )

#         except Exception as e:
#             self.logger.error(f"Error during schedule scraping: {str(e)}")
        
#         finally:
#             if self.driver:
#                 self.driver.quit()

#         return schedule

#     def save_to_json(self, schedule: Dict[str, List[Dict]], filename: str = "devfest_schedule.json"):
#         """Save schedule to JSON with pretty printing"""
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(schedule, f, ensure_ascii=False, indent=2)
#             self.logger.info(f"Successfully saved schedule to {filename}")
#         except IOError as e:
#             self.logger.error(f"Error saving to JSON: {str(e)}")

#     def display_schedule(self, schedule: Dict[str, List[Dict]]):
#         """Display schedule in a formatted table"""
#         for day, sessions in schedule.items():
#             table = Table(title=f"\n{day.upper()} Schedule")
#             table.add_column("Time", style="cyan")
#             table.add_column("Title", style="magenta")
#             table.add_column("Speaker", style="green")
#             table.add_column("Room", style="yellow")
#             table.add_column("Type", style="blue")

#             for session in sorted(sessions, key=lambda x: x['time']):
#                 table.add_row(
#                     session['time'],
#                     session['title'],
#                     session['speaker'],
#                     session['room'],
#                     session['session_type']
#                 )

#             self.console.print(table)

# def main():
#     # Set up console for rich output
#     console = Console()
    
#     try:
#         with console.status("[bold green]Initializing scraper...") as status:
#             scraper = DevFestScraper(headless=True)
            
#             status.update("[bold green]Scraping schedule...")
#             schedule = scraper.scrape_schedule()
            
#             status.update("[bold green]Saving to JSON...")
#             scraper.save_to_json(schedule)
            
#             status.update("[bold green]Displaying results...")
#             scraper.display_schedule(schedule)
            
#             # Print summary
#             total_sessions = len(schedule['day1']) + len(schedule['day2'])
#             console.print(f"\n[bold green]Successfully scraped {total_sessions} sessions!")
#             console.print(f"Day 1: {len(schedule['day1'])} sessions")
#             console.print(f"Day 2: {len(schedule['day2'])} sessions")
#             console.print("\nFull schedule has been saved to 'devfest_schedule.json'")

#     except Exception as e:
#         console.print(f"[bold red]Error: {str(e)}")

# if __name__ == "__main__":
#     main()


# W

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import time
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pytz
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

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
    difficulty: str = "Not specified"
    tags: List[str] = None

    def __post_init__(self):
        self.tags = self.tags or []

    def to_dict(self) -> Dict:
        return asdict(self)

class DevFestScraper:
    def __init__(self, headless: bool = True):
        self.logger = self._setup_logger()
        self.console = Console()
        self.base_url = "https://devfestlagos.com"
        self.schedule_url = f"{self.base_url}/schedule"
        self.headless = headless
        self.driver = None
        self.wait = None
        self.lagos_tz = pytz.timezone('Africa/Lagos')

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

    def _setup_webdriver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def _wait_for_element(self, by, value, timeout=10):
        """Wait for element with better error handling"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.error(f"Timeout waiting for element: {value}")
            return None

    def _wait_for_elements(self, by, value, timeout=10):
        """Wait for multiple elements with better error handling"""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            self.logger.error(f"Timeout waiting for elements: {value}")
            return []

    def _extract_general_session(self, event_element, day: str) -> Optional[DevFestSession]:
        """Extract data from general session element"""
        try:
            # Get title from h3
            title = event_element.find_element(By.TAG_NAME, 'h3').text.strip()
            
            # Get time
            time_element = event_element.find_element(By.CLASS_NAME, 'EventBlock_time__RQGQz')
            time_str = time_element.text.strip()
            
            # Get venue/room
            try:
                venue_element = event_element.find_element(By.CLASS_NAME, 'EventBlock_venue__wjpVu')
                venue_span = venue_element.find_element(By.TAG_NAME, 'span')
                room = venue_span.text.strip().title()
            except NoSuchElementException:
                room = "Main Hall"

            return DevFestSession(
                title=title,
                speaker="N/A",  # General sessions usually don't have speakers
                time=time_str,
                track="General",
                day=day,
                room=room,
                session_type="General"
            )
        except Exception as e:
            self.logger.error(f"Error extracting general session: {str(e)}")
            return None

    def _extract_breakout_session(self, event_element, day: str, room: str) -> Optional[DevFestSession]:
        """Extract data from breakout session element"""
        try:
            # Get title
            title = event_element.find_element(
                By.CLASS_NAME, 'EventCategory_eventSchedule__event-title__F2air'
            ).text.strip()
            
            # Get speaker
            speaker = event_element.find_element(
                By.CLASS_NAME, 'EventCategory_eventSchedule__event-facilitator__nWvuU'
            ).text.strip()
            
            # Get time
            time_str = event_element.find_element(
                By.CLASS_NAME, 'EventCategory_eventSchedule__event-time__f_zfq'
            ).find_element(By.TAG_NAME, 'span').text.strip()

            return DevFestSession(
                title=title,
                speaker=speaker,
                time=time_str,
                track="Breakout",
                day=day,
                room=room,
                session_type="Breakout"
            )
        except Exception as e:
            self.logger.error(f"Error extracting breakout session: {str(e)}")
            return None

    def _scrape_day_schedule(self, day_button, day_name: str) -> List[Dict]:
        """Scrape schedule for a specific day"""
        sessions = []
        
        try:
            # Click day button and wait for content to load
            self.driver.execute_script("arguments[0].click();", day_button)
            time.sleep(2)  # Wait for content to update
            
            # Get general sessions
            general_containers = self._wait_for_elements(
                By.CLASS_NAME, "EventBlock_event__UsJua"
            )
            
            for container in general_containers:
                session = self._extract_general_session(container, day_name)
                if session:
                    sessions.append(session.to_dict())

            # Get breakout sessions
            # First get the room tabs
            room_tabs = self._wait_for_elements(
                By.CLASS_NAME, "EventCategory_eventSchedule__tab___cJPm"
            )
            
            for room_tab in room_tabs:
                try:
                    room_name = room_tab.text.strip().split('\n')[0]  # Get room name from tab
                    self.driver.execute_script("arguments[0].click();", room_tab)
                    time.sleep(1)  # Wait for room content to load
                    
                    # Get all sessions for this room
                    breakout_events = self._wait_for_elements(
                        By.CLASS_NAME, "EventCategory_eventSchedule__event__AhbY3"
                    )
                    
                    for event in breakout_events:
                        session = self._extract_breakout_session(event, day_name, room_name)
                        if session:
                            sessions.append(session.to_dict())
                            
                except Exception as e:
                    self.logger.error(f"Error processing room tab: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error scraping {day_name} schedule: {str(e)}")

        return sessions

    def scrape_schedule(self) -> Dict[str, List[Dict]]:
        """Main method to scrape schedule for both days"""
        schedule = {
            'day1': [],
            'day2': []
        }
        
        try:
            self._setup_webdriver()
            self.driver.get(self.schedule_url)
            
            # Wait for page to load completely
            self._wait_for_element(By.CLASS_NAME, "schedule_scheduleContainer__HD8bi")
            
            # Get day buttons
            day_buttons = self._wait_for_elements(
                By.CSS_SELECTOR, 
                "button.Button_button__uaOkJ.Button_default__fQPmh.schedule_ctaButton__0a9VM"
            )
            
            if len(day_buttons) >= 2:
                # Scrape Day 1
                self.logger.info("Scraping Day 1 schedule...")
                schedule['day1'] = self._scrape_day_schedule(day_buttons[0], "Day 1 - Friday")
                
                # Scrape Day 2
                self.logger.info("Scraping Day 2 schedule...")
                schedule['day2'] = self._scrape_day_schedule(day_buttons[1], "Day 2 - Saturday")
            else:
                self.logger.error("Could not find day buttons")
                
        except Exception as e:
            self.logger.error(f"Error during schedule scraping: {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()

        return schedule

    def save_to_json(self, schedule: Dict[str, List[Dict]], filename: str = "devfest_schedule.json"):
        """Save schedule to JSON with pretty printing"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Successfully saved schedule to {filename}")
        except IOError as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")

    def display_schedule(self, schedule: Dict[str, List[Dict]]):
        """Display schedule in a formatted table"""
        for day, sessions in schedule.items():
            if sessions:
                table = Table(title=f"\n{day.upper()} Schedule")
                table.add_column("Time", style="cyan")
                table.add_column("Title", style="magenta")
                table.add_column("Speaker", style="green")
                table.add_column("Room", style="yellow")
                table.add_column("Type", style="blue")

                for session in sorted(sessions, key=lambda x: x['time']):
                    table.add_row(
                        session['time'],
                        session['title'][:50] + "..." if len(session['title']) > 50 else session['title'],
                        session['speaker'],
                        session['room'],
                        session['session_type']
                    )

                self.console.print(table)
            else:
                self.console.print(f"[yellow]No sessions found for {day}")

def main():
    console = Console()
    
    try:
        with console.status("[bold green]Initializing scraper...") as status:
            # Create scraper instance
            scraper = DevFestScraper(headless=True)
            
            # Scrape schedule
            status.update("[bold green]Scraping schedule...")
            schedule = scraper.scrape_schedule()
            
            # Save results
            status.update("[bold green]Saving results...")
            scraper.save_to_json(schedule)
            
            # Display results
            scraper.display_schedule(schedule)
            
            # Print summary
            total_sessions = len(schedule['day1']) + len(schedule['day2'])
            console.print(f"\n[bold green]Summary:")
            console.print(f"Total sessions scraped: {total_sessions}")
            console.print(f"Day 1 sessions: {len(schedule['day1'])}")
            console.print(f"Day 2 sessions: {len(schedule['day2'])}")
            console.print("\nFull schedule has been saved to 'devfest_schedule.json'")

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}")

if __name__ == "__main__":
    main()