"""
This module provides functionality to interact with the GKR (GCMD Keyword Recommender) API.

It contains a function to send requests to the GKR API with a given description and retrieve
filtered recommendations of GCMD Science Keyword groupings based on a score threshold. The module is designed to be used for
querying the GKR API with Earth science-related descriptions and obtaining relevant keywords
and concepts.

Note: The present version of the GKR only supports GCMD Science Keyword groupings.
"""
import requests


def run_gkr(input_description, min_score: float = 0.30):
    """
    Send a request to the GKR API with the given description and return filtered recommendations.

    This function sends a POST request to the GKR API with the provided description,
    retrieves recommendations, and filters them based on a score threshold.

    Args:
        input_description (str): The input description to send to the GKR API.
        min_score (float): The minimum score to filter recommendations. Defaults to 0.30.
    Returns:
        dict: A dictionary containing the API response with filtered recommendations.
              The 'recommendations' key contains a list of up to 10 recommendations
              with scores between 0.30 and 1 (inclusive).
    """
    url = 'https://gkr.earthdatacloud.nasa.gov/api/requests/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "model_id": 2,
        "description": input_description,
        "threshold": 0,
        "forced": False,
        "explain": False
    }

    response = requests.post(url, headers=headers, json=payload, timeout=300)
    data = response.json()

    # Filter recommendations to include entries with score between the min_score and 1 (inclusive)
    filtered_recommendations = []
    for rec in data['recommendations']:
        if min_score < rec['score'] <= 1:
            filtered_recommendations.append(rec)
    # Replace the original recommendations with the filtered ones
    data['recommendations'] = filtered_recommendations[:10]
    return data
