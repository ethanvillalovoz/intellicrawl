from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os

# Load environment variables from .env file for API keys
load_dotenv()

# Initialize the OpenAI chat model
model = ChatOpenAI(
    model="gpt-4.1-nano",  # Model name
    temperature=0,         # Deterministic output
    openai_api_key=os.getenv("OPENAI_API_KEY")  # API key from environment
)

# Set up server parameters for Firecrawl MCP
server_params = StdioServerParameters(
    command="npx",  # Command to run MCP server
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY"),  # API key from environment
    },
    args=["firecrawl-mcp"]  # Arguments for the command
)

async def main():
    """
    Main asynchronous function to run the agent loop.
    Connects to the MCP server, loads tools, and interacts with the user.
    """
    # Establish stdio client connection to MCP server
    async with stdio_client(server_params) as (read, write):
        # Create a client session for MCP communication
        async with ClientSession(read, write) as session:
            await session.initialize()  # Initialize session

            # Load available MCP tools for the agent
            tools = await load_mcp_tools(session)

            # Create the agent with the model and loaded tools
            agent = create_react_agent(model, tools)

            # Initial system message for context and instructions
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that can scrape websites, crawl pages, "
                        "and extract data using Firecrawl tools. Think step by step and use "
                        "the appropriate tools to help the user."
                    )
                }
            ]

            # Display available tools to the user
            print("Available Tools -", *[tool.name for tool in tools])
            print("-" * 60)

            # Main interaction loop for user input and agent response
            while True:
                user_input = input("\nYou: ")
                if user_input == "quit":
                    print("Goodbye")
                    break

                # Add user message to conversation history (truncate if too long)
                messages.append({"role": "user", "content": user_input[:175000]})

                try:
                    # Get agent response asynchronously using the conversation history
                    agent_response = await agent.ainvoke({"messages": messages})

                    # Extract and print the AI's message from the response
                    ai_message = agent_response["messages"][-1].content
                    print("\nAgent:", ai_message)
                except Exception as e:
                    # Print error if agent invocation fails
                    print("Error:", e)

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())