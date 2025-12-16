from __future__ import annotations

import glob
import os
import sys
import warnings
# --- SILENCE STARTUP NOISE ---
# 1. Hide the "Hello from pygame" message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
# 2. This line hides the "pkg_resources is deprecated" warning
# It tells Python: "If you see a UserWarning about pkg_resources, don't print it."
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")
# -----------------------------
# ... existing imports ...
import json
import logging
import mimetypes
import random
import re
import shutil
import socket
import subprocess
import time
import datetime
import urllib.error
import urllib.parse
import urllib.request
from typing import List
import qrcode
from qrcode import constants
import io
import psutil
import pyfiglet
import pygame
from colorama import Fore, Style, init
from ddgs import DDGS
from spellchecker import SpellChecker
# --- NEW IMPORT ---
try:
    # Use an alias for clarity
    import whisper as whisper_module
    whisper_available = True
except ImportError:
    # Set the module alias to None
    whisper_module = None
    whisper_available = False
    print(f"{Fore.YELLOW}Warning: 'openai-whisper' not found. Transcription features disabled.{Style.RESET_ALL}")
# ------------------
def load_configuration(config_file_path="config.json"):
    """
    Loads configuration settings from a JSON file.
    Returns a dictionary of settings, or sensible defaults if the file is missing or invalid.
    """
    settings = {}
    default_settings = {
        "history_file": "search_history.txt",
        "max_results": 10,
        "region": "us-en",
        "auto_open_first_result": False,
        "download_dir": "Mr_Searcher_Downloads",
        "whisper_model_name": "base",
        "prompt_for_transcription": True,
        "transcription_format": "txt"
    }
    try:
        with open(config_file_path, 'r') as f:
            # Use the json module to load the data, ignoring comments for simplicity
            # Note: json.load() is strict, so ensure config.json has no trailing commas or comments.
            # I will use a simple regex to strip C-style comments before parsing, for robustness.
            content = f.read()
            # Remove C-style comments (// ...) for cleaner parsing
            content_no_comments = '\n'.join(
                line for line in content.splitlines()
                if not line.strip().startswith('//')
            )
            settings = json.loads(content_no_comments)

        #logging.info(f"Configuration loaded successfully from {config_file_path}")
    except FileNotFoundError:
        logging.warning(f"Configuration file '{config_file_path}' not found. Using default settings.")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in '{config_file_path}': {e}. Using default settings.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading configuration: {e}. Using default settings.")

    # Merge loaded settings with defaults to ensure all keys are present
    final_config = {**default_settings, **settings}
    return final_config

CONFIG = load_configuration()
WHISPER_MODEL_NAME = CONFIG["whisper_model_name"]
# Initialize colorama
init(autoreset=True)  # ensure colors work on Windows
# --- NEW GLOBAL VARIABLE ---
# This logger object will be used throughout the script
# Initialize it right away, and configure it later
logger = logging.getLogger('MrSearcherApp')
# --- CONFIGURATION FLAGS ---
# These flags will be set in check_dependencies()
yt_dlp_enabled = True  # Assume true until proven otherwise

todo_list: List[str] = []
# Themes for text output
themes = {
    "default": {"banner": Fore.GREEN, "prompt": Fore.YELLOW},
    "dark": {"banner": Fore.WHITE, "prompt": Fore.CYAN},
    "neon": {"banner": Fore.MAGENTA, "prompt": Fore.GREEN}
}
current_theme = themes["default"]

SEARCH_FILTERS = {
    "{wiki}": "site:wikipedia.org",
    "{code}": "site:stackoverflow.com OR site:github.com",
    "{news}": "site:bbc.com OR site:cnn.com OR site:reuters.com",
    "{youtube}": "site:www.youtube.com"
}
# Trigger words for commands
trigger_words = {"{play}": "play", "{pause}": "pause", "{resume}": "unpause", "{stop}": "stop",
                 "{matrix}": "matrix_rain", "{about}": "show_about", "{clear}": "clear_screen", "{theme}": "set_theme",
                 "{terminal_art}": "show_art",
                 # --- NEW TRIGGERS ---
                 "{next}": "next_track",
                 "{prev}": "previous_track",
                 "{playlist}": "show_playlist",
                 "{weather}": "get_weather",
                 "{find}": "find_file",
                 "{animart}": "show_animated_art",
                 "{history}": "show_history",
                 "{select}": "select_track_by_number",  # New trigger for selection
                 "{art_text}": "generate_art_from_text",
                 "{todo}": "manage_todo_list",
                 "{lookup}": "lookup_address",
                 "{sysinfo}": "get_system_info",
                 "{vol}": "set_volume",
                 "{fetch}": "fetch_file_by_url", "{banner}": "show_banner", "{help}": "show_help",
                 "{myip}": "get_public_ip", "{config}": "manage_configuration", "{qr}": "generate_qr_code"
}
helping_words = {
        "{play}": "start or resumes audio playback.",
        "{pause}": "pauses the currently playing track.",
        "{resume}": "resumes the paused track.",
        "{stop}": "stops playback entirely.",
        "{matrix}": "display the classic 'Matrix rain' visual effect.",
        "{about}": "show information about the application or project.",
        "{clear}": "clear all text from the terminal screen.",
        "{theme}": "change or set the application's visual theme.",
        "{terminal_art}": "display static terminal art (e.g., ASCII art).",
        "{next}": "skip to the next track in the playlist.",
        "{prev}": "goes back to the previous track in the playlist.",
        "{playlist}": "show the current list of available tracks or items.",
        "{weather}": "fetch and displays the current weather information.",
        "{find}": "search for a specific file on the system or directory.",
        "{animart}": "display animated terminal art.",
        "{history}": "show the command history.",
        "{select}": "select and plays a track using its number in a list.",
        "{art_text}": "generate terminal art (e.g., ASCII/Figlet art) from a provided text string.",
        "{todo}": "allow managing a personal To-Do list (add, view, complete tasks).",
        "{lookup}": "perform a geographical, network, or DNS address lookup.",
        "{sysinfo}": "retrieve and displays information about the operating system and hardware.",
        "{vol}": "adjust the audio volume level.",
        "{fetch}": "download or retrieves a file from a specified URL.",
        "{banner}": "display a prominent welcome or information banner.",
        "{myip}": "fetch and displays the machine's public IP address.",
        "{config}": "allow viewing or changing application settings and configuration.",
        "{qr}": "generate a QR code from a provided text or link."
    }
def describe_triggers(helping_words: dict) -> None:
    """
    Writes a description of what each command trigger in the dictionary does.

    Args:
        trigger_words: A dictionary where keys are the trigger words (e.g., "{play}")
                      and values are the corresponding function names (e.g., "play").
    """
    # Map the internal function names to user-friendly descriptions
    print("\n--- Command Trigger Descriptions ---")
    # Sort the items by trigger word for a cleaner display
    sorted_triggers = sorted(helping_words.items())

    for trigger, action in sorted_triggers:
        # Get the description, or provide a default if the action is new/missing
        description =  helping_words.get(action, f"Executing the '{trigger}' will {action}")
        print(f"**{trigger}**\t\t-> {description}")
    print("----------------------------------\n")
# Defining the list of triggers that work offline
offline_triggers = [
    "{play}", "{pause}", "{resume}", "{stop}", "{next}", "{prev}", "{playlist}",
    "{matrix}", "{about}", "{clear}", "{terminal_art}", "{theme}", "{animart}",
    "{find}", "{history}", "{art_text}", "{todo}", "{sysinfo}", "{vol}", "{select}", "{config}", "{qr}"
]
#Some ascii emotions
ascii_emotions = [
    "( *^-^)ρ(*╯^╰)", "~(>_<。)＼", "＞﹏＜", "(❁´◡`❁)","(●'◡'●)"
    ,"╰(*°▽°*)╯","☆*: .｡. o(≧▽≦)o .｡.:*☆","ヾ(≧▽≦*)o","(ಥ _ ಥ)", "( ´･･)ﾉ(._.`)"
]
# Safe pygame init / load
# --- NEW GLOBAL VARIABLES ---
MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads")
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads")
last_search_results: List[dict] = []
MUSIC_FILES: List[str] = []
current_track_index = 0
# ----------------------------
# --- NEW GLOBAL VARIABLE ---
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
# Dictionary to hold the last fetched price
last_crypto_prices = {"bitcoin": "$ --", "ethereum": "$ --"}
# --- CACHE MECHANISM ADDITION ---
last_crypto_fetch_time = 0.0
CRYPTO_CACHE_DURATION = 300  # 5 minutes in seconds
# ----------------------------
history_file = CONFIG["history_file"]
search_history: List[str] = []

audio_enabled = False
try:
    pygame.mixer.init()
    # The actual loading and checking will be moved to check_dependencies()
    audio_enabled = True # Assume success until dependency check proves otherwise
except Exception as e:
    print(f"Pygame mixer init failed, audio disabled: {e}")
    audio_enabled = False

triggers = list(trigger_words.keys())
commands_per_line = 8
# Create a list of lines, where each line is a space-separated string of commands
command_lines = [
    " ".join(triggers[i:i + commands_per_line])
    for i in range(0, len(triggers), commands_per_line)
]
# Combine the lines with a newline and indentation
formatted_commands = ('\n    ').join(command_lines)
# --- Second Print Statement (Offline Commands - Single Line) ---
# Formatting the offline triggers into a slash-separated string
formatted_offline_commands = "/".join(offline_triggers)

# --- LOGGING SETUP ---
LOG_FILE = "mr_searcher.log"

def setup_logging():
    """
    Configures the root logger for file and console output.
    Logs use a structured format (key:value pairs) for easier parsing.
    """
    global logger
    logger = logging.getLogger('MrSearcherApp')
    logger.setLevel(logging.DEBUG)  # Set the lowest level for debugging
    # --- FIX 1: Prevent 'MrSearcherApp' messages from propagating to the root logger ---
    logger.propagate = False  # <--- ADD THIS LINE

    # --- FIX 2: Clear any default handlers from the root logger (stops 'basicConfig' output) ---
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers = []  # <--- ADD THIS BLOCK

    # File Handler: Logs all detailed information to a file
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Console Handler: Logs INFO and above to the terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Log Format: Structured format with key information
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Application logging successfully initialized.")

def log_critical_error_and_exit(message: str, recommendation: str, component: str):
    """Logs a critical error with structured data and terminates the application."""
    logger.critical(
        f"FATAL EXIT: {message}",
        extra={
            'component': component,
            'recommendation': recommendation,
            'exit_code': 1
        }
    )
    # Print a user-friendly error message to the console
    print(f"\n[{Fore.RED}CRITICAL ERROR{Style.RESET_ALL}] - Component: {component}")
    print(f"    - Error: {message}")
    print(f"    - Action: {recommendation}")
    print(f"The application cannot run without this. Check {LOG_FILE} for details.")
    sys.exit(1)

# --- DEPENDENCY CHECK ---
def check_dependencies():
    """
    Checks for all required Python packages and external system binaries.
    If a critical dependency is missing, it logs and exits the script.
    Non-critical binaries (like yt-dlp) are handled by setting a global flag.
    """
    global yt_dlp_enabled
    logger.info("Starting comprehensive dependency check...")
    # Inside Mr_Searcher.py, in a function like check_dependencies() or before loading the model:
    global whisper_available
    MIN_RAM_FOR_WHISPER_GB = 4  # Example: Require 4GB for the 'base' model
    # ...
    if whisper_available:
        available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        if available_ram_gb < MIN_RAM_FOR_WHISPER_GB:
            logger.warning(f"Low memory detected ({available_ram_gb:.1f}GB). Disabling Whisper.")
            print(
                f"{Fore.YELLOW}Warning: Low memory detected ({available_ram_gb:.1f}GB free). Transcription features disabled.{Style.RESET_ALL}")
            whisper_available = False
        else:
            logging.info(f"Sufficient memory ({available_ram_gb:.1f}GB free) available for Whisper.")
    # 1. Python Package Checks (using try-except ImportError) - CRITICAL
    required_packages = {
        # ... (Keep existing required_packages check as is)
    }
    # ... (Keep existing loop for required_packages as is - they are critical)
    # 2. External Binary Check (using shutil.which) - NON-CRITICAL
    required_binaries = {
        'yt-dlp': ('download',
                   'For video/audio downloads. Must be installed and in system PATH. This feature will be disabled if missing.'),
        'ffmpeg': ('download', 'For merging video/audio formats. (Often required by yt-dlp)'),
    }
    # Check for non-critical external binaries and set the flag
    for binary_name, (component, instruction) in required_binaries.items():
        if shutil.which(binary_name) is None:
            # Set flag to False if ANY required download binary is missing
            yt_dlp_enabled = False
            logger.warning(
                f"Missing external command: '{binary_name}'. Download features disabled.",
                extra={'component': component}
            )
            # Print a user-friendly warning
            print(f"\n[{Fore.YELLOW}WARNING{Style.RESET_ALL}] - Component: {component}")
            print(f"    - Missing: {binary_name}. Download features are now DISABLED.")
        else:
            logger.debug(f"External binary '{binary_name}' check OK.", extra={'component': component})

    if yt_dlp_enabled:
        logger.info("yt-dlp and download features are ENABLED.")
    else:
        logger.info("yt-dlp and download features are DISABLED.")

    logger.info("All critical dependencies are met. Starting application.")
    print(f"\n[{Fore.GREEN}SUCCESS{Style.RESET_ALL}] Dependencies OK. Starting Mr. Searcher...")
    # 3. Directory Checks
    try:
        if not os.path.exists(MUSIC_DIR):
            os.makedirs(MUSIC_DIR)
            logger.info(f"Created music directory: {MUSIC_DIR}")

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            logger.info(f"Created download directory: {DOWNLOAD_DIR}")

    except Exception as e:
        logger.error(f"Failed to create essential directories: {e}")
        # Not a fatal error, but important to log.
    # 4. Audio Content Check (Move this logic from the global scope)
    global audio_enabled
    # 4a. Refresh the music file list from the Downloads folder
    refresh_music_files()

    if not audio_enabled or not MUSIC_FILES:
        # Note: audio_enabled is set by the initial pygame.mixer.init() success.
        # We only disable if no files are found or mixer failed previously.
        audio_enabled = False
        logger.warning("No music files found or Pygame mixer failed. Audio functionality disabled.")
        print(f"\n[{Fore.YELLOW}WARNING{Style.RESET_ALL}] Audio files missing or mixer failed. Audio disabled.")
    else:
        # 4b. Attempt to load the first track here for immediate feedback
        try:
            pygame.mixer.music.load(os.path.join(MUSIC_DIR, MUSIC_FILES[current_track_index]))
            logger.info("Initial audio file loaded successfully.")
        except Exception as e:
            audio_enabled = False
            logger.error(f"Pygame failed to load initial track: {e}")
            print(f"\n[{Fore.YELLOW}WARNING{Style.RESET_ALL}] Audio file load failed. Audio disabled.")

        else:
            # 4b. Attempt to load the first track here for immediate feedback
            if MUSIC_FILES:  # <-- Explicitly check it's not empty, though the 'else' implies it
                try:
                    pygame.mixer.music.load(os.path.join(MUSIC_DIR, MUSIC_FILES[current_track_index]))
                    logger.info("Initial audio file loaded successfully.")
                except Exception as e:
                    audio_enabled = False
                    logger.error(f"Pygame failed to load initial track: {e}")
                    print(f"\n[{Fore.YELLOW}WARNING{Style.RESET_ALL}] Audio file load failed. Audio disabled.")
            else:
                # This branch should not be hit, but it handles the possibility
                audio_enabled = False
                logger.warning("No music files found after initial check. Audio disabled.")

# --- NEW FUNCTION: download_file ---
def download_file(url, destination_folder="."):
    """Downloads a file from a URL to a specified folder with a progress bar."""
    # 1. Determine filename from URL
    try:
        # Use os.path.basename to get the filename from the path part of the URL
        filename = os.path.basename(urllib.parse.urlparse(url).path)
        if not filename:
            filename = "downloaded_file"

        # Simple cleanup for common URL query parameters
        if '?' in filename:
            filename = filename.split('?')[0]

        # Ensure filename is not too generic (like index.html) or empty
        if len(filename.strip()) < 5 and not os.path.splitext(filename)[1]:
            ext = mimetypes.guess_extension(urllib.request.urlopen(url).info().get_content_type())
            if ext:
                filename = f"downloaded_file{ext}"
            else:
                filename = "downloaded_file.bin"  # fallback

        # 2. Define the full path
        full_path = os.path.join(destination_folder, filename)

        print(current_theme["prompt"] + f"\nDownloading to: {full_path}" + Style.RESET_ALL)

        # Download hook for progress bar
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = block_num * block_size / total_size
                progressbar(percent)  # Reuse your existing progressBar function

        # 3. Perform the download
        urllib.request.urlretrieve(url, full_path, progress_hook)

        # Final status
        print(f"\r[{Fore.GREEN}{'=' * 70}{Style.RESET_ALL}] {Fore.GREEN}100%{Style.RESET_ALL}")
        print(current_theme["prompt"] + f"Download successful: {filename}" + Style.RESET_ALL)

    except urllib.error.URLError as e:
        print(current_theme["prompt"] + f"\nDownload Error: Invalid URL or network issue: {e}" + Style.RESET_ALL)
    except Exception as e:
        print(current_theme["prompt"] + f"\nAn unexpected error occurred during download: {e}" + Style.RESET_ALL)

# Function to handle media transcription
def transcribe_media(file_path):
    """Loads the Whisper model and transcribes the specified media file."""
    if not whisper_available:
        print(f"{Fore.RED}Error: Whisper is not available. Check installation.{Style.RESET_ALL}")
        return

    print(
        f"\n{Fore.YELLOW}Loading Whisper model ('{WHISPER_MODEL_NAME}')... (This may take a moment the first time){Style.RESET_ALL}")

    try:
        # FIX IS HERE: We pass the WHISPER_MODEL_NAME variable.
        model = whisper_module.load_model(WHISPER_MODEL_NAME)

        print(f"{Fore.GREEN}Model loaded. Starting transcription...{Style.RESET_ALL}")

        # Note: Depending on your hardware, you might specify device='cpu' or device='cuda'
        # The default is usually fine for most users.
        result = model.transcribe(
            audio=file_path,
            fp16=False
        )# type: ignore [call-arg]

        # Save the transcript
        transcript_path = os.path.splitext(file_path)[0] + ".txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(f"{Fore.GREEN}Transcription complete!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Transcript saved to: {Style.RESET_ALL}{transcript_path}")

    except Exception as e:
        print(f"{Fore.RED}Transcription Error:{Style.RESET_ALL} Could not process file with Whisper.")
        print(f"Details: {e}")
        # Common issue: Not enough memory or missing dependency
        print(
            f"{Fore.YELLOW}Tip: Try changing WHISPER_MODEL_NAME to 'tiny' or ensure torch is installed correctly.{Style.RESET_ALL}")
# --- NEW FUNCTION: ping_host ---
def ping_host(hostname, count=2):
    """Pings a hostname and returns the average latency in ms."""
    if not hostname:
        return "N/A"

    # Use a simpler command for both Windows (ping -n) and Linux/macOS (ping -c)
    param = '-n' if os.name == 'nt' else '-c'
    command = [f'ping', param, str(count), hostname]

    try:
        # Run the command
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )
        # Regex to find the average time (different for Windows/Linux)
        if os.name == 'nt':  # Windows output parsing
            match = re.search(r'Average = (\d+)ms', output.stdout)
            if match:
                return f"{match.group(1)}ms"
        else:  # Unix/macOS output parsing
            match = re.search(r'avg/stddev/mdev = [\d.]+/[\d.]+/([\d.]+)ms', output.stdout)
            if match:
                return f"{match.group(1)}ms"

        # If ping command fails (e.g., DNS error, firewall)
        return "Failed"

    except subprocess.TimeoutExpired:
        return "Timeout"
    except Exception:
        return "Error"

# --- NEW FUNCTION: get_system_info ---
def get_system_info():
    """Displays current CPU, Memory, and Disk usage."""
    print(current_theme["prompt"] + "\n--- System Performance Monitor ---" + Style.RESET_ALL)

    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(current_theme["prompt"] + f"CPU Usage: {Fore.CYAN}{cpu_percent:.1f}%{Style.RESET_ALL}")

    # Memory Usage
    memory = psutil.virtual_memory()
    mem_used = memory.used / (1024 ** 3)  # Convert bytes to GB
    mem_total = memory.total / (1024 ** 3)
    print(current_theme["prompt"] + f"RAM Used: {Fore.CYAN}{mem_used:.2f} GB{Style.RESET_ALL} / {mem_total:.2f} GB")
    print(current_theme["prompt"] + f"RAM Percent: {Fore.CYAN}{memory.percent:.1f}%{Style.RESET_ALL}")

    # Disk Usage (using the root directory of the current script location)
    try:
        disk = psutil.disk_usage(os.path.abspath(os.sep))  # Use root directory for OS
        disk_total = disk.total / (1024 ** 3)
        disk_used = disk.used / (1024 ** 3)
        print(current_theme[
                  "prompt"] + f"Disk Used: {Fore.CYAN}{disk_used:.2f} GB{Style.RESET_ALL} / {disk_total:.2f} GB")
        print(current_theme["prompt"] + f"Disk Percent: {Fore.CYAN}{disk.percent:.1f}%{Style.RESET_ALL}")
    except Exception as e:
        print(current_theme["prompt"] + f"Disk info error: {e}" + Style.RESET_ALL)

    print(current_theme["prompt"] + "----------------------------------" + Style.RESET_ALL)

# --- NEW FUNCTION: get_system_snapshot ---
def get_system_snapshot():
    """Returns a single line string of current CPU and RAM usage."""

    # Refresh crypto prices (non-blocking call)
    fetch_crypto_prices()
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=None)  # Don't block, get instantaneous

    # Memory Usage
    memory = psutil.virtual_memory()
    mem_percent = memory.percent

    # --- START OF NEW ADDITION ---
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # --- END OF NEW ADDITION ---

    # Ping
    latency = ping_host("duckduckgo.com", count=1)  # Get a quick, non-blocking ping

    # Format the snapshot string
    snapshot = (
        f"⌚ Time: {current_time}{Style.RESET_ALL} | "
        f"🖥️ CPU: {Fore.CYAN}{cpu_percent:.1f}%{Style.RESET_ALL} | "
        f"🧠 RAM: {Fore.CYAN}{mem_percent:.1f}%{Style.RESET_ALL} | "
        f"🌐 Ping: {Fore.CYAN}{latency}{Style.RESET_ALL} | "
        f"₿ BTC: {Fore.YELLOW}{last_crypto_prices['bitcoin']}{Style.RESET_ALL} | "  # <--- NEW Ticker
        f"Ξ ETH: {Fore.YELLOW}{last_crypto_prices['ethereum']}{Style.RESET_ALL}"
    )

    return snapshot
# Place this function near `get_system_snapshot`
def fetch_crypto_prices():
    """
    Fetches the current price of Bitcoin and Ethereum from CoinGecko, but only if the cache has expired.
    Updates the global `last_crypto_prices` dictionary.
    """
    global last_crypto_prices, last_crypto_fetch_time

    # 1. Check cache duration
    if time.time() - last_crypto_fetch_time < CRYPTO_CACHE_DURATION:
        logger.debug("Using cached crypto prices.")
        return # Use existing, cached prices

    try:
        # 2. Perform Fetch
        with urllib.request.urlopen(CRYPTO_API_URL, timeout=2) as response:
            data = response.read()

        prices = json.loads(data)
        btc_price = prices.get('bitcoin', {}).get('usd')
        eth_price = prices.get('ethereum', {}).get('usd')

        if btc_price is not None:
            last_crypto_prices["bitcoin"] = f"${btc_price:,.2f}"
        if eth_price is not None:
            last_crypto_prices["ethereum"] = f"${eth_price:,.2f}"

        # 3. Update fetch time on SUCCESS
        last_crypto_fetch_time = time.time()
        logger.debug("Successfully fetched and updated crypto prices.")

    except urllib.error.HTTPError as e:
        # GRACEFUL DEGRADATION for Rate Limit (429) and other HTTP errors
        if e.code == 429:
            logger.warning(f"Failed to fetch crypto prices: HTTP Error 429: Too Many Requests (API rate limit).")
            # If it's the first time fetching, show a specific error
            if last_crypto_prices["bitcoin"] == "$ --":
                last_crypto_prices["bitcoin"] = f"{Fore.YELLOW}Rate Limit{Style.RESET_ALL}"
                last_crypto_prices["ethereum"] = f"{Fore.YELLOW}Rate Limit{Style.RESET_ALL}"
                # If it's *not* the first time, it keeps the last valid cached price.
        else:
            logger.warning(f"Failed to fetch crypto prices: {e}")
            last_crypto_prices["bitcoin"] = f"{Fore.RED}API Error{Style.RESET_ALL}"
            last_crypto_prices["ethereum"] = f"{Fore.RED}API Error{Style.RESET_ALL}"

    except Exception as e:
        logger.warning(f"Failed to fetch crypto prices (General Error): {e}")
        last_crypto_prices["bitcoin"] = f"{Fore.RED}API Error{Style.RESET_ALL}"
        last_crypto_prices["ethereum"] = f"{Fore.RED}API Error{Style.RESET_ALL}"
# --- NOTE ---
# You need to add 'import json' at the beginning of your script.
def get_public_ip():
    """Fetches the current external IP address."""
    print("Triangulating public identity...")
    show_progress()
    try:
        # Using a public API to get IP
        with urllib.request.urlopen('https://api.ipify.org') as response:
            ip = response.read().decode('utf-8')

        print(current_theme["prompt"] + "\n--- Public Identity ---" + Style.RESET_ALL)
        print(current_theme["prompt"] + f"External IP: {Fore.RED}{ip}{Style.RESET_ALL}" + Style.RESET_ALL)

        # Simple Geolocation based on IP (using another free API)
        with urllib.request.urlopen(f'https://ipapi.co/{ip}/country_name/') as response:
            country = response.read().decode('utf-8')
            print(current_theme["prompt"] + f"Location Node: {Fore.YELLOW}{country}{Style.RESET_ALL}" + Style.RESET_ALL)

        print(current_theme["prompt"] + "-----------------------" + Style.RESET_ALL)
    except Exception as e:
        print(f"Could not fetch public IP: {e}")

# --- NEW FUNCTION: lookup_address ---
def lookup_address():
    """Performs DNS lookup for an IP address or domain name."""
    address = input(current_theme["prompt"] + "Enter domain or hostname (e.g., google.com): " + Style.RESET_ALL).strip()

    if not address:
        print("Address cannot be empty.")
        return

    print(f"\nAttempting lookup for: {address}...")
    show_progress()  # Reuse progress bar for a nice effect

    try:
        # gethostbyname_ex returns (hostname, aliaslist, ipaddrlist)
        hostname, aliases, ip_list = socket.gethostbyname_ex(address)

        print(current_theme["prompt"] + "\n--- Host Resolution Report ---" + Style.RESET_ALL)
        print(current_theme["prompt"] + f"Primary Hostname: {hostname}" + Style.RESET_ALL)

        if aliases:
            print(current_theme["prompt"] + "Aliases (CNAMEs):" + Style.RESET_ALL)
            for alias in aliases:
                print(current_theme["prompt"] + f"   - {alias}" + Style.RESET_ALL)

        if ip_list:
            print(current_theme["prompt"] + "IP Addresses Found:" + Style.RESET_ALL)
            for ip in ip_list:
                print(current_theme["prompt"] + f"   - {Fore.RED}{ip}{Style.RESET_ALL}" + Style.RESET_ALL)

        print(current_theme["prompt"] + "------------------------------" + Style.RESET_ALL)

    except socket.gaierror:
        print(current_theme[
                  "prompt"] + f"Error: Could not resolve address '{address}'. Check spelling or network." + Style.RESET_ALL)
    except Exception as e:
        print(f"An unexpected error occurred during lookup: {e}")

# --- CORRECTED FUNCTION: manage_configuration ---
def manage_configuration():
    """Manages application configuration (show/set)."""
    global CONFIG, WHISPER_MODEL_NAME

    command = input(
        current_theme["prompt"] + "Config Command (show / set <key> <value>): " + Style.RESET_ALL
    ).strip().lower()

    parts = command.split(' ', 2)
    action = parts[0]

    print(current_theme["prompt"] + "\n--- Application Configuration ---" + Style.RESET_ALL)

    if action == "show":
        if not CONFIG:
            print(current_theme["prompt"] + "Configuration dictionary is empty." + Style.RESET_ALL)
            return

        print(Fore.GREEN + "Key" + Style.RESET_ALL + " " * 25 + Fore.GREEN + "Value" + Style.RESET_ALL)
        print("-" * 40)
        # Display settings in a clean key: value format
        for key, value in CONFIG.items():
            print(current_theme["prompt"] + f"{key:<30}: {Fore.CYAN}{value}{Style.RESET_ALL}")

    elif action == "set" and len(parts) == 3:
        key = parts[1]
        value_str = parts[2]

        if key not in CONFIG:
            print(current_theme["prompt"] + f"Error: Configuration key '{key}' not found." + Style.RESET_ALL)
            print(current_theme["prompt"] + "Use 'show' to see available keys." + Style.RESET_ALL)
            return
        # --- FIX APPLIED HERE ---
        # Get the expected type before the try block to ensure 'current_type' is always defined
        # when the 'except' block needs to reference it for the error message.
        current_type = type(CONFIG[key])

        try:
            # Type conversion logic (Handles booleans, integers, and strings)

            # Special validation for booleans
            if current_type is bool:
                if value_str.lower() in ('true', 't', '1'):
                    new_value = True
                elif value_str.lower() in ('false', 'f', '0'):
                    new_value = False
                else:
                    raise ValueError(f"Invalid boolean value for {key}. Use 'True' or 'False'.")
            else:
                # Convert string to the original type (e.g., int("10"), str("value"))
                new_value = current_type(value_str)

            # Special check for max_results
            if key == "max_results" and (new_value <= 0 or new_value > 50):
                raise ValueError("max_results must be between 1 and 50.")

            # Special check for whisper model
            if key == "whisper_model_name":
                WHISPER_MODEL_NAME = str(new_value)  # Update the global variable used by transcribe_media

            # Apply the new setting
            CONFIG[key] = new_value
            print(current_theme["prompt"] + f"Successfully set '{key}' to: {Fore.CYAN}{CONFIG[key]}{Style.RESET_ALL}")

        except ValueError as e:
            # current_type is now guaranteed to be defined
            # I also refined the type conversion logic slightly to be cleaner
            type_name = current_type.__name__
            print(current_theme[
                      "prompt"] + f"Error: Invalid value format for '{key}'. Expected type: {type_name}. Details: {e}" + Style.RESET_ALL)
        except Exception as e:
            print(f"An unexpected error occurred during set: {e}")

    else:
        print(current_theme["prompt"] + "Invalid command. Use 'show' or 'set <key> <value>'." + Style.RESET_ALL)

    print(current_theme["prompt"] + "---------------------------------" + Style.RESET_ALL)
# --- NEW FUNCTION: manage_todo_list ---
def manage_todo_list():
    """Manages the session-based To-Do list (add, show, clear)."""
    global todo_list

    command = input(
        current_theme["prompt"] + "To-Do Command (add <item> / show / clear): " + Style.RESET_ALL).strip().lower()

    parts = command.split(' ', 1)
    action = parts[0]

    print(current_theme["prompt"] + "\n--- Session To-Do List ---" + Style.RESET_ALL)

    if action == "add" and len(parts) > 1:
        item = parts[1].strip()
        todo_list.append(item)
        print(current_theme["prompt"] + f"Task added: '{item}'" + Style.RESET_ALL)

    elif action == "show":
        if not todo_list:
            print(current_theme["prompt"] + "The To-Do list is empty." + Style.RESET_ALL)
        else:
            for i, item in enumerate(todo_list):
                print(current_theme["prompt"] + f"   [{i + 1}] {item}" + Style.RESET_ALL)

    elif action == "clear":
        todo_list = []
        print(current_theme["prompt"] + "To-Do list cleared." + Style.RESET_ALL)

    else:
        print(current_theme["prompt"] + "Invalid command. Use 'add <item>', 'show', or 'clear'." + Style.RESET_ALL)

    print(current_theme["prompt"] + "--------------------------" + Style.RESET_ALL)

# --- NEW FUNCTION: generate_art_from_text ---
def generate_art_from_text():
    """Generates ASCII art using pyfiglet from user-provided text."""
    text = input(current_theme["prompt"] + "Enter text to convert to ASCII art: " + Style.RESET_ALL).strip()
    font = input(current_theme[
                     "prompt"] + "Enter font (e.g., 'doom', 'slant', 'standard', leave blank for default): " + Style.RESET_ALL).strip()

    if not text:
        print("Text cannot be empty.")
        return

    # Use 'standard' font if user input is empty
    if not font:
        font = "standard"

    print(current_theme["prompt"] + "\n--- Custom ASCII Art ---\n" + Style.RESET_ALL)

    try:
        # Generate the art using the specified font
        art = pyfiglet.figlet_format(text, font=font)

        # Apply the banner color to the art
        print(current_theme["banner"] + art + Style.RESET_ALL)

    except pyfiglet.FontNotFound:
        print(current_theme["prompt"] + f"Font '{font}' not found. Try 'doom' or 'standard'." + Style.RESET_ALL)
    except Exception as e:
        print(f"An error occurred during art generation: {e}")

    print(current_theme["prompt"] + "\n------------------------\n" + Style.RESET_ALL)

# --- NEW FUNCTION: generate_qr_code ---
def generate_qr_code():
    """Prompts for a URL or result number and displays a QR code in the terminal."""
    global last_search_results
    results_count = len(last_search_results)

    # 1. Get Input and refine the prompt based on available results
    if results_count > 0:
        prompt_text = (
            f"Enter URL or select a result number (1-{results_count}) for QR code: "
        )
        print(f"{Fore.CYAN}Last search had {results_count} results. Enter 1, 2, etc., to use one.{Style.RESET_ALL}")
    else:
        # If no results, just prompt for a direct URL
        prompt_text = "Enter URL for QR code: "

    input_data = input(current_theme["prompt"] + prompt_text + Style.RESET_ALL).strip()

    if not input_data:
        print("Input cannot be empty.")
        return

    target_url = ""

    # 2. Determine Target URL
    try:
        # Check if input is a number and within range of last results
        selection_index = int(input_data) - 1
        if 0 <= selection_index < results_count:
            # Try to get the URL from the search result object
            result = last_search_results[selection_index]
            target_url = result.get("url") or result.get("href")
            print(f"Generating QR for: {Fore.GREEN}{target_url}{Style.RESET_ALL}")
        else:
            print(f"Invalid number. Please enter a number between 1 and {results_count} or a direct URL.")
            return

    except ValueError:
        # Input is not a number, treat as a direct URL/text
        target_url = input_data

    if not target_url:
        print("Could not determine a valid URL/data for QR code.")
        return

    # 3. Generate and Print QR Code
    print(current_theme["prompt"] + "\n--- Generated QR Code ---" + Style.RESET_ALL)

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=1,  # Smallest box size for terminal print
            border=2,
        )
        qr.add_data(target_url)
        qr.make(fit=True)

        # Print the QR code directly to the terminal using the 'text' factory.
        f = io.StringIO()
        # --- FIX FOR "Not a tty": Removed tty=True argument ---
        qr.print_ascii(out=f)
        f.seek(0)

        # Capture the raw ASCII output (uses '##' for dark blocks by default)
        qr_output = f.read()

        # Print the QR code and manually apply color, fixing the previous coloring issue
        # This replaces the default '##' characters with the colored '██' blocks
        colored_qr = qr_output.replace('##', Fore.CYAN + "██" + Style.RESET_ALL)

        print(colored_qr)

        # Re-print the URL clearly
        print(f"{Fore.YELLOW}URL:{Style.RESET_ALL} {target_url}")

    except Exception as e:
        print(f"{Fore.RED}QR Code Generation Error:{Style.RESET_ALL} {e}")

    print(current_theme["prompt"] + "-------------------------" + Style.RESET_ALL)
# --- NEW FUNCTION: select_track_by_number ---
def select_track_by_number():
    """Allows the user to select a track by its number in the playlist."""
    global current_track_index

    show_playlist()  # Show the user the numbered list first

    selection = input(current_theme["prompt"] + "Enter track number to play: " + Style.RESET_ALL).strip()

    try:
        track_number = int(selection)
        # Convert 1-based index (user input) to 0-based index
        new_index = track_number - 1

        if 0 <= new_index < len(MUSIC_FILES):
            current_track_index = new_index
            load_and_play_track()
        else:
            print(current_theme[
                      "prompt"] + f"Invalid track number. Please choose a number between 1 and {len(MUSIC_FILES)}." + Style.RESET_ALL)

    except ValueError:
        print(current_theme["prompt"] + "Invalid input. Please enter a number." + Style.RESET_ALL)
        # Good: Uses a unique name 'ex'
    except Exception as ex:
        print(f"Error selecting track: {ex}")

# --- NEW FUNCTION: show_history ---
def show_history():
    """Displays the search history."""
    global search_history

    if not search_history:
        print(current_theme["prompt"] + "\n--- Search History is Empty ---" + Style.RESET_ALL)
        return

    print(current_theme["prompt"] + "\n=== Recent Search History ===" + Style.RESET_ALL)
    # Display the last 20 searches (or all if less than 20)
    for i, item in enumerate(search_history[-20:]):
        print(current_theme[
                  "prompt"] + f"   {len(search_history) - len(search_history[-20:]) + i + 1}. {item}" + Style.RESET_ALL)
        print(current_theme["prompt"] + "-----------------------------" + Style.RESET_ALL)

# --- NEW FUNCTION: get_weather ---
# Updated get_weather() function
def get_weather():
    """Fetches and displays the current weather using DDGS."""
    city = input(current_theme["prompt"] + "Enter city name for weather: " + Style.RESET_ALL).strip()
    if not city:
        print("City name cannot be empty.")
        return

    print(f"\nFetching weather for: {city}...")
    show_progress()

    try:
        with DDGS() as ddgs:
            # Use a specific, targeted query
            results = list(ddgs.text(f"current temperature and forecast for {city}", max_results=5))

            weather_result = None
            for result in results:
                # Look for clues in the title/body that it's a weather result
                title = result.get("title", "").lower()
                snippet = result.get("body", "").lower()
                if "weather" in title or "temperature" in snippet or "celsius" in snippet or "fahrenheit" in snippet:
                    weather_result = result
                    break

            if weather_result:
                title = weather_result.get("title", "Weather Info")
                snippet = weather_result.get("body", "No detailed report found.")

                print(current_theme["prompt"] + "\n--- Weather Report ---" + Style.RESET_ALL)
                # Use type_out for an effect only on the main details
                print(current_theme["prompt"] + f"City: {title}" + Style.RESET_ALL)
                type_out(current_theme["prompt"] + f"Forecast: {snippet}" + Style.RESET_ALL, delay=0.01)
                print(current_theme["prompt"] + "----------------------" + Style.RESET_ALL)
            else:
                print(f"Could not find specific weather information for '{city}'. Try a different name.")
    except Exception as e:
        print(f"Error fetching weather: {e}")

# --- NEW FUNCTION: find_file ---
def find_file():
    """Searches for a file or directory name from a given start path."""
    search_term = input(
        current_theme["prompt"] + "Enter file/folder name to search: " + Style.RESET_ALL).strip().lower()
    start_path = input(current_theme["prompt"] + "Enter start path (e.g., C:\\): " + Style.RESET_ALL).strip()

    if not search_term:
        print("Search term cannot be empty.")
        return

    print(f"\nSearching for '{search_term}' starting from '{start_path}'...")
    found_files = []

    try:
        for root, dirs, files in os.walk(start_path):
            # Check files and directories
            if search_term in root.lower():
                found_files.append(f"[DIR] {root}")
            for name in files:
                if search_term in name.lower():
                    found_files.append(f"[FILE] {os.path.join(root, name)}")
            for name in dirs:
                if search_term in name.lower() and os.path.join(root, name) not in found_files:
                    found_files.append(f"[DIR] {os.path.join(root, name)}")

        if found_files:
            print(current_theme["prompt"] + "\n--- Search Results ---" + Style.RESET_ALL)
            for i, item in enumerate(found_files[:10]):  # Limit output to 10 results
                print(current_theme["prompt"] + f"{i + 1}. {item}" + Style.RESET_ALL)
            if len(found_files) > 10:
                print(f"... and {len(found_files) - 10} more results.")
            print(current_theme["prompt"] + "----------------------" + Style.RESET_ALL)
        else:
            print("No matching files or directories found.")

    except PermissionError:
        print(
            "Permission denied: Cannot access this path. Try running the script as administrator or choosing a different path.")
    except FileNotFoundError:
        print("Error: The starting path was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- NEW FUNCTION: show_animated_art ---
def show_animated_art(frames=50, delay=0.1):
    """Displays a simple animated wave art."""
    w_ave_frames = [
        f"{Fore.BLUE}~~~{Style.RESET_ALL} {Fore.CYAN}~~~{Style.RESET_ALL} {Fore.BLUE}~~~{Style.RESET_ALL}",
        f" {Fore.BLUE}~~~{Style.RESET_ALL} {Fore.CYAN}~~~{Style.RESET_ALL} {Fore.BLUE}~~~{Style.RESET_ALL} ",
        f"  {Fore.BLUE}~~~{Style.RESET_ALL} {Fore.CYAN}~~~{Style.RESET_ALL} {Fore.BLUE}~~~{Style.RESET_ALL}  ",
        f" {Fore.BLUE}~~~{Style.RESET_ALL} {Fore.CYAN}~~~{Style.RESET_ALL} {Fore.BLUE}~~~{Style.RESET_ALL} "
    ]

    print(current_theme["prompt"] + "\n--- Animated Wave ---" + Style.RESET_ALL)
    for i in range(frames):
        # Use sys.stdout.write and \r to overwrite the line
        sys.stdout.write('\r' + w_ave_frames[i % len(w_ave_frames)])
        sys.stdout.flush()
        time.sleep(delay)

    print("\n" + current_theme["prompt"] + "---------------------\n" + Style.RESET_ALL)

# Place this function near your other music controls
def set_volume():
    """Allows the user to set the background music volume."""
    if not audio_enabled:
        print("Audio is disabled.")
        return

    # Get current volume for display (pygame returns a float between 0.0 and 1.0)
    current_vol = pygame.mixer.music.get_volume() * 100

    volume_input = input(
        current_theme["prompt"] +
        f"Current Volume is {current_vol:.0f}%. Enter new volume (0-100): " +
        Style.RESET_ALL
    ).strip()

    try:
        new_vol = int(volume_input)
        if 0 <= new_vol <= 100:
            # Convert percentage back to 0.0 to 1.0 float for pygame
            pygame.mixer.music.set_volume(new_vol / 100.0)
            print(current_theme["prompt"] + f"Volume set to {new_vol}% 🔊" + Style.RESET_ALL)
        else:
            print(current_theme["prompt"] + "Volume must be between 0 and 100." + Style.RESET_ALL)
    except ValueError:
        print(current_theme["prompt"] + "Invalid input. Please enter a whole number." + Style.RESET_ALL)

# Place this function near the music-related functions (e.g., set_volume, load_and_play_track)
def refresh_music_files():
    """
    Scans the MUSIC_DIR for MP3 files and updates the global MUSIC_FILES list.
    """
    global MUSIC_FILES, current_track_index, audio_enabled

    logger.debug(f"Scanning directory for music files: {MUSIC_DIR}")

    # Use glob to find all files ending in .mp3 (case-insensitive)
    # The [i]ndex part of glob is not needed as we just want the list.
    # We use os.path.basename to get just the filename, not the full path.
    new_files = [
        os.path.basename(f)
        for f in glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
        if os.path.isfile(f)  # Ensure it is a file and not a directory
    ]

    # Check if the list has changed
    if sorted(new_files) != sorted(MUSIC_FILES):
        # Preserve the currently playing track if it's still in the new list
        old_track = None
        if MUSIC_FILES:  # <--- ADD THIS CHECK
            old_track = MUSIC_FILES[current_track_index]

        MUSIC_FILES = new_files

        # If the old track is still there, find its new index.
        # Otherwise, reset to the first track.
        if old_track and old_track in MUSIC_FILES:  # <--- Check for old_track existence
            current_track_index = MUSIC_FILES.index(old_track)
        else:
            # Only reset if the new list is NOT empty.
            current_track_index = 0

        audio_enabled = bool(MUSIC_FILES)  # Enable audio only if files are found

        if MUSIC_FILES:
            logger.info(f"Music file list updated. Total tracks: {len(MUSIC_FILES)}")
        else:
            logger.info("No music files found in the directory.")

    logger.debug(f"Current MUSIC_FILES: {MUSIC_FILES}")

def load_and_play_track():
    """Loads the track at the current_track_index and plays it."""
    global current_track_index
    if not audio_enabled or not MUSIC_FILES:
        print("Audio is disabled.")
        return
    track_name = MUSIC_FILES[current_track_index]
    full_path = os.path.join(MUSIC_DIR, track_name)

    try:
        if not os.path.exists(full_path):
            print(f"File not found: {track_name}")
            return

        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play(-1, fade_ms=1000)
        print(current_theme["prompt"] + f"Now playing: {track_name} 🎶" + Style.RESET_ALL)
    except Exception as e:
        print(f"Error loading or playing track: {e}")

def next_track():
    """Skips to the next track in the playlist."""
    global current_track_index
    if not MUSIC_FILES:  # <-- ADDED Guard
        print("Playlist is empty.")
        return
    current_track_index = (current_track_index + 1) % len(MUSIC_FILES)
    load_and_play_track()


def previous_track():
    """Skips to the previous track in the playlist."""
    global current_track_index
    if not MUSIC_FILES:  # <-- ADDED Guard
        print("Playlist is empty.")
        return
    current_track_index = (current_track_index - 1 + len(MUSIC_FILES)) % len(MUSIC_FILES)
    load_and_play_track()

def show_playlist():
    """Displays the list of available music tracks."""
    print(current_theme["prompt"] + "\n=== Available Tracks ===" + Style.RESET_ALL)
    for i, track in enumerate(MUSIC_FILES):
        prefix = " > " if i == current_track_index else "   "
        print(current_theme["prompt"] + f"{prefix}{i + 1}. {track}" + Style.RESET_ALL)
    print(current_theme["prompt"] + "--------------------------" + Style.RESET_ALL)

# Initialize spell checker and define video URL pattern
spell = SpellChecker()
VIDEO_PATTERN = r"(youtube\.com|youtu\.be|\.mp4$|\.m3u8$|vimeo\.com)"

# Define color patterns for rainbow effect
rainbow_colors: List[str] = [str(Fore.RED), str(Fore.YELLOW), str(Fore.GREEN),
                             str(Fore.CYAN), str(Fore.BLUE), str(Fore.MAGENTA)]

ASCII_ARTS = [
    # Cat art
    f"{Fore.CYAN} /\\_/\\{Style.RESET_ALL}\n{Fore.CYAN}( o.o ){Style.RESET_ALL}\n{Fore.CYAN} > ^ <{Style.RESET_ALL}",
    # Star art
    f"{Fore.YELLOW}  ★  {Style.RESET_ALL}\n{Fore.YELLOW}*****{Style.RESET_ALL}\n{Fore.YELLOW} *** {Style.RESET_ALL}\n{Fore.YELLOW}  * {Style.RESET_ALL}",
    # Heart art
    f"{Fore.RED}  _  _{Style.RESET_ALL}\n{Fore.RED} <3 <3{Style.RESET_ALL}\n{Fore.RED}  \\ /{Style.RESET_ALL}\n{Fore.RED}   v{Style.RESET_ALL}"
]

def set_theme(name):
    """Set the color theme for the CLI."""
    global current_theme
    if name in themes:
        current_theme = themes[name]
        print(f"Theme switched to {name} ✨")
    else:
        print("Theme not found.")

def show_terminal_art():
    """Display a random piece of ASCII art."""
    art = random.choice(ASCII_ARTS)
    print(current_theme["prompt"] + "\n--- Hidden Art Piece ---\n" + Style.RESET_ALL)
    print(art)
    print(current_theme["prompt"] + "\n------------------------\n" + Style.RESET_ALL)

# ... (existing functions like clear_screen, correct_query, etc.)
def load_history():
    """Loads search history from the HISTORY_FILE."""
    global search_history
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                # Read all lines, strip leading/trailing whitespace
                search_history = [line.strip() for line in f.readlines() if line.strip()]
            logging.info("Search history loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading search history: {e}")

def save_history(query):
    """Saves a single search query to the history list and the file."""
    global search_history
    # Add the new query to the list
    search_history.append(query)
    # Write the entire list to the file (overwriting it for simplicity)
    try:
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(query + '\n')
    except Exception as e:
        print(f"Error saving history: {e}")

def matrix_rain(duration=5):
    """Display a matrix rain effect in the terminal."""
    chars = "01"
    try:
        columns = shutil.get_terminal_size(fallback=(80, 20)).columns
    except OSError:
        columns = 80
    end_time = time.time() + duration
    while time.time() < end_time:
        line = ""
        for i in range(columns):
            color = rainbow_colors[i % len(rainbow_colors)]
            line += color + random.choice(chars) + Style.RESET_ALL
        print(line)
        time.sleep(0.05)

def type_out(text, delay=0.03, rainbow=False, glitch=False):
    """Type out text with optional rainbow colors and glitch effect."""
    for i, char in enumerate(text):
        if rainbow:
            color = rainbow_colors[i % len(rainbow_colors)]
            sys.stdout.write(color + char + Style.RESET_ALL)
        # 🥚 ENHANCED GLITCH EFFECT
        elif glitch and random.random() < 0.05:  # Lower chance, but louder effect
            glitch_char = random.choice(["@", "#", "%", "&"])
            glitch_color = random.choice([Fore.RED, Fore.MAGENTA, Fore.YELLOW])
            sys.stdout.write(glitch_color + glitch_char + Style.RESET_ALL)
            time.sleep(0.01)  # Ultra-fast glitch character
            sys.stdout.write(glitch_color + glitch_char + Style.RESET_ALL)  # Double glitch
        else:
            sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Place this function near your other helper functions (e.g., show_progress, show_banner)
def execute_download_with_progress(cmd):
    """Executes a command (like yt-dlp) and parses its live output to update a custom progress bar."""

    # Regex to find the download percentage in yt-dlp output
    # Example match: [download] 10.5% of 12.34MiB at 1.23MiB/s ETA 00:05
    # Captures the percentage (group 1) and the rest of the info (group 2)
    progress_regex = re.compile(r"\[download]\s+(\d+\.\d+)% of (.*)ETA")

    print(current_theme["prompt"] + "Initiating Secure Data Stream..." + Style.RESET_ALL)

    try:
        # Use subprocess.Popen to run the command and capture the output pipe
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            universal_newlines=True,
            bufsize=1
        )

        for line in iter(process.stdout.readline, ''):
            match = progress_regex.search(line)

            if match:
                percentage = float(match.group(1))
                info = match.group(2).split(' at ')[0]  # Get up to 'at' for cleaner display

                # Create the custom progress bar display
                bar_length = 20
                bar_filled = int(percentage / (100 / bar_length))
                bar = Fore.GREEN + "#" * bar_filled + Fore.RED + "." * (bar_length - bar_filled) + Style.RESET_ALL

                # Use carriage return (\r) to overwrite the current line
                sys.stdout.write(
                    f"\r{current_theme['prompt']}[ {bar} ] {percentage:5.2f}% | {info.strip()}"
                )
                sys.stdout.flush()

        process.wait()

        # Final status message
        if process.returncode == 0:
            print(f"\r{current_theme['prompt']}[ {Fore.GREEN}DOWNLOAD COMPLETE{Style.RESET_ALL} ]" + " " * 80)
        else:
            print(
                f"\r{current_theme['prompt']}[ {Fore.RED}DOWNLOAD FAILED ({process.returncode}){Style.RESET_ALL} ]" + " " * 80)


    except FileNotFoundError:
        print(
            f"\r{current_theme['prompt']}[ {Fore.RED}ERROR:{Style.RESET_ALL} yt-dlp binary not found. Is it installed and in your PATH? ]")
    except Exception as e:
        print(
            f"\r{current_theme['prompt']}[ {Fore.RED}ERROR:{Style.RESET_ALL} An error occurred during download: {e} ]")

def show_banner():
    """Display the welcome banner for the CLI with a bada** look."""
    # Using 'doom' for a strong, blocky, old-school terminal vibe
    banner = pyfiglet.figlet_format("Mr . Searcher", font="doom")

    # Use the current theme's banner color (e.g., Fore.GREEN/WHITE/MAGENTA)
    print(current_theme["banner"] + banner + Style.RESET_ALL)

    print(Fore.RED + ">>> ACCESS GRANTED: MR.SEARCHER v1.4.2.3 <<<" + Style.RESET_ALL)
    print(current_theme["prompt"] + "A non-hostile, terminal-based information retrieval utility." + Style.RESET_ALL)
    print(current_theme["prompt"] + "--------------------------------------------------" + Style.RESET_ALL)
    # --- INSERT THE REAL-TIME SNAPSHOT HERE ---
    snapshot = get_system_snapshot()
    print(current_theme["prompt"] + f"[SYSTEM STATUS: {snapshot} ]" + Style.RESET_ALL)
    print(current_theme["prompt"] + "--------------------------------------------------" + Style.RESET_ALL)
    print(f'{current_theme["prompt"]}Available commands: {formatted_commands}{Style.RESET_ALL}')
    print(current_theme[
              "prompt"] + "Search Filters: {wiki}, {code}, {news}, {youtube} (e.g., {code} python sort list)" + Style.RESET_ALL)
    print(current_theme["prompt"] + "Type 'exit' to terminate session." + Style.RESET_ALL)
    print(current_theme["prompt"] + "--------------------------------------------------" + Style.RESET_ALL)

def show_about():
    """Display information about the CLI and its creator."""
    print(current_theme["prompt"] + "\n=== Mr.Searcher CLI v1.2.0.2===" + Style.RESET_ALL)
    print(current_theme["prompt"] + "A non-hostile, terminal-based information retrieval utility." + Style.RESET_ALL)
    print(current_theme["prompt"] + "Created by: Om Shailesh Vetale" + Style.RESET_ALL)
    print(current_theme["prompt"] + "Powered with DuckDuckGo + yt-dlp + pygame" + Style.RESET_ALL)
    print(current_theme["prompt"] + "Special Easter Eggs included 🎉\n" + Style.RESET_ALL)

def clear_screen():
    """Clear the terminal screen using a robust cross-platform method."""
    if os.name == 'nt':
        # 'nt' is for Windows (usually uses 'cls')
        os.system('cls')
    else:
        # 'posix' is for Linux, macOS, and other Unix-like systems (usually uses 'clear')
        os.system('clear')

    # Note: If this still fails, your execution environment (e.g., certain IDE terminals)
    # may be restricting shell commands. Running it directly from a system terminal
    # (CMD/PowerShell/Bash) is recommended for best results.

def correct_query(query):
    """Correct the spelling of the query using the spell checker."""
    if query.startswith("{") and query.endswith("}"):
        return query
    corrected_words = []
    for word in query.split():
        correction = spell.correction(word)
        corrected_words.append(correction if correction is not None else word)
    return " ".join(corrected_words)

def progressbar(percent):
    """Display a progress bar in the terminal."""
    bar_len = 70
    filled_len = int(round(bar_len * percent))
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write(f"\r[{bar}] {int(percent * 100)}%")
    sys.stdout.flush()

def show_progress():
    """Show a progress animation while searching."""
    for i in range(101):
        progressbar(i / 100)
        time.sleep(0.01)  # faster animation so search doesn’t feel too slow
    print("\nCompleted\n")

def cli_duck_search(action_descriptions=None):
    """Main function to run the CLI searcher."""
    # 🎵 Start background beat immediately with fade-in
    show_banner()
    type_out("Booting up Mr.Searcher system...")
    # --- UPDATED INITIAL PLAY ---
    if audio_enabled:
        load_and_play_track()
        print(current_theme["prompt"] + "Beat is now playing in the background 🎶\n" + Style.RESET_ALL)
    else:
        print(current_theme["prompt"] + "Background audio is disabled.\n" + Style.RESET_ALL)
    # -----------------------------
    while True:
        refresh_music_files()
        query = input(current_theme["prompt"] + "Mr.Searcher> " + Style.RESET_ALL)
        if query.lower() == "exit":
            print(current_theme["prompt"] + "~(>_<。)＼\nBye" + Style.RESET_ALL)
            pygame.mixer.music.fadeout(2000)  # smooth fade-out on exit{
            break

        if query in trigger_words:
            action = trigger_words[query]

            if action == "play":
                print(current_theme["prompt"] + "Alright, dropping your beat 🎶" + Style.RESET_ALL)
                pygame.mixer.music.play(-1, fade_ms=2000)
                continue
            elif action == "pause":
                print(current_theme["prompt"] + "Beat paused ⏸️" + Style.RESET_ALL)
                pygame.mixer.music.pause()
                continue
            elif action == "unpause":
                print(current_theme["prompt"] + "Resuming the beat ▶️" + Style.RESET_ALL)
                pygame.mixer.music.unpause()
                continue
            elif action == "stop":
                print(current_theme["prompt"] + "Beat stopped ⏹️" + Style.RESET_ALL)
                pygame.mixer.music.fadeout(2000)
                continue
            elif action == "next_track":
                next_track()
                continue
            elif action == "previous_track":
                previous_track()
                continue
            elif action == "show_playlist":
                show_playlist()
                continue
            elif action == "set_volume":  # <--- NEW EXECUTION BLOCK
                set_volume()
                continue
            elif action == "matrix_rain":
                matrix_rain()
                continue
            elif action == "show_about":
                show_about()
                continue
            elif action == "show_banner":
                show_banner()
                continue
            elif action == "show_help":
                describe_triggers(helping_words)
                continue
            elif action == "clear_screen":
                clear_screen()
                continue
            elif action == "set_theme":
                set_theme(input("Please enter the theme you want to use: "))
                continue
            elif action == "show_art":
                show_terminal_art()
                continue
            elif action == "get_weather":
                get_weather()
                continue
            elif action == "find_file":
                find_file()
                continue
            elif action == "show_animated_art":
                show_animated_art()
                continue
            elif action == "show_history":
                show_history()
                continue
            elif action == "select_track_by_number":
                select_track_by_number()
                continue
            elif action == "generate_art_from_text":
                generate_art_from_text()
                continue
            elif action == "manage_todo_list":
                manage_todo_list()
                continue
            elif action == "lookup_address":
                lookup_address()
                continue
            elif action == "get_system_info":  # New block
                get_system_info()
                continue
            elif action == "manage_configuration":  # <--- NEW EXECUTION BLOCK
                manage_configuration()
                continue
            elif action == "get_public_ip":
                get_public_ip()
                continue
            elif action == "generate_qr_code":  # <--- NEW EXECUTION BLOCK
                generate_qr_code()
                continue
            elif action == "fetch_file_by_url":
                if not yt_dlp_enabled:
                    # IMPROVED ERROR MESSAGE
                    print(current_theme["prompt"] + Fore.RED +
                          "Download features are DISABLED." + Style.RESET_ALL)
                    print(current_theme["prompt"] +
                          "Reason: yt-dlp or ffmpeg external binaries are missing." + Style.RESET_ALL)
                    print(current_theme["prompt"] +
                          "Action: Please install them and restart Mr.Searcher (see README for details)." + Style.RESET_ALL)
                    continue

                url = input(current_theme["prompt"] + "Enter file URL to download: " + Style.RESET_ALL).strip()
                # ... (rest of the download logic is unchanged)
                # Use the new dynamic DOWNLOAD_DIR
                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)
                    print(f"Created download directory: {DOWNLOAD_DIR}")

                download_file(url, destination_folder=DOWNLOAD_DIR)
                continue

        corrected_query = correct_query(query)

        if corrected_query != query:
            want_to = input(f"Did you mean: '{corrected_query}'? (y/n): ")
            if want_to.lower() == "y":
                query = corrected_query
        filter_applied = False
        final_query = query
        for prefix, site_filter in SEARCH_FILTERS.items():
            if query.lower().startswith(prefix):
                # Remove the prefix and append the site filter
                search_term = query[len(prefix):].strip()
                final_query = f"{search_term} {site_filter}"
                filter_applied = True
                print(current_theme[
                          "prompt"] + f"Applying filter: Searching for '{search_term}' ONLY on {prefix[1:-1].upper()} sites." + Style.RESET_ALL)
                break

        # If no filter applied, use the original corrected_query
        if not filter_applied:
            final_query = corrected_query

        try:
            urllib.request.urlopen("https://www.duckduckgo.com/", timeout=2)

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))  # consume iterator
                if not results:
                    print("No results found.\n")
                else:
                    print(f"\nTop results for: {query}\n")
                    save_history(query)
                    type_out("\nSearching, please wait... Attempting secure connection.", glitch=True, delay=0.01)
                    show_progress()

                    for i, result in enumerate(results):
                        url = result.get("url") or result.get("href")
                        title = result.get("title", "No title")
                        snippet = result.get("body", "No preview available")

                        latency = "Testing..."
                        host_to_ping = url.split("//")[-1].split("/")[0].split(":")[0]

                        if host_to_ping:
                            latency = ping_host(host_to_ping)

                        snapshot = get_system_snapshot()
                        print(current_theme["prompt"] + f"[SYSTEM STATUS: {snapshot} ]" + Style.RESET_ALL)
                        print(current_theme[
                                  "prompt"] + random.choice(ascii_emotions) + f" {i + 1}. {title}" + f"[{Fore.MAGENTA} Latency: {latency} {Style.RESET_ALL}]" + Style.RESET_ALL)
                        print(f" URL:{url}")
                        print(current_theme["prompt"] + f"   {snippet[:150]}..." + Style.RESET_ALL)

                        # ... (Existing code where you display the search results is above this)
                        #
                        if url and re.search(VIDEO_PATTERN, url, re.IGNORECASE):

                            if not yt_dlp_enabled:
                                print(current_theme[
                                          "prompt"] + "Video download is disabled on this system." + Style.RESET_ALL)
                                continue

                            user_choice = input("\nWould you like to download this video? (y/n): ").lower()
                            if user_choice == "y":
                                mode = input("Download as (1) Video MP4 or (2) Audio MP3? Enter 1/2: ").strip()

                                # Ensure download directory exists
                                if not os.path.exists(DOWNLOAD_DIR):
                                    os.makedirs(DOWNLOAD_DIR)

                                # Initialize variables to prevent the NameError
                                cmd = None
                                expected_ext = None
                                output_path = None

                                # Create the dynamic, OS-agnostic output path
                                output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
                                timestamp_id = int(time.time())

                                if mode == "1":
                                    output_template = os.path.join(DOWNLOAD_DIR, f"%(title)s_{timestamp_id}.%(ext)s")
                                    cmd = (
                                        f'yt-dlp -f bestvideo+bestaudio '
                                        f'--merge-output-format mp4 '
                                        f'--no-warnings '
                                        f'-o "{output_template}" "{url}"'
                                    )
                                    expected_ext = ".mp4"
                                elif mode == "2":
                                    output_template = os.path.join(DOWNLOAD_DIR, f"%(title)s_{timestamp_id}.%(ext)s")
                                    cmd = (
                                        f'yt-dlp -x --audio-format mp3 '
                                        f'--no-warnings '
                                        f'-o "{output_template}" "{url}"'
                                    )
                                    expected_ext = ".mp3"
                                else:
                                    print("Invalid choice, skipping download...")
                                    continue

                                print("Downloading...")
                                execute_download_with_progress(cmd)
                                # --- TRANSCRIPTION INTEGRATION START (FIXED) ---
                                # Use glob for a robust search based on the template pattern.
                                try:
                                    downloaded_file_path = None
                                    # Define the search pattern: look for any file starting with anything (*),
                                    # followed by the timestamp, and ending with the expected extension.
                                    # Example pattern: /path/to/Downloads/*_1701388800.mp4
                                    search_pattern = os.path.join(DOWNLOAD_DIR, f"*_{timestamp_id}{expected_ext}")

                                    # glob.glob returns a list of files matching the pattern.
                                    found_files = glob.glob(search_pattern)

                                    if found_files:
                                        # Assume the first result is the downloaded file (should only be one)
                                        downloaded_file_path = found_files[0]

                                    if downloaded_file_path and whisper_available:
                                        do_transcribe = input(
                                            f"\n{Fore.CYAN}Generate text transcript/subtitles for this file? (y/n): {Style.RESET_ALL}").lower()
                                        if do_transcribe == 'y':
                                            transcribe_media(downloaded_file_path)

                                except Exception as e:
                                    print(
                                        f"\n{Fore.RED}Could not initiate transcription (Error in file search):{Style.RESET_ALL} {e}")
                                # --- TRANSCRIPTION INTEGRATION END ---
                            else:
                                print("Skipping download...")

        except (urllib.error.URLError, socket.timeout) as e:
            print(current_theme[
                      "prompt"] + "Internet or network error:"  + Style.RESET_ALL, e)
            print(current_theme[
                      "prompt"] + random.choice(ascii_emotions) + "\nYou are Offline" + Style.RESET_ALL)
            print(current_theme[
                      "prompt"] + "Available commands in offline: " + formatted_offline_commands + Style.RESET_ALL)

# ... (after all function definitions)
# Setup logging first
setup_logging()
# Run checks and set flags
check_dependencies()
# Load previous history
load_history()
# Start the main application loop
cli_duck_search()