"""
Interactive CLI for Vision Agentic System
Using LangChain v1.0 patterns!

This is much simpler than the old approach because create_agent()
handles all the complexity for us.
"""

import uuid
from pathlib import Path

from graph import build_vision_agent
from src.tools.vision_utils import create_vision_message, validate_image_file
from config.settings import check_setup


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print("VISION AGENTIC SYSTEM - LangChain v1.0")
    print("="*70)
    print("\nFeatures:")
    print("  - Vision analysis with GPT-4o")
    print("  - Image properties, colors, quality detection")
    print("  - Automatic tool selection")
    print("  - Conversation memory (built-in!)")
    print("  - DRAG & DROP support for images!")
    print("\nCommands:")
    print("  - Type your message normally")
    print("  - 'image <path>' - Upload and analyze image")
    print("  - Or just DRAG & DROP an image file!")
    print("  - 'help' - Show this help")
    print("  - 'new' - Start new conversation")
    print("  - 'quit' or 'exit' - End chat")
    print("="*70 + "\n")


def print_help():
    """Print help information."""
    print("\nHELP")
    print("-" * 50)
    print("\n1. ANALYZE AN IMAGE (3 ways):")
    print("   a) Type: image product.jpg")
    print("   b) Drag & drop image file directly")
    print("   c) Paste file path")
    print("\n2. ASK SPECIFIC QUESTIONS:")
    print("   What colors are in this image?")
    print("   Is this image good quality?")
    print("\n3. EXAMPLES:")
    print("   image photo.png")
    print("   C:\\Users\\photos\\vacation.jpg  (drag-drop)")
    print("   What are the dominant colors?")
    print("\n4. SUPPORTED FORMATS:")
    print("   .jpg, .jpeg, .png, .gif, .bmp, .webp")
    print("-" * 50 + "\n")


def is_image_path(text: str) -> bool:
    """
    Check if the input text is likely an image file path.
    Handles drag-and-drop paths with or without quotes.
    """
    # Remove quotes (drag-drop often adds quotes)
    cleaned = text.strip().strip('"').strip("'")

    # Check if it's a file path
    path = Path(cleaned)

    # Check if it exists and has image extension
    if path.exists() and path.is_file():
        ext = path.suffix.lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
        return ext in image_extensions

    # Also check if it looks like a path (even if doesn't exist yet)
    # This helps with paths that might be valid but not accessible
    ext = path.suffix.lower()
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
    return ext in image_extensions


def clean_path(path_string: str) -> str:
    """
    Clean a file path from drag-and-drop or manual input.
    Removes quotes and normalizes the path.
    """
    # Remove surrounding quotes
    cleaned = path_string.strip().strip('"').strip("'")
    return cleaned


def interactive_chat():
    """
    Interactive chat with the vision agent.

    LEARNING NOTE - V1.0 Simplifications:

    OLD WAY (v0.x):
    - Manual thread_id management
    - Manual config passing
    - Manual state updates
    - Custom memory setup

    NEW WAY (v1.0):
    - Memory is automatic!
    - Just call agent.invoke()
    - LangGraph handles everything
    """

    print_header()

    # Check setup
    if not check_setup():
        print("\n[ERROR] Please configure API keys before continuing.")
        return

    # Build the agent (ONE line!)
    print("[INIT] Initializing vision agent...")

    try:
        agent = build_vision_agent()
        print("[OK] Agent ready!\n")
    except Exception as e:
        print(f"\n[ERROR] Error building agent: {e}")
        print("\nMake sure:")
        print("  1. Python 3.10+ is installed")
        print("  2. langchain>=1.0.0 is installed")
        print("  3. API key is valid")
        return

    # Generate conversation ID (for memory)
    # V1.0 note: Memory is automatic, but we can still use config for threads
    thread_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"thread_id": thread_id}}

    print(f"[CHAT] Conversation started (ID: {thread_id})")
    print("Type 'help' for commands or start chatting!\n")

    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if user_input.lower() == 'new':
                thread_id = str(uuid.uuid4())[:8]
                config = {"configurable": {"thread_id": thread_id}}
                print(f"\n[NEW] New conversation started (ID: {thread_id})\n")
                continue

            if user_input.lower() == 'help':
                print_help()
                continue

            # Handle image upload (with "image" prefix OR auto-detect drag-drop)
            image_path = None

            # Check if input starts with "image " command
            if user_input.lower().startswith('image '):
                image_path = clean_path(user_input[6:])
            # Auto-detect if user just dragged/pasted an image path
            elif is_image_path(user_input):
                image_path = clean_path(user_input)
                print("[DETECTED] Image file detected!")

            # Process image if we have a path
            if image_path:
                # Validate image
                is_valid, error_msg = validate_image_file(image_path)
                if not is_valid:
                    print(f"[ERROR] {error_msg}\n")
                    continue

                # Ask what to do with the image
                print(f"[IMAGE] {image_path}")
                prompt = input("   What would you like to know? ").strip()

                if not prompt:
                    prompt = "Analyze this image in detail"

                # Create multimodal message
                print("\n[ANALYZING] Processing image...\n")

                try:
                    message = create_vision_message(prompt, image_path)

                    # Invoke agent with image
                    # V1.0: Just pass messages in the standard format!
                    result = agent.invoke(
                        {"messages": [message]},
                        config=config
                    )

                    # Print response
                    response = result['messages'][-1].content
                    print(f"Agent: {response}\n")

                except Exception as e:
                    print(f"[ERROR] {e}\n")
                    continue

            else:
                # Regular text message
                print()  # Newline

                try:
                    # V1.0: Simple message format
                    result = agent.invoke(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=config
                    )

                    # Print response
                    response = result['messages'][-1].content
                    print(f"Agent: {response}\n")

                except Exception as e:
                    print(f"[ERROR] {e}\n")
                    continue

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Type 'quit' to exit.\n")
            continue
        except EOFError:
            print("\n\nGoodbye!")
            break

if __name__ == "__main__":
    interactive_chat()
