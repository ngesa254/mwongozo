import asyncio
import logging
from typing import Dict, List
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress
from rich.style import Style
from rich.text import Text
from mwongozo_schedule_tool import MwongozoScheduleTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vertex AI configuration
PROJECT_ID = "angelic-bee-193823"
LOCATION = "us-central1"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

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

class MwongozoTerminal:
    def __init__(self):
        self.console = Console()
        self.schedule_tool = MwongozoScheduleTool()
        
        # Initialize Gemini model with tools
        self.schedule_tools = Tool(
            function_declarations=[
                get_schedule,
                search_sessions,
                get_recommendations,
            ]
        )
        
        # Initialize model
        try:
            self.model = GenerativeModel(
                "gemini-1.5-pro",
                generation_config=GenerationConfig(
                    temperature=0.7,
                    top_k=40,
                    top_p=0.8,
                    max_output_tokens=2048,
                ),
                tools=[self.schedule_tools]
            )
            
            self.chat = self.model.start_chat()
            self.system_prompt = self._load_prompt()
            logger.info("Successfully initialized Gemini model")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise

    def _load_prompt(self) -> str:
        """Load the system prompt from prompt.md"""
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return "You are Mwongozo, the DevFest Lagos conference assistant."

    async def _handle_tool_response(self, function_call) -> str:
        """Handle function calls from the model and format response"""
        try:
            name = function_call.name
            args = function_call.args
            logger.info(f"Handling function call: {name} with args: {args}")

            if name == "get_schedule":
                result = await self.schedule_tool.get_schedule()
                day = args.get("day")
                track = args.get("track")
                
                if day:
                    result = {day.lower().replace(" ", ""): result[day.lower().replace(" ", "")]}
                if track:
                    for day_sessions in result.values():
                        day_sessions[:] = [s for s in day_sessions if track.lower() in s['track'].lower()]
                
                return self._format_schedule_response(result)
            
            elif name == "search_sessions":
                result = await self.schedule_tool.search_sessions(
                    query=args.get("query"),
                    day=args.get("day"),
                    track=args.get("track"),
                    speaker=args.get("speaker")
                )
                return self._format_search_response(result)
            
            elif name == "get_recommendations":
                result = await self.schedule_tool.get_recommendations(
                    interests=args.get("interests", []),
                    expertise_level=args.get("expertise_level", "intermediate"),
                    preferred_formats=args.get("preferred_formats", []),
                    day=args.get("day"),
                    limit=args.get("limit", 5)
                )
                return self._format_recommendations_response(result)
            
            else:
                return "I don't know how to handle that request."

        except Exception as e:
            logger.error(f"Error handling tool response: {e}")
            return "Sorry, I encountered an error processing your request."

    def _format_schedule_response(self, schedule: Dict) -> str:
        """Format schedule data into rich text"""
        output = []
        for day, sessions in schedule.items():
            table = Table(
                title=f"\n{day.upper()} SCHEDULE",
                show_header=True,
                header_style="bold magenta"
            )
            
            table.add_column("Time", style="cyan", width=15)
            table.add_column("Title", style="green", width=40)
            table.add_column("Speaker", style="yellow", width=20)
            table.add_column("Track", style="blue", width=15)
            table.add_column("Room", style="red", width=15)
            
            # Sort sessions by time
            sorted_sessions = sorted(sessions, key=lambda x: x['time'])
            
            for session in sorted_sessions:
                table.add_row(
                    session['time'],
                    Text(session['title'], style=Style(overflow="fold")),
                    session['speaker'],
                    session['track'],
                    session['room']
                )
            
            output.append(table)
        
        return "\n".join(str(table) for table in output)

    def _format_search_response(self, sessions: List[Dict]) -> str:
        """Format search results into rich text"""
        if not sessions:
            return "I couldn't find any sessions matching your criteria."
        
        table = Table(
            title="\nFOUND SESSIONS",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Time", style="cyan", width=15)
        table.add_column("Title", style="green", width=40)
        table.add_column("Speaker", style="yellow", width=20)
        table.add_column("Track", style="blue", width=15)
        
        for session in sessions:
            table.add_row(
                session['time'],
                Text(session['title'], style=Style(overflow="fold")),
                session['speaker'],
                session['track']
            )
        
        return str(table)

    def _format_recommendations_response(self, recommendations: List[Dict]) -> str:
        """Format recommendations into rich text"""
        if not recommendations:
            return "I couldn't find any sessions matching your interests."
        
        output = []
        
        # Main recommendations table
        table = Table(
            title="\nRECOMMENDED SESSIONS",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Time", style="cyan", width=15)
        table.add_column("Title", style="green", width=40)
        table.add_column("Speaker", style="yellow", width=20)
        table.add_column("Relevance", style="blue", width=10)
        table.add_column("Level", style="red", width=12)
        
        for rec in recommendations:
            table.add_row(
                rec.session['time'],
                Text(rec.session['title'], style=Style(overflow="fold")),
                rec.session['speaker'],
                "⭐" * int(rec.relevance_score * 5),
                rec.expertise_level
            )
            
            # Add match reasons
            if rec.match_reasons:
                panel = Panel(
                    "\n".join(f"• {reason}" for reason in rec.match_reasons),
                    title="Why this matches",
                    style="dim"
                )
                output.append(panel)
            
            # Add prerequisites if any
            if rec.prerequisites:
                panel = Panel(
                    "\n".join(f"• {prereq}" for prereq in rec.prerequisites),
                    title="Prerequisites",
                    style="yellow"
                )
                output.append(panel)
        
        output.insert(0, table)
        return "\n".join(str(item) for item in output)

    async def chat_loop(self):
        """Main chat loop for terminal interaction"""
        # Display welcome message
        self.console.print(Panel.fit(
            "[bold green]Welcome to Mwongozo - DevFest Lagos Conference Assistant![/]\n"
            "Ask me about sessions, schedules, or get personalized recommendations.\n"
            "Type 'exit' to end the conversation.",
            title="🎯 Mwongozo"
        ))

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.console.print("\n[bold green]Goodbye! Enjoy DevFest Lagos! 👋[/]")
                    break

                # Show thinking indicator
                with Progress(
                    "⚡ Processing",
                    "⚙️ Analyzing",
                    "🔍 Finding matches",
                    "📝 Formatting response"
                ) as progress:
                    task1 = progress.add_task("Processing", total=100)
                    task2 = progress.add_task("Analyzing", total=100)
                    task3 = progress.add_task("Finding matches", total=100)
                    task4 = progress.add_task("Formatting response", total=100)

                    # Send message to model
                    progress.update(task1, advance=50)
                    response = await self.chat.send_message_async(
                        f"{self.system_prompt}\n\nUser: {user_input}"
                    )
                    progress.update(task1, completed=100)

                    # Handle function calling if present
                    progress.update(task2, advance=50)
                    if hasattr(response.candidates[0].content.parts[0], 'function_call'):
                        function_call = response.candidates[0].content.parts[0].function_call
                        progress.update(task2, completed=100)
                        
                        progress.update(task3, advance=50)
                        formatted_response = await self._handle_tool_response(function_call)
                        progress.update(task3, completed=100)
                    else:
                        progress.update(task2, completed=100)
                        progress.update(task3, completed=100)
                        formatted_response = response.text

                    # Display response
                    progress.update(task4, advance=50)
                    self.console.print("\n[bold green]Mwongozo:", style="bold green")
                    self.console.print(Markdown(formatted_response))
                    progress.update(task4, completed=100)

            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                self.console.print(
                    Panel.fit(
                        "[bold red]Sorry, I encountered an error. Please try your question again.[/]",
                        title="Error"
                    )
                )

async def main():
    try:
        # Create and run terminal
        terminal = MwongozoTerminal()
        await terminal.chat_loop()

    except Exception as e:
        logger.error(f"Application error: {e}")
        Console().print(
            Panel.fit(
                f"[bold red]Failed to start Mwongozo: {str(e)}\n"
                "Please try again or contact support if the issue persists.",
                title="Error"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
