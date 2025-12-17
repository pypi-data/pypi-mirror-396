import os
import psutil
import logging

def get_system_resources():
    """
    Detects available system resources to determine optimal backend.
    """
    resources = {
        "cpu_count": psutil.cpu_count(logical=True),
        "total_ram": psutil.virtual_memory().total,
        "available_ram": psutil.virtual_memory().available,
        "gpu_available": False,
        "gpu_name": None
    }

    try:
        import torch
        if torch.cuda.is_available():
            resources["gpu_available"] = True
            resources["gpu_name"] = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    
    return resources

def get_optimal_backend():
    """
    Decides whether to use 'numpy' or 'torch'/'cupy' based on availability.
    """
    resources = get_system_resources()
    if resources["gpu_available"]:
        return "torch"  # Prefer PyTorch if GPU is present
    return "numpy"
