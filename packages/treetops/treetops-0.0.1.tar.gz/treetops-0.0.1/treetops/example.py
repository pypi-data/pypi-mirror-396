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
