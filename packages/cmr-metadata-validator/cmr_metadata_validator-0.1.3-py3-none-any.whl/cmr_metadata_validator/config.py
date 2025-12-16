"""
config.py
This module contains functions for configuration, including certificate path.
"""

import os
from pathlib import Path

PEM_CERT = "PEM_CERT"
DEFAULT_USER_PATH = Path.cwd() / 'cert.pem'

def get_cert_path() -> Path:
    """
    Resolve the certificate path in this priority order:
    1. Environment variable PEM_CERT
    2. Default to current working directory / cert.pem
    returns:
        str: The path to the certificate file.
    """
    env_path = os.getenv(PEM_CERT)
    
    if env_path:
        return str(Path(env_path).expanduser())

    return str(DEFAULT_USER_PATH)


CMR_VALIDATION_REPORTS_PATH = "CMR_VALIDATION_REPORTS_PATH"
def get_cmr_validation_reports_path() -> Path:
    """
    Get the path to the CMR validation reports directory.
    returns:
        Path: The path to the CMR validation reports directory.
    """
    env_path = os.getenv(CMR_VALIDATION_REPORTS_PATH)   
    if env_path:
        return Path(env_path).expanduser()

    return Path.cwd() / 'cmr_validation_reports'
