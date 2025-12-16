#!/usr/bin/env python3
"""Command-line interface for Dataform Inventory Exporter"""

import argparse
import sys
import urllib.request
import json
from . import __version__
from .exporter import DataformInventoryExporter


def check_for_updates():
    """Check PyPI for latest version and notify if update available"""
    try:
        # Quick timeout to avoid blocking the tool
        req = urllib.request.Request('https://pypi.org/pypi/dataform-checklist/json')
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            latest_version = data['info']['version']
            
            if latest_version != __version__:
                print("=" * 72)
                print(" UPDATE AVAILABLE")
                print(f"   Current version: {__version__}")
                print(f"   Latest version:  {latest_version}")
                print("   Run: pip install --upgrade dataform-checklist")
                print("=" * 72)
                print()
    except:
        # Silently fail if can't check - don't block the tool
        pass


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Export Dataform .sqlx files inventory to Excel deployment checklist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo
  %(prog)s /path/to/repo -v v1.01.00
  %(prog)s /path/to/repo -o /output/path -n MyRepo -v v2.00.00
        """
    )
    
    parser.add_argument(
        'repository_path',
        help='Path to the Dataform repository root directory'
    )
    parser.add_argument(
        '-o', '--output-path',
        help='Output directory for Excel file (default: repository root)',
        default=None
    )
    parser.add_argument(
        '-n', '--repository-name',
        help='Repository name for filename (default: auto-detected)',
        default=None
    )
    parser.add_argument(
        '-v', '--version',
        help='Version number for filename (optional, will use existing file version or v1.00.00)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Check for updates
    check_for_updates()
    
    # Create and run exporter
    try:
        exporter = DataformInventoryExporter(
            repository_path=args.repository_path,
            output_path=args.output_path,
            repository_name=args.repository_name,
            version=args.version
        )
        
        exporter.run()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
