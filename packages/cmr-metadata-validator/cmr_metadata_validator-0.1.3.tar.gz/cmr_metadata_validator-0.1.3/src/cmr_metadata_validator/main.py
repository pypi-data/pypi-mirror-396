"""
main.py

This script serves as the entry point for the NASA Earthdata metadata validation tool.
It orchestrates the process of fetching, validating, and recording metadata for
NASA Earth Science collections into a CSV file.

Key functionalities:
1. Retrieves a list of available providers from the NASA CMR API.
2. Parses command-line arguments to determine the configuration (provider or consortium).
3. Generates an authentication token for API access.
4. Constructs and executes a CMR API query to fetch collections using a specified date range.
5. Processes each collection item, including:
   - Checking if the record is publicly accessible
   - Validating the record using the CMR Ingest API's validation feature
   - Retrieving the granule count for each collection
6. Writes the validation results and associated information to a CSV file.

The script handles pagination for large datasets and implements error handling and 
retry mechanisms for robust execution. It utilizes parallel processing to efficiently
handle multiple records simultaneously.

Usage:
    python main.py --provider <provider_name> [--start_date <YYYY-MM-DD>] [--end_date <YYYY-MM-DD>]
    or
    python main.py --consortium <consortium_name> [--start_date <YYYY-MM-DD>] [--end_date <YYYY-MM-DD>]

Dependencies:
    - api_utils.py: Contains utility functions for API interactions
    - validation.py: Includes functions for validating collection records
    - file_operations.py: Handles file operations like writing to CSV
    - data_processing.py: Contains functions for data processing and parallel execution

Note: This script requires proper setup for authentication (cert.pem file) and
      assumes access to the necessary NASA Earthdata APIs.

Author: Michael Morahan
Creation Date: 2025-08-08
Update date: 2025-11-14
Version: 1.2
"""

from datetime import datetime
from cmr_metadata_validator.api_utils import (
    get_provider_list, scripts_ingest_arguments, launchpad_token_cert, fetch_and_save_data
)
from cmr_metadata_validator.file_operations import (
    calculate_validation_percentage, write_to_csv
)
from cmr_metadata_validator.data_processing import records_pool

def main():
    """
    Main function to execute the NASA Earthdata metadata validation process.
    """
    print("Starting script...")

    # Gathers list of CMR Providers and/or Consortiums
    providers = get_provider_list()
    consortiums = {'EOSDIS', 'CWIC', 'CEOS', 'GEOSS', 'FEDEO'}
    start_date = "2000-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    config_type, config_value, start_date, end_date = scripts_ingest_arguments(
        providers, consortiums, start_date, end_date)

    if config_type == 'provider' and config_value not in providers:
        print(f"Warning: The selected provider '{config_value}' is not in the "
              f"list of available providers.")
        print("Available providers:", ', '.join(providers))

    print(f"Selected {config_type}: {config_value}")
    print(f"Date range: {start_date} to {end_date}")

    token = launchpad_token_cert()
    print(token[:128])

    cmr_endpoint = (
        'https://cmr.earthdata.nasa.gov/search/collections.umm_json'
        f'?created_at={start_date},{end_date}'
    )
    params = {
        config_type: config_value,
        'page_size': 2000,
        'pretty': 'true'
    }
    print(f"API Endpoint: {cmr_endpoint}")
    print(f"Params: {params}")

    all_items = fetch_and_save_data(cmr_endpoint, params, launchpad_token_cert)
    print(f"Number of items to process for {config_value}: {len(all_items)}")
    print(all_items)

    if not all_items:
        print("No items were fetched. Exiting the program.")
        return

    print(f"Number of items fetched: {len(all_items)}")

    results = records_pool(all_items, token, launchpad_token_cert)
    percent = calculate_validation_percentage(results)
    print(f"Validation {config_value} Collections Percentage: {percent:.2f}%")

    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"{config_value}_collections_{current_datetime}-{start_date}_{end_date}.csv"

    write_to_csv(csv_file, results, percent)

    print(f"Data successfully written to {csv_file}")
    print("Script execution completed.")

if __name__ == "__main__":
    main()
