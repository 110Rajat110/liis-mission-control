"""
Error handling utilities for LIIS application.
Provides decorators and functions for safe data generation and processing.
"""
import streamlit as st
import logging
from functools import wraps
from typing import Callable, Any, Optional
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def safe_cache(func: Callable) -> Callable:
    """
    Decorator that wraps Streamlit cached functions with error handling.
    Catches exceptions and displays user-friendly error messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Optional[Any]:
        try:
            result = func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except MemoryError as e:
            logger.error(f"Memory error in {func.__name__}: {str(e)}")
            st.error("🚨 Memory Error: Data too large. Try reducing resolution.")
            return None
        except ValueError as e:
            logger.error(f"Value error in {func.__name__}: {str(e)}")
            st.error(f"🚨 Data Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            st.error(f"🚨 Error generating data: {str(e)}")
            return None
    
    return wrapper


def validate_array(arr: np.ndarray, name: str = "array") -> bool:
    """
    Validate numpy array for common issues.
    
    Args:
        arr: Array to validate
        name: Name of the array for error messages
        
    Returns:
        True if valid, False otherwise
    """
    if arr is None:
        logger.error(f"{name} is None")
        return False
    
    if not isinstance(arr, np.ndarray):
        logger.error(f"{name} is not a numpy array")
        return False
    
    if np.any(np.isnan(arr)):
        logger.warning(f"{name} contains NaN values")
        return False
    
    if np.any(np.isinf(arr)):
        logger.warning(f"{name} contains infinite values")
        return False
    
    return True


def validate_terrain_data(X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> bool:
    """
    Validate terrain data arrays.
    
    Args:
        X, Y, Z: Terrain coordinate arrays
        
    Returns:
        True if valid, False otherwise
    """
    if not (validate_array(X, "X") and validate_array(Y, "Y") and validate_array(Z, "Z")):
        return False
    
    if X.shape != Y.shape or X.shape != Z.shape:
        logger.error(f"Shape mismatch: X={X.shape}, Y={Y.shape}, Z={Z.shape}")
        return False
    
    return True


def validate_resolution(resolution: int, min_res: int = 128, max_res: int = 512) -> bool:
    """
    Validate resolution parameter.
    
    Args:
        resolution: Resolution value to validate
        min_res: Minimum allowed resolution
        max_res: Maximum allowed resolution
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(resolution, int):
        logger.error(f"Resolution must be integer, got {type(resolution)}")
        return False
    
    if resolution < min_res or resolution > max_res:
        logger.error(f"Resolution {resolution} out of range [{min_res}, {max_res}]")
        return False
    
    return True


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division that handles division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division fails
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            logger.warning("Division by zero, returning default")
            return default
        return numerator / denominator
    except Exception as e:
        logger.error(f"Division error: {str(e)}")
        return default


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))
