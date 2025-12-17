"""cl-wrangler: Switch between multiple Cloudflare/Wrangler accounts."""

import os
import platform
import stat
import subprocess
import sys
import tarfile
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

__version__ = "0.2.1"

REPO = "groo-dev/cl-wrangler"


def get_platform_info():
    """Get platform and architecture for binary download."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture
    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    # Normalize OS
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    elif system == "windows":
        os_name = "windows"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    return os_name, arch


def get_binary_path():
    """Get the path where the binary should be stored."""
    cache_dir = Path.home() / ".cache" / "cl-wrangler"
    cache_dir.mkdir(parents=True, exist_ok=True)

    os_name, _ = get_platform_info()
    binary_name = "cl.exe" if os_name == "windows" else "cl"

    return cache_dir / binary_name


def download_binary():
    """Download the cl binary for the current platform."""
    os_name, arch = get_platform_info()
    binary_path = get_binary_path()

    # Determine archive name
    if os_name == "windows":
        archive_name = f"cl_{os_name}_{arch}.zip"
    else:
        archive_name = f"cl_{os_name}_{arch}.tar.gz"

    url = f"https://github.com/{REPO}/releases/download/v{__version__}/{archive_name}"

    print(f"Downloading cl v{__version__} for {os_name}/{arch}...")

    try:
        with urlopen(url, timeout=60) as response:
            data = BytesIO(response.read())
    except Exception as e:
        raise RuntimeError(f"Failed to download binary from {url}: {e}")

    # Extract binary
    binary_name = "cl.exe" if os_name == "windows" else "cl"

    if os_name == "windows":
        with zipfile.ZipFile(data) as zf:
            for name in zf.namelist():
                if name.endswith(binary_name):
                    with zf.open(name) as src, open(binary_path, "wb") as dst:
                        dst.write(src.read())
                    break
    else:
        with tarfile.open(fileobj=data, mode="r:gz") as tf:
            for member in tf.getmembers():
                if member.name.endswith(binary_name):
                    f = tf.extractfile(member)
                    if f:
                        with open(binary_path, "wb") as dst:
                            dst.write(f.read())
                    break

    # Make executable on Unix
    if os_name != "windows":
        binary_path.chmod(binary_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"Installed cl to {binary_path}")
    return binary_path


def ensure_binary():
    """Ensure the binary exists, downloading if necessary."""
    binary_path = get_binary_path()

    # Check if binary exists and matches version
    version_file = binary_path.parent / ".version"

    if binary_path.exists() and version_file.exists():
        cached_version = version_file.read_text().strip()
        if cached_version == __version__:
            return binary_path

    # Download binary
    download_binary()

    # Save version
    version_file.write_text(__version__)

    return binary_path


def main():
    """Main entry point - run the cl binary."""
    try:
        binary_path = ensure_binary()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Run the binary with all arguments
    try:
        result = subprocess.run([str(binary_path)] + sys.argv[1:])
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error running cl: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
