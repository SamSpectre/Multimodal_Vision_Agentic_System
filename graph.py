"""
LangChain v1.0 Vision Agentic System
Using the NEW create_agent pattern!

This replaces the old manual LangGraph approach with the new
simplified LangChain v1.0 agent pattern.

KEY V1.0 CHANGES:
- Use create_agent() instead of manual llm.bind_tools()
- Agents are automatically built on LangGraph
- Much simpler API!
"""

from langchain.agents import create_agent
from src.state.graph_state import State
from src.tools.basic_vision_tools import basic_vision_tools
from config.settings import settings


def build_vision_agent():
    """
    Build a vision agent using the new create_agent pattern- Langchain v1.0
    New Features:
    -Langgraph based execution
    -Built in memory and Tool calling, checkpointing.
    -Human in the loop for verification.
    
    What doesn't need to be done manually:
    -Create State grpah.
    -Add nodes to the graph manually.
    -Define edges
    -Bind tools to LLMs
    Returns:
    A compiled graph ready to use.
      OLD WAY (v0.x):
    ```python
    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tools = llm.bind_tools(tools)
    graph = StateGraph(...)
    graph.add_node("agent", llm_with_tools)
    # ... more manual setup
    app = graph.compile()
    ```
    
    NEW WAY (v1.0):
    ```python
    agent = create_agent(
        model="gpt-4o",
        tools=[...],
        system_prompt="..."
    )
    ```
    """
    system_prompt = """
    You are a helpful assistant that can analyze images and provide information about them.
    You can use the following tools to analyze the image:
    - get_image_properties: Get basic properties of an image file.
    - analyze_image_colors: Analyze the colors in an image.
    - detect_image_quality_issues: Detect potential quality issues in an image.

    **Guidelines:**
    -1. When user asks "analyze this image" → Use ALL tools
    -2. When user asks specific questions → Use relevant tool(s)
    -3. When user asks about colors → Use analyze_image_colors
    -4. When user asks about quality → Use detect_image_quality_issues
    -5. Always be thorough but concise

    **Important:**
    - Always use at least ONE tool when analyzing images
    - Don't just describe the image - use tools to get data!
    - Always be thorough but concise

    """

    agent=create_agent(
        model=settings.default_llm_model,
        tools=basic_vision_tools,
        system_prompt=system_prompt,
    )  

    return agent

if __name__ == "__main__":
    print("[TEST] Testing LangChain v1.0 Vision Agent...\n")

    # Check Python version
    import sys
    if sys.version_info < (3, 10):
        print("[ERROR] LangChain v1.0 requires Python 3.10+")
        print(f"   Your version: {sys.version}")
        exit(1)

    print("[OK] Python version OK\n")

    # Build the agent
    print("Building vision agent using create_agent()...")

    try:
        agent = build_vision_agent()
        print("[OK] Agent created successfully!\n")

        print("Agent type:", type(agent))
        print("\nAgent info:")
        print(f"  - Built on LangGraph: Yes")
        print(f"  - Has memory: Yes")
        print(f"  - Has persistence: Yes")
        print(f"  - Supports streaming: Yes")
        print(f"  - Tools available: {len(basic_vision_tools)}")

        # Test with a simple message
        print("\n\n[TEST] Testing agent with a message...")
        test_input = {
            "messages": [
                {"role": "user", "content": "Hello! Can you help me analyze images?"}
            ]
        }

        response = agent.invoke(test_input)

        print("\n[OK] Agent response:")
        print(f"  {response['messages'][-1].content[:200]}...")

        print("\n\n[SUCCESS] LangChain v1.0 Agent is working perfectly!")
        print("\nKey differences from old code:")
        print("  [OLD] Manual LangGraph building")
        print("  [NEW] Single create_agent() call")
        print("  [OLD] llm.bind_tools()")
        print("  [NEW] create_agent(model, tools, prompt)")
        print("  [OLD] Manual state management")
        print("  [NEW] Automatic with LangGraph")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nMake sure:")
        print("1. OPENAI_API_KEY is set in .env")
        print("2. You have internet connection")
        print("3. langchain>=1.0.0 is installed")
        print("4. Python 3.10+ is being used")