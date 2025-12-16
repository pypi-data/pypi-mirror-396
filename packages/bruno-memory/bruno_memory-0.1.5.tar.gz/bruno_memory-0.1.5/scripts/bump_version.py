#!/usr/bin/env python3
"""Version bumping script for bruno-memory."""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

VersionPart = Literal["major", "minor", "patch"]


def get_current_version() -> str:
    """Get current version from git tags."""
    try:
        # Get the latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True
        )
        tag = result.stdout.strip()
        # Remove 'v' prefix if present
        version = tag[1:] if tag.startswith('v') else tag
        return version
    except subprocess.CalledProcessError:
        # No tags yet, start with 0.1.0
        print("No existing tags found, starting with 0.1.0")
        return "0.1.0"


def bump_version(current: str, part: VersionPart) -> str:
    """Bump the specified part of the version."""
    major, minor, patch = map(int, current.split("."))
    
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid version part: {part}")


def update_pyproject(new_version: str) -> None:
    """Update version in pyproject.toml (if static version exists)."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    
    # Check if version is static or dynamic
    if 'dynamic = ["version"]' in content or "dynamic = ['version']" in content:
        print(f"✓ Using dynamic versioning from git tags (v{new_version})")
        return
    
    # Update static version
    updated = re.sub(
        r'^version = "\d+\.\d+\.\d+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    if updated != content:
        pyproject.write_text(updated)
        print(f"✓ Updated pyproject.toml to version {new_version}")
    else:
        print(f"✓ Version in pyproject.toml unchanged (using git tags)")


def update_init(new_version: str) -> None:
    """Update version in __init__.py."""
    init_file = Path("bruno_memory/__init__.py")
    if not init_file.exists():
        print(f"! __init__.py not found, skipping")
        return
    
    content = init_file.read_text()
    
    # Update __version__ if it exists
    if '__version__' in content:
        updated = re.sub(
            r'^__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            content,
            flags=re.MULTILINE
        )
        init_file.write_text(updated)
        print(f"✓ Updated bruno_memory/__init__.py to version {new_version}")
    else:
        print(f"✓ No __version__ in __init__.py (using dynamic versioning)")


def create_git_tag(version: str, commit: bool = True) -> None:
    """Create git commit and tag for the version bump."""
    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    
    if commit and result.stdout.strip():
        # Add changed files
        subprocess.run(["git", "add", "-u"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Bump version to {version}"],
            check=True
        )
        print(f"✓ Created git commit for version {version}")
    elif commit:
        print(f"✓ No changes to commit (using git tag for versioning)")
    
    # Create the tag
    subprocess.run(
        ["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"],
        check=True
    )
    print(f"✓ Created git tag v{version}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bump bruno-memory version")
    parser.add_argument(
        "part",
        type=str,
        choices=["major", "minor", "patch"],
        help="Part of version to bump"
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Don't create git commit"
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Don't create git tag"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        current_version = get_current_version()
        new_version = bump_version(current_version, args.part)
        
        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        
        if args.dry_run:
            print("\nDry run - no changes made")
            return 0
        
        # Update files
        update_pyproject(new_version)
        update_init(new_version)
        
        # Create git commit and tag
        if not args.no_tag:
            create_git_tag(new_version, commit=not args.no_commit)
        
        print(f"\n✓ Successfully bumped version to {new_version}")
        print("\nNext steps:")
        print(f"  git push origin main")
        print(f"  git push origin v{new_version}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
