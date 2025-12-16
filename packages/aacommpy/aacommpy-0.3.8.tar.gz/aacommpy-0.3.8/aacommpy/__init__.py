from .settings import AACOMM_DLL_PATH, AACOMM_SERVER_EXE_PATH

# Re-export commonly used classes for convenience
# Usage: from aacommpy import CommAPI, Services, Shared
try:
    from .AAComm import CommAPI, Services, Shared
    __all__ = ['AACOMM_DLL_PATH', 'AACOMM_SERVER_EXE_PATH', 'CommAPI', 'Services', 'Shared']
except ImportError:
    # AAComm not installed yet - only export settings
    __all__ = ['AACOMM_DLL_PATH', 'AACOMM_SERVER_EXE_PATH']
