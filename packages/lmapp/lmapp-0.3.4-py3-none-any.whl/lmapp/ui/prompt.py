
from rich.prompt import Confirm
from lmapp.core.config import get_config

def confirm(question: str, default: bool = True) -> bool:
    """
    Ask for confirmation, respecting the global assume_yes flag.
    
    Args:
        question: The question to ask
        default: Default answer (True=Yes, False=No)
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    config = get_config()
    if config.assume_yes:
        return True
        
    return Confirm.ask(question, default=default)
