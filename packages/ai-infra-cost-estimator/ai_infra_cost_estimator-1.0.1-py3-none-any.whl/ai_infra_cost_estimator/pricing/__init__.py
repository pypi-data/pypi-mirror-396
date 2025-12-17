"""
Pricing data module for AI Infrastructure Cost Estimation.
"""

import importlib.resources
import json
from typing import Dict, Any


def get_pricing_file_path() -> str:
    """
    Get the path to the bundled pricing data file.
    
    Returns:
        Path to the models.json file
    """
    try:
        # Python 3.9+
        with importlib.resources.files('ai_infra_cost_estimator.pricing').joinpath('models.json') as path:
            return str(path)
    except AttributeError:
        # Fallback for older Python versions
        import pkg_resources
        return pkg_resources.resource_filename('ai_infra_cost_estimator.pricing', 'models.json')


def load_pricing_data() -> Dict[str, Any]:
    """
    Load pricing data from the bundled JSON file.
    
    Returns:
        Dictionary containing pricing data
    """
    pricing_path = get_pricing_file_path()
    with open(pricing_path, 'r') as f:
        return json.load(f)


__all__ = ['get_pricing_file_path', 'load_pricing_data']
