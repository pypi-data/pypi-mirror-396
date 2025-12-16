import clr
import os
from aacommpy.category import categories
from aacommpy.settings import AACOMM_DLL_PATH

def _auto_install_aacomm():
    """Automatically install AAComm NuGet package if not found."""
    print("AAComm not found. Installing AAComm NuGet package...")
    from aacommpy.nugetmanagement import download_nuget_exe, download_aacomm_nuget
    download_nuget_exe()
    download_aacomm_nuget()
    print("AAComm installation complete.")

if not os.path.isfile(AACOMM_DLL_PATH):
    _auto_install_aacomm()

if os.path.isfile(AACOMM_DLL_PATH):
    clr.AddReference(AACOMM_DLL_PATH)
    for category in categories:
        if category["enable"]:
            exec(f"from {category['from']} import {category['name']}")
    __all__ = [category["name"] for category in categories if category["enable"]]
else:
    raise RuntimeError("AAComm installation failed. Please run 'aacommpy install' manually.")
