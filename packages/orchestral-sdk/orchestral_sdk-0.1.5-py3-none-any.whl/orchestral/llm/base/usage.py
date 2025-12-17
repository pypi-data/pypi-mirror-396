from typing import Dict


class PricingModel:
    """Base class for pricing models.

    Pricing is defined as a mapping from token type -> rate in USD per million tokens.
    """

    def __init__(self, rates: Dict[str, Dict[str, float]]):
        self.rates = rates

    def get_cost(self, tokens: Dict[str, int], model_name: str) -> float:
        """Compute the cost for a set of token tokens."""
        total = 0.0
        # Try to get rates for the specific model, fall back to 'default' if not found
        rates = self.rates.get(model_name, self.rates.get('default', {}))
        for token_type, count in tokens.items():
            rate = rates.get(token_type)
            if rate is not None:
                total += (count / 1_000_000) * rate
        return total


class Usage:
    """Tracks usage for a single model response and its cost."""

    def __init__(self, model_name: str,
                 tokens: Dict[str, int],
                 cost: float):
        """
        Args:
            model_name: The model name (e.g. "gpt-4o-mini").
            tokens: Mapping of token type -> count (e.g. {"input": 1200, "output": 300}).
            cost: The cost of this usage in USD.
        """
        self.model_name = model_name
        self.tokens = tokens
        self.cost = cost

    def get_cost(self) -> float:
        """Return the cost of this usage in USD."""
        return self.cost

    def __repr__(self):
        return f"Usage(total_cost=${self.get_cost():.6f}, tokens={self.tokens})"
    
    def to_dict(self):
        return {
            "model_name": self.model_name,
            "tokens": self.tokens,
            "cost": self.get_cost()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            model_name=data["model_name"],
            tokens=data["tokens"],
            cost=data.get("cost", 0.0),
        )