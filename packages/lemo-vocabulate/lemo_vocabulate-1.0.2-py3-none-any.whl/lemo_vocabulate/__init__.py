"""
LEMO Vocabulate - Dictionary-based text analysis tool using Python.
"""

from .core import run_vocabulate_analysis
from pathlib import Path

def get_data_path(filename):
    """
    Get the full path to a data file included with the package.
    
    Parameters:
    -----------
    filename : str
        Name of the data file (e.g., 'AEV_Dict.csv', 'stopwords.txt')
    
    Returns:
    --------
    str : Full path to the data file
    
    Examples:
    ---------
    >>> from lemo_vocabulate import get_data_path
    >>> dict_path = get_data_path("AEV_Dict.csv")
    >>> stopwords_path = get_data_path("stopwords.txt")
    """
    package_dir = Path(__file__).parent
    data_path = package_dir / 'data' / filename
    
    if not data_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {filename}\n"
            f"Expected location: {data_path}\n"
            f"Available files: {list((package_dir / 'data').glob('*')) if (package_dir / 'data').exists() else 'data directory not found'}"
        )
    
    return str(data_path)

__version__ = "1.0.2" # update version number as needed
__all__ = ['run_vocabulate_analysis', 'get_data_path']