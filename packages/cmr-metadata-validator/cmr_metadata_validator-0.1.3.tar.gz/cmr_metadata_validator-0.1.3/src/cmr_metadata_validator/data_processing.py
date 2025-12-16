"""
data_processing.py
This module contains functions for processing data, including parallel processing.
"""

from concurrent.futures import ProcessPoolExecutor
import concurrent
import sys
from typing import List, Tuple, Optional, Callable
import requests
from cmr_metadata_validator.api_utils import get_record_public, get_granules
from cmr_metadata_validator.validation import validate_a_record

def records_pool(
        all_items: List[dict],
        token: str,
        get_token: Callable[[], str]
        ) -> List[Tuple[dict, bool, dict, int]]:
    """
    Process a list of items in parallel using a process pool.

    This function takes a list of items and processes them concurrently using a ProcessPoolExecutor.
    It handles token management and error handling during the parallel processing.

    Args:
        all_items (List[dict]): A list of dictionaries containing the items to be processed.
        token (str): The initial authentication token to use for processing.
        get_token (Callable[[], str]): A function that returns a new authentication token
        when called.

    Returns:
        List[Tuple[dict, bool, dict, int]]: A list of processed results. Each result is 
        a tuple containing:
            - The original item dictionary
            - A boolean indicating if the record is public or private
            - The validation result dictionary
            - The count of granules

    The function filters out any None results, which occur when item processing fails.
    Note:
        This function uses a ProcessPoolExecutor with a maximum of 10 workers.
    """
    print('Starting to run pool')
    print(f"Number of items to process: {len(all_items)}")
    results = []

    try:
        # Include the token in the args tuples
        args = [(item, token, get_token) for item in all_items]
        with ProcessPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(worker, *zip(*args)))

    except concurrent.futures.process.BrokenProcessPool as e:
        print(f"BrokenProcessPool error: {e}", file=sys.stderr)
    except concurrent.futures.CancelledError as e:
        print(f"CancelledError: {e}", file=sys.stderr)
    except concurrent.futures.TimeoutError as e:
        print(f"TimeoutError: {e}", file=sys.stderr)

    # Filter out None results
    results = [result for result in results if result is not None]

    return results

def process_item(item: dict, current_token: str) -> Optional[Tuple[dict, bool, dict, int]]:
    """
    Process a single item with the given token.

    Args:
        item (dict): The item to be processed, containing metadata information.
        current_token (str): The authentication token to use.

    Returns:
        Optional[Tuple[dict, bool, dict, int]]: A tuple containing the processed item information,
        or None if processing fails. The tuple contains:
        - The original item dictionary
        - A boolean indicating if the record is public or private
        - The validation result dictionary
        - The count of granules
    """
    try:
        record_public_or_private = get_record_public(item['conceptId'])

        validated_result = validate_a_record(
            item['provider'],
            item['conceptId'],
            item['nativeId'],
            item['metadata_spec_version'],
            current_token
        )

        if validated_result is None:
            print(f"Validation failed for item {item['conceptId']}. Skipping.", file=sys.stderr)
            return None

        granules_count = get_granules(item.get('conceptId', ''), current_token)
        return (item, record_public_or_private, validated_result, granules_count)

    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise  # Re-raise to be caught in the retry loop
        print(f"HTTP error processing item {item['conceptId']}: {e}", file=sys.stderr)
        print(f"Response content: {e.response.content}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"Network error processing item {item['conceptId']}: {e}", file=sys.stderr)
    except ValueError as e:
        print(f"Value error processing item {item['conceptId']}: {e}", file=sys.stderr)
    except KeyError as e:
        print(f"Key error processing item {item['conceptId']}: {e}", file=sys.stderr)
    return None

def worker(
        item: dict,
        token: str, get_token: Callable[[], str]
        ) -> Optional[Tuple[dict, bool, dict, int]]:
    """ 
    Process a single item with retry logic and token refresh capabilities.
    This function attempts to process an item, handling potential authentication issues
    and network errors. It will retry the operation up to a maximum number of times,
    refreshing the authentication token if necessary.

    Args:
        item (dict): The item to be processed, containing metadata information.
        token (str): The initial authentication token to use.
        get_token (Callable[[], str]): A function to call for obtaining a fresh token.

    Returns:
        Optional[Tuple[dict, bool, dict, int]]: A tuple containing the processed item information,
        or None if processing ultimately fails.

    The function will print error messages to stderr for various failure scenarios.
    """
    max_retries = 3
    for retry_count in range(max_retries):
        try:
            return process_item(item, token if retry_count == 0 else get_token())
        except requests.HTTPError as e:
            if e.response.status_code == 401 and retry_count < max_retries - 1:
                print(f"Unauthorized error for item {item['conceptId']}. "
                      f"Retrying with new token...", file=sys.stderr)
                continue
            print(f"Max retries reached for item {item['conceptId']}. Skipping.", file=sys.stderr)
            break

    print(f"Failed to process item {item['conceptId']} after {max_retries} "
          f"attempts.", file=sys.stderr)
    return None
