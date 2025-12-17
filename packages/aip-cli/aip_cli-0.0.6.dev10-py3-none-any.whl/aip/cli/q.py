"""
***********************************************************************************************************************
* DISCLAIMER
* This software is supplied by Renesas Electronics Corporation and is only intended for use with Renesas products. No
* other uses are authorized. This software is owned by Renesas Electronics Corporation and is protected under all
* applicable laws, including copyright laws.
* THIS SOFTWARE IS PROVIDED "AS IS" AND RENESAS MAKES NO WARRANTIES REGARDING
* THIS SOFTWARE, WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. ALL SUCH WARRANTIES ARE EXPRESSLY DISCLAIMED. TO THE MAXIMUM
* EXTENT PERMITTED NOT PROHIBITED BY LAW, NEITHER RENESAS ELECTRONICS CORPORATION NOR ANY OF ITS AFFILIATED COMPANIES
* SHALL BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES FOR ANY REASON RELATED TO THIS
* SOFTWARE, EVEN IF RENESAS OR ITS AFFILIATES HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
* Renesas reserves the right, without notice, to make changes to this software and to discontinue the availability of
* this software. By using this software, you agree to the additional terms and conditions found by accessing the
* following link:
* http://www.renesas.com/disclaimer
*
* Copyright (C) 2025 Renesas Electronics Corporation. All rights reserved.
***********************************************************************************************************************
***********************************************************************************************************************
* File Name    : q.py
* Version      : 1.12
* Product Name : AIP-CLI
* Device(s)    : N/A
* Description  : Renesas Q command
***********************************************************************************************************************
***********************************************************************************************************************
* History      :
* Ver   DD.MM.YYYY  Author  Description
* 1.00  05.11.2025  CSe     Initial revision
* 1.01  20.11.2025  AEk     Enhance conversation history handling
* 1.02  24.11.2025  AEk     Add confirmation prompt for session deletion
* 1.03  24.11.2025  TR      Add timeout for chat input
* 1.04  24.11.2025  Sam     Added --validate flag to run Renesas Q in validation mode.
* 1.05  24.11.2025  AEk     Update title of recent chat history table for clarity
* 1.06  25.11.2025  AEk     Refactor UX: Chat starts new session, History command added
* 1.07  26.11.2025  Sam     Changed --validate name flag to --no-banner.
* 1.08  28.11.2025  Msh     Updated env variable names
* 1.09  02.12.2025  CSe     Fixed exiting shell on authentication failure and renamed Vision Designer references
* 1.10  03.12.2025  AKu     Commands Modified
* 1.11  03.12.2025  AEk     Reverted handling timeout related changes to fix freezing issue
* 1.12  03.12.2025  PKa     Introduction of settings
***********************************************************************************************************************
"""

import collections.abc
import logging
import os
import queue
import random
import shutil
import sys
import threading
import time
import traceback

from aip.cli.history import ChatHistoryDB
from aip.core import Client
from aip.settings import get_settings

import click
import pyfiglet
from botocore.exceptions import ClientError
from click_shell import shell
from colorama import Fore, Style, init
from rich.console import Console
from rich.live import Live

# Additional imports for code formatting
from rich.markdown import Markdown
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich_gradient import Gradient
from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands.types.content import Message
from strands_tools import retrieve

AIP_Q_SESSION_TIMEOUT = 60 * 60  # 1 hour

# Platform-specific imports for terminal control
try:
    import termios
    import tty

    POSIX = True
except ImportError:
    # Fix: Define variables as None to satisfy linters
    termios = None
    tty = None
    POSIX = False

# Initialize colorama for cross-platform color support
init()

# Get terminal width for better formatting
terminal_width = shutil.get_terminal_size().columns
console = Console()
logger = logging.getLogger(__name__)


def ensure_terminal_echo():
    """
    Ensure terminal echo is enabled for input visibility
    Parameters:
    - None
    Return:
    - None
    """
    if POSIX and termios:
        try:
            fd = sys.stdin.fileno()
            attrs = termios.tcgetattr(fd)
            # Enable ECHO flag (index 3 is lflag)
            attrs[3] = attrs[3] | termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
        except (OSError, termios.error):
            # Ignore errors if stdin is not a terminal (e.g. pipe)
            pass
        except Exception:  # noqa: S110
            # Catch-all for other unexpected terminal errors to prevent crashing
            pass

    # Also use ANSI escape codes as fallback
    sys.stdout.write("\033[?25h")  # Show cursor
    sys.stdout.flush()


def get_bootstrap_config(client: Client) -> dict:
    """
    Fetch bootstrap config from the Renesas Q backend
    Parameters:
    - client: client to get the bootstrap config
    Return:
    - dict: Bootstrap configuration
    """
    api_url = f"{client.aip_url}/q/bootstrap"
    token = client.load_auth_token()

    response, error = client.request(api_url, headers={"Authorization": f"Bearer {token.get('id_token')}"})

    if not error:
        return response

    message, code = response.get("message"), response.get("code")
    details = f"Err[{code}]: {message}" if message and code else ""
    # Raise Exception instead of sys.exit(1) to allow caller to handle gracefully
    raise RuntimeError(f"Error fetching bootstrap config {details}")


def create_callback_function(status_queue: queue.Queue) -> collections.abc.Callable:
    """
    Create a callback function that puts status messages into a queue.
    Parameters:
    - status_queue: Queue to put status messages into
    Return:
    - Callable: The universal callback function
    """

    def callback_function(*args, **kwargs):
        """
        Universal callback function that handles all event types with any arguments
        Parameters:
        - *args: Positional arguments
        - **kwargs: Keyword arguments
        Return:
        - None
        """
        # Try to extract event type from args or kwargs
        event_type = None
        if args and isinstance(args[0], str):
            event_type = args[0]
        if not event_type and "event_type" in kwargs:
            event_type = kwargs["event_type"]

        # Track event loop lifecycle
        if kwargs.get("init_event_loop", False):
            status_queue.put("🚀 Renesas Q initialized")
        elif kwargs.get("start_event_loop", False):
            status_queue.put("🤔 Renesas Q assistant is thinking...")
        elif "message" in kwargs:
            status_queue.put("✍️  Generating detailed answer...")
        elif kwargs.get("complete", False):
            status_queue.put("🏁 Finalizing response...")
        elif kwargs.get("force_stop", False):
            status_queue.put(f"🛑 Event loop force-stopped: {kwargs.get('force_stop_reason', 'unknown reason')}")

        # Track tool usage
        if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_name = kwargs["current_tool_use"]["name"]
            if tool_name == "retrieve":
                status_queue.put("🔍 Retrieving information from knowledge base")

    return callback_function


def load_conversation_history(agent: Agent, session_id: int, db: ChatHistoryDB) -> bool:
    """
    Load conversation history directly into the agent's messages
    Parameters:
    - agent: The AI agent instance
    - session_id: The ID of the session to load
    - db: The ChatHistoryDB instance
    Return:
    - bool: True if successful, False otherwise
    """
    settings = get_settings()
    debug = settings.debug
    old_messages = db.get_session_messages(session_id)
    if not old_messages:
        return True

    if debug:
        print(f"{Fore.CYAN}[DEBUG] Loading {len(old_messages)} messages into agent...{Style.RESET_ALL}")

    try:
        formatted_messages = [Message(role=msg["role"], content=[{"text": msg["content"]}]) for msg in old_messages]

        # Inject into agent's internal message list
        agent.messages = formatted_messages

        if debug:
            print(f"{Fore.GREEN}[DEBUG] ✓ Loaded {len(formatted_messages)} messages {Style.RESET_ALL}")

        return True  # noqa: TRY300

    except Exception as e:
        if debug:
            print(f"{Fore.RED}[DEBUG] ✗ Failed to load history: {e}{Style.RESET_ALL}")
            traceback.print_exc()
        return False


def print_banner() -> None:
    """
    Print a fancy Renesas Q banner
    Parameters:
    - None
    Return:
    - None
    """
    font_list = ["smmono12", "kban", "mono9", "3-d", "blocky"]
    print("\n")
    # Suppress cryptographic random warning for font selection (S311)
    selected_font = random.choice(font_list)  # noqa: S311
    figlet_text = pyfiglet.figlet_format("Renesas Q", font=selected_font)

    with Live(console=console, refresh_per_second=2) as live:
        for _i in range(5):
            rainbow_text = Gradient(figlet_text, rainbow=True, justify="center")
            live.update(rainbow_text)
            time.sleep(0.2)

    console.print(Gradient("Your AI assistant for the Renesas AI Platform CLI (aip CLI)", rainbow=True, justify="center"))
    print("\n")

    # Restore terminal echo after animations
    ensure_terminal_echo()


def typing_effect(text: str, speed: float = 0.01) -> None:
    """
    Create a typing effect for text output.
    Parameters:
    - text: Text to display
    - speed: Delay between each character in seconds
    Return:
    - None
    """
    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)
    print()


@shell(prompt=f"{Style.BRIGHT}{Fore.CYAN}Q >{Style.RESET_ALL} ", intro="")
@click.pass_obj
@click.option("--no-banner", is_flag=True, help="Disable Renesas Q banner printing")
def q(client: Client, *, no_banner: bool) -> None:
    """
    Interactive chat agent Renesas Q
    Parameters:
    - client: Authenticated client object
    - validate: Flag to run in validation mode
    Return:
    - None
    """
    try:
        client.require_auth()
        if not no_banner:
            print_banner()
            typing_effect(f"{Style.BRIGHT}Welcome to Renesas Q!{Style.RESET_ALL} How can I help you today?")
            print(f"\n{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}chat{Style.RESET_ALL}    - Start a new interactive chat session")
            print(f"  {Fore.GREEN}history{Style.RESET_ALL} - Continue a previous chat session")
            print(f"  {Fore.GREEN}help{Style.RESET_ALL}    - How the Renesas Q agent can assist you")
            print()  # Empty line for spacing
        # Ensure terminal is ready for shell prompts
        ensure_terminal_echo()
    except Exception as e:
        print(f"{Fore.RED}Authentication check failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


@q.command(name="help")
def show_help():
    """
    Show how this Renesas Q agent can assist you
    Parameters:
    - None
    Return:
    - None
    """
    help_text = f"""\n{Fore.YELLOW}
    Renesas Q is your intelligent assistant for Renesas AI Platform CLI (aip CLI) {Style.RESET_ALL}

    Here are some ways I can assist you:
    - Answer questions about Renesas Vision Designer features and capabilities
    - Provide guidance on using Vision Designer
    - Help troubleshoot common issues
    - Offer best practices for AI model development and deployment

    \n{Fore.GREEN}Just type "{Fore.YELLOW}chat{Style.RESET_ALL}{Fore.GREEN}" to start a new session {Style.RESET_ALL}
    """
    md = Markdown(help_text)
    console.print(md)


def _select_session_from_history(db: ChatHistoryDB) -> int | None:  # noqa: PLR0915
    """
    Display recent sessions and prompt user for selection
    Parameters:
    - db: ChatHistoryDB instance
    Return:
    - int | None: Selected session ID or None if cancelled
    """
    while True:
        recent_sessions = db.get_recent_sessions(limit=20)

        if not recent_sessions:
            print(f"\n{Fore.YELLOW}No history found Starting a new chat...{Style.RESET_ALL}\n")
            return None
        table_width = 150
        topic_width = table_width - 30  # Reserve space for Index(8) + Date(18) + Borders

        table = Table(title="Recent Chat History", width=table_width)
        table.add_column("Index", justify="center", style="cyan", no_wrap=True, width=8)
        table.add_column("Date", style="magenta", width=18)
        table.add_column("Topic", style="green", no_wrap=False, width=topic_width)

        for idx, session in enumerate(recent_sessions, 1):
            date_str = str(session["updated_at"])[:16]
            table.add_row(str(idx), date_str, session["title"])

        console.print(table)
        print(f"\n{Fore.CYAN}Tip: Type 'd1' to delete a chat, or 'q' to return to main menu.{Style.RESET_ALL}")

        ensure_terminal_echo()
        time.sleep(0.1)
        sys.stdout.flush()

        prompt_txt = f"{Fore.YELLOW}Select Index (1-{len(recent_sessions)}){Style.RESET_ALL} > "

        try:
            user_input = input(prompt_txt).strip()

            if not user_input:
                continue

            # --- Handle Exit ---
            if user_input.lower() in ("exit", "quit", "q"):
                return None

            # --- Handle Deletion (d1, d2, etc.) ---
            if user_input.lower().startswith("d"):
                try:
                    idx_to_delete = int(user_input[1:])
                    if 1 <= idx_to_delete <= len(recent_sessions):
                        session_to_delete = recent_sessions[idx_to_delete - 1]
                        confirm_txt = f"{Fore.RED}Are you sure you want to delete '{session_to_delete['title']}'? (y/N) > {Style.RESET_ALL}"
                        confirm = input(confirm_txt).strip().lower()
                        if confirm in ("y", "yes"):
                            db.delete_session(session_to_delete["id"])
                            print(f"{Fore.GREEN}Deleted session: {session_to_delete['title']}{Style.RESET_ALL}\n")
                        else:
                            print(f"{Fore.YELLOW}Deletion cancelled {Style.RESET_ALL}\n")
                        continue
                    print(f"{Fore.RED}Invalid deletion index {Style.RESET_ALL}")
                    continue
                except ValueError:
                    print(f"{Fore.RED}Invalid format Use 'd1' to delete item 1 {Style.RESET_ALL}")
                    continue

            # --- Handle Selection ---
            choice = int(user_input)

            if 1 <= choice <= len(recent_sessions):
                selected_session = recent_sessions[choice - 1]
                print(f"\nResuming chat: {Fore.GREEN}{selected_session['title']}{Style.RESET_ALL}\n")
                return selected_session["id"]

            print(f"{Fore.RED}Invalid selection {Style.RESET_ALL}")

        except (ValueError, IndexError):
            print(f"{Fore.RED}Please enter a valid number {Style.RESET_ALL}")
        except KeyboardInterrupt:
            print("\n")
            return None


def _initialize_agent_system(client: Client, current_session_id: int | None, db: ChatHistoryDB, *, load_history: bool, debug: bool) -> tuple[Agent, queue.Queue] | None:
    """
    Initialize the Bedrock model, Agent, and Status Queue
    Parameters:
    - client: Authenticated client object
    - current_session_id: ID of the current chat session
    - db: ChatHistoryDB instance
    - load_history: Boolean flag to load conversation history
    - debug: Boolean flag for debug output
    Return:
    - tuple[Agent, queue.Queue] | None: Initialized Agent and Status Queue, or None on failure
    """
    try:
        config = get_bootstrap_config(client)
        kb_id = config.get("bedrock_knowledgebase_id")
        guardrail_id = config.get("guardrail_id", "renesas_q_guardrail_v1")
        guardrail_version = config.get("guardrail_version", "1")

        os.environ["AWS_ACCESS_KEY_ID"] = config.get("aws_access_key_id", "")
        os.environ["AWS_SECRET_ACCESS_KEY"] = config.get("aws_secret_access_key", "")
        os.environ["AWS_SESSION_TOKEN"] = config.get("aws_session_token", "")
        region = "ap-northeast-1"
        os.environ["AWS_REGION"] = region
        model_id = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"

        status_queue = queue.Queue()

        bedrock_model = BedrockModel(
            model_id=model_id,
            region_name=region,
            max_tokens=2048,
            streaming=True,
            temperature=0.2,
            guardrail_id=guardrail_id,
            guardrail_version=guardrail_version,
        )

        conversation_manager = SlidingWindowConversationManager(window_size=20)

        callback_function = create_callback_function(status_queue)

        agent = Agent(
            system_prompt=f"""You are an intelligent assistant for Renesas AI Platform CLI (aip CLI)
            Format your responses using Markdown
            Provide concise facts about Vision Designer etc.. Use knowledge base with ID {kb_id}""",
            tools=[retrieve],
            model=bedrock_model,
            callback_handler=callback_function,
            conversation_manager=conversation_manager,
        )

        if load_history and current_session_id:
            history_loaded = load_conversation_history(agent, current_session_id, db)
            if history_loaded and debug:
                print(f"{Fore.GREEN}History restored {Style.RESET_ALL}")

        return agent, status_queue  # noqa: TRY300

    except Exception as e:
        print(f"{Fore.RED}Failed to initialize: {e}{Style.RESET_ALL}")
        if debug:
            traceback.print_exc()
        return None


def _run_chat_loop(agent: Agent, status_queue: queue.Queue, db: ChatHistoryDB, current_session_id: int, *, debug: bool):  # noqa: PLR0915 C901
    """
    Main interactive loop for the chat session
    Parameters:
    - agent: Initialized Agent
    - status_queue: Status Queue
    - db: Database instance
    - current_session_id: Current Session ID
    - debug: Debug Flag
    Return:
    - None
    """
    table_width = terminal_width - 10

    while True:
        try:
            ensure_terminal_echo()
            time.sleep(0.05)
            prompt_style = f"{Fore.GREEN}{Style.BRIGHT}You{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}>{Style.RESET_ALL} "
            user_input = input(prompt_style)
            if not user_input.strip():
                continue

            if user_input.lower() in ("exit", "quit", "bye"):
                print(f"\n{Fore.CYAN}Thank you for using Renesas Q Goodbye!{Style.RESET_ALL}")
                break

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            break

        # --- SAVE USER MESSAGE TO DB ---
        msgs = db.get_session_messages(current_session_id, limit=20)
        if len(msgs) == 0:
            safe_len = min(len(user_input), table_width)
            new_title = user_input[:safe_len] + ".." if len(user_input) > table_width else user_input
            db.update_session_title(current_session_id, new_title)
        db.add_message(current_session_id, "user", user_input)

        # --- AGENT THREAD & UI LOOP ---
        result_queue = queue.Queue()

        def run_agent_task(u_input, q_out):
            """
            Run the agent task and put result in queue

            Parameters:
            - u_input: User input string
            - q_out: Queue output result
            Return:
                None
            """
            try:
                res = agent(u_input)
                q_out.put(("success", res))
            except Exception as ex:
                q_out.put(("error", ex))

        agent_thread = threading.Thread(target=run_agent_task, args=(user_input, result_queue))
        agent_thread.start()

        progress = Progress(TextColumn("[bold blue]{task.description}"), BarColumn(), TimeElapsedColumn())
        task = progress.add_task("Starting...", total=None)
        status_queue.put("Thinking...")

        with Live(progress, refresh_per_second=10, transient=True) as _:
            while agent_thread.is_alive():
                try:
                    while not status_queue.empty():
                        status = status_queue.get_nowait()
                        progress.update(task, description=f"{status}")
                except queue.Empty:
                    pass
                time.sleep(0.1)

        agent_thread.join()
        ensure_terminal_echo()
        print("\r" + " " * terminal_width + "\r", end="", flush=True)

        if not result_queue.empty():
            status, payload = result_queue.get()

            if status == "error":
                if isinstance(payload, ClientError):
                    print(f"\n{Fore.YELLOW}Session expired Please re-authenticate {Style.RESET_ALL}")
                    break
                print(f"\n{Fore.RED}Error: {payload}{Style.RESET_ALL}")

            elif status == "success":
                response = payload

                if debug:
                    print(f"{Fore.GREEN}--- Agent Debug Information ---{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Total tokens: {response.metrics.accumulated_usage['totalTokens']}")
                    latency = response.metrics.accumulated_metrics.get("latencyMs", 0)
                    print(f"{Fore.GREEN}Latency: {latency / 1000:.2f}s")
                    print(f"{Fore.GREEN}--- End of Debug Information ---{Style.RESET_ALL}\n")

                if isinstance(response, str):
                    resp_text = response
                else:
                    resp_text = None
                    for attr in ("text", "output", "content", "result"):
                        if hasattr(response, attr):
                            resp_text = getattr(response, attr)
                            break
                    if resp_text is None:
                        resp_text = str(response)

                if current_session_id and resp_text:
                    db.add_message(current_session_id, "assistant", resp_text)

                print(f"\n{Style.BRIGHT}{Fore.CYAN}Renesas Q:{Style.RESET_ALL} ")
                console.print(Markdown(resp_text))
                print()


@q.command()
@click.pass_obj
@click.option("--debug", is_flag=True, help="Show agent debug information")
def chat(client: Client, *, debug: bool) -> None:
    """
    Start a new interactive chat session
    Parameters:
    - client: Authenticated client object
    - debug: Boolean flag for debug output
    Return:
    - None
    """
    print(f"\n{Style.BRIGHT}Starting a new session {Style.RESET_ALL}")
    ensure_terminal_echo()

    db = ChatHistoryDB()
    current_session_id = db.create_session(title="New Session")

    init_result = _initialize_agent_system(client=client, current_session_id=current_session_id, db=db, load_history=False, debug=debug)
    if current_session_id is None:
        print(f"{Fore.RED}Error: Failed to create a new chat session database entry {Style.RESET_ALL}")
        return

    if init_result:
        agent, status_queue = init_result
        _run_chat_loop(agent, status_queue, db, current_session_id, debug=debug)


@q.command()
@click.pass_obj
@click.option("--debug", is_flag=True, help="Show agent debug information")
def history(client: Client, *, debug: bool) -> None:
    """
    View history and continue a previous chat session
    Parameters:
    - client: Authenticated client object
    - debug: Boolean flag for debug output
    Return:
    - None
    """
    ensure_terminal_echo()
    db = ChatHistoryDB()

    current_session_id = _select_session_from_history(db)

    if current_session_id:
        # Resume the selected session
        init_result = _initialize_agent_system(client=client, current_session_id=current_session_id, db=db, load_history=True, debug=debug)

        if init_result:
            agent, status_queue = init_result
            _run_chat_loop(agent, status_queue, db, current_session_id, debug=debug)
