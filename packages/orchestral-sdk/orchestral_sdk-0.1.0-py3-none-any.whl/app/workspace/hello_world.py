def greet(name="World"):
    """
    Generate a friendly greeting.
    
    Args:
        name (str, optional): The name to greet. Defaults to 'World'.
    
    Returns:
        str: A personalized greeting message.
    """
    return f"Hello, {name}!"

# Demonstration
if __name__ == "__main__":
    print(greet())
    print(greet("World"))