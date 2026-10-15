import asyncio
import random

def retry_with_backoff(exception = Exception, max_attempts: int =3, back_off = 1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                
                except exception as e:
                    print(f"Retrying {func.__name__} : {i}/{max_attempts}")
                    await asyncio.sleep(delay= back_off * 0.25 * (2 * random.random() - 1))
                    if (i==max_attempts-1):
                        raise e
                    
        return wrapper
    return decorator
    
                
                
# *args = positional arguments, **kwargs = keyword arguments. 
# They capture whatever arguments get passed to the wrapped function so you can forward them along.
