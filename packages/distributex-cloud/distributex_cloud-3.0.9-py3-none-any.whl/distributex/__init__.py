"""
DistributeX Python SDK
======================
Distributed computing platform for running code on a global pool of resources.

Quick Start:
    from distributex import DistributeX
    
    dx = DistributeX(api_key="your_api_key")
    result = dx.run(my_function, args=(data,), workers=4, gpu=True)

Documentation:
    https://distributex.cloud/
"""

from .client import DistributeX, Task

__version__ = "3.0.9"
__author__ = "DistributeX Team"
__all__ = ["DistributeX", "Task"]
