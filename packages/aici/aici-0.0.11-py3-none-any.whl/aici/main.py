"""
aici  CLI for AI

This module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

Functions:
    def query_chatgpt(prompt:str, complete:bool=False, model:str=DEFAULT_MODEL, 
                  system:str=DEFAULT_SYSTEM, output=sys.stdout) -> None:

    def main() -> None:

Examples:
    >>> sys.argv = ['/path/to/aici', 'Hello']
    >>> aici.main()
    Hello! How can I assist you today

"""

import os
import io
import sys
import argparse
import openai
from openai import OpenAI
import pyperclip
import logging
from . import __version__

# Default settings
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SYSTEM = "You are a helpful assistant."

# Log settings - Default is INFO level
logger = logging.getLogger("aici")

# Flag to track if logging has been initialized
_logging_initialized = False

# Set log file path to the same location as the config file
def setup_logging():
    global _logging_initialized

    # Only initialize once
    if _logging_initialized:
        return

    from . import ENV_FILE, CONFIG_LOADED

    # Default log file path
    log_dir = os.path.expanduser("~/.config/aici")
    log_file = os.path.join(log_dir, "aici.log")

    # If config file is loaded, create log file in that directory
    if CONFIG_LOADED and ENV_FILE:
        config_dir = os.path.dirname(ENV_FILE)
        if os.path.isdir(config_dir):
            log_file = os.path.join(config_dir, "aici.log")

    # Try to create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Set up log file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

    except (IOError, PermissionError) as e:
        # If can't write to log file, show warning and continue
        print(f"Warning: Could not create log file at {log_file}. Logging to file is disabled.")
        print(f"Error: {str(e)}")

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Default is to show only warnings and above
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(console_handler)

    # Set logger level
    logger.setLevel(logging.INFO)

    _logging_initialized = True

# Function to check if we're in test mode (check dynamically)
def is_test_mode():
    return os.environ.get('AICI_TEST_MODE', 'false').lower() == 'true'

# Default model can also be retrieved from environment variables
DEFAULT_OPENAI_MODEL = os.getenv("AICI_OPENAI_MODEL", DEFAULT_MODEL)
DEFAULT_DEEPSEEK_MODEL = os.getenv("AICI_DEEPSEEK_MODEL", "deepseek-chat")

# Constants
DEPRECATED_MODELS = {
    "gpt-3.5-turbo": "Deprecated in February 2026. Migration to gpt-4o-mini is recommended.",
    "chatgpt-4o-latest": "Deprecated on February 17, 2026. Migration to gpt-4o is recommended.",
    "gpt-4.5-preview": "Already deprecated. Migration to gpt-4o or gpt-4.1 is recommended."
}

OPENAI_MODEL_EXAMPLES = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4.1", "gpt-5", "o3"]
DEEPSEEK_MODEL_EXAMPLES = ["deepseek-chat"]

API_KEY_PREVIEW_LENGTH = 4
CLIPBOARD_OUTPUTS = {"clip", "clipboard"}

# Helper function to get API key
def get_api_key(primary_key, fallback_key):
    """Get API key from environment variables"""
    return os.getenv(primary_key) or os.getenv(fallback_key)

# Function to select API provider based on model name
def select_api_provider(model_name):
    """Return appropriate API key and base URL based on model name"""
    # Check for deprecated models and log warning
    if model_name in DEPRECATED_MODELS:
        logger.warning("Model '%s' is %s", model_name, DEPRECATED_MODELS[model_name])

    if model_name.startswith("deepseek"):
        # For DeepSeek models
        provider_api_key = get_api_key("AICI_DEEPSEEK_KEY", "DEEPSEEK_API_KEY")
        if not provider_api_key:
            raise RuntimeError("When model name starts with deepseek, AICI_DEEPSEEK_KEY or DEEPSEEK_API_KEY is required")
        return provider_api_key, "https://api.deepseek.com"
    else:
        # Otherwise treat as OpenAI by default
        provider_api_key = get_api_key("AICI_OPENAI_KEY", "OPENAI_API_KEY")
        if not provider_api_key:
            raise RuntimeError("When model name doesn't start with deepseek, AICI_OPENAI_KEY or OPENAI_API_KEY is required")
        return provider_api_key, "https://api.openai.com/v1"

# Client cache for reuse
_client_cache = {}

def get_or_create_client(api_key, base_url):
    """Get cached client or create new one"""
    cache_key = (api_key, base_url)
    if cache_key not in _client_cache:
        _client_cache[cache_key] = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    return _client_cache[cache_key]

# Get system message from environment variable
DEFAULT_SYSTEM = os.getenv("AICI_SYSTEM", DEFAULT_SYSTEM)

# Helper function to normalize file path for cross-platform compatibility
def normalize_path(file_path):
    """Normalize file path to handle both forward and backward slashes on Windows

    Args:
        file_path (str): File path that may contain forward slashes

    Returns:
        str: Normalized file path with proper separators for the OS
    """
    # Expand user home directory first
    expanded = os.path.expanduser(file_path)
    # Normalize path separators (converts / to \\ on Windows, keeps / on Unix)
    normalized = os.path.normpath(expanded)
    return normalized

# Function to load system message from file
def read_system_from_file(file_path):
    """Load system message from file"""
    try:
        normalized_path = normalize_path(file_path)
        with open(normalized_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error("Error loading system message file: %s", e)
        return None

# Get system message file from environment variable
system_file = os.getenv("AICI_SYSTEM_FILE")
if system_file:
    file_content = read_system_from_file(system_file)
    if file_content:
        DEFAULT_SYSTEM = file_content


def query_deepseek(
    prompt: str,
    complete: bool = False,
    model: str = DEFAULT_MODEL,
    system: str = DEFAULT_SYSTEM,
    output=sys.stdout,
) -> str:
    """Sends a prompt to the AI API and handles the response, either streaming or complete.
    
    Args:
        prompt (str): The prompt to send to the API.
        complete (bool, optional): Whether to return the complete response or stream it. Defaults to False.
        model (str, optional): The model to use. Defaults to DEFAULT_MODEL.
        system (str, optional): The system message to use. Defaults to DEFAULT_SYSTEM.
        output (optional): Where to write the output. Defaults to sys.stdout.
        
    Returns:
        str: The complete response if complete=True, otherwise an empty string.

    Raises:
        openai.APIConnectionError: If the server could not be reached.
        openai.RateLimitError: If the API rate limit is exceeded (429 status code).
        openai.APIStatusError: If any other non-200-range status code is received.
    """
    # Select API provider based on model name
    provider_api_key, provider_base_url = select_api_provider(model)

    # Get or create cached client
    client = get_or_create_client(provider_api_key, provider_base_url)

    logger.debug("Selected API provider: %s", provider_base_url)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    try:
        # Use mock API in test mode
        if is_test_mode():
            from .mock_api import mock_create
            if complete:
                # For complete response in test mode
                response = mock_create(
                    model=model,
                    messages=messages,
                    stream=False
                )
                response_content = "Mocked DeepSeek Response"
                print(response_content, flush=True, file=output)
                return response_content
            else:
                # For streaming response in test mode
                collected_response = "Mocked DeepSeek Response"
                print(collected_response, flush=True, file=output)
                return collected_response
        else:
            if not complete:
                # Streaming response from DeepSeek API
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,  # Enable streaming mode
                )

                # Collecting and printing the streamed response
                chunks = []
                for chunk in stream:
                    chunk_message = chunk.choices[0].delta.content or ""
                    print(chunk_message, end="", flush=True, file=output)
                    chunks.append(chunk_message)

                print()  # Print a newline at the end
                return ''.join(chunks)
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=False,  # Explicitly disable streaming for complete mode
                )
                # Print a newline at the end
                response_content = response.choices[0].message.content
                print(response_content, flush=True, file=output)
                return response_content

    except openai.APIConnectionError as e:
        logger.error("The server could not be reached", exc_info=e)
        # Keep detailed error in logs, but show concise message to user
        return "Error: Could not connect to the server. Please check your internet connection."
    except openai.RateLimitError as e:
        logger.error(
            "A 429 status code was received; we should back off a bit.", exc_info=e
        )
        return "Error: API rate limit exceeded. Please wait a moment and try again."
    except openai.NotFoundError as e:
        logger.error("404 Not Found error occurred", exc_info=e)
        # For 404 errors, show error message related to model name
        error_message = str(e)
        if "model" in error_message.lower() and "not exist" in error_message.lower():
            # Show examples of available models
            openai_examples = ", ".join(OPENAI_MODEL_EXAMPLES)
            deepseek_examples = ", ".join(DEEPSEEK_MODEL_EXAMPLES)

            if model.startswith("deepseek"):
                return f"Error: Model '{model}' does not exist or you do not have access to it.\nAvailable DeepSeek models: {deepseek_examples}"
            elif model.startswith("gpt") or model.startswith("chatgpt"):
                return f"Error: Model '{model}' does not exist or you do not have access to it.\nAvailable OpenAI models: {openai_examples}"
            else:
                return f"Error: Model '{model}' does not exist or you do not have access to it.\nAvailable models:\n- OpenAI: {openai_examples}\n- DeepSeek: {deepseek_examples}"
        else:
            return "Error: API endpoint not found. Please check if the API version or URL is correct."
    except openai.APIStatusError as e:
        logger.error("Non-200-range status code was received", exc_info=e)
        # Message based on status code
        if hasattr(e, 'status_code'):
            if e.status_code == 401:
                return "Error: Authentication failed. Please check if your API key is correct."
            elif e.status_code == 403:
                return "Error: Access denied. Please check the permissions of your API key."
            else:
                return f"Error: The API server returned an error (status code: {e.status_code})."
        else:
            return "Error: The API server returned an error."


def query_chatgpt(
    prompt: str,
    complete: bool = False,
    model: str = DEFAULT_MODEL,
    system: str = DEFAULT_SYSTEM,
    output=sys.stdout,
) -> str:
    """Sends a prompt to the ChatGPT API and handles the response, either streaming or complete.

    This function is an alias for query_deepseek and provides backward compatibility.

    Args:
        prompt (str): The prompt to send to the API.
        complete (bool, optional): Whether to return the complete response or stream it. Defaults to False.
        model (str, optional): The model to use. Defaults to DEFAULT_MODEL.
        system (str, optional): The system message to use. Defaults to DEFAULT_SYSTEM.
        output (optional): Where to write the output. Defaults to sys.stdout.

    Returns:
        str: The complete response if complete=True, otherwise an empty string.

    Raises:
        openai.APIConnectionError: If the server could not be reached.
        openai.RateLimitError: If the API rate limit is exceeded (429 status code).
        openai.APIStatusError: If any other non-200-range status code is received.
    """
    return query_deepseek(prompt, complete, model, system, output)


def main() -> None:
    """Main function for the CLI"""
    # Initialize log settings
    setup_logging()
    
    try:
        parser = argparse.ArgumentParser(
            description="AICI - AI Chat Interface: Command line tool for easy use of OpenAI/DeepSeek models",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""Examples:
  aici "What is the capital of Japan"                  # Basic usage
  aici -m gpt-4o "What is the capital of Japan"        # Specify model
  aici -S system.txt "What is the capital of Japan"   # Specify system message file
  aici -o clip "What is the capital of Japan"        # Copy result to clipboard
  echo "What is the capital of Japan" | aici -       # Read from standard input
"""
        )
        parser.add_argument(
            "prompt",
            type=str,
            nargs="?",
            default=argparse.SUPPRESS,
            help='Prompt to send to AI. Specify "-" to read from standard input',
        )
        parser.add_argument(
            "-v", "--version", action="store_true", help="Show version and exit"
        )
        # Get model name from command line argument or environment variable
        default_model = DEFAULT_MODEL
        if os.getenv("AICI_MODEL"):
            default_model = os.getenv("AICI_MODEL")
        elif os.getenv("AICI_OPENAI_MODEL") and not os.getenv("AICI_DEEPSEEK_MODEL"):
            default_model = os.getenv("AICI_OPENAI_MODEL")
        elif os.getenv("AICI_DEEPSEEK_MODEL") and not os.getenv("AICI_OPENAI_MODEL"):
            default_model = os.getenv("AICI_DEEPSEEK_MODEL")
            
        # Create model examples for help text
        model_examples = ", ".join(OPENAI_MODEL_EXAMPLES[:3] + DEEPSEEK_MODEL_EXAMPLES)

        parser.add_argument(
            "-m", "--model",
            default=default_model,
            help=f"Model name to use (e.g., {model_examples})"
        )
        parser.add_argument(
            "-c",
            "--complete",
            default=False,
            action="store_true",
            help="Get complete response at once without streaming",
        )
        parser.add_argument(
            "-s", "--system", default=DEFAULT_SYSTEM, help="Specify system message"
        )
        parser.add_argument(
            "-S", "--system-file", 
            help="Specify file containing system message"
        )
        parser.add_argument(
            "-V", "--verbose", "--VERBOSE", 
            dest="verbose",
            action="store_true", 
            help="Show detailed debug information"
        )
        parser.add_argument(
            "-o",
            "--output",
            help='Specify output destination. Use "clip" to copy to clipboard',
            default=sys.stdout,
        )
        args = parser.parse_args()

        if args.version:
            print(__version__)
            sys.exit(0)
            
        # Set debug mode
        if args.verbose:
            # Set log level to DEBUG
            logger.setLevel(logging.DEBUG)
            
            # Set all handlers' level to DEBUG
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.DEBUG)
            
            logger.debug("Debug mode enabled")
            logger.debug("Model: %s", args.model)
            
            # Show config file loading status
            from . import ENV_FILE, CONFIG_LOADED
            if CONFIG_LOADED:
                logger.debug("Config file loaded from: %s", ENV_FILE)
            else:
                logger.debug("No config file loaded. Using environment variables.")
            
            # Check available API keys
            openai_key = get_api_key("AICI_OPENAI_KEY", "OPENAI_API_KEY")
            deepseek_key = get_api_key("AICI_DEEPSEEK_KEY", "DEEPSEEK_API_KEY")

            if openai_key:
                logger.debug("OpenAI API key: %s%s", openai_key[:API_KEY_PREVIEW_LENGTH], '*' * 8)
            else:
                logger.debug("OpenAI API key: Not set")

            if deepseek_key:
                logger.debug("DeepSeek API key: %s%s", deepseek_key[:API_KEY_PREVIEW_LENGTH], '*' * 8)
            else:
                logger.debug("DeepSeek API key: Not set")
                
            # Check model settings in environment variables
            aici_model = os.getenv("AICI_MODEL")
            aici_openai_model = os.getenv("AICI_OPENAI_MODEL")
            aici_deepseek_model = os.getenv("AICI_DEEPSEEK_MODEL")
            
            if aici_model:
                logger.debug("AICI_MODEL: %s", aici_model)
            if aici_openai_model:
                logger.debug("AICI_OPENAI_MODEL: %s", aici_openai_model)
            if aici_deepseek_model:
                logger.debug("AICI_DEEPSEEK_MODEL: %s", aici_deepseek_model)
            
            # Show API provider used based on model name
            try:
                selected_api_key, selected_base_url = select_api_provider(args.model)
                logger.debug("Selected API key: %s%s", selected_api_key[:API_KEY_PREVIEW_LENGTH], '*' * 8)
                logger.debug("Selected base URL: %s", selected_base_url)
            except Exception as e:
                logger.debug("Model selection error: %s", e)

        # Load system file if specified
        if args.system_file:
            file_content = read_system_from_file(args.system_file)
            if file_content:
                args.system = file_content
            else:
                print(f"Error: Could not read system message from file: {args.system_file}", file=sys.stderr)
                sys.exit(1)

        # Check if 'prompt' exists and is not None
        if getattr(args, "prompt", None) is None or args.prompt is None:
            parser.error("the following arguments are required: prompt")

        # Check if the prompt is "-" and read from stdin if so
        if args.prompt == "-":
            prompt = sys.stdin.read().strip()
        else:
            prompt = args.prompt

        if args.output in CLIPBOARD_OUTPUTS:
            buffer = io.StringIO()
        else:
            buffer = sys.stdout

        # Record debug information
        if args.verbose:
            prompt_preview = prompt[:50] + ('...' if len(prompt) > 50 else '')
            system_preview = args.system[:50] + ('...' if len(args.system) > 50 else '')
            logger.debug("Prompt: %s", prompt_preview)
            logger.debug("System message: %s", system_preview)
            
        response = query_deepseek(
            prompt,
            model=args.model,
            complete=args.complete,
            system=args.system,
            output=buffer,
        )
        
        # Display error message if returned
        if response and response.startswith("Error:"):
            print(response, file=sys.stderr)
            sys.exit(1)

        if args.output in CLIPBOARD_OUTPUTS:
            pyperclip.copy(buffer.getvalue() if hasattr(buffer, 'getvalue') else str(buffer))

    except Exception as e:
        logger.error("Error", exc_info=e)
        # Don't show stack trace, display user-friendly error message
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
