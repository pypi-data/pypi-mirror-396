import os
import shutil
import subprocess
import threading
import time
import requests
import zipfile
import xml.etree.ElementTree as ET

from aacommpy.settings import NET48, NET60, NET80, SYSTEM_IO_PORTS, YAML_DOT_NET
from aacommpy.settings import AGITO_AACOMM, DEFAULT_NET_FRAMEWORK, NET_FRAMEWORK_CHOICES, NUGET_EXE, NUGET_EXE_PATH, TARGET_FOLDER
from aacommpy.settings import AACOMM_DLL, AACOMMSERVER

# Framework compatibility mapping (in order of preference)
# For net48, we can use net48 > net47 > net46 > net45 > netstandard2.0
FRAMEWORK_COMPAT = {
    'net48': ['net48', 'net47', 'net46', 'net45', 'netstandard2.0'],
    'net6.0': ['net6.0', 'netstandard2.1', 'netstandard2.0'],
    'net8.0': ['net8.0', 'net6.0', 'netstandard2.1', 'netstandard2.0'],
}

def dotnetfw(version: str = DEFAULT_NET_FRAMEWORK) -> None:
    if version not in NET_FRAMEWORK_CHOICES:
        raise ValueError(f".NET framework version {version} is not supported.")
    
    latest_version  = aacomm_nuget_version()
    source_dir      = os.path.join(TARGET_FOLDER, f"{AGITO_AACOMM}.{latest_version}")
    dest_dir        = os.path.dirname(__file__)    
    source_dir      = os.path.join(source_dir, 'lib', version)  
    dll_path        = os.path.join(source_dir, AACOMM_DLL)
    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find {AACOMM_DLL} in {source_dir}.")
    
    shutil.copy2(dll_path, dest_dir)
    print(f"The AAComm .NET target framework is {version}")

    #copy dependencies to the working directory according to the target version
    copy_nuget_dependencies(version, dest_dir)

    return None

def download_nuget_exe() -> None:
    os.makedirs(TARGET_FOLDER, exist_ok=True)  # Create the directory if it doesn't exist

    nuget_path = os.path.join(TARGET_FOLDER, NUGET_EXE)
    if os.path.exists(nuget_path):
        return None
    
    # Start the progress indicator in a separate thread
    progress_thread = threading.Thread(target=show_progress_indicator, args=(nuget_path,))
    progress_thread.start()

    # Perform the download
    print(f'downloading {NUGET_EXE}...')
    url = f'https://dist.nuget.org/win-x86-commandline/latest/{NUGET_EXE}'
    r = requests.get(url)
    with open(nuget_path, 'wb') as f:
        f.write(r.content)

    # Wait for the progress thread to complete
    progress_thread.join()

    print(f'{NUGET_EXE} downloaded successfully.')
    return None

def show_progress_indicator(nuget_path):
    while not os.path.exists(nuget_path):
        print('.', end='', flush=True)
        time.sleep(0.5)
    print('')

def download_aacomm_nuget(version: str = "", update: bool = False) -> None:
    # check if old version is installed and remove it if update is True
    installed = False
    for dirname in os.listdir(TARGET_FOLDER):
        if dirname.startswith(f'{AGITO_AACOMM}.') and os.path.isdir(os.path.join(TARGET_FOLDER, dirname)):
            installed = True
            old_version = dirname.split('.')[2:]
            old_version = '.'.join(old_version)
            break

    if update and installed:
        shutil.rmtree(os.path.join(TARGET_FOLDER, f'{AGITO_AACOMM}.{old_version}'))

    # Download the main package
    install_nuget_package(AGITO_AACOMM, version)

    # Extract the .nuspec file from the downloaded package
    aacomm_folder = f'{AGITO_AACOMM}.{aacomm_nuget_version()}'
    package_path = os.path.join(TARGET_FOLDER, aacomm_folder, f"{aacomm_folder}.nupkg")
    nuspec_path = extract_nuspec(package_path, TARGET_FOLDER)

    # Parse the .nuspec file to get the dependencies
    dependencies = parse_nuspec(nuspec_path)

    # Install each dependency with the exact version
    for id, version in dependencies:
        print(f'Installing {id} version {version}...')
        install_nuget_package(id, version)

    print('All dependencies installed.')

    # Copy the AACommServer.exe and AACommServerAPI.dll to the working directory
    aacs_dir = os.path.join(TARGET_FOLDER, aacomm_folder, 'build', AACOMMSERVER)
    dest_dir = os.path.dirname(__file__)
    shutil.copy2(os.path.join(aacs_dir, f'{AACOMMSERVER}.exe'), dest_dir)
    shutil.copy2(os.path.join(aacs_dir, f'{AACOMMSERVER}API.dll'), dest_dir)

    # copy AAComm.dll + dependencies to the working directory
    dotnetfw()

    return None

def install_nuget_package(id, version):
    nuget_cmd = [
        NUGET_EXE_PATH,
        'install',
        id,
        '-OutputDirectory', TARGET_FOLDER,
        '-Source', 'https://api.nuget.org/v3/index.json',
    ]

    if version != "":
        nuget_cmd.extend(['-Version', version])

    subprocess.run(nuget_cmd, check=True)

def extract_nuspec(package_path, output_dir):
    with zipfile.ZipFile(package_path, 'r') as zip_ref:
        nuspec_file = [f for f in zip_ref.namelist() if f.endswith('.nuspec')][0]
        zip_ref.extract(nuspec_file, output_dir)
    return os.path.join(output_dir, nuspec_file)

def parse_nuspec(nuspec_path):
    """Parse nuspec and return dependencies only for supported frameworks."""
    tree = ET.parse(nuspec_path)
    root = tree.getroot()
    namespace = {'default': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
    dependencies = set()

    # Map nuspec targetFramework to our supported frameworks
    supported_frameworks = {
        '.NETFramework4.8': True,
        'net6.0': True,
        'net8.0': True,
        # .NETFramework4.0 is NOT supported
    }

    for group in root.findall('.//default:dependencies/default:group', namespace):
        target_fw = group.get('targetFramework', '')
        if target_fw not in supported_frameworks:
            continue  # Skip unsupported frameworks like .NETFramework4.0

        for dependency in group.findall('default:dependency', namespace):
            id = dependency.get('id')
            version = dependency.get('version').strip('[]')
            dependencies.add((id, version))
    
    return list(dependencies)

def aacomm_nuget_version() -> str:
    if not os.path.exists(NUGET_EXE_PATH):
        raise RuntimeError("Nuget executable not found. Please run the 'install' command.")
    
    installed = False
    latest_version = None
    for dirname in os.listdir(TARGET_FOLDER):
        if dirname.startswith(f'{AGITO_AACOMM}.') and os.path.isdir(os.path.join(TARGET_FOLDER, dirname)):
            installed = True
            version = dirname.split('.')[2:]
            latest_version = '.'.join(version)
            print(f"The installed version of {AGITO_AACOMM} is {latest_version}.")
            break

    if not installed:
        raise RuntimeError(f'{AGITO_AACOMM} nuget package is not installed.')
    
    return latest_version


def parse_version(ver_str):
    """Parse version string into tuple for comparison."""
    try:
        return tuple(int(x) for x in ver_str.split('.'))
    except ValueError:
        return (0,)


def find_package_version(package_name, prefix_parts=1):
    """Find the highest version of a package in TARGET_FOLDER.

    prefix_parts: number of parts in package name (e.g., 1 for 'YamlDotNet', 3 for 'System.IO.Ports')
    """
    best_ver = None
    best_ver_tuple = (0,)

    for dir in os.listdir(TARGET_FOLDER):
        if dir.startswith(f'{package_name}.'):
            ver = '.'.join(dir.split('.')[prefix_parts:])
            ver_tuple = parse_version(ver)
            if ver_tuple > best_ver_tuple:
                best_ver = ver
                best_ver_tuple = ver_tuple

    return best_ver


def copy_nuget_dependencies(version, dest_dir):
    yaml_ver = find_package_version(YAML_DOT_NET, prefix_parts=1)
    sysio_ver = find_package_version(SYSTEM_IO_PORTS, prefix_parts=3)

    if yaml_ver:
        copy_dll(YAML_DOT_NET, yaml_ver, version, dest_dir)

    if version in [NET60, NET80] and sysio_ver:
        copy_dll(SYSTEM_IO_PORTS, sysio_ver, version, dest_dir)


def find_compatible_framework(package_dir, target_version):
    """Find the best compatible framework folder for the target version."""
    lib_dir = os.path.join(package_dir, 'lib')
    if not os.path.isdir(lib_dir):
        return None

    available = set(os.listdir(lib_dir))
    for compat in FRAMEWORK_COMPAT.get(target_version, [target_version]):
        if compat in available:
            return compat
    return None


def copy_dll(package_name, package_version, target_version, dest_dir):
    package_dir = os.path.join(TARGET_FOLDER, f"{package_name}.{package_version}")
    framework = find_compatible_framework(package_dir, target_version)

    if not framework:
        raise FileNotFoundError(f"No compatible framework found for {package_name} targeting {target_version}")

    dll_path = os.path.join(package_dir, "lib", framework, f"{package_name}.dll")
    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find {package_name}.dll in {dll_path}")

    shutil.copy2(dll_path, dest_dir)
    print(f"Copied {package_name}.dll ({framework})")