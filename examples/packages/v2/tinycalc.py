def add(a, b):
    """An intentional breaking change: only integers are accepted."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError('add() now requires integers')
    return a + b
