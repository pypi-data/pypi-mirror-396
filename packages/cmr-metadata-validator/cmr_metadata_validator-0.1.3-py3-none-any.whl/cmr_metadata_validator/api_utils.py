"""
api_utils.py
This module contains utility functions for API interactions.
"""

import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict
import requests
from cmr_metadata_validator.config import get_cert_path

# Global constant for Client-Id
global CLIENT_ID
CLIENT_ID = 'metadata_stewardship_validator'

def get_provider_list():
    """
    Fetches the list of CMR providers from the NASA Earthdata API.
    
    Returns:
        list: A list of provider IDs.
    """
    results = requests.get('https://cmr.earthdata.nasa.gov/ingest/providers', timeout=120)
    results.raise_for_status()  # Raise an exception for HTTP errors
    data = json.loads(results.text)

    # Extract provider IDs based on the actual structure of the response
    if isinstance(data, list):
        provider_ids = [
            provider['provider-id']
            for provider in data
            if 'provider-id' in provider
        ]
    elif isinstance(data, dict) and 'provider-id' in data:
        provider_ids = data['provider-id']
    else:
        raise ValueError("Unexpected response structure from the API.")

    if not provider_ids:
        print("Warning: No providers found. This might cause issues with the API request.")

    return provider_ids

def scripts_ingest_arguments(providers, consortiums, start_date, end_date):
    """
    Parses command-line arguments to select the configuration type and value.

    Args:
        providers (list): List of available provider values.
        consortiums (list): List of available consortium values.

    Returns:
        tuple: A tuple containing (config_type, config_value, start_date, end_date) where:
               config_type is either "provider" or "consortium"
               config_value is the selected provider or consortium name
               start_date is the start date for data ingestion (default: 2000-01-01)
               end_date is the end date for data ingestion (default: current date)

    Raises:
        SystemExit: If the command-line arguments are invalid or not provided.
    """
    parser = argparse.ArgumentParser(
        description="NASA Earthdata metadata validation tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--provider",
        choices=providers,
        help=f"Specify which provider to use: {', '.join(providers)}.")

    parser.add_argument(
        "--consortium",
        choices=consortiums,
        help=f"Specify which consortium to use: {', '.join(consortiums)}.")

    parser.add_argument(
        "--start_date",
        default="2000-01-01",
        help="Start date for the first metadata ingestion of collections "
        "(format: YYYY-MM-DD, default: 2000-01-01).")

    parser.add_argument(
        "--end_date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date for the last metadata ingestion of collections "
        "(format: YYYY-MM-DD, default: current date).")

    args = parser.parse_args()

    if args.provider:
        return "provider", args.provider, args.start_date, args.end_date
    elif args.consortium:
        return "consortium", args.consortium, args.start_date, args.end_date
    else:
        parser.print_help()
        sys.exit(1)

def launchpad_token_cert():
    """
    Generates a Launchpad token using a PEM certificate file.
    Returns:
        str: The generated Launchpad token (sm_token).
    """
    results = requests.get(
        'https://api.launchpad.nasa.gov/icam/api/sm/v1/gettoken',
        cert=get_cert_path(), timeout=180)
    data = json.loads(results.text)
    token = data['sm_token']
    return token

def get_items(json_data: Dict) -> List[Dict]:
    """
    Extracts and processes items from the JSON data returned by the CMR API.

    This function parses the 'items' array from the input JSON data and extracts
    relevant information for each item, creating a list of dictionaries with
    standardized keys.
    Args:
        json_data (Dict): The JSON data returned by the CMR API, expected to
                          contain an 'items' key with an array of item objects.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents an
                    item with the following keys:
                    - provider: The provider ID
                    - conceptId: The concept ID
                    - nativeId: The native ID
                    - ShortName: The ShortName values
                    - Version: The Version values
                    - collectionProgress: The collection progress status
                    - metadataFormat: The metadata format
                    - title: The entry title
                    - metadata_spec_version: The metadata specification version

    Note:
        - The function assumes a specific structure of the input JSON data.
        - Some fields (e.g., 'CollectionProgress' and 'MetadataSpecification')
          are optional and will be set to empty string or None if not present.
    """
    items = []
    for item in json_data['items']:
        meta = item['meta']
        umm = item['umm']

        item_data = {
            'provider': meta['provider-id'],
            'conceptId': meta['concept-id'],
            'nativeId': meta['native-id'],
            'collectionProgress': umm.get('CollectionProgress', ''),
            'metadataFormat': meta['format'],
            'ShortName': umm['ShortName'],
            'Version': umm['Version'],
            'title': umm['EntryTitle'],
            'metadata_spec_version': umm.get('MetadataSpecification', {}).get('Version', '')
        }
        items.append(item_data)
    return items

def fetch_and_save_data(cmr_endpoint, params, get_token):
    """
    Fetches data from the CMR API endpoint and saves it.

    This function makes paginated requests to the CMR API, processes the
    received data, and accumulates all items. It continues fetching until
    all available pages have been retrieved or an error occurs.

    Args:
        cmr_endpoint (str): The URL of the CMR API endpoint.
        params (dict): A dictionary of query parameters for the API request.
        get_token (callable): A function that returns the authorization token.

    Returns:
        List[Dict]: A list of dictionaries containing the fetched and processed items.

    Note:
        - The function uses the 'get_items' helper function to process each page of results.
        - It prints progress and error messages to the console.
        - If no data is fetched, it returns an empty list.
    """
    all_items = []
    page = 1

    token = get_token()
    headers = {
        'Authorization': token,
        'Accept': 'application/json',
        'Client-Id': CLIENT_ID
    }

    while True:
        params['page_num'] = page
        response = requests.get(cmr_endpoint, headers=headers, params=params, timeout=300)
        if response.status_code == 200:
            json_data = response.json()
            items = get_items(json_data)
            all_items.extend(items)

            if len(items) < params['page_size']:
                break
            page += 1
        else:
            print(f"Failed to fetch data for page {page}. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            break
    if all_items:
        print(f"Total items fetched: {len(all_items)}")
    else:
        print("No data was fetched.")

    return all_items

def get_record_public(concept_id):
    """
    Determines if a collection record is publicly accessible from the CMR search API.

    Args:
        concept_id (str): The concept ID of the collection to check.

    Returns:
        str: "Public record" if the record is publicly accessible,
             "Private record" if the record is not publicly accessible.
    """
    url = f'https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}'
    private_json_value = (
        '{"errors":["Concept with concept-id [' + concept_id + '] could not be found."]}')

    private_xml_value = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<errors><error>Concept with concept-id [{concept_id}] '
        f'could not be found.</error></errors>'
    )
    try:
        response = requests.get(url, timeout=180)
        response_text = response.text
        if response_text == private_json_value or response_text == private_xml_value:
            return "Private record"
        else:
            return "Public record"
    except requests.RequestException as e:
        print(f"💣  Error in get_record_public retrieving record {concept_id}: "
              f"{str(e)}", file=sys.stderr)
        return "Error"

def get_record(concept_id, metadata_spec_version, token):
    """
    Retrieves a collection record from the CMR search API using the given concept ID.

    Args:
        concept_id (str): The concept ID of the collection to retrieve.
        token (str): The authorization token for accessing the API.

    Returns:
        str: The collection record in UMM-JSON format if successful, None otherwise.
    """
    url = f'https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}'
    print(f"Retrieving record from URL: {url}")
    headers = {
        'Authorization': token,
        'Accept': f'application/vnd.nasa.cmr.umm+json;version={metadata_spec_version}',
        'Client-Id': CLIENT_ID
    }
    try:
        response = requests.get(url, headers=headers, timeout=180)
        response.raise_for_status()
        record = response.text
        print(f"Successfully retrieved record for {concept_id}")
        return record
    except requests.RequestException as e:
        print(f"💣  Error in get_record retrieving record {concept_id}: {str(e)}", file=sys.stderr)
        return None

def get_granules(concept_id, token):
    """
    Retrieves the granule count for a specified collection from the CMR search API.

    Args:
        concept_id (str): The concept ID of the collection for which to retrieve the granule count.
        token (str): The authorization token for accessing the CMR API.

    Returns:
        int: The number of granules associated with the collection. 
             Returns 0 if unable to retrieve the count.
    """
    url = (f'https://cmr.earthdata.nasa.gov/search/granules.umm_json?'
           f'collection_concept_id={concept_id}&page_size=1')
    print(f"Retrieving granules from URL: {url}")
    headers = {
        'Authorization': token,
        'Accept': 'application/json',
        'Client-Id': CLIENT_ID
    }
    granules_count = 0
    try:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        granules_count = data['hits']
        print(f"Successfully retrieved granule count for {concept_id}: {granules_count}")
    except requests.RequestException as e:
        print(f"💣  Error retrieving granules for {concept_id}: {str(e)}", file=sys.stderr)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"💣  Error parsing response for {concept_id}: {str(e)}", file=sys.stderr)
    except ValueError as e:
        print(f"💣  Unexpected error for get_granule in {concept_id}: {str(e)}", file=sys.stderr)

    return granules_count
