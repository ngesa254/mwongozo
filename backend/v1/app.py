# import asyncio
# import logging
# from typing import Dict, List
# import vertexai
# from vertexai.generative_models import (
#     FunctionDeclaration,
#     GenerationConfig,
#     GenerativeModel,
#     Part,
#     Tool,
# )
# from rich.console import Console
# from rich.markdown import Markdown
# from rich.panel import Panel
# from rich.prompt import Prompt
# from mwongozo_schedule_tool import MwongozoScheduleTool

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Vertex AI configuration
# PROJECT_ID = "angelic-bee-193823"
# LOCATION = "us-central1"

# # Initialize Vertex AI
# vertexai.init(project=PROJECT_ID, location=LOCATION)

# # Define function declarations
# get_schedule = FunctionDeclaration(
#     name="get_schedule",
#     description="Get the complete DevFest Lagos schedule",
#     parameters={
#         "type": "object",
#         "properties": {
#             "day": {
#                 "type": "string",
#                 "enum": ["Day 1", "Day 2"],
#                 "description": "Specific day to get schedule for"
#             }
#         }
#     },
# )

# search_sessions = FunctionDeclaration(
#     name="search_sessions",
#     description="Search for specific sessions in the schedule",
#     parameters={
#         "type": "object",
#         "properties": {
#             "query": {
#                 "type": "string",
#                 "description": "Search query for finding sessions"
#             },
#             "day": {
#                 "type": "string",
#                 "enum": ["Day 1", "Day 2"],
#                 "description": "Specific day to search"
#             },
#             "track": {
#                 "type": "string",
#                 "description": "Specific track to search"
#             },
#             "speaker": {
#                 "type": "string",
#                 "description": "Speaker name to search for"
#             }
#         }
#     },
# )

# get_recommendations = FunctionDeclaration(
#     name="get_recommendations",
#     description="Get personalized session recommendations based on interests",
#     parameters={
#         "type": "object",
#         "properties": {
#             "interests": {
#                 "type": "array",
#                 "items": {"type": "string"},
#                 "description": "List of user interests"
#             },
#             "day": {
#                 "type": "string",
#                 "enum": ["Day 1", "Day 2"],
#                 "description": "Specific day for recommendations"
#             },
#             "limit": {
#                 "type": "integer",
#                 "description": "Maximum number of recommendations",
#                 "default": 5
#             }
#         },
#         "required": ["interests"]
#     },
# )

# class MwongozoTerminal:
#     def __init__(self):
#         self.console = Console()
#         self.schedule_tool = MwongozoScheduleTool()
        
#         # Initialize Gemini model with tools
#         self.schedule_tools = Tool(
#             function_declarations=[
#                 get_schedule,
#                 search_sessions,
#                 get_recommendations,
#             ]
#         )
        
#         # Initialize model
#         try:
#             self.model = GenerativeModel(
#                 "gemini-1.5-pro",
#                 generation_config=GenerationConfig(
#                     temperature=0.7,
#                     top_k=40,
#                     top_p=0.8,
#                     max_output_tokens=2048,
#                 ),
#                 tools=[self.schedule_tools]
#             )
            
#             self.chat = self.model.start_chat()
#             self.system_prompt = self._load_prompt()
#             logger.info("Successfully initialized Gemini model")
#         except Exception as e:
#             logger.error(f"Failed to initialize model: {e}")
#             raise

#     def _load_prompt(self) -> str:
#         """Load the system prompt from prompt.md"""
#         try:
#             with open("prompt.md", "r", encoding="utf-8") as f:
#                 return f.read()
#         except Exception as e:
#             logger.error(f"Error loading prompt: {e}")
#             return "You are Mwongozo, the DevFest Lagos conference assistant."

# #     async def _handle_tool_response(self, function_call: Dict) -> Part:
# #         """Handle function calls from the model"""
# #         try:
# #             name = function_call["name"]
# #             args = function_call.get("args", {})
# #             logger.info(f"Handling function call: {name} with args: {args}")

# #             if name == "get_schedule":
# #                 result = await self.schedule_tool.get_schedule()
# #                 day = args.get("day")
# #                 if day:
# #                     result = {day.lower().replace(" ", ""): result[day.lower().replace(" ", "")]}
            
# #             elif name == "search_sessions":
# #                 result = await self.schedule_tool.search_sessions(
# #                     query=args.get("query"),
# #                     day=args.get("day"),
# #                     track=args.get("track"),
# #                     speaker=args.get("speaker")
# #                 )
            
# #             elif name == "get_recommendations":
# #                 result = await self.schedule_tool.get_recommendations(
# #                     interests=args["interests"],
# #                     day=args.get("day"),
# #                     limit=args.get("limit", 5)
# #                 )
            
# #             else:
# #                 raise ValueError(f"Unknown function: {name}")

# #             return Part.from_function_response(
# #                 name=name,
# #                 response={"content": result}
# #             )

# #         except Exception as e:
# #             logger.error(f"Error handling tool response: {e}")
# #             return None

# #     async def chat_loop(self):
# #         """Main chat loop for terminal interaction"""
# #         # Display welcome message
# #         self.console.print(Panel.fit(
# #             "[bold green]Welcome to Mwongozo - DevFest Lagos Conference Assistant![/]\n"
# #             "Ask me about sessions, schedules, or get personalized recommendations.\n"
# #             "Type 'exit' to end the conversation.",
# #             title="🎯 Mwongozo"
# #         ))

# #         while True:
# #             try:
# #                 # Get user input
# #                 user_input = Prompt.ask("\n[bold blue]You")
                
# #                 if user_input.lower() in ['exit', 'quit', 'bye']:
# #                     self.console.print("\n[bold green]Goodbye! Enjoy DevFest Lagos! 👋[/]")
# #                     break

# #                 # Show thinking indicator
# #                 with self.console.status("[bold yellow]Thinking..."):
# #                     # Send initial message to model
# #                     response = await self.chat.send_message_async(
# #                         f"{self.system_prompt}\n\nUser: {user_input}"
# #                     )

# #                     # Handle function calling if present
# #                     if hasattr(response.candidates[0].content.parts[0], 'function_call'):
# #                         function_call = response.candidates[0].content.parts[0].function_call
# #                         tool_response = await self._handle_tool_response(function_call)
                        
# #                         if tool_response:
# #                             response = await self.chat.send_message_async(tool_response)

# #                     # Format and display response
# #                     formatted_response = response.text.replace('```', '').strip()
# #                     self.console.print("\n[bold green]Mwongozo:", style="bold green")
# #                     self.console.print(Markdown(formatted_response))

# #             except Exception as e:
# #                 logger.error(f"Error in chat loop: {e}")
# #                 self.console.print(
# #                     Panel.fit(
# #                         f"[bold red]Sorry, I encountered an error: {str(e)}\n"
# #                         "Please try your question again or rephrase it.",
# #                         title="Error"
# #                     )
# #                 )
                

# async def _handle_tool_response(self, function_call) -> str:
#     """Handle function calls from the model and return formatted response"""
#     try:
#         name = function_call.name
#         args = function_call.args

#         if name == "get_schedule":
#             result = await self.schedule_tool.get_schedule()
#             return self._format_schedule_response(result)
        
#         elif name == "search_sessions":
#             result = await self.schedule_tool.search_sessions(
#                 query=args.get("query"),
#                 day=args.get("day"),
#                 track=args.get("track"),
#                 speaker=args.get("speaker")
#             )
#             return self._format_search_response(result)
        
#         elif name == "get_recommendations":
#             result = await self.schedule_tool.get_recommendations(
#                 interests=args.get("interests", []),
#                 day=args.get("day"),
#                 limit=args.get("limit", 5)
#             )
#             return self._format_recommendations_response(result)
        
#         else:
#             return "I don't know how to handle that request."

#     except Exception as e:
#         logger.error(f"Error handling tool response: {e}")
#         return "Sorry, I encountered an error processing your request."

# def _format_schedule_response(self, schedule: Dict) -> str:
#     """Format schedule data into readable text"""
#     output = []
#     for day, sessions in schedule.items():
#         output.append(f"\n## {day.upper()}")
#         for session in sessions:
#             output.append(
#                 f"\n* {session['time']} - {session['title']}\n"
#                 f"  Speaker: {session['speaker']}\n"
#                 f"  Room: {session['room']}\n"
#                 f"  Track: {session['track']}"
#             )
#     return "\n".join(output)

# def _format_search_response(self, sessions: List[Dict]) -> str:
#     """Format search results into readable text"""
#     if not sessions:
#         return "I couldn't find any sessions matching your criteria."
    
#     output = ["\n### Found Sessions:"]
#     for session in sessions:
#         output.append(
#             f"\n* {session['time']} - {session['title']}\n"
#             f"  Speaker: {session['speaker']}\n"
#             f"  Room: {session['room']}\n"
#             f"  Track: {session['track']}"
#         )
#     return "\n".join(output)

# def _format_recommendations_response(self, sessions: List[Dict]) -> str:
#     """Format recommendations into readable text"""
#     if not sessions:
#         return "I couldn't find any sessions matching your interests."
    
#     output = ["\n### Recommended Sessions:"]
#     for session in sessions:
#         relevance = session.get('relevance_score', 0)
#         output.append(
#             f"\n* {session['time']} - {session['title']}\n"
#             f"  Speaker: {session['speaker']}\n"
#             f"  Room: {session['room']}\n"
#             f"  Track: {session['track']}\n"
#             f"  Relevance: {'⭐' * int(relevance * 5)}"
#         )
#     return "\n".join(output)

# async def chat_loop(self):
#     """Main chat loop for terminal interaction"""
#     # Display welcome message
#     self.console.print(Panel.fit(
#         "[bold green]Welcome to Mwongozo - DevFest Lagos Conference Assistant![/]\n"
#         "Ask me about sessions, schedules, or get personalized recommendations.\n"
#         "Type 'exit' to end the conversation.",
#         title="🎯 Mwongozo"
#     ))

#     while True:
#         try:
#             # Get user input
#             user_input = Prompt.ask("\n[bold blue]You")
            
#             if user_input.lower() in ['exit', 'quit', 'bye']:
#                 self.console.print("\n[bold green]Goodbye! Enjoy DevFest Lagos! 👋[/]")
#                 break

#             # Show thinking indicator
#             with self.console.status("[bold yellow]Thinking..."):
#                 response = await self.chat.send_message_async(user_input)
                
#                 if hasattr(response.candidates[0].content.parts[0], 'function_call'):
#                     # Handle function call and get formatted response
#                     function_call = response.candidates[0].content.parts[0].function_call
#                     formatted_response = await self._handle_tool_response(function_call)
#                 else:
#                     formatted_response = response.text

#                 # Display response
#                 self.console.print("\n[bold green]Mwongozo:", style="bold green")
#                 self.console.print(Markdown(formatted_response))

#         except Exception as e:
#             logger.error(f"Error in chat loop: {e}")
#             self.console.print(
#                 Panel.fit(
#                     "[bold red]Sorry, I encountered an error. Please try your question again.[/]",
#                     title="Error"
#                 )
#             )


# async def main():
#     try:
#         # Create and run terminal
#         terminal = MwongozoTerminal()
#         await terminal.chat_loop()

#     except Exception as e:
#         logger.error(f"Application error: {e}")
#         Console().print(
#             Panel.fit(
#                 f"[bold red]Failed to start Mwongozo: {str(e)}\n"
#                 "Please try again or contact support if the issue persists.",
#                 title="Error"
#             )
#         )

# if __name__ == "__main__":
#     asyncio.run(main())




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
    description="Get the complete DevFest Lagos schedule",
    parameters={
        "type": "object",
        "properties": {
            "day": {
                "type": "string",
                "enum": ["Day 1", "Day 2"],
                "description": "Specific day to get schedule for"
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
    description="Get personalized session recommendations based on interests",
    parameters={
        "type": "object",
        "properties": {
            "interests": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of user interests"
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
        """Handle function calls from the model and return formatted response"""
        try:
            name = function_call.name
            args = function_call.args
            logger.info(f"Handling function call: {name} with args: {args}")

            if name == "get_schedule":
                result = await self.schedule_tool.get_schedule()
                day = args.get("day")
                if day:
                    result = {day.lower().replace(" ", ""): result[day.lower().replace(" ", "")]}
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
        """Format schedule data into readable text"""
        output = []
        for day, sessions in schedule.items():
            output.append(f"\n## {day.upper()}")
            for session in sessions:
                output.append(
                    f"\n* {session['time']} - {session['title']}\n"
                    f"  Speaker: {session['speaker']}\n"
                    f"  Room: {session['room']}\n"
                    f"  Track: {session['track']}"
                )
        return "\n".join(output)

    def _format_search_response(self, sessions: List[Dict]) -> str:
        """Format search results into readable text"""
        if not sessions:
            return "I couldn't find any sessions matching your criteria."
        
        output = ["\n### Found Sessions:"]
        for session in sessions:
            output.append(
                f"\n* {session['time']} - {session['title']}\n"
                f"  Speaker: {session['speaker']}\n"
                f"  Room: {session['room']}\n"
                f"  Track: {session['track']}"
            )
        return "\n".join(output)

    def _format_recommendations_response(self, sessions: List[Dict]) -> str:
        """Format recommendations into readable text"""
        if not sessions:
            return "I couldn't find any sessions matching your interests."
        
        output = ["\n### Recommended Sessions:"]
        for session in sessions:
            relevance = session.get('relevance_score', 0)
            output.append(
                f"\n* {session['time']} - {session['title']}\n"
                f"  Speaker: {session['speaker']}\n"
                f"  Room: {session['room']}\n"
                f"  Track: {session['track']}\n"
                f"  Relevance: {'⭐' * int(relevance * 5)}"
            )
        return "\n".join(output)

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
                with self.console.status("[bold yellow]Thinking..."):
                    # Send message to model
                    response = await self.chat.send_message_async(
                        f"{self.system_prompt}\n\nUser: {user_input}"
                    )

                    # Handle function calling if present
                    if hasattr(response.candidates[0].content.parts[0], 'function_call'):
                        function_call = response.candidates[0].content.parts[0].function_call
                        formatted_response = await self._handle_tool_response(function_call)
                    else:
                        formatted_response = response.text

                    # Display response
                    self.console.print("\n[bold green]Mwongozo:", style="bold green")
                    self.console.print(Markdown(formatted_response))

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

