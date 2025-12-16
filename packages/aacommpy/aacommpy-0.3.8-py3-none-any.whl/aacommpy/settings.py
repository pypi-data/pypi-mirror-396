import os

# .NET framework versions supported by AAComm nuget package
NET48                   = 'net48'
NET60                   = 'net6.0'
NET80                   = 'net8.0'

NET_FRAMEWORK_CHOICES   = [NET48, NET60, NET80]
TARGET_FRAMEWORKS       = ["4.8", "6.0", "8.0"]
DEFAULT_NET_FRAMEWORK   = NET48

TARGET_FOLDER           = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main')
NUGET_EXE               = 'nuget.exe'
NUGET_EXE_PATH          = os.path.join(TARGET_FOLDER, NUGET_EXE)

# nuget dependencies
YAML_DOT_NET            = 'YamlDotNet'
SYSTEM_IO_PORTS         = 'System.IO.Ports'

AGITO_AACOMM            = 'Agito.AAComm'
AACOMM_DLL              = 'AAComm.dll'
AACOMMSERVER            = 'AACommServer'

# Dynamic paths - computed at runtime relative to this module
_MODULE_DIR             = os.path.dirname(__file__)
AACOMM_DLL_PATH         = os.path.join(_MODULE_DIR, AACOMM_DLL)
AACOMM_SERVER_EXE_PATH  = os.path.join(_MODULE_DIR, f'{AACOMMSERVER}.exe')