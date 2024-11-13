import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Tool,
)
from utils import (
    MwongozoTerminal, 
    SessionAnalyzer,
    format_response,
    setup_logging
)

# Configure logging
logger = setup_logging()

# Vertex AI configuration
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"

# Define function declarations
get_schedule = FunctionDeclaration(
    name="get_schedule",
    description="Get the complete DevFest Lagos schedule with filtering options",
    parameters={
        "type": "object",
        "properties": {
            "day": {
                "type": "string",
                "enum": ["Day 1", "Day 2"],
                "description": "Specific day to get schedule for"
            },
            "track": {
                "type": "string",
                "description": "Specific track to filter by"
            }
        }
    },
)

search_sessions = FunctionDeclaration(
    name="search_sessions",
    description="Search for specific sessions in the schedule",
    parameters={
        "type": "object",
        "properties": {
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
            }
        }
    },
)

get_recommendations = FunctionDeclaration(
    name="get_recommendations",
    description="Get personalized session recommendations based on interests and preferences",
    parameters={
        "type": "object",
        "properties": {
            "interests": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of user interests and technologies"
            },
            "expertise_level": {
                "type": "string",
                "enum": ["beginner", "intermediate", "advanced"],
                "description": "User's expertise level"
            },
            "preferred_formats": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Preferred session formats (workshop, talk, panel, keynote)"
            },
            "day": {
                "type": "string",
                "enum": ["Day 1", "Day 2"],
                "description": "Specific day for recommendations"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of recommendations",
                "default": 5
            }
        },
        "required": ["interests"]
    },
)

class MwongozoApp:
    def __init__(self):
        self.terminal = MwongozoTerminal()
        self.session_analyzer = SessionAnalyzer()
        
        # Initialize Vertex AI
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.model = self._initialize_model()
            self.chat = self.model.start_chat()
            self.system_prompt = self._load_prompt()
            logger.info("Successfully initialized Mwongozo")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    def _initialize_model(self) -> GenerativeModel:
        """Initialize the Gemini model"""
        try:
            return GenerativeModel(
                "gemini-1.5-pro",
                generation_config=GenerationConfig(
                    temperature=0.7,
                    top_k=40,
                    top_p=0.8,
                    max_output_tokens=2048,
                ),
                tools=[Tool(
                    function_declarations=[
                        get_schedule,
                        search_sessions,
                        get_recommendations
                    ]
                )]
            )
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise

    def _load_prompt(self) -> str:
        """Load the system prompt"""
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return "You are Mwongozo, the DevFest Lagos conference assistant."

    async def _handle_function_call(self, function_call) -> str:
        """Handle function calls from the model"""
        name = function_call.name
        args = function_call.args
        logger.info(f"Handling function: {name} with args: {args}")

        try:
            if name == "get_schedule":
                result = await self.session_analyzer.get_schedule(
                    day=args.get("day"),
                    track=args.get("track")
                )
                return format_response("schedule", result)

            elif name == "search_sessions":
                result = await self.session_analyzer.search_sessions(
                    query=args.get("query"),
                    day=args.get("day"),
                    track=args.get("track"),
                    speaker=args.get("speaker")
                )
                return format_response("search", result)

            elif name == "get_recommendations":
                result = await self.session_analyzer.get_recommendations(
                    interests=args.get("interests", []),
                    expertise_level=args.get("expertise_level", "intermediate"),
                    preferred_formats=args.get("preferred_formats", []),
                    day=args.get("day"),
                    limit=args.get("limit", 5)
                )
                return format_response("recommendations", result)

            return "I don't know how to handle that request."

        except Exception as e:
            logger.error(f"Error in function call: {e}")
            return "Sorry, I encountered an error processing your request."

    async def start(self):
        """Start the Mwongozo application"""
        self.terminal.display_welcome()

        while True:
            try:
                user_input = self.terminal.get_input()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.terminal.display_goodbye()
                    break

                # Process request with progress indicator
                with self.terminal.progress_indicator() as progress:
                    # Send message to model
                    progress.update(description="Processing...")
                    response = await self.chat.send_message_async(
                        f"{self.system_prompt}\n\nUser: {user_input}"
                    )
                    
                    # Handle function calling if present
                    if hasattr(response.candidates[0].content.parts[0], 'function_call'):
                        progress.update(description="Analyzing...")
                        function_call = response.candidates[0].content.parts[0].function_call
                        formatted_response = await self._handle_function_call(function_call)
                    else:
                        formatted_response = response.text

                    # Display response
                    progress.update(description="Formatting...")
                    self.terminal.display_response(formatted_response)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.terminal.display_error(str(e))

async def main():
    try:
        app = MwongozoApp()
        await app.start()
    except Exception as e:
        logger.error(f"Application error: {e}")
        MwongozoTerminal().display_error(
            "Failed to start Mwongozo. Please try again or contact support."
        )

if __name__ == "__main__":
    asyncio.run(main())
