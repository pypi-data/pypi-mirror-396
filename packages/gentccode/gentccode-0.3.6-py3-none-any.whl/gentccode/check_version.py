import subprocess
import sys
import json
import urllib.request
import importlib.metadata
from packaging.version import Version


def get_latest_version(package_name) -> str:
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except Exception as e:
        # print(f"Error fetching version information for '{package_name}': {str(e)}")
        return ""


def check_package_version(package_name):
    latest_version = get_latest_version(package_name)

    if latest_version is "":
        print(f"Could not fetch latest version for {package_name}.")
    else:
        # 获取当前版本号。
        try:
            current_version = importlib.metadata.version(package_name)
            if Version(current_version) < Version(latest_version):
                print(
                    f"{package_name} is outdated. Current version: {current_version}, latest version: {latest_version}."
                )
                print("Upgrade using `gtc update`.")
        except importlib.metadata.PackageNotFoundError:
            print(f"Package {package_name} is not installed.")


def get_current_version(package_name):
    try:
        current_version = importlib.metadata.version(package_name)
        return current_version
    except importlib.metadata.PackageNotFoundError:
        return None


def update_package(package_name):
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
        )
        current_version = get_current_version(package_name)
        if current_version:
            print(
                f"{package_name} has been updated to the latest version: {current_version}"
            )
        else:
            print(f"Updated {package_name}, but could not retrieve current version.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update {package_name}: {e}")
