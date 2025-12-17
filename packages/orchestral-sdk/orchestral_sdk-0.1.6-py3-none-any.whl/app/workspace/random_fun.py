import random
import math

def generate_magic_numbers(count=5, max_value=100):
    """
    Generate a list of 'magic' numbers with some interesting properties.
    
    Args:
        count (int): Number of magic numbers to generate
        max_value (int): Maximum value for the magic numbers
    
    Returns:
        list: A list of unique, sorted magic numbers
    """
    magic_numbers = set()
    while len(magic_numbers) < count:
        # Generate a number that is both prime and a perfect square
        num = random.randint(1, max_value)
        if is_prime(num) and is_perfect_square(num):
            magic_numbers.add(num)
    
    return sorted(list(magic_numbers))

def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_perfect_square(n):
    """Check if a number is a perfect square."""
    return int(math.sqrt(n)) ** 2 == n

# Demonstration
if __name__ == "__main__":
    print("Magical numbers generated:", generate_magic_numbers())