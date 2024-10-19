import asyncio

def auto_async(func):
  if func is None:
    return None

  if asyncio.iscoroutinefunction(func):
    return func

  async def wrapper(*args, **kwargs):
    return func(*args, **kwargs)

  return wrapper
