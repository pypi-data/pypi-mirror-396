"""
Auralis Worker - Distributed AI Compute Platform
"""

__version__ = "0.1.0"
__author__ = "Auralis Team"

from .worker import AuralisWorker
from .job_runner import JobRunner

__all__ = ["AuralisWorker", "JobRunner", "__version__"]
