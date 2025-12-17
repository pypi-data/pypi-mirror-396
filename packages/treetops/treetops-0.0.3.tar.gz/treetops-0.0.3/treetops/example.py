"""Example module demonstrating package functionality."""

def hello(name: str = "World") -> str:
    """
    Return a greeting message.
    
    Args:
        name: Name to greet (default: "World")
    
    Returns:
        A greeting string
    """
    return f"Hello, {name}!"


def goodbye(name: str = "World") -> str:
    """
    Return a farewell message.
    
    Args:
        name: Name to bid farewell to (default: "World")
    
    Returns:
        A farewell string
    """
    return f"Goodbye, {name}!"


def welcome(name: str = "World") -> str:
    """
    Return a welcome message.
    
    Args:
        name: Name to welcome (default: "World")
    
    Returns:
        A welcome string
    """
    return f"Welcome, {name}!"
