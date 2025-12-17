def calculate_total_cost(items):
    """
    Calculate the total cost of items in the shopping cart.
    Each item is a dictionary with 'price' and 'quantity' keys.
    """
    total = 0
    for item in items:
        # FIX: Multiply price by quantity to calculate correct total
        total += item['price'] * item['quantity']
    return total