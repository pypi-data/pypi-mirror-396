from functools import wraps

def ui_component(func):
    """Decorador para crear componentes de manera súper fácil"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
