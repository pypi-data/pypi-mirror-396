"""
Installation and configuration logic for serena-vbnet.
"""

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import List, Dict, Any
import requests

from . import __version__

# Installation paths
SERENA_DIR = Path.home() / ".serena"
LS_DIR = SERENA_DIR / "language_servers" / "roslyn_vbnet"

# GitHub repository for pre-built binaries
GITHUB_REPO = "LaunchCG/roslyn-vbnet-languageserver"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def get_platform_rid() -> str:
    """Detect platform runtime identifier (RID)"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map to .NET RIDs
    if system == "linux":
        if machine in ["x86_64", "amd64"]:
            return "linux-x64"
        elif machine in ["aarch64", "arm64"]:
            return "linux-arm64"
    elif system == "darwin":
        if machine == "x86_64":
            return "osx-x64"
        elif machine in ["arm64", "aarch64"]:
            return "osx-arm64"
    elif system == "windows":
        if machine in ["amd64", "x86_64"]:
            return "win-x64"
        elif machine in ["arm64", "aarch64"]:
            return "win-arm64"

    raise RuntimeError(f"Unsupported platform: {system}/{machine}")


def download_prebuilt_binary() -> Path:
    """Download pre-built binary from GitHub Releases"""
    rid = get_platform_rid()
    print(f"Detected platform: {rid}")

    # Get latest release info
    print(f"Fetching latest release from {GITHUB_REPO}...")
    response = requests.get(GITHUB_API)
    response.raise_for_status()

    release_data = response.json()
    tag_name = release_data["tag_name"]
    print(f"Latest version: {tag_name}")

    # Find asset for this platform
    ext = "zip" if "win" in rid else "tar.gz"
    asset_name = f"roslyn-vbnet-{rid}.{ext}"

    asset = None
    for a in release_data["assets"]:
        if a["name"] == asset_name:
            asset = a
            break

    if not asset:
        raise RuntimeError(f"No pre-built binary found for {rid}")

    # Download
    download_url = asset["browser_download_url"]
    print(f"Downloading {asset_name}...")

    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    # Save to temp file
    temp_file = Path(f"/tmp/{asset_name}")
    with open(temp_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded to {temp_file}")
    return temp_file


def extract_binary(archive_path: Path, dest_dir: Path):
    """Extract downloaded binary to destination"""
    print(f"Extracting to {dest_dir}...")

    # Create destination
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Extract based on file type
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(dest_dir)
    else:  # .tar.gz
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(dest_dir)

    print("✅ Extraction complete")


def build_from_source():
    """Build Roslyn LanguageServer from source"""
    print("Building from source...")
    print("This will take 10-15 minutes...")

    # Check for .NET SDK
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Using .NET SDK: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            ".NET SDK not found. Please install .NET 8 SDK or later from https://dot.net"
        )

    # Get build script from GitHub
    script_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/scripts/build-roslyn-vbnet.sh"
    script_path = Path("/tmp/build-roslyn-vbnet.sh")

    print("Downloading build script...")
    response = requests.get(script_url)
    response.raise_for_status()

    script_path.write_text(response.text)
    script_path.chmod(0o755)

    # Run build
    rid = get_platform_rid()
    print(f"Building for {rid}...")

    result = subprocess.run(
        [str(script_path), rid],
        cwd="/tmp",
        check=True,
    )

    # Copy output
    source_dir = Path("/tmp/roslyn-build/output")
    if not source_dir.exists():
        raise RuntimeError("Build failed - output directory not found")

    LS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Copying to {LS_DIR}...")
    for item in source_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, LS_DIR / item.name)
        elif item.is_dir():
            shutil.copytree(item, LS_DIR / item.name, dirs_exist_ok=True)

    print("✅ Build complete")


def install_language_server(force: bool = False, build_from_source: bool = False):
    """Install VB.NET language server"""
    if LS_DIR.exists() and not force:
        print(f"Language server already installed at {LS_DIR}")
        print("Use --force to reinstall")
        return

    if LS_DIR.exists():
        print("Removing existing installation...")
        shutil.rmtree(LS_DIR)

    if build_from_source:
        build_from_source()
    else:
        try:
            archive_path = download_prebuilt_binary()
            extract_binary(archive_path, LS_DIR)
            archive_path.unlink()  # Clean up
        except Exception as e:
            print(f"⚠️  Failed to download pre-built binary: {e}")
            print("Falling back to build from source...")
            build_from_source()

    # Verify installation
    issues = verify_installation()
    if issues:
        raise RuntimeError(f"Installation incomplete: {', '.join(issues)}")


def find_serena_installation() -> Path:
    """Find Serena's Python package installation"""
    try:
        import solidlsp
        return Path(solidlsp.__file__).parent
    except ImportError:
        raise RuntimeError(
            "Serena not found. Please install: pip install serena-agent"
        )


def patch_serena():
    """Add VB.NET support to Serena's ls_config.py"""
    serena_path = find_serena_installation()
    ls_config_path = serena_path / "ls_config.py"

    if not ls_config_path.exists():
        raise RuntimeError(f"ls_config.py not found at {ls_config_path}")

    # Copy vbnet_language_server.py into Serena's solidlsp/language_servers directory
    solidlsp_path = serena_path / "solidlsp"
    if not solidlsp_path.exists():
        # Try parent directory structure
        solidlsp_path = serena_path.parent / "solidlsp"

    language_servers_path = solidlsp_path / "language_servers"
    if not language_servers_path.exists():
        raise RuntimeError(f"Language servers directory not found: {language_servers_path}")

    # Copy our vbnet_language_server.py
    import shutil
    from pathlib import Path

    source_file = Path(__file__).parent / "vbnet_language_server.py"
    dest_file = language_servers_path / "vbnet_language_server.py"

    if not dest_file.exists():
        print(f"Copying VB.NET language server to {dest_file}...")
        shutil.copy(source_file, dest_file)
        print("✅ VB.NET language server file installed")

    # Read current content
    content = ls_config_path.read_text()

    # Check if already patched
    if "VBNET" in content:
        print("Serena already configured for VB.NET")
        return

    print("Patching ls_config.py...")

    # Add VBNET enum entry
    if "class Language(str, Enum):" in content:
        # Find the enum and add VBNET
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "class Language(str, Enum):" in line:
                # Find a good place to insert (after existing entries)
                for j in range(i, len(lines)):
                    if "FSHARP" in lines[j]:
                        lines.insert(j + 1, '    VBNET = "vbnet"')
                        break
                break

        content = "\n".join(lines)

    # Add file matcher
    file_matcher_marker = "case self.FSHARP:"
    if file_matcher_marker in content:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if file_matcher_marker in line:
                # Insert after FSHARP case
                for j in range(i, len(lines)):
                    if "return FilenameMatcher" in lines[j]:
                        lines.insert(
                            j + 1,
                            '        case self.VBNET:\n            return FilenameMatcher("*.vb")',
                        )
                        break
                break
        content = "\n".join(lines)

    # Add language server class
    ls_class_marker = "case self.FSHARP:"
    if 'from solidlsp.language_servers.fsharp_language_server import FSharpLanguageServer' in content:
        lines = content.split("\n")

        # Add import
        for i, line in enumerate(lines):
            if "from solidlsp.language_servers.fsharp_language_server" in line:
                lines.insert(
                    i + 1,
                    "from solidlsp.language_servers.vbnet_language_server import VBNetLanguageServer",
                )
                break

        # Add case statement
        for i, line in enumerate(lines):
            if 'return FSharpLanguageServer' in line and 'case self.FSHARP:' in lines[i-1]:
                lines.insert(i + 1, "        case self.VBNET:")
                lines.insert(i + 2, "            return VBNetLanguageServer")
                break

        content = "\n".join(lines)

    # Write back
    ls_config_path.write_text(content)
    print("✅ Serena patched successfully")


def unpatch_serena():
    """Remove VB.NET support from Serena's ls_config.py"""
    serena_path = find_serena_installation()
    ls_config_path = serena_path / "ls_config.py"

    if not ls_config_path.exists():
        return

    content = ls_config_path.read_text()

    if "VBNET" not in content:
        print("Serena not patched")
        return

    # Remove VBNET lines
    lines = content.split("\n")
    filtered_lines = [
        line
        for line in lines
        if "VBNET" not in line and "VBNetLanguageServer" not in line and "serena_vbnet" not in line
    ]

    ls_config_path.write_text("\n".join(filtered_lines))
    print("✅ Serena unpat ched")


def verify_installation() -> List[str]:
    """Verify installation and return list of issues"""
    issues = []

    # Check language server directory
    if not LS_DIR.exists():
        issues.append("Language server directory not found")
        return issues

    # Check main DLL
    main_dll = LS_DIR / "Microsoft.CodeAnalysis.LanguageServer.dll"
    if not main_dll.exists():
        issues.append("Main language server DLL not found")

    # Check VB.NET assemblies
    vb_dlls = [
        "Microsoft.CodeAnalysis.VisualBasic.dll",
        "Microsoft.CodeAnalysis.VisualBasic.Features.dll",
        "Microsoft.CodeAnalysis.VisualBasic.Workspaces.dll",
    ]

    for dll in vb_dlls:
        dll_path = LS_DIR / dll
        if not dll_path.exists():
            issues.append(f"Missing VB.NET assembly: {dll}")

    # Check Serena patch
    try:
        serena_path = find_serena_installation()
        ls_config = (serena_path / "ls_config.py").read_text()
        if "VBNET" not in ls_config:
            issues.append("Serena not patched with VB.NET support")
    except Exception as e:
        issues.append(f"Cannot verify Serena patch: {e}")

    return issues


def update_language_server():
    """Update language server to latest version"""
    print("Checking for updates...")
    # For now, just reinstall
    install_language_server(force=True)


def uninstall_language_server():
    """Remove language server"""
    if not LS_DIR.exists():
        print("Language server not installed")
        return

    shutil.rmtree(LS_DIR)
    print(f"Removed {LS_DIR}")


def get_installation_info() -> Dict[str, Any]:
    """Get installation information"""
    info = {
        "plugin_version": __version__,
        "ls_path": str(LS_DIR),
        "ls_status": "Installed" if LS_DIR.exists() else "Not installed",
        "serena_patched": False,
        "ls_assemblies": [],
    }

    # Check for assemblies
    if LS_DIR.exists():
        vb_dlls = [
            "Microsoft.CodeAnalysis.VisualBasic.dll",
            "Microsoft.CodeAnalysis.VisualBasic.Features.dll",
            "Microsoft.CodeAnalysis.VisualBasic.Workspaces.dll",
        ]
        info["ls_assemblies"] = [dll for dll in vb_dlls if (LS_DIR / dll).exists()]

    # Check Serena patch
    try:
        serena_path = find_serena_installation()
        ls_config = (serena_path / "ls_config.py").read_text()
        info["serena_patched"] = "VBNET" in ls_config
    except:
        pass

    return info
