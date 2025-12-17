def calculate_area(length, width):
    """Calculate the area of a rectangle with error checking."""
    if length < 0 or width < 0:
        raise ValueError("Dimensions must be non-negative")
    return length * width

def calculate_perimeter(length, width):
    """Calculate the perimeter of a rectangle."""
    return 2 * (length + width)

if __name__ == "__main__":
    print("Area of 5x3 rectangle:", calculate_area(5, 3))
    print("Perimeter of 5x3 rectangle:", calculate_perimeter(5, 3))