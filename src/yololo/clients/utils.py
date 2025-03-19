import requests
from typing import Union


def request_content_no_interrupt(url: str) -> Union[None, str]:
    res = None
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        res = response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching feed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return res
