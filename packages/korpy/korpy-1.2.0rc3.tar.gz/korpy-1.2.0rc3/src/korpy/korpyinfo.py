"""
a module to give information about korpy
"""
import requests

def get_release_note() -> str:
    """
    gets korpy's release notes by .rst format
    """
    url = "https://raw.githubusercontent.com/MatthewKim12/korpy/main/HISTORY.rst"
    response = requests.get(url, headers={"User-Agent": "KorPy/1.0"})
    response.raise_for_status()
    return response.text.strip()