"""
OCR Agent - Specialized agent for text extraction and document analysis.

This agent focuses on:
- Text extraction from images
- Document structure analysis
- Text region detection and localization
- Receipt and form processing

Built using LangChain v1.0's create_agent() pattern.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config.settings import settings
from src.state.graph_state import GraphState
from src.tools.ocr_tools import (
    extract_text_from_image,
    detect_text_regions,
    analyze_document_structure
)


def create_ocr_agent():
    """
    Create an OCR-specialized agent for text extraction and document analysis.

    This agent uses:
    - GPT-4o (multimodal) for understanding context
    - EasyOCR tools for text extraction
    - Document analysis tools for structure understanding

    Returns:
        Compiled LangGraph agent ready for invocation
    """
    # Initialize the LLM (using GPT-4o for multimodal capabilities)
    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.temperature,
        api_key=settings.openai_api_key
    )

    # Define OCR-specific tools
    ocr_tools = [
        extract_text_from_image,
        detect_text_regions,
        analyze_document_structure
    ]

    # Create system message with OCR-specific instructions
    system_message = """You are an OCR specialist assistant focused on text extraction and document analysis.

Your expertise includes:
- Extracting text from documents, receipts, forms, screenshots, and signs
- Analyzing document structure and layout
- Detecting and localizing text regions
- Processing multi-language documents
- Providing detailed document analysis

When a user asks you to analyze a document or extract text:
1. First, use extract_text_from_image to get the text content
2. If needed, use detect_text_regions to understand text layout
3. For complex documents, use analyze_document_structure for deeper insights
4. Always provide clear, structured responses

You have access to three OCR tools:
- extract_text_from_image: Extract all text from an image
- detect_text_regions: Detect text locations with bounding boxes
- analyze_document_structure: Analyze document layout and reading order

Be helpful, accurate, and thorough in your text extraction and analysis."""

    # Create the agent using LangChain v1.0 pattern
    # This automatically:
    # - Binds tools to the LLM
    # - Creates the LangGraph execution graph
    # - Manages conversation state
    # - Handles tool calling loop
    agent = create_react_agent(
        llm,
        tools=ocr_tools,
        state_modifier=system_message,
        checkpointer=MemorySaver()  # In-memory conversation persistence
    )

    return agent


def invoke_ocr_agent(agent, user_message: str, image_path: str = None, thread_id: str = "default"):
    """
    Invoke the OCR agent with a user message and optional image.

    Args:
        agent: The compiled OCR agent
        user_message: User's text query
        image_path: Optional path to document/image to analyze
        thread_id: Thread ID for conversation persistence

    Returns:
        Agent response
    """
    # Prepare the message
    if image_path:
        # For OCR, we mainly work with file paths passed to tools
        # But we could also send the image to the VLM for visual understanding
        from src.tools.vision_utils import create_vision_message
        message = create_vision_message(user_message, image_path)
    else:
        message = HumanMessage(content=user_message)

    # Invoke the agent with conversation threading
    config = {"configurable": {"thread_id": thread_id}}
    response = agent.invoke(
        {"messages": [message]},
        config=config
    )

    return response


# Demo/Testing code
if __name__ == "__main__":
    import sys
    from pathlib import Path

    print("Creating OCR Agent...")
    agent = create_ocr_agent()

    # Interactive demo
    print("\n" + "="*60)
    print("OCR AGENT - Document Analysis Assistant")
    print("="*60)
    print("\nCommands:")
    print("  - Type 'analyze <image_path>' to analyze a document")
    print("  - Type 'extract <image_path>' to extract text")
    print("  - Type 'quit' to exit")
    print("="*60 + "\n")

    thread_id = "ocr_demo_session"

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        # Parse command
        if user_input.startswith("analyze ") or user_input.startswith("extract "):
            parts = user_input.split(" ", 1)
            if len(parts) == 2:
                command = parts[0]
                image_path = parts[1].strip('"\'')

                if not Path(image_path).exists():
                    print(f"Error: Image not found at {image_path}")
                    continue

                if command == "analyze":
                    query = f"Please analyze the document at {image_path}. Provide detailed structure analysis and extract the text."
                else:  # extract
                    query = f"Please extract all text from {image_path}."

                print(f"\nOCR Agent: Processing {image_path}...")
                response = invoke_ocr_agent(agent, query, image_path, thread_id)

                # Print the final response
                final_message = response["messages"][-1]
                print(f"\nOCR Agent: {final_message.content}")
            else:
                print("Usage: analyze <image_path> or extract <image_path>")
        else:
            # General query
            response = invoke_ocr_agent(agent, user_input, thread_id=thread_id)
            final_message = response["messages"][-1]
            print(f"\nOCR Agent: {final_message.content}")
