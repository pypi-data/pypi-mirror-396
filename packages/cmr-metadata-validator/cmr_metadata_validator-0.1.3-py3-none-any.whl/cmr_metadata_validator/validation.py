"""
validation.py
This module contains functions for validating collection records.
"""

import json
import time
import subprocess
import sys
import requests
from cmr_metadata_validator.api_utils import get_record

def validate_a_record(provider, concept_id, native_id, metadata_spec_version, token):
    """
    Validates a collection record using the CMR validation API.

    Args:
        provider (str): The provider name.
        concept_id (str): The concept ID of the collection.
        native_id (str): The native ID of the collection.
        token (str): The authorization token for accessing the API.

    Returns:
        dict: A dictionary containing validation results.
    """
    try:
        time.sleep(1)
        data = get_record(concept_id, metadata_spec_version, token)

        headers = {
            'Content-Type': f'application/vnd.nasa.cmr.umm+json;version={metadata_spec_version}',
            'Cmr-Validate-Keywords': 'true',
            'Accept': 'application/json',
            'Client-Id': 'metadata_stewardship_validator'
            }
        print (headers)
        # Validate that data is not empty
        if not data:
            raise ValueError(f"No data retrieved for collection: {native_id}")

        url_format = ("https://cmr.earthdata.nasa.gov"
                      "/ingest/providers/{}/validate/collection/{}")
        url = url_format.format(provider, concept_id)
        print ("Validated record url: " + url)
        # Make the POST request
        validating = requests.post(url, headers=headers, data=data.encode('utf-8'), timeout=300)
        if len(validating.text) < 1:
            if validating.status_code == 200:
                return {"no_errors": "Empty response with status code 200"}
            else:
                return {"errors": [f"💣  Validation request failed with status code: "
                                   f"{validating.status_code}"]}
        validation_results = json.loads(validating.text)
        return validation_results
    except requests.RequestException as e:
        print (
            f"💣  Error on request validating record: "
            f"{native_id} {concept_id} {e}",
            file=sys.stderr
        )
        return {"💣  errors": [f"Request error: {str(e)}"]}
    except ValueError as e:
        print (
            f"💣  Error ValueError validating record: "
            f"{native_id} {concept_id} {e}",
            file=sys.stderr
        )
        print ("done")
        return {"errors": [str(e)]}
    except Exception as e:
        print (
            f"💣  Unexpected error validating record: "
            f"{native_id} {concept_id} {e}",
            file=sys.stderr
        )
        if 'data' in locals():
            print(data, file=sys.stderr)
            try:
                subprocess.run(
                    ['jq', '.', '-e'],
                    input=data.encode(),
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"Data for {native_id} is valid JSON according to jq.")
            except subprocess.CalledProcessError as jq_error:
                print(
                    f"💣  Error: Data for {native_id} "
                    f"is not valid JSON according to jq.",
                    file=sys.stderr
                )
                print(f"jq error: {jq_error.stderr.strip()}", file=sys.stderr)
                return {"💣  errors": [f"Invalid JSON: {jq_error.stderr.strip()}"]}
        return {"💣  errors": [f"Unexpected error: {str(e)}"]}
