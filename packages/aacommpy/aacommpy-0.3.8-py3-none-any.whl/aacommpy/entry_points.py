import argparse

from aacommpy.dotnetmanagement import check_dotnet_versions
from aacommpy.nugetmanagement import download_aacomm_nuget, download_nuget_exe, aacomm_nuget_version, dotnetfw
from aacommpy.settings import DEFAULT_NET_FRAMEWORK, NET_FRAMEWORK_CHOICES

##########################
# run like this:
# python -m aacommpy.entry_points install
##########################

def download_and_install(version: str = "") -> None:
    # Download nuget.exe
    download_nuget_exe()

    # nuget.exe is fully downloaded, proceed with download_aacomm_nuget()
    # Note: download_aacomm_nuget() already calls dotnetfw() internally
    if version != "":
        download_aacomm_nuget(version)
    else:
        download_aacomm_nuget()

INSTALL     = 'install'
VERSION     = 'version'
UPDATE      = 'update'
DOTNETFW    = 'dotnetfw'

def main() -> None:
    parser = argparse.ArgumentParser(description='Download aacommpy package.')
    parser.add_argument('command', choices=[INSTALL, VERSION, UPDATE, DOTNETFW], help='Choose a command to execute.')
    parser.add_argument('--version', help='Specify version to install/download.')
    parser.add_argument('--netfw', choices=NET_FRAMEWORK_CHOICES, default=DEFAULT_NET_FRAMEWORK, help='Choose the .NET framework version to use.')
    parser.add_argument('--check', action='store_true', help='Check compatibility versions of .NET framework.')
    args = parser.parse_args()

    if args.command == INSTALL:
        if args.version:
            download_and_install(args.version)
        else:
            download_and_install()
    elif args.command == VERSION:
        aacomm_nuget_version()
    elif args.command == UPDATE:
        download_aacomm_nuget(update=True)
    elif args.command == DOTNETFW:
        if args.check:
            check_dotnet_versions()
        else:
            dotnetfw(version=args.netfw)
    else:
        raise RuntimeError(f"Please specify a valid aacommpy argument, i.e. '{INSTALL}'.")

    return None

if __name__ == '__main__':
    main()