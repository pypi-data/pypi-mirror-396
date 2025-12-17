def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a given text."""
    return word_count_heuristic(text)


def word_count_heuristic(text: str) -> int:
    """A simple heuristic to estimate token count based on word count."""
    words = text.split()
    return len(words) * 1.333  # type: ignore # Assume average of 4 words per 3 tokens


def character_count_heuristic(text: str) -> int:
    """A simple heuristic to estimate token count based on character count."""
    return len(text) / 4  # type: ignore # Assume average of 4 characters per token