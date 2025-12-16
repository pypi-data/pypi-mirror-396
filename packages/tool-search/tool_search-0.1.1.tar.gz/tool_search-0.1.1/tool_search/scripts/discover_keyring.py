#!/usr/bin/env python3
"""Discover Factory's keyring key patterns.

Run this after authenticating with Linear via 'droid /mcp' to find
the exact keyring keys Factory uses for OAuth tokens.

Usage:
    python tool_search/scripts/discover_keyring.py

Prerequisites:
    1. Run 'droid' and type '/mcp'
    2. Connect to Linear and complete OAuth
    3. Exit droid and run this script
"""

import subprocess
import sys


def discover_macos() -> None:
    """List Factory-related keychain entries on macOS.

    Uses the security CLI to dump and search the macOS Keychain
    for entries related to Factory, MCP, Linear, etc.
    """
    print("=== macOS Keychain Discovery ===\n")

    patterns = ["factory", "mcp", "linear", "context7", "oauth"]

    for pattern in patterns:
        print(f"Searching for '{pattern}'...")
        try:
            result = subprocess.run(
                ["security", "dump-keychain"], capture_output=True, text=True, timeout=30
            )

            matches_found = False
            for line in result.stdout.split("\n"):
                if pattern.lower() in line.lower():
                    print(f"  {line.strip()}")
                    matches_found = True

            if not matches_found:
                print("  No matches found")
        except subprocess.TimeoutExpired:
            print("  Timeout while searching keychain")
        except FileNotFoundError:
            print("  'security' command not found")
        except Exception as e:
            print(f"  Error: {e}")

    print()


def discover_with_keyring() -> None:
    """Try common Factory keyring patterns using the Python keyring library.

    Attempts to read from various service/key combinations that
    Factory might use to store OAuth tokens.
    """
    print("=== Python Keyring Discovery ===\n")

    try:
        import keyring
    except ImportError:
        print("Error: keyring package not installed")
        print("Run: pip install keyring")
        return

    service_patterns = [
        "factory-mcp-oauth",
        "factory-mcp",
        "com.factory.cli.mcp",
        "factory",
        "com.factory.cli",
    ]

    key_patterns = [
        "https://mcp.linear.app/mcp",
        "mcp.linear.app",
        "linear",
        "linear.app",
        "https://context7.com/mcp",
        "context7.com",
        "context7",
    ]

    print(f"Keyring backend: {keyring.get_keyring()}\n")

    found_count = 0
    for service in service_patterns:
        for key in key_patterns:
            try:
                value = keyring.get_password(service, key)
                if value:
                    # Don't print full token, just confirm it exists
                    preview = value[:20] + "..." if len(value) > 20 else value
                    print(f"FOUND: service='{service}' key='{key}'")
                    print(f"       value starts with: {preview}\n")
                    found_count += 1
            except Exception:
                pass  # Silently skip errors

    if found_count == 0:
        print("No tokens found with known patterns.\n")
        print("Try authenticating first:")
        print("  1. Run 'droid'")
        print("  2. Type '/mcp'")
        print("  3. Select Linear and complete OAuth flow")
        print("  4. Exit and re-run this script")
    else:
        print(f"Found {found_count} token(s).")


def main() -> None:
    """Main entry point for keyring discovery."""
    print("Factory OAuth Token Discovery Script")
    print("=" * 40)
    print()
    print("Prerequisites:")
    print("  1. Run 'droid' and type '/mcp'")
    print("  2. Connect to Linear and complete OAuth")
    print("  3. Exit droid and run this script")
    print()

    if sys.platform == "darwin":
        discover_macos()
    else:
        print(f"Platform: {sys.platform} (macOS-specific discovery skipped)\n")

    discover_with_keyring()

    print()
    print("Discovery complete. Update SERVICE_PATTERNS in keyring_provider.py")
    print("with any patterns found above.")


if __name__ == "__main__":
    main()
