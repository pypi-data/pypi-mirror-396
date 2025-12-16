import warnings
from .error_handler import ErrorHandler

whitelisted_commands = [
    "RERUN",
    "SEND",
    "EXTRACT",
    "LOAD_IMAGE",
    "CHOOSE_MODEL",
    "CHOOSE_EXTRACTION_MODEL",
    "CURRENT_MODEL",
    "CURRENT_EXTRACTION_MODEL",
    "LIST_MODELS",
]

error_handler = ErrorHandler()


# ANSI escape codes for coloring
YELLOW = "\033[93m"
RESET = "\033[0m"


def format_warning(message, category, *args, **kwargs):
    return f"{YELLOW}[WARNING] {category.__name__}: {message}{RESET}\n"


warnings.formatwarning = format_warning

### CHAT VALUES ###

CATEGORY_CHAT_CONTROL = "Chat control commands"
CATEGORY_LLM_CONTROL = "Language model controls"
CATEGORY_SCRIPT_CONTROL = "Script control commands"
CATEGORY_AGENT_CONTROL = "Agent control commands"

ROLE_PROMPT = "ara prompt"
ROLE_RESPONSE = "ara response"

INTRO = """/***************************************/
                 araarar
               aa       ara
             aa    aa   aara
             a        araarar
             a        ar  ar
           aa          ara
          a               a
          a               aa
           a              a
   ar      aa           aa
    (c) ara chat by talsen team
              aa      aa
               aa    a
                a aa
                 aa
/***************************************/
Start chatting (type 'HELP'/'h' for available commands, 'QUIT'/'q' to exit chat mode):"""

BINARY_TYPE_MAPPING = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

DOCUMENT_TYPE_EXTENSIONS = [".docx", ".doc", ".odt", ".pdf"]


# Chat available agents
AVAILABLE_AGENTS = [
    "interview_agent",
    "autocoder_v2_agent",
    "question_and_answer_agent",
    "feature_creation_guide_agent",
]
