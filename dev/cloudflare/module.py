from utile.modules.Module import Module
import platform
import subprocess
import requests
import utile.utils
import sys
import os
import termcolor


def has_cloudflared_in_path():
    try:
        if "windows" in platform.platform():
            subprocess.check_output(["where", "cloudflared"])
        else:
            subprocess.check_output(["which", "cloudflared"])
        return True
    except:
        return False
        

def get_cloudflared_release():
    try:
        api_request = requests.get("https://api.github.com/repos/cloudflare/cloudflared/releases/latest")
    except:
        print("Could not fetch GitHub API")
        sys.exit(-1)
    if api_request.status_code != 200:
        print("Could not fetch last cloudflared version. Error HTTP {}".format(api_request.status_code))
        sys.exit(-1)
    try:
        json = api_request.json()
    except:
        print("Could not parse GitHub API response.")
        sys.exit(-1)
    return json


def get_latest_cloudflared_versions():
    json = get_cloudflared_release()
    return json["assets"], json["name"]


def get_appropriate_latest_cloudflared_version():
    arch = platform.machine()
    if arch == "":
        print("Arch cannot be determined.")
        sys.exit(-1)
    plat = platform.platform()
    
    versions, release_version = get_latest_cloudflared_versions()
    for version in versions:
        url = version.get("browser_download_url")
        splitted = url.split(".")
        filename, extension = splitted[-2], splitted[-1]
        if extension.lower() == "exe" and "windows" in plat.lower() and arch.lower() in filename.lower():
            return version, release_version
        if "linux" in plat.lower() and "linux" in extension.lower() and arch.lower() in extension.lower():
            return version, release_version
    raise RuntimeError("Could not determine proper version of cloudflared for your system.")


cloudflare_path = utile.utils.Directory.create_cache_directory("cloudflare")
cloudflared_path = os.path.join(cloudflare_path, "cloudflared.exe")
cloudflared_version_path = os.path.join(cloudflare_path, "cloudflared.exe.version")
def has_cloudflared_in_cache():
    if "cloudflared.exe" in os.listdir(cloudflare_path) and os.path.isfile(os.path.join(cloudflare_path, "cloudflared.exe")):
        size = os.path.getsize(cloudflared_path)
        if size < 100:
            return False
        return True
    return False


def download_latest_cloudflared_version():
    version, release_version = get_appropriate_latest_cloudflared_version()
    url = version["browser_download_url"]
    download_cloudflared(url, release_version)
    
def download_cloudflared(url: str, version: str):
    with utile.utils.create_spinner() as spinner:
        if os.path.isfile(cloudflared_version_path):
            spinner.text = "Cleaning..."
            os.unlink(cloudflared_version_path)
        
        spinner.text = "Downloading cloudflared from {}...".format(termcolor.colored(url, "green"))
        try:
            cloudflared_bytes = (requests.get(url).content)
            spinner.text = "Writing..."
            with open(cloudflared_path, "wb") as f:
                f.write(cloudflared_bytes)
            with open(cloudflared_version_path, "w") as f:
                f.write(version)
        except:
            spinner.text = ""
            spinner.fail("Couldn't download cloudflared.")
            sys.exit(-1)


def ensure_cloudflared(update_cloudflared: bool = False) -> str:
    """Ensures that cloudflared is installed. Installs it if needed. Returns the path to the executable or the command name if cloudflared is in the PATH

    Args:
        update_cloudflared (bool, optional): If cloudflared is in the cache, should we update it if a new version is available ? Defaults to False.

    Returns:
        str: _description_
    """

    if has_cloudflared_in_path():
        return "cloudflared"
    
    if has_cloudflared_in_cache():
        if update_cloudflared:
            try:
                with open(cloudflared_version_path, "r") as f:
                    version = f.read()
                    major, minor, fix = version.split(".")
                    major = int(major)
            except FileNotFoundError:
                major = -1
            latest_version = int(get_cloudflared_release()["name"].split(".")[0])
            if latest_version > major:
                print("Cloudflared needs to be updated.")
                download_latest_cloudflared_version()
                if not has_cloudflared_in_cache():
                    print("An error occurred while updating cloudflared.")
                    sys.exit(-1)
        return cloudflared_path
    
    download_latest_cloudflared_version()
    if not has_cloudflared_in_cache():
        print("An error occurred while downloading cloudflared.")
        sys.exit(-1)
    return cloudflared_path



def run_cloudflared_command(_arguments: list[str], should_update: bool = False):
    arguments = [ensure_cloudflared(should_update)]
    for arg in _arguments:
        arguments.append(arg)
    subprocess.check_output(arguments)


class Execute:
    def __init__(self, should_update_cloudflared: bool = False) -> None:
        self.should_update_cloudflared: bool = should_update_cloudflared
    def create_tunnel(self, route_to: str):
        ensure_cloudflared(self.should_update_cloudflared)
        run_cloudflared_command(["tunnel", "--url", route_to])


def execute():
    if not "windows" in platform.platform().lower():
        return print("Cloudflare module is currently only compatible with windows systems. Sorry !")
    return Execute


MODULE = execute
