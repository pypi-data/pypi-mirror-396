"""
file_operations.py
This module contains functions for file operations, such as writing to CSV.
"""

import csv
import re
from pathlib import Path
from cmr_metadata_validator.config import get_cmr_validation_reports_path

def calculate_validation_percentage(results):
    """
    Calculates the percentage of validated_result conceptIds with 'No Errors' or 'Warning'
    against the unique 'Error' validated_result.

    Args:
        results (list): A list of tuples containing validation results.

    Returns:
        float: The percentage of 'No Errors' or 'Warning' results against unique 'Error' results.
    """
    error_conceptIds = set()
    no_error_warning_count = 0
    total_count = 0

    for item, _, validated_result, _ in results:
        conceptId = item.get('conceptId', '')
        total_count += 1

        if 'errors' in validated_result:
            error_conceptIds.add(conceptId)
        elif 'warnings' in validated_result or 'no_errors' in validated_result:
            no_error_warning_count += 1

    unique_error_count = len(error_conceptIds)
    if unique_error_count == 0:
        return 100.0  # If there are no errors, return 100%

    percentage = (no_error_warning_count / (no_error_warning_count + unique_error_count)) * 100
    return round(percentage, 2)

def write_to_csv(csv_file, results, percent):
    """
    Writes validation results to a CSV file.

    Args:
        csv_file (str): The name of the CSV file to write the results to.
        results (list): A list of tuples containing validation results.

    The CSV file will have the following columns:
    - provider
    - conceptId
    - nativeId
    - ShortName
    - Version
    - collectionProgress
    - granule counts
    - Public or Private Collection
    - Issue Type (Error or Warning)
    - Error/Warning Path
    - Error/Warning Message
    """
    # Get the reports directory path and ensure it exists
    reports_dir = get_cmr_validation_reports_path()
    # Convert to Path if it's a string (from env var) or use as-is if already Path
    if isinstance(reports_dir, str):
        reports_dir = Path(reports_dir)
    
    # Create the reports directory if it doesn't exist
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Construct the full path by joining the reports directory with the filename
    csv_path = reports_dir / csv_file
    
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "provider", "conceptId", "nativeId", "ShortName", "Version", "collectionProgress",
            "granule counts", "Public or Private Collection", "Issue Type",
            "Error/Warning Path", "Error/Warning Message"
        ])
        for item, record_public_or_private, validated_result, granules_count in results:

            if 'errors' in validated_result:
                issue_type = 'Error'
                issues = validated_result['errors']
            elif 'warnings' in validated_result:
                issue_type = 'Warning'
                issues = validated_result['warnings']
            elif 'no_errors' in validated_result:
                issue_type = 'No Errors'
                error_path = 'Good Collection'
                issues = [validated_result['no_errors']]
            else:
                continue

            for issue in issues:
                error_path = ''
                if isinstance(issue, dict) and 'path' in issue:
                    error_path = ' > '.join(map(str, issue['path']))
                    error_path = re.sub(r'\s*>\s*\d+', '', error_path)
                    error_path = re.sub(r'Platforms > ', '', error_path)
                elif issue_type == 'No Errors':
                    error_path = 'Good Collection'

                if isinstance(issue, dict):
                    error_messages = issue.get('errors', [issue.get('message', '')])
                else:
                    error_messages = [str(issue)]

                for error_message in error_messages:
                    writer.writerow([
                        item.get('provider', ''),
                        item.get('conceptId', ''),
                        item.get('nativeId', ''),
                        item.get('ShortName', ''),
                        item.get('Version', ''),
                        item.get('collectionProgress', ''),
                        granules_count,
                        record_public_or_private,
                        issue_type,
                        error_path,
                        error_message
                    ])
        # Append the percent value to the last line
        writer.writerow(
            [f"Validation {item.get('provider', '')} Collections Percentage: {percent:.2f}%"]
            )
