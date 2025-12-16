"""
Command-line interface for serena-vbnet plugin.
"""

import click
import os
import sys
from pathlib import Path

from . import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Serena VB.NET Plugin - Adds Visual Basic .NET support to Serena"""
    pass


@main.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstallation even if already installed",
)
@click.option(
    "--build",
    is_flag=True,
    help="Build from source instead of downloading pre-built binaries",
)
def setup(force: bool, build: bool):
    """Install VB.NET language server and configure Serena"""
    from .installer import install_language_server, patch_serena

    click.echo("🚀 Serena VB.NET Setup")
    click.echo("=" * 50)

    # Step 1: Install language server
    click.echo("\n📦 Step 1: Installing Roslyn LanguageServer with VB.NET support...")

    try:
        install_language_server(force=force, build_from_source=build)
        click.echo("✅ Language server installed successfully")
    except Exception as e:
        click.echo(f"❌ Failed to install language server: {e}", err=True)
        sys.exit(1)

    # Step 2: Patch Serena
    click.echo("\n🔧 Step 2: Registering VB.NET with Serena...")

    try:
        patch_serena()
        click.echo("✅ Serena configured successfully")
    except Exception as e:
        click.echo(f"❌ Failed to configure Serena: {e}", err=True)
        sys.exit(1)

    click.echo("\n✨ Setup complete!")
    click.echo("\nNext steps:")
    click.echo("  1. cd /path/to/your/vbnet-project")
    click.echo("  2. serena init")
    click.echo("  3. Edit .serena/project.yml and add 'vbnet' to languages")
    click.echo("  4. serena start-mcp-server")


@main.command()
def verify():
    """Verify VB.NET installation"""
    from .installer import verify_installation

    click.echo("🔍 Verifying VB.NET installation...")
    click.echo("=" * 50)

    try:
        issues = verify_installation()

        if not issues:
            click.echo("\n✅ All checks passed! VB.NET is ready to use.")
            return 0
        else:
            click.echo("\n❌ Found issues:")
            for issue in issues:
                click.echo(f"  - {issue}")
            return 1

    except Exception as e:
        click.echo(f"❌ Verification failed: {e}", err=True)
        return 1


@main.command()
def update():
    """Update VB.NET language server to latest version"""
    from .installer import update_language_server

    click.echo("🔄 Updating VB.NET language server...")

    try:
        update_language_server()
        click.echo("✅ Update complete!")
    except Exception as e:
        click.echo(f"❌ Update failed: {e}", err=True)
        sys.exit(1)


@main.command()
@click.confirmation_option(
    prompt="Are you sure you want to uninstall VB.NET support?"
)
def uninstall():
    """Remove VB.NET support from Serena"""
    from .installer import uninstall_language_server, unpatch_serena

    click.echo("🗑️  Uninstalling VB.NET support...")

    # Remove language server
    try:
        uninstall_language_server()
        click.echo("✅ Language server removed")
    except Exception as e:
        click.echo(f"⚠️  Warning: {e}", err=True)

    # Unpatch Serena
    try:
        unpatch_serena()
        click.echo("✅ Serena configuration reverted")
    except Exception as e:
        click.echo(f"⚠️  Warning: {e}", err=True)

    click.echo("\n✅ Uninstall complete")


@main.command()
def info():
    """Show installation information"""
    from .installer import get_installation_info

    click.echo("ℹ️  Serena VB.NET Installation Info")
    click.echo("=" * 50)

    info = get_installation_info()

    click.echo(f"\nPlugin Version: {info['plugin_version']}")
    click.echo(f"Language Server: {info['ls_status']}")
    click.echo(f"Installation Path: {info['ls_path']}")
    click.echo(f"Serena Patched: {info['serena_patched']}")

    if info['ls_assemblies']:
        click.echo("\nVB.NET Assemblies:")
        for asm in info['ls_assemblies']:
            click.echo(f"  ✅ {asm}")


if __name__ == "__main__":
    main()
