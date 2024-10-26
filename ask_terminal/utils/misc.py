from functools import wraps
import asyncio
from typing import Union, Coroutine, Any

def auto_async(func):
  if func is None:
    return None

  @wraps(func)
  async def wrapper(*args, **kwargs):
    ret = func(*args, **kwargs)
    if asyncio.iscoroutine(ret):
      return await ret
    else:
      return ret

  return wrapper
