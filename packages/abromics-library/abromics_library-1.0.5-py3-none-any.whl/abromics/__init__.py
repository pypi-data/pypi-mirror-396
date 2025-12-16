"""
ABRomics Lightweight Python SDK

A lightweight Python SDK for interacting with the ABRomics API.
"""

from .client import AbromicsClient
from .auth.api_key import ApiKeyAuth
from .models.project import Project
from .models.sample import Sample
from .models.experiment import Experiment
from .models.template import Template
from .upload.tus_client import TusUploader
from .batch.processor import BatchProcessor
from .exceptions import AbromicsAPIError, AbromicsUploadError, AbromicsAuthenticationError

__version__ = "1.0.5"
__author__ = "ABRomics Team"

__all__ = [
    "AbromicsClient",
    "ApiKeyAuth", 
    "Project",
    "Sample",
    "Experiment",
    "Template",
    "TusUploader",
    "BatchProcessor",
    "AbromicsAPIError",
    "AbromicsUploadError", 
    "AbromicsAuthenticationError",
]
