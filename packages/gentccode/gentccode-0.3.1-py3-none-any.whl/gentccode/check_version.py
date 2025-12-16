import subprocess
import sys
import xmlrpc.client
import importlib.metadata


def get_latest_version(package_name):
    try:
        client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
        package_info = client.package_releases(package_name)
        if package_info:
            latest_version = package_info[0]
            return latest_version
        else:
            return None
    except Exception as e:
        # print(f"Error fetching version information for '{package_name}': {str(e)}")
        return None


def check_package_version(package_name):
    latest_version = get_latest_version(package_name)

    if latest_version is None:
        pass
    else:
        # 获取当前版本号。

        current_version = importlib.metadata.version(package_name)
        if current_version < latest_version:
            print(
                f"{package_name} is outdated. latest version is {current_version} -> {latest_version}."
            )
            print("upgrade using `gtc update`.")


def get_current_version(package_name):
    current_version = importlib.metadata.version(package_name)
    return current_version


def update_package(package_name):
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
        )
        current_version = get_current_version(package_name)
        print(
            f"{package_name} has been updated to the latest version: {current_version}"
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to update {package_name}: {e}")
