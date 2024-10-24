#!/usr/bin/env python3
""" Redis exercise

This module contains functions and a class for storing and retrieving data
from a Redis database. The functions are decorated to count the number of
times they are called and to store the inputs and outputs of each call in
Redis. The class provides methods for storing and retrieving data in Redis.
"""
import redis
from uuid import uuid4
from functools import wraps
from typing import Any, Callable, Optional, Union


def count_calls(method: Callable) -> Callable:
    """Count the number of times a method is called

    This decorator increments a counter in Redis each time the decorated
    method is called.

    Args:
        method: The method to be decorated

    Returns:
        The decorated method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Store the inputs and outputs of a method in Redis

    This decorator stores the inputs and outputs of the decorated method in
    Redis each time the method is called.

    Args:
        method: The method to be decorated

    Returns:
        The decorated method
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        input = str(args)
        self._redis.rpush(f"{method.__qualname__}:inputs", input)

        output = str(method(self, *args, **kwargs))
        self._redis.rpush(f"{method.__qualname__}:outputs", output)

        return output
    return wrapper


def replay(fn: Callable) -> None:
    """Replay the history of a function

    This function replays the history of a function by retrieving the inputs
    and outputs from Redis and printing them to the console.

    Args:
        fn: The function to replay the history of
    """
    client = redis.Redis()
    calls = client.get(fn.__qualname__).decode('utf-8')
    inputs = [input.decode('utf-8') for input in
              client.lrange(f'{fn.__qualname__}:inputs', 0, -1)]
    outputs = [output.decode('utf-8') for output in
               client.lrange(f'{fn.__qualname__}:outputs', 0, -1)]
    print(f'{fn.__qualname__} was called {calls} times:')
    for input, output in zip(inputs, outputs):
        print(f'{fn.__qualname__}(*{input}) -> {output}')


class Cache:
    """Cache class

    This class provides methods for storing and retrieving data in Redis.
    """

    def __init__(self) -> None:
        """Initialize the Cache class

        This method initializes the Cache class by creating a Redis client
        and flushing the Redis database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes,  int,  float]) -> str:
        """Store data in Redis

        This method stores data in Redis and returns a unique key for the
        data.

        Args:
            data: The data to be stored

        Returns:
            A unique key for the data
        """
        key = str(uuid4())
        client = self._redis
        client.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Any:
        """Retrieve data from Redis

        This method retrieves data from Redis and returns it. If a function is
        provided, it will be called on the retrieved data.

        Args:
            key: The key of the data to be retrieved
            fn: An optional function to be called on the retrieved data

        Returns:
            The retrieved data or the result of calling the function on the
            retrieved data
        """
        client = self._redis
        value = client.get(key)
        if not value:
            return
        if fn is int:
            return self.get_int(value)
        if fn is str:
            return self.get_str(value)
        if callable(fn):
            return fn(value)
        return value

    def get_str(self, data: bytes) -> str:
        """Retrieve data from Redis as a string

        Args:
            data: The data to be retrieved

        Returns:
            The retrieved data as a string
        """
        return data.decode('utf-8')

    def get_int(self, data: bytes) -> int:
        """Retrieve data from Redis as an integer

        Args:
            data: The data to be retrieved

        Returns:
            The retrieved data as an integer
        """
        return int(data)
