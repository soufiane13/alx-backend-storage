#!/usr/bin/env python3
"""
Caching request module

This module provides a decorator, track_get_page, which tracks the number of
times a given URL is requested and caches the response for a short period of
time.
"""
import redis
import requests
from functools import wraps
from typing import Callable


def track_get_page(fn: Callable) -> Callable:
    """
    A decorator to track how many times a given URL is requested and cache the
    response for a short period of time.

    The decorator takes a function as an argument and returns a new function
    which wraps the argument function. The new function will track how many
    times the argument function is called with a given URL and cache the
    response for a short period of time.

    Args:
        fn: The function to decorate.

    Returns:
        A new function which wraps the argument function.
    """
    @wraps(fn)
    def wrapper(url: str) -> str:
        """
        A wrapper function which tracks how many times the argument function is
        called with a given URL and caches the response for a short period of
        time.

        Args:
            url: The URL to request.

        Returns:
            The response from the argument function.
        """
        client = redis.Redis()
        client.incr(f'count:{url}')
        cached_page = client.get(f'{url}')
        if cached_page:
            return cached_page.decode('utf-8')
        response = fn(url)
        client.set(f'{url}', response, 10)
        return response
    return wrapper


@track_get_page
def get_page(url: str) -> str:
    """
    A function which requests a given URL and returns the response.

    Args:
        url: The URL to request.

    Returns:
        The response from the URL.
    """
    response = requests.get(url)
    return response.text
