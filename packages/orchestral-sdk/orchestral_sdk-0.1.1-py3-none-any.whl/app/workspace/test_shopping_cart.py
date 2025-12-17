import pytest
from shopping_cart import calculate_total_cost

def test_calculate_total_cost():
    # Test case with multiple items
    cart_items = [
        {'name': 'Apple', 'price': 0.50, 'quantity': 3},
        {'name': 'Banana', 'price': 0.25, 'quantity': 4}
    ]
    
    # The correct total should be (0.50 * 3) + (0.25 * 4) = 1.50 + 1.00 = 2.50
    assert calculate_total_cost(cart_items) == 2.50, "Total cost calculation is incorrect"