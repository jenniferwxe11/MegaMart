REGISTRY = {}


def register(name: str):
    """
    Decorator to register data generator functions.
    """

    def wrapper(fn):
        REGISTRY[name] = fn
        return fn

    return wrapper
