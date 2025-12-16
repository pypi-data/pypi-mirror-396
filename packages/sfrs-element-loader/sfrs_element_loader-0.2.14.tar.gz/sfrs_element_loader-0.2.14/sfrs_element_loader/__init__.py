import subprocess
import sys
import pkg_resources
import requests

PACKAGE_NAME = "sfrs-element-loader"

def check_and_update_package():
    try:
        print("Checking for new installations..")
        # Current installed version
        installed_version = pkg_resources.get_distribution(PACKAGE_NAME).version

        # Get latest version from PyPI
        resp = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=5)
        latest_version = resp.json()["info"]["version"]

        if installed_version != latest_version:
            print(f"Updating {PACKAGE_NAME} from {installed_version} to {latest_version}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME])
    except Exception as e:
        print(f"Could not check/update {PACKAGE_NAME}: {e}")

# Run on import
check_and_update_package()